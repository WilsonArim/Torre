from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, Tuple
import json

DEFAULT = {
    "profiles": {
        "PATCH": {
            "temperature": 0.1, "top_p": 0.2, "max_tokens": 1200,
            "stop": ["\n\ndiff --git ", "\n```", "\n# END_PATCH"],
            "seed": 42, "repetition_penalty": 1.02
        },
        "PATCH_B": {
            "temperature": 0.3, "top_p": 0.3, "max_tokens": 1200,
            "stop": ["\n\ndiff --git ", "\n```", "\n# END_PATCH"],
            "seed": 43
        }
    },
    "routing": {"default_profile": "PATCH", "ab_fallback_profile": "PATCH_B"}
}

def _yaml_fallback(text: str) -> Dict[str, Any]:
    """
    Fallback muito simples para YAML→dict quando PyYAML não existir.
    Suporta apenas chaves/valores escalares comuns usados no decode.yaml.
    """
    data: Dict[str, Any] = {}
    cur = data
    stack = [(-1, data)]
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1] if stack else data
        if ":" in line:
            k, v = line.lstrip().split(":", 1)
            k = k.strip()
            v = v.strip()
            if not v:
                # new dict
                parent[k] = {}
                stack.append((indent, parent[k]))
            else:
                # normalize scalar
                if v.lower() in ("true", "false"):
                    parent[k] = (v.lower() == "true")
                elif v.isdigit():
                    parent[k] = int(v)
                else:
                    try:
                        parent[k] = float(v)
                    except Exception:
                        if v.startswith("[") and v.endswith("]"):
                            try:
                                parent[k] = json.loads(v.replace("'", '"'))
                            except Exception:
                                parent[k] = v
                        else:
                            parent[k] = v.strip('"').strip("'")
    return data

def load_decode_config(repo_root: Path) -> Dict[str, Any]:
    cfg_path = repo_root / "fortaleza-llm" / "configs" / "models.decode.yaml"
    if not cfg_path.exists():
        return DEFAULT
    try:
        import yaml  # type: ignore
        return yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or DEFAULT
    except Exception:
        return _yaml_fallback(cfg_path.read_text(encoding="utf-8")) or DEFAULT

def get_profiles(repo_root: Path) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    cfg = load_decode_config(repo_root)
    profiles = cfg.get("profiles") or DEFAULT["profiles"]
    routing = cfg.get("routing") or DEFAULT["routing"]
    main = profiles.get(routing.get("default_profile", "PATCH"), profiles["PATCH"])
    ab   = profiles.get(routing.get("ab_fallback_profile", "PATCH_B"), profiles["PATCH_B"])
    return main, ab, routing
