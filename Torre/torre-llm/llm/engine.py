from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, Tuple
import os
from .decoder import get_profiles
from .prompt import load_system_prompt, build_user_prompt
from .postprocess import extract_patch
try:
    from ..utils.diff_utils import validate_unified_diff
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from utils.diff_utils import validate_unified_diff
from .backends.openai_compat import OpenAICompat

def _choose_backend() -> str:
    # por agora, apenas "openai_compat" — extensível
    return os.getenv("LLM_BACKEND", "openai_compat")

def _backend_instance(name: str):
    if name == "openai_compat":
        return OpenAICompat()
    raise ValueError(f"Unsupported backend: {name}")

def run_inference(repo_root: Path, logs: Dict[str,str] | None, files: Dict[str,str] | None) -> Dict[str, Any]:
    """
    Executa A/B com perfis (PATCH, PATCH_B) e escolhe o melhor diff válido.
    Critério: diff válido; desempate por menor comprimento.
    """
    main, ab, routing = get_profiles(repo_root)
    system = load_system_prompt(repo_root)
    user = build_user_prompt(logs, files)
    backend_name = _choose_backend()
    backend = _backend_instance(backend_name)

    # Decode MAIN
    text_a, meta_a = backend.generate(system, user, main)
    diff_a, info_a = extract_patch(text_a)
    size_a = len(diff_a or "")

    # Decode AB (fallback)
    text_b, meta_b = backend.generate(system, user, ab)
    diff_b, info_b = extract_patch(text_b)
    size_b = len(diff_b or "")

    # Escolha
    winner = "A"
    diff = diff_a
    info = info_a
    meta = meta_a
    if size_b and (size_b < size_a or not size_a):
        winner = "B"
        diff, info, meta = diff_b, info_b, meta_b

    # Validação final (levanta se inválido)
    validate_unified_diff(diff)

    metrics = {
        "decode_profile": routing.get("default_profile","PATCH"),
        "decode_profile_ab": routing.get("ab_fallback_profile","PATCH_B"),
        "decode_backend": backend_name,
        "decode_winner": winner,
        "diff_size_bytes": len(diff.encode("utf-8")),
        "patch_info_present": bool(info),
    }
    return {"diff": diff, "metrics": metrics, "patch_info": info}
