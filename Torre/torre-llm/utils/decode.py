from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, Tuple

_DEFAULTS: Dict[str, Any] = {
    "profiles": {
        "PATCH": {
            "temperature": 0.1, "top_p": 0.2, "max_tokens": 1200,
            "stop": ["\n\ndiff --git ", "\n```", "\n# END_PATCH"],
            "seed": 42, "repetition_penalty": 1.02,
        },
        "PATCH_B": {
            "temperature": 0.3, "top_p": 0.3, "max_tokens": 1200,
            "stop": ["\n\ndiff --git ", "\n```", "\n# END_PATCH"],
            "seed": 43, "repetition_penalty": 1.02,
        },
    },
    "routing": {"default_profile": "PATCH", "ab_fallback_profile": "PATCH_B"},
}

def load_decode_profiles(path: str | Path = "fortaleza-llm/configs/models.decode.yaml") -> Dict[str, Any]:
    """
    Carrega YAML; se não existir ou PyYAML não estiver instalado, devolve defaults.
    Nunca lança; sempre devolve um dicionário utilizável.
    """
    p = Path(path)
    if not p.exists():
        return dict(_DEFAULTS)
    try:
        try:
            import yaml  # type: ignore
        except Exception:
            return dict(_DEFAULTS)
        with p.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        if not isinstance(data, dict):
            return dict(_DEFAULTS)
        # validações mínimas
        if "profiles" not in data or "routing" not in data:
            return dict(_DEFAULTS)
        return data
    except Exception:
        return dict(_DEFAULTS)

def choose_profiles(cfg: Dict[str, Any]) -> Tuple[str, str]:
    r = cfg.get("routing", {}) or {}
    main = r.get("default_profile") or "PATCH"
    alt = r.get("ab_fallback_profile") or "PATCH_B"
    return str(main), str(alt)

def get_profile(cfg: Dict[str, Any], name: str) -> Dict[str, Any]:
    return dict((cfg.get("profiles", {}) or {}).get(name, {}))
