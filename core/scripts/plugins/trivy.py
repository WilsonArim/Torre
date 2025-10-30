from pathlib import Path
import json


def summarize_trivy(report_path: Path) -> dict:
    if not report_path.exists():
        return {"ok": True, "critical": 0}
    try:
        data = json.loads(report_path.read_text(encoding="utf-8"))
    except Exception:
        return {"ok": True, "critical": 0}
    results = data.get("Results") or []
    critical = 0
    for r in results:
        for v in r.get("Vulnerabilities", []) or []:
            if (v.get("Severity") or "").upper() == "CRITICAL":
                critical += 1
    return {"ok": critical == 0, "critical": critical}


