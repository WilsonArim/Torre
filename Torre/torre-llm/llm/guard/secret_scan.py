from typing import List, Dict
import re

try:
    # Usa o regex já calibrado se existir
    from llm.forensics.impact_analyzer import _SECRET_RE  # type: ignore
except Exception:
    # Fallback robusto (OpenAI, GH PAT, Slack, Google, genérico)
    _SECRET_RE = re.compile(
        r'(sk-[A-Za-z0-9_\-]{16,}'
        r'|ghp_[A-Za-z0-9]{20,}'
        r'|xox[baprs]-[A-Za-z0-9\-]{10,}'
        r'|AIza[0-9A-Za-z\-_]{35}'
        r'|(?:api|token|secret|key)[-_]?[=:]\s*["\'][A-Za-z0-9_\-]{16,}["\'])',
        re.I,
    )

def scan_diff_for_secrets(diff: str) -> List[Dict[str, str]]:
    """Procura potenciais segredos em linhas adicionadas/removidas de um diff unificado."""
    out: List[Dict[str, str]] = []
    for i, line in enumerate(diff.splitlines(), 1):
        if line.startswith(('---', '+++', '@@')):  # metadados do diff
            continue
        if line and line[0] in '+- ':  # apenas conteúdo
            for m in _SECRET_RE.finditer(line):
                out.append({"line": str(i), "match": m.group(0)})
    return out
