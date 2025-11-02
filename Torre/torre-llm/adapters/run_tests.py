from pathlib import Path
from typing import Dict, Any
from . import run

def _guess_test_cmd(root: Path) -> str:
    if (root / "pytest.ini").exists() or (root / "tests").exists() or (root / "pyproject.toml").exists():
        return "pytest -q"
    if (root / "package.json").exists():
        return "npm test --silent"
    return "true"

def run_tests(root: Path) -> Dict[str, Any]:
    cmd = _guess_test_cmd(root)
    ok, out = run(cmd, str(root))
    tail = "\n".join(out.splitlines()[-60:])
    return {"ok": ok, "summary": tail, "cmd": cmd}
