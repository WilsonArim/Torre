from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, List
import re
from ..utils.diff_utils import make_replace_file_diff

SHIM = (
    "// @fortaleza: shim para garantir que `base` existe em runtime (Vite/Tauri)\n"
    "// Evita \"ReferenceError: base is not defined\".\n"
    "const base: string =\n"
    "  ((globalThis as any).__FORTALEZA_BASE__ as string) ??\n"
    "  (((import.meta as any)?.env?.BASE_URL as string) ?? '/');\n"
    "(globalThis as any).__FORTALEZA_BASE__ = base;\n"
    "\n"
)

def _find_target_tsx(root: Path) -> Path | None:
    preferred = root / "src" / "components" / "SettingsPage.tsx"
    if preferred.exists():
        return preferred
    # fallback: procurar primeiro *.tsx que refira 'base'
    for p in (root / "src").rglob("*.tsx"):
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if "base" in txt and "__FORTALEZA_BASE__" not in txt:
            return p
    return None

def _needs_shim(txt: str) -> bool:
    if "__FORTALEZA_BASE__" in txt:
        return False
    # heurística: uso de variável 'base' isolada ou acesso aparente
    return re.search(r"(^|\W)base(\W)", txt) is not None

def generate_diffs(root: Path, classification: Dict[str, Any]) -> List[str]:
    """
    Se detetar `base` usado sem shim, gera um diff que insere o SHIM no topo do ficheiro alvo.
    Idempotente: se o SHIM já existe, não gera nada.
    """
    diffs: List[str] = []
    target = _find_target_tsx(root)
    if not target or not target.exists():
        return diffs
    try:
        original = target.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return diffs
    if not _needs_shim(original):
        return diffs
    new_text = SHIM + original
    diffs.append(make_replace_file_diff(target, original, new_text))
    return diffs
