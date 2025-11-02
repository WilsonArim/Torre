from pathlib import Path
from typing import Dict, Any
from . import run

def _guess_lint_cmd(root: Path) -> str:
    if (root / "package.json").exists():
        return "npm run lint"
    if (root / "pyproject.toml").exists() or (root / "ruff.toml").exists():
        return "ruff ."
    return "true"

def run_lint(root: Path) -> Dict[str, Any]:
    cmd = _guess_lint_cmd(root)
    ok, out = run(cmd, str(root))
    tail = "\n".join(out.splitlines()[-40:])
    return {"ok": ok, "summary": tail, "cmd": cmd}
