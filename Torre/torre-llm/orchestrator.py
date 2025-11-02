import os, json
from pathlib import Path
from typing import Dict, Any, List, Tuple
from .adapters.run_lint import run_lint
from .adapters.run_tests import run_tests
from .adapters.run_build import run_build
from .strategies.playbook_simple import propose_patch
from .utils.diff_utils import make_new_file_diff, join_unified_diffs, validate_unified_diff
from .client import ingest_report, get_pipeline_state, write_pipeline_state
from importlib import import_module
from .code_index import build_code_index, write_index_json, make_overview_md
from .logic.aristotelian import verify_invariants
from .strategies import ts_codemods as _ts_codemods
from .strategies.ab_select import Candidate, make_candidate, pick_best
from .utils.decode import load_decode_profiles, choose_profiles

ROOT = Path(os.getenv("REPO_ROOT", ".")).resolve()
WS = os.getenv("TORRE_WS", "default")

def classify_errors(lint: Dict[str, Any], tests: Dict[str, Any], build: Dict[str, Any]) -> Dict[str, Any]:
    classes = []
    if not lint.get("ok", True): classes.append("lint")
    if not tests.get("ok", True): classes.append("tests")
    if not build.get("ok", True): classes.append("build")
    return {"classes": classes, "lint": lint, "tests": tests, "build": build}

def guardrails_diff(diff: str) -> None:
    if not validate_unified_diff(diff):
        raise RuntimeError("validate_unified_diff: falhou")
    forbidden = ("/.env", "/.ssh/", ".pem", "id_rsa", "secrets.")
    for f in forbidden:
        if f in diff:
            raise RuntimeError(f"diff inválido: toca em ficheiro sensível ({f})")

def score_patch(metrics: Dict[str, Any]) -> float:
    """Calcula score simples do patch baseado nas métricas."""
    score = 0.0
    if metrics.get("apply_clean"): score += 1.0
    if metrics.get("lint_clean"): score += 0.5
    if metrics.get("tests_pass"): score += 0.5
    return score

def main() -> None:
    # Perfis de decodificação (determinismo e A/B); robusto a ausência de PyYAML
    _decode_cfg = load_decode_profiles()
    _profile_main, _profile_ab = choose_profiles(_decode_cfg)

    # 1) coletar erros
    lint = run_lint(ROOT)
    tests = run_tests(ROOT)
    build = run_build(ROOT)
    classification = classify_errors(lint, tests, build)

    # 1.1) Indexar código (RAG-of-Code mínimo)
    try:
        idx = build_code_index(ROOT)
        write_index_json(ROOT, idx)
        index_overview = make_overview_md(idx)
    except Exception:
        idx = {"files_indexed": 0, "symbols": 0}
        index_overview = "# INDEX_OVERVIEW — falha ao gerar índice\n"

    # 2) Propor patch mínimo (docs) com base nos erros
    file_changes: List[Tuple[str, str]] = propose_patch(ROOT, classification)

    # 3) Se não houver mudanças, criar no máximo um README de progresso (idempotente)
    if not file_changes:
        onboarding_path = "torre-llm/ONBOARDING.md"
        content = (
            "# Torre LLM-Engenheira — Progresso\n\n"
            "- Ciclo inicial: esqueleto criado.\n"
            "- Próximo passo: executar orquestrador em CI para gerar patch baseado nos erros reais.\n"
        )
        file_changes = [(onboarding_path, content)]

    # 3.1) Anexar EVIDENCE.md com comandos e tails de logs (markdown)
    try:
        from .evidence import make_evidence
        note = f"index: files={idx.get('files_indexed',0)}, symbols={idx.get('symbols',0)}"
        evidence_md = make_evidence(classification, [p for (p, _) in file_changes], notes=note)
        file_changes.append(("torre-llm/EVIDENCE.md", evidence_md))
    except Exception:
        pass

    # 3.2) Adicionar overview do índice ao patch
    file_changes.append(("torre-llm/INDEX_OVERVIEW.md", index_overview))

    # 4) Construir diffs (novos ficheiros) para docs/evidence/index
    base_diffs = [make_new_file_diff(Path(p), c) for (p, c) in file_changes]

    # Recolher CANDIDATOS de código (ficheiros existentes) — A/B
    candidates: List[Candidate] = []

    # A) Auto-fix opcional
    try:
        af = import_module(".strategies.autofix_base_shim", package=__package__)
        extra = af.generate_diffs(ROOT, classification) or []
        for d in extra:
            c = make_candidate("autofix_base_shim", d)
            if c: candidates.append(c)
    except Exception:
        pass

    # B) Codemods TS v1 (AST preferido; fallback Python)
    try:
        extra = _ts_codemods.generate_diffs(ROOT, classification) or []
        for d in extra:
            c = make_candidate("ts_codemods", d)
            if c: candidates.append(c)
    except Exception:
        pass

    # Se não houver candidatos, seguimos só com docs
    diffs = list(base_diffs)

    # Se nada para fazer, abortar de forma limpa
    if not diffs and not candidates:
        print(json.dumps({"metrics": {"apply_clean": False}, "summary": "sem alterações"}))
        return

    # 4.1) A/B + score (v1): escolher 1 candidato (menor diff_size)
    ab_meta = {"ab_candidates": 0, "ab_winner": None}
    if candidates:
        winner, meta = pick_best(candidates)
        ab_meta.update(meta)
        if winner:
            diffs.append(winner.diff)  # concatenamos só o vencedor

    unified = join_unified_diffs(diffs)
    guardrails_diff(unified)

    # 4) validate → dry_run → apply
    v_ok = ingest_report(WS, "validate", unified, "text/plain")
    if not v_ok: raise RuntimeError("validate falhou")
    d_ok = ingest_report(WS, "dry_run", unified, "text/plain")
    if not d_ok: raise RuntimeError("dry_run falhou")
    a_ok = ingest_report(WS, "apply", unified, "text/plain")

    # 5) Métricas, score e invariantes lógicos
    metrics = {
        "apply_clean": bool(a_ok),
        "lint_clean": lint.get("ok", False),
        "tests_pass": tests.get("ok", False),
        "diff_size": len(unified.splitlines()),
        "classes": classification.get("classes", []),
        "decode_profile": _profile_main,
        "decode_profile_ab": _profile_ab,
    }
    try:
        metrics["score_patch"] = score_patch(metrics)
    except Exception:
        metrics["score_patch"] = 0.0
    metrics.update(ab_meta)  # ab_candidates, ab_winner

    try:
        logic = verify_invariants(
            classification=classification,
            validate_ok=bool(v_ok),
            dry_ok=bool(d_ok),
            apply_ok=bool(a_ok),
            metrics=metrics,
        )
        metrics["logic_proofs"] = len(logic.get("proofs", []))
        metrics["logic_violations"] = logic.get("violations", [])
    except Exception:
        metrics["logic_proofs"] = 0
        metrics["logic_violations"] = ["erro ao verificar invariantes"]

    print(json.dumps({"metrics": metrics, "summary": "patch aplicado" if a_ok else "patch não aplicado"}))

    # Atualizar estado se apply ok
    if a_ok:
        state = get_pipeline_state(WS)
        state["last_apply"] = {"ok": True, "metrics": metrics}
        write_pipeline_state(state)

if __name__ == "__main__":
    main()
