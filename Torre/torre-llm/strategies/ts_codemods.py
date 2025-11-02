from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import json, re, subprocess, sys, shutil
try:
    from ..utils.diff_utils import make_replace_file_diff
except ImportError:
    # Fallback para quando executado diretamente
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from utils.diff_utils import make_replace_file_diff

SRC_GLOB_EXTS = (".ts", ".tsx")

RX_UNUSED = re.compile(r"[\"'](?P<name>[A-Za-z_][A-Za-z0-9_]*)[\"'].*?(?:never used|never read)")
RX_TS_CANNOT_FIND = re.compile(r"Cannot\s+find\s+name\s+'(?P<name>[^']+)'")
RX_MODULE_NOT_FOUND = re.compile(r"Module\s+not\s+found:\s*Can't\s+resolve\s+['\"](?P<mod>[^'\"]+)['\"]")

def _load_index() -> Dict[str, Any]:
    p = Path(".torre/code_index.json")
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def _iter_src_files(root: Path) -> List[Path]:
    out: List[Path] = []
    src = root / "src"
    if not src.exists():
        return out
    for p in src.rglob("*"):
        if p.is_file() and p.suffix in SRC_GLOB_EXTS:
            out.append(p)
    return out

def _guess_file_for_symbol(root: Path, symbol: str) -> Optional[Path]:
    """Procura em .torre/code_index.json um ficheiro que exporte `symbol`."""
    idx = _load_index()
    by_file = idx.get("by_file", {})
    for path, syms in by_file.items():
        try:
            if symbol in syms:
                p = Path(path)
                if p.exists():
                    return p
        except Exception:
            continue
    return None

def _relative_import(from_file: Path, to_file: Path) -> str:
    try:
        rel = Path(Path(to_file).with_suffix("")).relative_to(from_file.parent)
        s = str(rel).replace("\\", "/")
        if not s.startswith("."):
            s = "./" + s
        return s
    except ValueError:
        # Se não conseguir calcular caminho relativo, usar caminho absoluto
        return str(to_file.with_suffix(""))

def _python_fallback_prefix_unused(path: Path, text: str, names: List[str]) -> Optional[str]:
    """Heurística: prefixa identificadores declarados (const/let/function param) com '_' se não começarem por '_'."""
    new = text
    changed = False
    for name in names:
        if name.startswith("_"):
            continue
        # const/let/var name = ...
        new2, n = re.subn(rf"\b(const|let|var)\s+{re.escape(name)}\b", rf"\1 _{name}", new)
        if n > 0:
            new = new2; changed = True; continue
        # function foo(name) { ... }  or  (name: T) => ...
        new2, n = re.subn(rf"\(([^)]*?)\b{re.escape(name)}\b", lambda m: m.group(0).replace(name, f"_{name}"), new, count=1)
        if n > 0:
            new = new2; changed = True
    return new if changed else None

def _python_fallback_add_import(path: Path, text: str, symbol: str, from_path: Path) -> Optional[str]:
    """Adiciona import simples se não existir já."""
    escaped_symbol = re.escape(symbol)
    pattern1 = r"\bimport\s+\{[^}]*\b" + escaped_symbol + r"\b[^}]*\}\s+from\s+['\"]"
    pattern2 = r"\bimport\s+\*\s+as\s+\w+\s+from\s+['\"]"
    if re.search(pattern1, text) or re.search(pattern2, text):
        return None
    module = _relative_import(path, from_path)
    line = f"import {{ {symbol} }} from '{module}';\n"
    # inserir após imports existentes ou no topo
    m = re.search(r"^(import[^\n]*;\n)+", text, flags=re.M)
    if m:
        i = m.end(0)
        return text[:i] + line + text[i:]
    return line + text

def _python_fallback_fix_import_path(path: Path, text: str) -> Optional[str]:
    """Corrige imports sem extensão quando existe ficheiro correspondente com extensão adequada."""
    changed = False
    def repl(m):
        nonlocal changed
        mod = m.group("mod")
        if not (mod.startswith(".") or mod.startswith("/")):
            return m.group(0)
        base = (path.parent / mod)
        for ext in (".tsx", ".ts", ".jsx", ".js"):
            cand = base.with_suffix(ext)
            if cand.exists():
                changed = True
                return f"{m.group('pre')}{mod+ext}{m.group('post')}"
        return m.group(0)
    new = re.sub(r"(?P<pre>from\s+['\"])(?P<mod>[^'\"]+)(?P<post>['\"];)", repl, text)
    return new if changed else None

def _build_plan(root: Path, classification: Dict[str, Any]) -> Dict[str, Any]:
    plan: Dict[str, Any] = {"ops": []}
    summaries = []
    for key in ("lint", "tests", "build"):
        s = (classification.get(key) or {}).get("summary") or ""
        if isinstance(s, str) and s.strip():
            summaries.append(s)
    text = "\n".join(summaries)
    if not text.strip():
        return plan
    # no-unused
    unused = list({m.group("name") for m in RX_UNUSED.finditer(text)})
    for name in unused:
        plan["ops"].append({"type": "prefixUnused", "name": name})
    # Cannot find name
    missing = list({m.group("name") for m in RX_TS_CANNOT_FIND.finditer(text)})
    for name in missing:
        src = _guess_file_for_symbol(root, name)
        if src:
            plan["ops"].append({"type": "addImport", "symbol": name, "from": str(src)})
    # Module not found (we try to fix missing extension)
    if RX_MODULE_NOT_FOUND.search(text):
        plan["ops"].append({"type": "fixImportPath"})
    return plan

def _node_apply_codemods(root: Path, plan: Dict[str, Any]) -> List[Tuple[Path, str]]:
    node = shutil.which("node")
    script = Path(__file__).resolve().parent.parent / "codemods" / "ts" / "apply_codemods.mjs"
    if not node or not script.exists():
        return []
    try:
        p = subprocess.Popen([node, str(script)], cwd=str(root), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        out, err = p.communicate(json.dumps(plan), timeout=20)
        if p.returncode != 0:
            return []
        result = json.loads(out or "{}").get("files", [])
        out_changes: List[Tuple[Path, str]] = []
        for item in result:
            try:
                out_changes.append((Path(item["path"]), item["content"]))
            except Exception:
                continue
        return out_changes
    except Exception:
        return []

def _python_apply_codemods(root: Path, plan: Dict[str, Any]) -> List[Tuple[Path, str]]:
    changes: List[Tuple[Path, str]] = []
    names_unused = [op["name"] for op in plan.get("ops", []) if op.get("type") == "prefixUnused"]
    add_imports = [op for op in plan.get("ops", []) if op.get("type") == "addImport"]
    fix_import = any(op.get("type") == "fixImportPath" for op in plan.get("ops", []))
    for path in _iter_src_files(root):
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        updated = text
        # A) prefixUnused
        if names_unused:
            v = _python_fallback_prefix_unused(path, updated, names_unused) or updated
            updated = v
        # B) addImport (para primeiro match por ficheiro)
        for op in add_imports:
            sym = op["symbol"]
            src = Path(op["from"])
            if sym in updated and not re.search(rf"\bimport\s+.*\b{re.escape(sym)}\b.*from\s+['\"]", updated):
                v = _python_fallback_add_import(path, updated, sym, src)
                if v:
                    updated = v
        # C) fixImportPath
        if fix_import:
            v = _python_fallback_fix_import_path(path, updated)
            if v:
                updated = v
        if updated != text:
            changes.append((path, updated))
    return changes

def generate_diffs(root: Path, classification: Dict[str, Any]) -> List[str]:
    """
    Estratégia: construir plano a partir de logs e índice; tentar Node/AST; fallback Python.
    Retorna lista de diffs unificados (modify-in-place) prontos a concatenar.
    """
    plan = _build_plan(root, classification)
    if not plan.get("ops"):
        return []
    # 1) Node/AST (preferido)
    changes = _node_apply_codemods(root, plan)
    diffs: List[str] = []
    if not changes:
        # 2) Fallback Python
        changes = _python_apply_codemods(root, plan)
    for path, new_text in changes:
        try:
            old_text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        # Idempotência: se já igual, ignora
        if old_text == new_text:
            continue
        diffs.append(make_replace_file_diff(path, old_text, new_text))
    return diffs
