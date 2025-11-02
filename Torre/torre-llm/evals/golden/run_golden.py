#!/usr/bin/env python3
from __future__ import annotations
import json, os, subprocess, sys, time
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
CASES_DIR = ROOT / "evals" / "golden" / "cases"
OUT_DIR = ROOT / ".fortaleza" / "golden"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def _utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00","Z")

def _run_cli(case: dict, timeout=20) -> tuple[int, dict]:
    inp = (json.dumps(case) + "\n").encode()
    env = os.environ.copy()
    env.setdefault("LLM_RERANK","1")
    env.setdefault("STRATEGOS_V2","1")
    p = subprocess.run([sys.executable,"-m","llm.cli"], input=inp, env=env,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
    code = p.returncode
    try:
        out = json.loads(p.stdout.decode() or "{}")
    except Exception:
        out = {"error":"invalid_json","stdout":p.stdout[:200].decode(errors="ignore")}
    return code, out

def main(limit: int|None = None) -> int:
    cases = sorted(CASES_DIR.glob("*.json"))
    if limit: cases = cases[:limit]
    results = []
    ok = 0
    for path in cases:
        case = json.loads(path.read_text())
        started = time.time()
        code, out = _run_cli(case)
        dur_ms = int((time.time()-started)*1000)
        passed = (code == 0) and bool(out.get("diff") or out.get("advice") or out.get("report"))
        ok += int(passed)
        results.append({
            "case": path.name, "passed": passed, "rc": code, "dur_ms": dur_ms,
            "trace_id": out.get("trace_id"), "metrics": out.get("metrics",{}),
        })
    summary = {
        "ts": _utc(), "total": len(results), "passed": ok,
        "success_rate": (ok/len(results)*100.0 if results else 0.0),
        "results": results,
    }
    outpath = OUT_DIR / f"golden-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    outpath.write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    print(json.dumps(summary, ensure_ascii=False))
    # gate default: 95%
    return 0 if summary["success_rate"] >= float(os.getenv("GOLDEN_MIN_SR","95")) else 1

if __name__ == "__main__":
    lim = int(sys.argv[1]) if len(sys.argv) > 1 else None
    raise SystemExit(main(lim))
