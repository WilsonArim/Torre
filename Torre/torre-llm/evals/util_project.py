from __future__ import annotations
import os, re, pathlib, hashlib
from typing import Dict, Any, List, Tuple, Set

def load_fixture_tree(root: str) -> Dict[str, str]:
    out = {}
    base = pathlib.Path(root)
    for p in base.rglob("*"):
        if p.is_file():
            rel = str(p.relative_to(base))
            out[rel] = p.read_text(encoding="utf-8", errors="ignore")
    return out

def read_tree_as_dict(root: str) -> Dict[str, str]:
    return load_fixture_tree(root)

IMP_RE = re.compile(r"^\s*import\s+.*?from\s+['\"](.+?)['\"];?", re.M)

def build_import_graph(tree: Dict[str, str]) -> Dict[str, Set[str]]:
    g = {}
    for path, src in tree.items():
        if not path.endswith((".ts", ".tsx", ".js", ".jsx")): 
            continue
        base = os.path.splitext(path)[0]
        g.setdefault(path, set())
        for m in IMP_RE.finditer(src):
            ref = m.group(1)
            if ref.startswith("."):
                # normaliza caminho relativo (sem resolver extensão)
                tgt = os.path.normpath(os.path.join(os.path.dirname(path), ref))
                g[path].add(tgt)
    return g

def has_circular_import(g: Dict[str, Set[str]]) -> bool:
    # ciclo simples por DFS
    seen = set()
    stack = set()
    def dfs(u):
        if u in stack: return True
        if u in seen: return False
        seen.add(u); stack.add(u)
        for v in g.get(u, ()):
            if dfs(v): return True
        stack.remove(u)
        return False
    return any(dfs(u) for u in g)

def detect_potential_new_cycle(graph_before: Dict[str, Set[str]], diff_text: str) -> bool:
    # se o diff adiciona "import ... from './X'" em arquivo F e já existe aresta X->F antes → potencial novo ciclo
    added = []
    cur_file = None
    for line in diff_text.splitlines():
        if line.startswith("+++ b/"):
            cur_file = line[len("+++ b/"):].strip()
        if line.startswith("+") and "import" in line and "from" in line:
            m = IMP_RE.search(line[1:])
            if m and cur_file:
                ref = m.group(1)
                if ref.startswith("."):
                    tgt = os.path.normpath(os.path.join(os.path.dirname(cur_file), ref))
                    added.append((cur_file, tgt))
    for f, t in added:
        # se já havia t -> f antes, teremos ciclo
        if f and t and f in graph_before and t in graph_before and f in graph_before[t]:
            return True
    return False

FUNC_RE = re.compile(r"(?:function\s+([A-Za-z0-9_]+)\s*\(|const\s+([A-Za-z0-9_]+)\s*=\s*\()", re.M)

def _func_names(src: str) -> Set[str]:
    out = set()
    for m in FUNC_RE.finditer(src or ""):
        name = m.group(1) or m.group(2)
        if name: out.add(name)
    return out

def detect_function_duplication(before: Dict[str, str], after: Dict[str, str]) -> Set[str]:
    # Detecta apenas duplicações NOVAS criadas pelo patch
    before_names = set()
    for p, src in before.items():
        before_names |= _func_names(src)
    
    # Mapeia funções por arquivo antes e depois
    before_by_file = {}
    after_by_file = {}
    
    for p, src in before.items():
        before_by_file[p] = _func_names(src)
    
    for p, src in after.items():
        after_by_file[p] = _func_names(src)
    
    dups = set()
    # Só marca como duplicação se uma função foi ADICIONADA em arquivo diferente
    for p, after_funcs in after_by_file.items():
        before_funcs = before_by_file.get(p, set())
        new_funcs = after_funcs - before_funcs  # funções adicionadas neste arquivo
        
        for new_func in new_funcs:
            # Verifica se esta função nova já existia em OUTRO arquivo
            for other_file, other_funcs in before_by_file.items():
                if other_file != p and new_func in other_funcs:
                    dups.add(new_func)
                    break
    
    return dups

def detect_unreachable_after_return(diff_text: str) -> Set[str]:
    # heurística: linhas adicionadas após 'return' no mesmo hunk com indent >=
    res = set()
    hunk_fn = None; seen_return = False
    for line in diff_text.splitlines():
        if line.startswith("@@"):
            hunk_fn = None; seen_return = False
        elif line.startswith("+++ b/"):
            hunk_fn = line[len("+++ b/"):]
        elif line.startswith("+"):
            code = line[1:]
            if "return " in code or code.strip() == "return":
                seen_return = True
            elif seen_return and code.strip():
                res.add(hunk_fn or "<unknown>")
    return res

def detect_hygiene_issues(diff_text: str) -> Set[str]:
    bad = set()
    for line in diff_text.splitlines():
        if not line.startswith("+"): 
            continue
        code = line[1:].strip()
        if "eslint-disable" in code or "@ts-ignore" in code:
            bad.add("lint-disable")
        if "TODO" in code or "FIXME" in code:
            bad.add("todo-fixme")
        if "eval(" in code or "new Function" in code:
            bad.add("eval")
        if "console.log" in code:
            bad.add("console-log")
    return bad
