from pathlib import Path
from typing import List
import difflib

def make_new_file_diff(path: Path, content: str) -> str:
    b = str(path).replace("\\", "/")
    header = f"diff --git a/{b} b/{b}\nnew file mode 100644\nindex 0000000..0000001\n--- /dev/null\n+++ b/{b}\n"
    body_lines = content.splitlines()
    body = "".join([f"+{line}\n" for line in body_lines])
    return header + f"@@ -0,0 +1,{len(body_lines)} @@\n" + body

def join_unified_diffs(diffs: List[str]) -> str:
    return "".join(diffs)

def validate_unified_diff(diff: str) -> bool:
    return diff.strip().startswith("diff --git")

def make_replace_file_diff(path: Path, old_text: str, new_text: str) -> str:
    """
    Cria diff unificado (modify-in-place) para ficheiro existente, usando difflib.
    Gera cabeçalho 'diff --git' + hunks '--- a/...', '+++ b/...'.
    """
    posix = path.as_posix()
    old_lines = old_text.splitlines(keepends=True)
    new_lines = new_text.splitlines(keepends=True)
    hunks = "".join(difflib.unified_diff(
        old_lines, new_lines,
        fromfile=f"a/{posix}", tofile=f"b/{posix}", n=3
    ))
    header = f"diff --git a/{posix} b/{posix}\n"
    return header + hunks
