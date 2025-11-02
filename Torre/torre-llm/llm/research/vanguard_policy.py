from __future__ import annotations
from typing import Dict, Any, List
import re

# Escopo "engenharia-only": bloqueia conteúdo não-técnico irrelevante para decisão técnica
_BAN_PATTERNS = [
    r"\b(price|buy|signal|trading|pump|moon)\b",
    r"\bpoem(s)?\b",
    r"\bcelebrity|gossip|horoscope\b",
]
_ban_re = re.compile("|".join(_BAN_PATTERNS), re.I)

def in_scope(text: str) -> bool:
    """Retorna True se o texto estiver dentro do escopo de engenharia."""
    return not _ban_re.search(text or "")

def normalize_source(src: Dict[str, Any]) -> Dict[str, Any]:
    """Normaliza campos essenciais de uma fonte."""
    return {
        "title": (src.get("title") or "").strip(),
        "url": (src.get("url") or "").strip(),
        "date": (src.get("date") or "").strip(),  # ISO ou data legível
        "snippet": (src.get("snippet") or "").strip(),
        "domain": (src.get("domain") or "").strip(),
    }

def validate_sources(sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filtra e normaliza fontes: exige url+date, dentro de escopo."""
    out: List[Dict[str, Any]] = []
    for s in sources or []:
        s2 = normalize_source(s)
        if s2["url"] and s2["date"] and in_scope(" ".join(s2.values())):
            out.append(s2)
    return out
