from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, List, Tuple

# Mapeamento simples de camadas por prefixos (podes ajustar via parâmetro)
DEFAULT_LAYERS = {
    "UI": ["src/ui/", "src/components/", "src/pages/", "app/"],
    "DOMAIN": ["src/domain/", "domain/"],
    "SERVICE": ["src/services/", "src/api/", "api/"],
    "INFRA": ["src/infra/", "infra/", "src/config/", "config/"],
    "TEST": ["tests/", "__tests__/"],
}

# Regras proibidas (origem -> destino)
FORBIDDEN = {
    ("UI", "INFRA"),
    ("UI", "DOMAIN"),      # UI fala com SERVICE/DTOs, não com domain interno
    ("DOMAIN", "UI"),
    ("INFRA", "UI"),
}

def _layer_of(path: str, layers: Dict[str, list]) -> str | None:
    p = path.lower()
    for k, prefixes in layers.items():
        for pref in prefixes:
            if p.startswith(pref.lower()):
                return k
    return None

class CouplingSentinel:
    """
    Deteta arestas do grafo que violam regras de arquitetura (camadas).
    """
    def __init__(self, layers: Dict[str, list] | None = None) -> None:
        self.layers = layers or DEFAULT_LAYERS

    def analyze(self, codemap: Dict[str, Any]) -> Dict[str, Any]:
        viol: List[Dict[str, Any]] = []
        for a, b in codemap.get("edges", []):
            if b.startswith("pkg:"):
                continue
            la = _layer_of(a, self.layers)
            lb = _layer_of(b, self.layers)
            if la and lb and (la, lb) in FORBIDDEN:
                viol.append({"from": a, "to": b, "from_layer": la, "to_layer": lb, "rule": f"{la}->{lb} forbidden"})
        return {"violations": viol, "count": len(viol)}
