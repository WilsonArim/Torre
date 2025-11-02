from pathlib import Path
from typing import Dict, Any, List, Tuple
from . import pick_strategy
try:
    from ..parsers.error_patterns import extract_hints
except ImportError:
    # Fallback para quando executado diretamente
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from parsers.error_patterns import extract_hints

README = """# Torre LLM-Engenheira — Estratégia mínima
Este patch é idempotente e não toca em segredos. Em ciclos seguintes, substituir por correções cirúrgicas reais.
"""

def propose_patch(root: Path, classification: Dict[str, Any]) -> List[Tuple[str, str]]:
    """
    Mantém o comportamento idempotente e acrescenta ADVICE.md com dicas
    baseadas nos summaries de lint/tests/build.
    """
    changes: List[Tuple[str, str]] = []

    # 1) marcador de estratégia (idempotente)
    strat = Path("torre-llm/STRATEGY.md")
    if not (root / strat).exists():
        changes.append((str(strat), README))

    # 2) gerar conselhos acionáveis a partir dos logs
    summaries = []
    for key in ("lint", "tests", "build"):
        part = classification.get(key) or {}
        s = part.get("summary") or ""
        if isinstance(s, str) and s.strip():
            summaries.append(s)
    combined = "\n".join(summaries)
    hints = extract_hints(combined) if combined else []

    advice_path = Path("torre-llm/ADVICE.md")
    advice = "# ADVICE — Torre LLM-Engenheira\n\n"
    if hints:
        advice += "## Dicas priorizadas\n\n" + "\n".join([f"- {h}" for h in hints]) + "\n"
    else:
        advice += "_Sem erros detetados nos summaries — nada a aconselhar neste ciclo._\n"

    changes.append((str(advice_path), advice))
    return changes
