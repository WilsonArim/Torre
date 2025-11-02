from pathlib import Path
from typing import Dict, Any
from . import run

def _guess_build_cmd(root: Path) -> str:
    if (root / "package.json").exists():
        return "npm run build"
    if (root / "pyproject.toml").exists():
        return "python -c \"print('build-skip')\""
    return "true"

def run_build(root: Path) -> Dict[str, Any]:
    cmd = _guess_build_cmd(root)
    ok, out = run(cmd, str(root))
    tail = "\n".join(out.splitlines()[-60:])
    return {"ok": ok, "summary": tail, "cmd": cmd}
