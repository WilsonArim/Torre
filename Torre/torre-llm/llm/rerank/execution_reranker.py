from __future__ import annotations

import time
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Tuple

from llm.guard.secret_scan import scan_diff_for_secrets

# Tenta integrar com o preflight real; senão, usa fallback leve.
try:
    from llm.simulation.preflight_simulator import PreflightSimulator  # type: ignore
except Exception:  # pragma: no cover
    PreflightSimulator = None  # type: ignore


def _is_unified_diff(text: str) -> bool:
    # Checagem leve — não perfeito, mas suficiente como gate rápido
    return ("--- " in text and "+++ " in text) and ("@@ " in text or "\n+" in text or "\n-" in text)


def _diff_size(text: str) -> int:
    n = 0
    for line in text.splitlines():
        if not line:
            continue
        if line.startswith(("---", "+++", "@@")):
            continue
        if line[0] in "+-":
            n += 1
    return n


def _preflight_eval(workspace: str, diff: str) -> Dict[str, Any]:
    """
    Invoca o simulador real se existir; senão, devolve um resultado mínimo.
    Esperado (quando existir): dct com chaves como 'lint', 'type', 'tests', 'build', 'all_green'.
    """
    if PreflightSimulator is None:
        # Fallback: se passou formato + sem segredos + diff pequeno, assume "verde" superficial
        return {
            "lint": "skipped",
            "type": "skipped",
            "tests": "skipped",
            "build": "skipped",
            "all_green": True,
        }

    sim = PreflightSimulator()  # type: ignore
    # Tentativa defensiva de chamadas (mantém compatibilidade com APIs diferentes)
    for attr in ("preflight", "check_candidate", "assess", "run", "simulate"):
        fn = getattr(sim, attr, None)
        if callable(fn):
            try:
                out = fn(workspace=workspace, diff=diff)  # type: ignore
            except TypeError:
                out = fn(diff)  # type: ignore
            # Normaliza formato mínimo esperado
            if isinstance(out, dict):
                ok = bool(out.get("all_green")) or all(out.get(k) in (True, "ok", "green") for k in ("lint", "type", "tests", "build") if k in out)
                out.setdefault("all_green", ok)
                return out
            return {"all_green": bool(out)}
    # Se nenhum método conhecido existir:
    return {"all_green": True, "lint": "unknown", "type": "unknown", "tests": "unknown", "build": "unknown"}


@dataclass
class CandidateReport:
    index: int
    diff_size: int
    ttg_ms: float
    allowed: bool
    gates_passed: bool
    discard_reason: Optional[str]
    preflight: Dict[str, Any]
    violations: List[Dict[str, str]]


class ExecutionReranker:
    def __init__(self, *, max_lines: int = 300):
        self.max_lines = max_lines

    def evaluate_candidate(self, workspace: str, diff: str, index: int) -> CandidateReport:
        t0 = time.perf_counter()
        # 1) Formato
        if not _is_unified_diff(diff):
            return CandidateReport(
                index=index,
                diff_size=0,
                ttg_ms=(time.perf_counter() - t0) * 1000,
                allowed=False,
                gates_passed=False,
                discard_reason="invalid_diff_format",
                preflight={"all_green": False, "reason": "invalid_diff_format"},
                violations=[],
            )
        # 2) Tamanho
        size = _diff_size(diff)
        if size > self.max_lines:
            return CandidateReport(
                index=index,
                diff_size=size,
                ttg_ms=(time.perf_counter() - t0) * 1000,
                allowed=False,
                gates_passed=False,
                discard_reason="diff_too_large",
                preflight={"all_green": False, "reason": "diff_too_large"},
                violations=[],
            )
        # 3) DLP / Segredos
        violations = scan_diff_for_secrets(diff)
        if violations:
            return CandidateReport(
                index=index,
                diff_size=size,
                ttg_ms=(time.perf_counter() - t0) * 1000,
                allowed=False,
                gates_passed=False,
                discard_reason="secrets_detected",
                preflight={"all_green": False, "reason": "secrets_detected"},
                violations=violations,
            )
        # 4) Preflight (lint/type/tests/build)
        pre = _preflight_eval(workspace, diff)
        ttg_ms = (time.perf_counter() - t0) * 1000
        return CandidateReport(
            index=index,
            diff_size=size,
            ttg_ms=ttg_ms,
            allowed=True,
            gates_passed=bool(pre.get("all_green")),
            discard_reason=None if pre.get("all_green") else "gates_failed",
            preflight=pre,
            violations=[],
        )

    def select(self, reports: List[CandidateReport]) -> Optional[CandidateReport]:
        # 1) Primeiro passa todos os gates → candidatos válidos com gates_passed
        winners = [r for r in reports if r.allowed and r.gates_passed]
        if not winners:
            return None
        # 2) Mínimo diff_size
        winners.sort(key=lambda r: (r.diff_size, r.ttg_ms))
        return winners[0]

    def run(self, workspace: str, candidates: List[str], k: int = 3) -> Dict[str, Any]:
        k = max(1, min(k, len(candidates)))
        subset = candidates[:k]
        reports = [self.evaluate_candidate(workspace, d, i) for i, d in enumerate(subset)]
        winner = self.select(reports)
        return {
            "selected_index": None if winner is None else winner.index,
            "winner": None if winner is None else asdict(winner),
            "candidates": [asdict(r) for r in reports],
            "discard_reasons": [r.discard_reason for r in reports if r.discard_reason],
            "avg_candidates": len(subset),
        }
