from __future__ import annotations
import re, json
from typing import Tuple, Dict, Any
try:
    from ..utils.diff_utils import validate_unified_diff
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from utils.diff_utils import validate_unified_diff

PATCH_INFO_RX = re.compile(r"<patch-info>(.*?)</patch-info>", re.S)
FENCE_RX = re.compile(r"```diff\\n(.*?)```", re.S)

def extract_patch(text: str) -> Tuple[str, Dict[str, Any]]:
    """
    Extrai o bloco ```diff``` e um JSON opcional entre <patch-info>...</patch-info>.
    Valida o diff como unificado; lança se inválido.
    """
    info: Dict[str, Any] = {}
    m = PATCH_INFO_RX.search(text or "")
    if m:
        raw = m.group(1).strip()
        try:
            info = json.loads(raw)
        except Exception:
            info = {"raw": raw}
    dm = FENCE_RX.search(text or "")
    if dm:
        diff = dm.group(1).strip()
    else:
        # fallback: tentar detectar um unificado "cru"
        s = text.find("--- a/")
        if s == -1:
            s = text.find("diff --git ")
        if s == -1:
            raise ValueError("MISSING:diff block")
        diff = text[s:].strip()
    validate_unified_diff(diff)
    return diff, info
