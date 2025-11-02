from __future__ import annotations
import re
from typing import Dict, Any, List, Optional, Tuple

Severity = str  # "block" | "advisory"

SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|token)\s*[:=]\s*['\"][A-Za-z0-9_\-]{16,}"),
    re.compile(r"-----BEGIN (RSA|EC) PRIVATE KEY-----"),
]
FORBIDDEN_PATH_HINTS = [
    ".env", ".ssh/", "secrets.", "id_rsa", ".pem"
]

FUNC_DEF = re.compile(r"\b(function\s+([A-Za-z0-9_]+)\s*\(|const\s+([A-Za-z0-9_]+)\s*=\s*\(|export\s+function\s+([A-Za-z0-9_]+)\s*\()", re.M)
IMPORT_LINE = re.compile(r"^\s*import\s+.*from\s+['\"]([^'\"]+)['\"]", re.M)

def _collect_added_hunks(diff: str) -> Dict[str, List[str]]:
    """Return {path: [added_lines...]} from unified diff."""
    files: Dict[str, List[str]] = {}
    cur: Optional[str] = None
    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            cur = line[6:].strip()
            files[cur] = []
            continue
        if cur is None:
            continue
        if line.startswith("+") and not line.startswith("+++"):
            files[cur].append(line[1:])
    return files

def _looks_layer_violation(path: str, import_target: str) -> bool:
    p = path.lower()
    t = import_target.lower()
    # Ex.: UI/Components não devem importar infra/db diretamente
    if ("src/components" in p or "src/ui" in p) and ("/infra" in t or "/db" in t or "infra/" in t or "db/" in t):
        return True
    # Evitar imports ascendentes perigosos
    if t.startswith("..") and ("/infra" in t or "/db" in t):
        return True
    return False

def _nested_loop_score(lines: List[str]) -> int:
    # Heurística leve: conta pares de for/while/map aninhados na mesma região
    code = "\n".join(lines)
    # Simplista: dois 'for' próximos ou map dentro de map
    nested = re.search(r"(for\s*\(.*\).{0,120}for\s*\()|(map\s*\(.*map\s*\()", code, re.S)
    return 1 if nested else 0

def scan_secrets_and_paths(added: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    for path, lines in added.items():
        low = path.lower()
        if any(h in low for h in FORBIDDEN_PATH_HINTS):
            findings.append({"kind":"security/path", "severity":"block", "path":path, "msg":"Path sensível referenciado no diff."})
        text = "\n".join(lines)
        for pat in SECRET_PATTERNS:
            if pat.search(text):
                findings.append({"kind":"security/secret", "severity":"block", "path":path, "msg":"Possível segredo detectado nas adições."})
    return findings

def scan_architecture(added: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    for path, lines in added.items():
        blob = "\n".join(lines)
        for m in IMPORT_LINE.finditer(blob):
            target = m.group(1)
            if _looks_layer_violation(path, target):
                findings.append({"kind":"arch/layer", "severity":"advisory", "path":path,
                                 "msg":f"Import possivelmente cruzando camadas: {target}"})
    return findings

def scan_duplication(files_before: Dict[str, str], added: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    """Marca possível duplicação quando um novo símbolo igual já existe noutro ficheiro (heurística segura)."""
    findings: List[Dict[str, Any]] = []
    # Construir índice de símbolos existentes (nome -> paths)
    symbol_index: Dict[str, List[str]] = {}
    for p, content in (files_before or {}).items():
        for m in FUNC_DEF.finditer(content):
            name = next(g for g in m.groups()[1:] if g)  # pega o nome capturado
            symbol_index.setdefault(name, []).append(p)
    for path, lines in added.items():
        snippet = "\n".join(lines)
        for m in FUNC_DEF.finditer(snippet):
            name = next(g for g in m.groups()[1:] if g)
            owners = symbol_index.get(name, [])
            # Só reporta se o símbolo já existe em OUTRO ficheiro (evita falsos positivos)
            if owners and all(op != path for op in owners):
                findings.append({"kind":"quality/duplication", "severity":"advisory", "path":path,
                                 "msg":f"Símbolo '{name}' já existe em {len(owners)} ficheiro(s). Considera reutilizar ou renomear."})
    return findings

def scan_scalability(added: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    for path, lines in added.items():
        score = _nested_loop_score(lines)
        if score >= 1:
            findings.append({"kind":"perf/nested-loop", "severity":"advisory", "path":path,
                             "msg":"Possível loop aninhado detectado; verifica complexidade (O(n^2))."})
    return findings

def analyze_patch(files_before: Optional[Dict[str, str]], diff_text: str) -> Dict[str, Any]:
    """
    Retorna {"violations":[...], "proofs":[...], "score":float}
    Score (0-1) penaliza apenas violações 'block'; 'advisory' não bloqueia.
    """
    added = _collect_added_hunks(diff_text)
    v: List[Dict[str, Any]] = []
    v += scan_secrets_and_paths(added)
    v += scan_architecture(added)
    v += scan_duplication(files_before or {}, added)
    v += scan_scalability(added)

    blocks = [x for x in v if x["severity"] == "block"]
    score = 1.0 if not blocks else max(0.0, 1.0 - 0.3*len(blocks))
    proofs = [
        "Aristóteles/Não-contradição: políticas de paths sensíveis não podem coexistir com diffs que os tocam.",
        "Saltzer/Schroeder (mínimo privilégio): bloquear secretes e chaves privadas no patch.",
        "Knuth/Engenharia: avisos de performance e duplicação como melhoria contínua (não bloqueante)."
    ]
    return {"violations": v, "proofs": proofs, "score": score}

def enforce_policy(result: Dict[str, Any]) -> Tuple[bool, Severity, List[str]]:
    """
    Decide se bloqueia (False) ou segue com 'advisory'.
    Retorna (ok, mode, reasons)
    """
    reasons = []
    blocks = [x for x in result.get("violations", []) if x["severity"] == "block"]
    if blocks:
        reasons = [f"{x['kind']}@{x['path']}" for x in blocks][:5]
        return (False, "block", reasons)
    return (True, "advisory", [])
