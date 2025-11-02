#!/usr/bin/env python3
from __future__ import annotations
import csv, json, os, sys, glob
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
FORT = ROOT / ".fortaleza"
KPIS = FORT / "kpis"
KPIS.mkdir(parents=True, exist_ok=True)

def _utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00","Z")

def _latest(pattern: Path) -> Path|None:
    files = sorted(glob.glob(str(pattern)))
    return Path(files[-1]) if files else None

def _load_json(p: Path) -> dict:
    try:
        return json.loads(p.read_text())
    except Exception:
        return {}

def _collect():
    # Golden
    golden = _latest(FORT / "golden" / "golden-*.json")
    golden_sr = None
    if golden and golden.exists():
        golden_sr = float(_load_json(golden).get("success_rate") or 0.0)
    # Red-team (opcional)
    red_dir = FORT / "redteam"
    red_dir.mkdir(exist_ok=True, parents=True)
    red = _latest(red_dir / "redteam-*.json")
    red_pass = None
    if red and red.exists():
        rj = _load_json(red)
        tot = int(rj.get("total") or 0); pas = int(rj.get("passed") or 0)
        red_pass = (pas / tot * 100.0) if tot else None
    # Memory episodic (opcional)
    mem_meta = FORT / "memory" / "meta.json"
    mem = _load_json(mem_meta) if mem_meta.exists() else {}
    repeat_rate = mem.get("repeat_error_rate")
    rules_promoted = mem.get("rules_promoted")
    rules_hit_rate = mem.get("rules_hit_rate")
    # Traces de hoje → reqs, latência média/mediana
    trace_today = FORT / "trace" / f"trace-{datetime.now().strftime('%Y%m%d')}.jsonl"
    reqs = 0; lat_list = []
    if trace_today.exists():
        with trace_today.open() as fh:
            for line in fh:
                try:
                    ev = json.loads(line)
                except Exception:
                    continue
                reqs += 1
                lat = ev.get("latency_ms")
                if isinstance(lat,(int,float)): lat_list.append(float(lat))
    avg_lat = (sum(lat_list)/len(lat_list)) if lat_list else None
    p95_lat = None
    if lat_list:
        lat_list.sort()
        p95_lat = lat_list[int(0.95*len(lat_list))-1]
    return {
        "ts": _utc_now(),
        "golden_success_rate": golden_sr,
        "redteam_denials_rate": red_pass,
        "repeat_error_rate": repeat_rate,
        "rules_promoted": rules_promoted,
        "rules_hit_rate": rules_hit_rate,
        "requests_today": reqs,
        "latency_ms_avg": avg_lat,
        "latency_ms_p95": p95_lat,
    }

def main():
    snap = _collect()
    # JSON snapshot
    out_json = KPIS / f"kpis-{datetime.now().strftime('%Y%m%d')}.json"
    out_json.write_text(json.dumps(snap, indent=2, ensure_ascii=False))
    # CSV (append diário)
    csv_path = KPIS / "daily.csv"
    header = ["ts","golden_success_rate","redteam_denials_rate","repeat_error_rate","rules_promoted","rules_hit_rate","requests_today","latency_ms_avg","latency_ms_p95"]
    write_header = not csv_path.exists()
    with csv_path.open("a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=header)
        if write_header: w.writeheader()
        w.writerow({k: snap.get(k) for k in header})
    print(json.dumps({"ok": True, "json": str(out_json), "csv": str(csv_path)}))

if __name__ == "__main__":
    raise SystemExit(main())
