from __future__ import annotations
import json, os, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

TEST_FILES = [
    "evals/test_phase1.py",
    "evals/test_phase2.py",
    "evals/test_phase6.py",
    "evals/test_phase7.py",
    "evals/test_phase8.py",
    "evals/test_phase9.py",
    "evals/test_phase10.py",
    "evals/test_phase11.py",
]

def run(cmd: list[str]) -> dict:
    t0 = time.time()
    p = subprocess.run([sys.executable, *cmd], capture_output=True, text=True)
    dt = int((time.time() - t0) * 1000)
    return {
        "cmd": " ".join(["python3", *cmd]),
        "rc": p.returncode,
        "ms": dt,
        "stdout": p.stdout[-2000:],  # tail
        "stderr": p.stderr[-2000:],
    }

def main():
    os.environ.setdefault("LLM_RERANK", "1")  # garantir rerank ligado
    report = {
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "rerank_default": os.getenv("LLM_RERANK"),
        "results": [],
    }
    ok = 0
    for tf in TEST_FILES:
        if not Path(tf).exists():
            report["results"].append({"file": tf, "skipped": True})
            continue
        r = run([tf])
        r["file"] = tf
        r["status"] = "ok" if r["rc"] == 0 else "fail"
        if r["rc"] == 0:
            ok += 1
        report["results"].append(r)

    report["summary"] = {
        "passed": ok,
        "total": len([f for f in TEST_FILES if Path(f).exists()]),
        "pass_rate": round(100.0 * ok / max(1, len([f for f in TEST_FILES if Path(f).exists()])), 2),
    }
    outdir = Path(".fortaleza/audit")
    outdir.mkdir(parents=True, exist_ok=True)
    # rotação leve: mantém até 20 arquivos
    existing = sorted([p for p in outdir.glob("audit-*.json")])
    if len(existing) > 20:
        for p in existing[:-20]:
            try: p.unlink()
            except Exception: pass
    outfile = outdir / f"audit-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}.json"
    outfile.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(json.dumps(report["summary"], ensure_ascii=False))

if __name__ == "__main__":
    main()
