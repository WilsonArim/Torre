#!/usr/bin/env python3
import json, os, subprocess, sys, time, shutil
from datetime import datetime, timezone

METRICS_FILE = os.environ.get("METRICS_FILE", ".metrics")
ESL_EXT = os.environ.get("ESL_EXT", ".ts,.tsx")
ROOT = os.getcwd()

def _run(cmd, timeout=300):
    try:
        return subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
    except Exception as e:
        return None

def _now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00","Z")

def eslint_count():
    """Retorna contagem total de erros+warnings do ESLint em JSON (0 se indisponível)."""
    if not shutil.which("npx"):
        return 0
    cmd = f"npx eslint . --ext {ESL_EXT} -f json"
    r = _run(cmd, timeout=300)
    if not r or (r.returncode not in (0,1)):  # 1 também acontece quando há erros
        try:
            data = json.loads(r.stdout or "[]")
        except Exception:
            return 0
    try:
        data = json.loads(r.stdout or "[]")
    except Exception:
        return 0
    total = 0
    for file in data:
        total += int(file.get("errorCount",0)) + int(file.get("warningCount",0))
    return total

def semgrep_count(config_path):
    """Retorna número de achados do Semgrep para um config (0 se indisponível)."""
    if not shutil.which("semgrep"):
        return 0
    cmd = f"semgrep --quiet --json --config {config_path}"
    r = _run(cmd, timeout=300)
    if not r or r.returncode not in (0,1,2):  # 1/2 podem indicar achados
        return 0
    try:
        data = json.loads(r.stdout or "{}")
    except Exception:
        return 0
    results = data.get("results")
    if isinstance(results, list):
        return len(results)
    return 0

def ts_codefix_apply():
    """Roda tsserver CodeFix e retorna 'applied' (edits)."""
    if not shutil.which("npx"):
        return 0
    r = _run("npx ts-node tools/fixer/tsserver_fix.ts", timeout=300)
    if not r:
        return 0
    try:
        data = json.loads(r.stdout or "{}")
        return int(data.get("applied", 0))
    except Exception:
        return 0

def eslint_fix():
    if not shutil.which("npx"):
        return
    _run(f"npx eslint . --ext {ESL_EXT} --fix", timeout=600)

def biome_apply():
    if not shutil.which("npx"):
        return
    _run("npx biome check . --apply --diagnostic-level=info", timeout=600)

def semgrep_fix_all():
    if not shutil.which("semgrep"):
        return
    _run("semgrep scan --config tools/semgrep/ts-react.yml --autofix || true", timeout=600)
    _run("semgrep scan --config tools/semgrep/python-fastapi.yml --autofix || true", timeout=600)

def codemods_apply():
    if not shutil.which("npx"):
        return {"edits_total":0, "per_codemod":{}}
    r = _run("npx ts-node tools/codemods/tsmods.ts", timeout=600)
    try:
        data = json.loads((r.stdout or "{}").strip())
        return {
            "edits_total": int(data.get("edits_total", 0)),
            "per_codemod": data.get("per_codemod", {})
        }
    except Exception:
        return {"edits_total":0, "per_codemod":{}}

def git_changed_files_count():
    if not shutil.which("git"):
        return None
    r = _run("git diff --name-only", timeout=120)
    if not r:
        return None
    names = [x for x in (r.stdout or "").splitlines() if x.strip()]
    return len(names)

def main():
    started = time.time()
    ts0 = _now()

    # BEFORE counts
    eslint_before = eslint_count()
    sg_ts_before = semgrep_count("tools/semgrep/ts-react.yml")
    sg_py_before = semgrep_count("tools/semgrep/python-fastapi.yml")

    # RUN: tsserver CodeFix
    ts_applied = ts_codefix_apply()

    # RUN: ESLint + Biome
    eslint_fix()
    biome_apply()

    # RUN: Semgrep --fix
    semgrep_fix_all()

    # RUN: Codemods ts-morph
    codemods = codemods_apply()

    # AFTER counts
    eslint_after = eslint_count()
    sg_ts_after = semgrep_count("tools/semgrep/ts-react.yml")
    sg_py_after = semgrep_count("tools/semgrep/python-fastapi.yml")

    # deltas
    eslint_resolved = max(0, eslint_before - eslint_after)
    semgrep_resolved = max(0, (sg_ts_before + sg_py_before) - (sg_ts_after + sg_py_after))
    codemods_edits = int(codemods.get("edits_total", 0))

    files_changed = git_changed_files_count()

    out = {
        "ts": ts0,
        "duration_ms": int((time.time() - started) * 1000),
        "step_metrics": {
            "ts_codefix_resolved": int(ts_applied),
            "eslint_resolved": int(eslint_resolved),
            "semgrep_resolved": int(semgrep_resolved),
            "codemods_edits": int(codemods_edits),
        },
        "codemods_per_codemod": codemods.get("per_codemod", {}),
        "files_changed": files_changed,
        "root": ROOT
    }

    # Append em JSONL no arquivo .metrics
    with open(METRICS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(out, ensure_ascii=False) + "\n")

    print(json.dumps({"ok": True, "written": METRICS_FILE, **out}, ensure_ascii=False))

if __name__ == "__main__":
    sys.exit(main() or 0)
