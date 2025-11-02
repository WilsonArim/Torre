from __future__ import annotations
from typing import Any, Dict, List

# [ARISTÓTELES] Guardrails práticos para runtime:
# - Não-contradição: não pode haver p ∧ ¬p
# - Terceiro excluído: métricas booleanas ∈ {True, False}
# - Silogismo operacional: (validate ∧ dry_run) ⇒ apply

def _implies(p: bool, q: bool) -> bool:
    return (not p) or q

def _bool(v: Any) -> bool | None:
    if v is True: return True
    if v is False: return False
    return None

def verify_invariants(
    classification: Dict[str, Any],
    validate_ok: bool,
    dry_ok: bool,
    apply_ok: bool,
    metrics: Dict[str, Any],
) -> Dict[str, Any]:
    proofs: List[str] = []
    violations: List[str] = []

    # 1) Silogismo operacional: (validate ∧ dry_run) ⇒ apply
    if _implies(validate_ok and dry_ok, apply_ok):
        proofs.append("Se validate && dry_run, então apply não viola as regras (modus ponens).")
    else:
        violations.append("Violação: validate && dry_run verdadeiros mas apply==False.")

    # 2) Coerência entre classification e metrics (não-contradição)
    lint_ok = bool((classification.get("lint") or {}).get("ok", False))
    tests_ok = bool((classification.get("tests") or {}).get("ok", False))
    m_lint = _bool(metrics.get("lint_clean"))
    m_tests = _bool(metrics.get("tests_pass"))
    if m_lint is None:
        violations.append("Lei do terceiro excluído violada: metrics.lint_clean ∉ {True, False}.")
    else:
        # Aceitamos pequenas divergências em cenários parciais, mas sinalizamos
        if m_lint and not lint_ok:
            violations.append("Contradição: metrics.lint_clean=True mas classification.lint.ok=False.")
        elif (not m_lint) and lint_ok:
            violations.append("Contradição: lint.ok=True mas metrics.lint_clean=False.")
        else:
            proofs.append("Coerência: lint_clean ↔ classification.lint.ok.")
    if m_tests is None:
        violations.append("Lei do terceiro excluído violada: metrics.tests_pass ∉ {True, False}.")
    else:
        if m_tests and not tests_ok:
            violations.append("Contradição: metrics.tests_pass=True mas classification.tests.ok=False.")
        elif (not m_tests) and tests_ok:
            violations.append("Contradição: tests.ok=True mas metrics.tests_pass=False.")
        else:
            proofs.append("Coerência: tests_pass ↔ classification.tests.ok.")

    # 3) Booleans essenciais obedecem ao terceiro excluído
    for k in ("apply_clean", "lint_clean", "tests_pass"):
        v = metrics.get(k, None)
        if v not in (True, False):
            violations.append(f"Lei do terceiro excluído violada: metrics.{k} ∉ {{True, False}}.")
        else:
            proofs.append(f"'{k}' ∈ {{True, False}}.")

    return {"proofs": proofs, "violations": violations}
