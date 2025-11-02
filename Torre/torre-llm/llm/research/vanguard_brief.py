from __future__ import annotations
from typing import Dict, Any, List
from .vanguard_policy import validate_sources, in_scope

def generate_brief(query: str, raw_sources: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Gera um Vanguard Brief (5–10 pontos) a partir de fontes validadas.
    Não faz scraping: assume 'raw_sources' vindo do teu radar/pesquisa.
    """
    sources = validate_sources(raw_sources)
    # Heurística: requer ≥3 fontes para robustez
    bullets: List[str] = []
    for s in sources[:10]:
        t = s["title"] or s["snippet"] or s["url"]
        bullets.append(f"{t} — {s['domain'] or s['url']} ({s['date']})")
    bullets = bullets[:10]
    return {
        "query": query,
        "bullets": bullets,                 # 5–10 linhas curtas
        "citations": sources,               # url + date obrigatórios
        "pipeline": [
            "Validar versões e breaking changes",
            "Esboçar arquitetura alvo + ADR curto",
            "Definir gates (latência/custo/sec)",
            "Prototipar em branch isolada",
        ],
        "gates": {
            "citations_min": 3,
            "scope": "engineering-only",
        },
        "approved": False,                  # promoção ao CANON depende de admin
    }

def validate_brief(brief: Dict[str, Any]) -> Dict[str, Any]:
    """Valida gates da F11: ≥3 citações com data; escopo técnico; 5–10 bullets."""
    citations = brief.get("citations") or []
    bullets = brief.get("bullets") or []
    reasons: List[str] = []
    if len(citations) < 3:
        reasons.append("citations<3")
    if not (5 <= len(bullets) <= 10):
        reasons.append("bullets_not_5_10")
    if not in_scope(" ".join(bullets)):
        reasons.append("out_of_scope")
    return {
        "ok": len(reasons) == 0,
        "reasons": reasons,
        "counts": {"citations": len(citations), "bullets": len(bullets)},
    }
