import os, json
from urllib import request, parse
from typing import Any, Dict
from pathlib import Path

API_BASE = os.getenv("TORRE_API_BASE", "http://localhost:8000")

def _post(url: str, data: bytes, content_type: str="application/json") -> bool:
    req = request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", content_type)
    try:
        with request.urlopen(req, timeout=30) as resp:
            return 200 <= resp.status < 300
    except Exception:
        return False

def ingest_report(ws: str, mode: str, payload: Any, content_type: str="application/json") -> bool:
    url = f"{API_BASE}/workspaces/{ws}/reports/ingest?mode={parse.quote(mode)}"
    if isinstance(payload, str) and content_type == "text/plain":
        data = payload.encode("utf-8")
    else:
        data = json.dumps(payload).encode("utf-8")
    return _post(url, data, content_type=content_type)

def get_pipeline_state(ws: str) -> Dict[str, Any]:
    url = f"{API_BASE}/workspaces/{ws}/pipeline/state"
    try:
        with request.urlopen(url, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return {"workspace": ws, "state": "unknown"}

def write_pipeline_state(state: Dict[str, Any]) -> None:
    p = Path(".torre")
    p.mkdir(exist_ok=True)
    with open(p / "pipeline_state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
