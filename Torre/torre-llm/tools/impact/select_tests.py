#!/usr/bin/env python3
"""
Seleciona testes afetados por um conjunto de ficheiros alterados.
Heurística simples: mapeia por prefixos e extensões. Fallback: smoke.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
MAP = [
  (("src/", "apps/"), ("tests/test_fastapi_contract.py", "evals/test_phase*.py")),
  (("llm/",), ("tests/test_fastapi_contract.py",)),
  (("evals/",), ("evals/test_phase*.py",)),
]
def main():
    changed = json.loads(sys.stdin.read() or "[]")
    selected = set()
    for f in changed:
        for prefixes, tests in MAP:
            if any(f.startswith(p) for p in prefixes):
                selected.update(tests)
    if not selected:
        selected = {"tests/test_fastapi_simple.py"}
    print(json.dumps(sorted(selected)))
if __name__ == "__main__":
    main()
