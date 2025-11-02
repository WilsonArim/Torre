"""
Reverse-engineering toolkit (Fase 8)
------------------------------------
CodeMap:        Grafo multi-linguagem (TS/JS/TSX/JSX/Py) + estatísticas
HotspotMiner:   Sinal de hotspots (churn aproximado, TODOs, grau do grafo)
CouplingSentinel:Deteção de acoplamentos proibidos entre camadas
RefactorAdvisor:Plano de refactor mínimo + provas (gates) em modo advisory
"""
from .codemap import CodeMap
from .hotspot_miner import HotspotMiner
from .coupling_sentinel import CouplingSentinel, DEFAULT_LAYERS
from .refactor_advisor import RefactorAdvisor

__all__ = [
    "CodeMap",
    "HotspotMiner",
    "CouplingSentinel",
    "DEFAULT_LAYERS",
    "RefactorAdvisor",
]
