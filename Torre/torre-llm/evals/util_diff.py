from __future__ import annotations
import re
from typing import Tuple

_FENCE_RE = re.compile(r"```diff\s*(.*?)```", re.S)

def extract_diff(text: str) -> str:
    """
    Aceita:
      - JSON da nossa LLM CLI: já deve conter campo diff (tratado fora)
      - Texto com bloco ```diff ... ```
      - Texto que começa com '--- a/' e contém '+++ b/'
    """
    if not text:
        return ""
    m = _FENCE_RE.search(text)
    if m:
        return m.group(1).strip()
    t = text.strip()
    if t.startswith("--- a/") and "\n+++ b/" in t:
        return t
    return ""

def looks_unified_diff(d: str) -> bool:
    if not d:
        return False
    return d.startswith("--- a/") and "\n+++ b/" in d

def patch_size(d: str) -> Tuple[int,int,int]:
    """
    Retorna (adds, removes, total_changed_lines) ignorando cabeçalhos.
    """
    adds = removes = 0
    for line in d.splitlines():
        if line.startswith("+++") or line.startswith("---") or line.startswith("@@"):
            continue
        if line.startswith("+"):
            adds += 1
        elif line.startswith("-"):
            removes += 1
    return adds, removes, adds + removes
