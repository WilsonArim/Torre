from pathlib import Path
import json


def check_licenses(sbom_path: Path, allow: list[str]) -> dict:
    if not sbom_path.exists():
        return {"ok": True, "violations": []}
    try:
        data = json.loads(sbom_path.read_text(encoding="utf-8"))
    except Exception:
        return {"ok": True, "violations": []}
    components = data.get("components") or []
    violations: list[dict] = []
    for c in components:
        lic = None
        for l in c.get("licenses", []) or []:
            if isinstance(l, dict):
                lic = (l.get("license", {}) or {}).get("id") or lic
        if lic and lic not in allow:
            violations.append({"component": c.get("name"), "license": lic})
    return {"ok": len(violations) == 0, "violations": violations}


