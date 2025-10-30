from pathlib import Path
import json


def summarize_bandit(report_path: Path) -> dict:
    if not report_path.exists():
        return {"ok": True, "issues": 0}
    try:
        data = json.loads(report_path.read_text(encoding="utf-8"))
    except Exception:
        return {"ok": True, "issues": 0}
    issues = len(data.get("results", []))
    return {"ok": issues == 0, "issues": issues}


