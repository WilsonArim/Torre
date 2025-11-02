from __future__ import annotations
from pathlib import Path

def load_canon(repo_root: str | Path, max_chars: int = 4000) -> str:
    """
    Carrega o CANON (Cartas dos Mestres) para uso opcional em RAG.
    Não possui dependências externas; caller decide se injeta no prompt.
    """
    root = Path(repo_root or ".").resolve()
    p = root / "fortaleza-llm" / "llm" / "rag" / "CANON.md"
    if not p.exists():
        return ""
    txt = p.read_text(encoding="utf-8", errors="ignore")
    return txt[:max_chars]
