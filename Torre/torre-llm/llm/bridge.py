from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any
from .engine import run_inference

def run_patch_from_json(repo_root: Path, json_input: str) -> Dict[str, Any]:
    """
    Reutiliza a lógica do engine para gerar patch a partir de JSON string.
    """
    try:
        body = json.loads(json_input or "{}")
    except Exception:
        body = {}
    
    logs = body.get("logs") or {}
    files = body.get("files") or {}
    
    return run_inference(repo_root, logs=logs, files=files)
