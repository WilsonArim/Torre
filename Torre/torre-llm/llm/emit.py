from __future__ import annotations
import sys, os, json, time
from pathlib import Path
from .bridge import run_patch_from_json

def _print_patch(diff: str, patch_info: dict | None) -> None:
    info = patch_info or {}
    if not info:
        info = {"generator": "fortaleza-llm", "ts": int(time.time())}
    # Emite exatamente no protocolo: <patch-info> + bloco ```diff```
    sys.stdout.write(f"<patch-info>{json.dumps(info, ensure_ascii=False)}</patch-info>\n")
    sys.stdout.write("```diff\n")
    sys.stdout.write(diff.rstrip() + "\n")
    sys.stdout.write("```\n")
    sys.stdout.flush()

def main() -> None:
    """
    CLI de emissão em texto (Protocolo Vanguarda).
    Lê JSON de stdin: {"logs": {...}, "files": {...}}
    Escreve em stdout: <patch-info>{...}</patch-info> + ```diff ...```
    """
    raw = sys.stdin.read()
    try:
        # não falhar se o input vier vazio — usar dicionários vazios
        payload = raw if raw.strip() else "{}"
        out = run_patch_from_json(Path(os.getenv("REPO_ROOT", ".")), payload)
    except Exception as e:
        # mantém silêncio fora do protocolo
        info = {"generator": "fortaleza-llm", "error": str(e), "ts": int(time.time())}
        sys.stdout.write(f"<patch-info>{json.dumps(info, ensure_ascii=False)}</patch-info>\n")
        sys.stdout.write("```diff\n")
        sys.stdout.write("--- a/EMPTY\n+++ b/EMPTY\n@@ -0,0 +1,1 @@\n+// fallback: no-diff\n")
        sys.stdout.write("```\n")
        sys.stdout.flush()
        return
    _print_patch(out.get("diff",""), out.get("patch_info"))

if __name__ == "__main__":
    main()
