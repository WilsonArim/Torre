from __future__ import annotations
from typing import Dict, Any, List

LENSES = {
    "ARISTOTELES": {
        "rule": "Não-contradição e linguagem precisa — evitar outputs ambíguos.",
        "when": ["patch grande", "múltiplos módulos", "mensurar invariantes"],
    },
    "DIJKSTRA": {
        "rule": "Passo mínimo com prova (invariantes/testes).",
        "when": ["erro de build/types", "refactor pequeno"],
    },
    "HOARE": {
        "rule": "Pré/pós-condições tornam-se asserts e testes.",
        "when": ["alteração de API", "contratos"],
    },
    "KNUTH": {
        "rule": "Medir antes de otimizar; evidência > opinião.",
        "when": ["performance", "diff grande"],
    },
    "SALTZER": {
        "rule": "Princípios de segurança: mínimo privilégio, fail-safe defaults.",
        "when": ["segurança", "segredos", "infra"],
    },
}

def pick_lenses(logs:Dict[str,str], diff:str)->List[str]:
    lenses=[]
    txt=" ".join([*logs.values(), diff]).lower()
    if "ts" in txt or "type" in txt or "build" in txt:
        lenses.append("DIJKSTRA")
    if "api" in txt or "contract" in txt:
        lenses.append("HOARE")
    if "perf" in txt or "slow" in txt or len(diff.splitlines())>300:
        lenses.append("KNUTH")
    if "secret" in txt or "token" in txt or "key" in txt or "infra" in txt:
        lenses.append("SALTZER")
    if not lenses:
        lenses.append("ARISTOTELES")
    # único e estável
    out=[]; seen=set()
    for l in lenses:
        if l not in seen:
            out.append(l); seen.add(l)
    return out[:3]

def lens_report(lenses:List[str])->List[Dict[str,Any]]:
    return [{"lens": l, "rule": LENSES[l]["rule"]} for l in lenses if l in LENSES]
