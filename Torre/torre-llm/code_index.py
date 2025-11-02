from __future__ import annotations
from pathlib import Path
from typing import Dict, List
import json, re

IGNORE_DIRS = {".git", "node_modules", "dist", "build", ".venv", "venv", ".pytest_cache", ".tox"}
EXTS = {".ts", ".tsx", ".js", ".jsx"}

RX_EXPORT = re.compile(r"^\s*export\s+(?:const|let|var|function|class)\s+(?P<name>[A-Za-z_]\w*)", re.M)
RX_EXPORT_DEFAULT = re.compile(r"^\s*export\s+default\s+(?:function|class)?\s*(?P<name>[A-Za-z_]\w*)?", re.M)
RX_EXPORT_TYPE = re.compile(r"^\s*export\s+(?:type|interface)\s+(?P<name>[A-Za-z_]\w*)", re.M)

def _iter_code_files(root: Path) -> List[Path]:
    files: List[Path] = []
    for p in root.rglob("*"):
        if p.is_dir():
            if p.name in IGNORE_DIRS:
                # skip subtree
                for _ in p.rglob("*"):
                    pass
                continue
            continue
        if p.suffix in EXTS:
            files.append(p)
    return files

def _extract_symbols(text: str) -> List[str]:
    out: List[str] = []
    for rx in (RX_EXPORT, RX_EXPORT_DEFAULT, RX_EXPORT_TYPE):
        for m in rx.finditer(text):
            name = (m.group("name") or "default").strip()
            if name and name not in out:
                out.append(name)
    return out

def build_code_index(root: Path) -> Dict:
    """
    Indexa símbolos exportados em ficheiros .ts/.tsx/.js/.jsx.
    Retorna dicionário com estatísticas e mapa por ficheiro.
    """
    by_file: Dict[str, List[str]] = {}
    total_symbols = 0
    files = _iter_code_files(root)
    for f in files:
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        syms = _extract_symbols(text)
        if syms:
            by_file[str(f)] = syms
            total_symbols += len(syms)
    return {
        "root": str(root),
        "files_indexed": len(files),
        "files_with_symbols": len(by_file),
        "symbols": total_symbols,
        "by_file": by_file,
    }

def write_index_json(root: Path, idx: Dict) -> None:
    outdir = Path(".torre")
    outdir.mkdir(exist_ok=True)
    (outdir / "code_index.json").write_text(json.dumps(idx, ensure_ascii=False, indent=2), encoding="utf-8")

def make_overview_md(idx: Dict) -> str:
    lines = [
        "# INDEX_OVERVIEW — Torre RAG-of-Code (mínimo)",
        "",
        f"*root*: `{idx.get('root','')}`",
        f"*files_indexed*: {idx.get('files_indexed',0)}",
        f"*files_with_symbols*: {idx.get('files_with_symbols',0)}",
        f"*symbols*: {idx.get('symbols',0)}",
        "",
        "## Exemplos (até 10 ficheiros)",
    ]
    shown = 0
    for path, syms in list(idx.get("by_file", {}).items())[:10]:
        preview = ", ".join(syms[:8])
        lines.append(f"- `{path}`: {preview}")
        shown += 1
    if shown == 0:
        lines.append("_Sem símbolos detetados nas extensões suportadas._")
    lines.append("")  # final newline
    return "\n".join(lines)
