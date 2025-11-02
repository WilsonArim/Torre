from __future__ import annotations

import json
import os
from typing import Any, Dict, List

# Fallback local
from llm.rerank.execution_reranker import ExecutionReranker


def _post_json(url: str, payload: Dict[str, Any], timeout: float = 2.0) -> Dict[str, Any]:
    """POST JSON sem dependências externas (urllib)."""
    import urllib.request
    import urllib.error

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8")
        return json.loads(body) if body else {}


def rerank(workspace: str, candidates: List[str], k: int = 3) -> Dict[str, Any]:
    """
    Tenta via HTTP (server.py → /rerank/execute). Se falhar, usa ExecutionReranker local.
    """
    api_base = os.getenv("FORTALEZA_API", "http://localhost:8765").rstrip("/")
    url = f"{api_base}/rerank/execute"
    payload = {"workspace": workspace or "default", "candidates": candidates, "k": int(max(1, min(k, len(candidates))))}

    try:
        return _post_json(url, payload)
    except Exception:
        # Fallback local (sem rede)
        rr = ExecutionReranker()
        return rr.run(payload["workspace"], payload["candidates"], k=payload["k"])
