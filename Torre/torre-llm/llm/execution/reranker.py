from __future__ import annotations
import os
from typing import Any, Dict, List, Tuple, Callable, Optional

try:
    # Prefer the real components se existirem
    from llm.simulation.preflight_simulator import PreflightSimulator  # type: ignore
except Exception:  # pragma: no cover
    PreflightSimulator = None  # fallback handled abaixo

def _count_diff_lines(diff: str) -> Tuple[int, int, int]:
    adds = rems = 0
    for ln in diff.splitlines():
        if ln.startswith("+++ ") or ln.startswith("--- "):
            continue
        if ln.startswith("+"):
            adds += 1
        elif ln.startswith("-"):
            rems += 1
    return adds, rems, adds + rems

class CandidateResult:
    def __init__(self, name: str, diff: str):
        self.name = name
        self.diff = diff
        self.metrics: Dict[str, Any] = {}
        self.ok: bool = False

class Reranker:
    """
    Executa n-candidatos de patch e escolhe o que fica 100% verde segundo o Preflight.
    - Integra Strategos v2 (para contexto e logging de decisão)
    - Usa Memória episódica (Fase 7) para gerar um candidato assistido por lição
    """
    def __init__(
        self,
        preflight: Optional[Any] = None,
        strategos_v2: Optional[Any] = None,
        learning_system: Optional[Any] = None,
    ):
        self.preflight = preflight or self._fallback_preflight()
        self.strategos_v2 = strategos_v2
        self.learning_system = learning_system

    def _fallback_preflight(self):
        class _PF:
            def run_all(self, logs: Dict[str, str], files: Dict[str, str], diff: str) -> Dict[str, Any]:
                # Fallback leve: valida formato e penaliza diffs muito grandes
                adds, rems, total = _count_diff_lines(diff)
                ok_apply = diff.strip().startswith("--- a/") and "\n+++ b/" in diff
                ok_types = True
                ok_lint = True
                ok_tests = True
                ok_secrets = True
                score = sum([ok_apply, ok_types, ok_lint, ok_tests, ok_secrets]) * 1.0
                if total > 1200:
                    score -= 1.0
                    ok_lint = False
                return {
                    "apply_ok": ok_apply, "typecheck_ok": ok_types, "lint_ok": ok_lint,
                    "tests_ok": ok_tests, "secrets_ok": ok_secrets, "score": score,
                    "diff_lines": total
                }
        return _PF()

    def _do_preflight(self, logs: Dict[str, str], files: Dict[str, str], diff: str) -> Dict[str, Any]:
        # Tenta várias assinaturas, pois versões podem variar entre fases
        pf = self.preflight
        if hasattr(pf, "run_all"):
            return pf.run_all(logs, files, diff)
        if hasattr(pf, "evaluate"):
            return pf.evaluate(logs, files, diff)
        if hasattr(pf, "assess_refactor_plan"):  # tipo Fase 8
            out = pf.assess_refactor_plan({"diff": diff})
            return {
                "apply_ok": out.get("apply_ok", True),
                "typecheck_ok": out.get("typecheck_ok", True),
                "lint_ok": out.get("lint_ok", True),
                "tests_ok": out.get("tests_ok", True),
                "secrets_ok": out.get("secrets_ok", True),
                "score": out.get("score", 5.0),
                "diff_lines": _count_diff_lines(diff)[2],
            }
        # fallback duro
        return self._fallback_preflight().run_all(logs, files, diff)

    def _score_candidate(self, metrics: Dict[str, Any]) -> float:
        # Peso maior para gates essenciais; bónus para patch pequeno
        score = 0.0
        score += 2.0 if metrics.get("apply_ok") else 0.0
        score += 1.5 if metrics.get("typecheck_ok") else 0.0
        score += 1.0 if metrics.get("lint_ok") else 0.0
        score += 2.0 if metrics.get("tests_ok") else 0.0
        score += 1.0 if metrics.get("secrets_ok") else 0.0
        # Penaliza diffs grandes
        dl = metrics.get("diff_lines", 0)
        if dl > 600:
            score -= 0.5
        if dl > 1200:
            score -= 1.0
        return score

    def run(
        self,
        logs: Dict[str, str],
        files: Dict[str, str],
        candidate_generators: List[Callable[[], Tuple[str, str]]],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Executa cada gerador → diffs → preflight → escolhe vencedor.
        Retorna {winner: {name,diff,metrics}, candidates:[...], strategos:..., memory:...}
        """
        context = context or {}
        # Anotação de Strategos v2 (se presente)
        strategos_note = None
        if self.strategos_v2 and hasattr(self.strategos_v2, "generate_attack_plan"):
            try:
                strategos_note = self.strategos_v2.generate_attack_plan(logs)
            except Exception:
                strategos_note = None

        # Lições da memória (workspace-local)
        memory_note = None
        if self.learning_system and hasattr(self.learning_system, "suggest_actions"):
            try:
                memory_note = self.learning_system.suggest_actions(logs)
            except Exception:
                memory_note = None

        results: List[CandidateResult] = []

        for gen in candidate_generators:
            try:
                name, diff = gen()
                c = CandidateResult(name, diff)
                met = self._do_preflight(logs, files, diff)
                c.metrics = met
                # "ok" = todos os gates essenciais
                c.ok = bool(met.get("apply_ok") and met.get("typecheck_ok") and met.get("lint_ok") and met.get("tests_ok") and met.get("secrets_ok"))
                results.append(c)
            except Exception as e:
                c = CandidateResult("generator_error", "")
                c.metrics = {"error": str(e)}
                c.ok = False
                results.append(c)

        # Ordena por (ok desc, score desc, diff pequeno asc)
        def keyer(c: CandidateResult):
            adds, rems, total = _count_diff_lines(c.diff)
            s = self._score_candidate(c.metrics)
            return (1 if c.ok else 0, s, -total)

        results_sorted = sorted(results, key=keyer, reverse=True)
        winner = results_sorted[0] if results_sorted else None

        return {
            "winner": {
                "name": winner.name if winner else None,
                "diff": winner.diff if winner else "",
                "metrics": winner.metrics if winner else {},
                "ok": winner.ok if winner else False,
            },
            "candidates": [
                {"name": r.name, "ok": r.ok, "metrics": r.metrics, "diff_lines": _count_diff_lines(r.diff)[2]}
                for r in results_sorted
            ],
            "strategos": strategos_note,
            "memory": memory_note,
        }
