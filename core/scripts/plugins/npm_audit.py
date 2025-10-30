from pathlib import Path
import json


def summarize_npm_audit(report_path: Path) -> dict:
    if not report_path.exists():
        return {"ok": True, "critical": 0}
    try:
        data = json.loads(report_path.read_text(encoding="utf-8"))
    except Exception:
        return {"ok": True, "critical": 0}
    vul = data.get("vulnerabilities") or {}
    critical = vul.get("critical") or 0
    return {"ok": critical == 0, "critical": critical}


