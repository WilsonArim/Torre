from pathlib import Path
import json


def summarize_semgrep(sarif_path: Path) -> dict:
    if not sarif_path.exists():
        return {"ok": True, "findings": 0, "blocking": 0}
    try:
        data = json.loads(sarif_path.read_text(encoding="utf-8"))
    except Exception:
        return {"ok": True, "findings": 0, "blocking": 0}
    findings = 0
    blocking = 0
    for run in data.get("runs", []):
        for r in run.get("results", []):
            findings += 1
            level = (r.get("level") or "").upper()
            if level in {"ERROR", "HIGH"}:
                blocking += 1
    return {"ok": blocking == 0, "findings": findings, "blocking": blocking}


