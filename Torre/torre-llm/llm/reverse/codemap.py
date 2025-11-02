from __future__ import annotations
import os, re, json
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any

JS_IMPORT_RE = re.compile(
    r"""(?x)
    ^\s*import\s+(?:.+?\s+from\s+)?['"](?P<mod>[^'"]+)['"]\s*;?|
    ^\s*export\s+.+?\s+from\s+['"](?P<mod2>[^'"]+)['"]\s*;?|
    require\(\s*['"](?P<mod3>[^'"]+)['"]\s*\)
    """
)
PY_IMPORT_RE = re.compile(
    r"""(?x)
    ^\s*from\s+(?P<from>[a-zA-Z0-9_\.]+)\s+import\s+[a-zA-Z0-9_\*,\s]+|
    ^\s*import\s+(?P<imp>[a-zA-Z0-9_\.]+)
    """
)

EXTS = {".ts", ".tsx", ".js", ".jsx", ".py"}

def _norm(p: str) -> str:
    return str(Path(p).as_posix())

def _is_rel(mod: str) -> bool:
    return mod.startswith(".")

def _strip_ext(p: str) -> str:
    for e in (".ts", ".tsx", ".js", ".jsx", ".py"):
        if p.endswith(e):
            return p[: -len(e)]
    return p

class CodeMap:
    """
    Lê o repositório e constrói um grafo de dependências leve (arquivo->arquivo).
    - Resolve imports relativos (./, ../)
    - Mantém import "externo" como nó especial (pkg:xxx)
    - Estatísticas: cobertura, grau, contagem
    """
    def __init__(self, repo_root: str = ".") -> None:
        self.root = Path(repo_root).resolve()
        self.nodes: Set[str] = set()
        self.edges: List[Tuple[str, str]] = []
        self.externals: Set[str] = set()
        self.files_scanned: int = 0
        self.files_total: int = 0

    def _list_files(self) -> List[Path]:
        files: List[Path] = []
        for p in self.root.rglob("*"):
            if p.is_file() and p.suffix in EXTS and ".venv" not in p.parts and "node_modules" not in p.parts:
                files.append(p)
        self.files_total = len(files)
        return files

    def _resolve_rel(self, src: Path, mod: str) -> str | None:
        # tenta variantes: ./x, ./x.tsx, ./x/index.ts, etc.
        base = (src.parent / mod).resolve()
        cands = [base]
        # ficheiro direto
        for e in (".ts", ".tsx", ".js", ".jsx", ".py"):
            cands.append(Path(str(base) + e))
        # index.*
        cands.extend([(base / "index.ts"), (base / "index.tsx"), (base / "index.js"), (base / "index.jsx"), (base / "__init__.py")])
        for c in cands:
            if c.exists() and c.is_file():
                try:
                    rel = _norm(c.relative_to(self.root))
                except Exception:
                    rel = _norm(c)
                return rel
        return None

    def _parse_imports(self, p: Path) -> List[str]:
        out: List[str] = []
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return out
        if p.suffix in {".ts", ".tsx", ".js", ".jsx"}:
            for m in JS_IMPORT_RE.finditer(text):
                mod = m.group("mod") or m.group("mod2") or m.group("mod3")
                if not mod:
                    continue
                out.append(mod.strip())
        elif p.suffix == ".py":
            for m in PY_IMPORT_RE.finditer(text):
                mod = m.group("from") or m.group("imp")
                if not mod:
                    continue
                out.append(mod.strip().replace(".", "/"))
        return out

    def build(self) -> Dict[str, Any]:
        files = self._list_files()
        for f in files:
            src = _norm(f.relative_to(self.root))
            self.nodes.add(src)
            mods = self._parse_imports(f)
            for mod in mods:
                if _is_rel(mod):
                    tgt = self._resolve_rel(f, mod)
                    if tgt:
                        self.edges.append((src, tgt))
                        self.nodes.add(tgt)
                else:
                    # externo (pacote)
                    self.edges.append((src, f"pkg:{_strip_ext(mod)}"))
                    self.externals.add(f"pkg:{_strip_ext(mod)}")
            self.files_scanned += 1
        return self.to_dict()

    def stats(self) -> Dict[str, Any]:
        indeg: Dict[str, int] = {}
        outdeg: Dict[str, int] = {}
        for n in self.nodes:
            indeg[n] = 0
            outdeg[n] = 0
        for a, b in self.edges:
            outdeg[a] = outdeg.get(a, 0) + 1
            indeg[b] = indeg.get(b, 0) + 1
        covered = 0 if self.files_total == 0 else round(100.0 * (self.files_scanned / self.files_total), 2)
        return {
            "nodes": len(self.nodes),
            "edges": len(self.edges),
            "externals": len(self.externals),
            "coverage_files_pct": covered,
            "max_outdeg": max(outdeg.values() or [0]),
            "max_indeg": max(indeg.values() or [0]),
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "root": str(self.root),
            "nodes": sorted(self.nodes),
            "edges": self.edges[:],
            "externals": sorted(self.externals),
            "stats": self.stats(),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
