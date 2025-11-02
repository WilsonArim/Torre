from typing import Tuple
import subprocess, shlex

def run(cmd: str, cwd: str) -> Tuple[bool, str]:
    try:
        p = subprocess.Popen(shlex.split(cmd), cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        out, _ = p.communicate()
        return (p.returncode == 0, out or "")
    except FileNotFoundError:
        return (False, f"command not found: {cmd}")
    except Exception as e:
        return (False, f"exec error: {e}")
