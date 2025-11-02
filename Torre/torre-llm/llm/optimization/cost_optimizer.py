from __future__ import annotations
import os, math
from typing import Dict, Any, Tuple

DEFAULT_7B=os.getenv("LLM_MODEL_7B","qwen2.5-coder-7b-instruct")
DEFAULT_14B=os.getenv("LLM_MODEL_14B","qwen2.5-coder-14b-instruct")

def _len(obj:Any)->int:
    try:
        if isinstance(obj, dict):
            return sum(len(str(v)) for v in obj.values())
        return len(str(obj))
    except Exception:
        return 0

def compress_logs(logs:Dict[str,str], budget:int=4000)->Dict[str,str]:
    """Compressão ingênua: mantém as últimas N linhas por chave; corta excesso."""
    out={}
    remaining=budget
    keys=list(logs.keys())
    each=max(1, budget//max(1,len(keys)))
    for k in keys:
        v=logs.get(k,"")
        lines=v.splitlines()[-each:]
        s="\n".join(lines)
        remaining-=len(s)
        out[k]=s
    return out

def choose_route(logs:Dict[str,str], files:Dict[str,str])->Dict[str,Any]:
    size=_len(logs)+_len(files)
    # threshold heurístico (podes calibrar via métricas)
    if size<120_000:
        model=DEFAULT_7B
        window="short"
    elif size<360_000:
        model=DEFAULT_14B
        window="medium"
    else:
        model=DEFAULT_14B
        window="long"
    return {
        "model": model,
        "window": window,
        "compressed_logs": compress_logs(logs, budget=6000 if model==DEFAULT_7B else 12000),
    }
