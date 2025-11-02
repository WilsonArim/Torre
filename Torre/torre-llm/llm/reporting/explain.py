from __future__ import annotations
from typing import Dict, Any, List

def build_justification(analysis: Dict[str, Any], lenses: List[str] | None = None) -> str:
    lenses = lenses or ["ARISTÓTELES", "DIJKSTRA", "HOARE", "KNUTH", "SALTZER"]
    v = analysis.get("violations", [])
    proofs = analysis.get("proofs", [])
    lines = []
    lines.append("# report.md — Justificativa (Fase 3)")
    lines.append("")
    lines.append("## Lentes aplicadas")
    lines.append("- " + ", ".join(lenses))
    lines.append("")
    if not v:
        lines.append("## Guardrails")
        lines.append("- Sem violações. Patch segue como **aplicável**.")
    else:
        lines.append("## Guardrails")
        for item in v[:20]:
            lines.append(f"- [{item['severity']}] {item['kind']} — {item['path']}: {item['msg']}")
    lines.append("")
    if proofs:
        lines.append("## Provas/Princípios")
        for p in proofs:
            lines.append(f"- {p}")
    lines.append("")
    lines.append("## Nota")
    lines.append("Alterações mínimas e reversíveis. Caso haja *advisories*, recomenda-se refino subsequente.")
    lines.append("")
    return "\n".join(lines)
