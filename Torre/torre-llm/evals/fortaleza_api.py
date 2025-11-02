from __future__ import annotations
from typing import Optional, Tuple
import os, json, urllib.request

def _post(url: str, body: bytes, ctype: str="text/plain", timeout: int=30) -> Tuple[int, bytes]:
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", ctype)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.getcode(), resp.read()

def validate_diff(diff_text: str) -> dict:
    """
    Tenta validar o diff via backend Fortaleza (se env presente).
    Caso contrário, devolve {"ok": False, "skipped": True}.
    """
    base = os.getenv("FORTALEZA_API_BASE", "").rstrip("/")
    ws = os.getenv("FORTALEZA_WS", "default")
    if not base:
        return {"ok": False, "skipped": True}
    url = f"{base}/workspaces/{ws}/reports/ingest?mode=validate"
    code, data = _post(url, diff_text.encode("utf-8"), "text/plain")
    if code // 100 == 2:
        try:
            return json.loads(data.decode("utf-8"))
        except Exception:
            return {"ok": True, "raw": data.decode("utf-8","ignore")}
    return {"ok": False, "status": code, "raw": data.decode("utf-8","ignore")}
