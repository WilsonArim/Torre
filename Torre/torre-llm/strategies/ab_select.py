from __future__ import annotations
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass

@dataclass
class Candidate:
    name: str           # origem (ex.: 'autofix_base_shim' | 'ts_codemods')
    diff: str           # diff unificado do candidato
    diff_size: int      # nº de linhas do diff

def _size(diff: str) -> int:
    return len(diff.splitlines())

def pick_best(cands: List[Candidate]) -> Tuple[Candidate | None, Dict[str, Any]]:
    """
    Seleciona o vencedor pelo menor `diff_size`.
    Empate: menor `name` (ordem alfabética).
    """
    if not cands:
        return None, {"ab_candidates": 0, "ab_winner": None}
    cands = sorted(cands, key=lambda c: (c.diff_size, c.name))
    winner = cands[0]
    return winner, {
        "ab_candidates": len(cands),
        "ab_winner": {"name": winner.name, "diff_size": winner.diff_size},
    }

def make_candidate(name: str, diff: str) -> Candidate | None:
    if not diff or not diff.strip().startswith("diff --git"):
        return None
    return Candidate(name=name, diff=diff, diff_size=_size(diff))
