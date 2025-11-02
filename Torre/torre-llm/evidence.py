from __future__ import annotations
from typing import Dict, Any, List
from datetime import datetime

def make_evidence(classification: Dict[str, Any], changed_files: List[str], notes: str = "") -> str:
    """
    Gera EVIDENCE.md com comandos executados e resumo da classificação.
    """
    lines = [
        "# EVIDENCE — Torre LLM-Engenheira",
        "",
        f"*timestamp*: {datetime.now().isoformat()}",
        f"*files_changed*: {len(changed_files)}",
        "",
        "## Classificação de Erros",
    ]
    
    classes = classification.get("classes", [])
    if classes:
        lines.append(f"- Classes detetadas: {', '.join(classes)}")
    else:
        lines.append("- Sem erros detetados")
    
    # Adicionar resumos dos adapters
    for key in ("lint", "tests", "build"):
        data = classification.get(key, {})
        if data:
            ok = data.get("ok", False)
            summary = data.get("summary", "")
            lines.append(f"- {key}: {'✅' if ok else '❌'} {summary[:100]}...")
    
    if changed_files:
        lines.extend([
            "",
            "## Ficheiros Alterados",
        ])
        for f in changed_files:
            lines.append(f"- `{f}`")
    
    if notes:
        lines.extend([
            "",
            "## Notas",
            notes
        ])
    
    lines.append("")  # final newline
    return "\n".join(lines)
