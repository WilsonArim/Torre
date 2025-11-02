from __future__ import annotations
import os, json, time
from typing import Dict, Any, Tuple
import urllib.request

class OpenAICompat:
    """
    Cliente compatível com o endpoint /chat/completions (OpenAI-like).
    Funciona com provedores: vLLM, Together, OpenRouter, servidores self-hosted, etc.
    """
    def __init__(self) -> None:
        self.base = os.getenv("OPENAI_BASE", "https://api.openai.com/v1")
        self.model = os.getenv("OPENAI_MODEL", "qwen2.5-coder-7b-instruct")
        self.api_key = os.getenv("OPENAI_API_KEY", "")

    def generate(self, system: str, user: str, profile: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        # --- SMOKE MODE (offline) -------------------------------------------------
        if os.getenv("LLM_SMOKE", "0") == "1":
            ts = int(time.time())
            dummy = f"""<patch-info>{{"generator":"openai_compat","mode":"smoke","ts":{ts}}}</patch-info>
```diff
--- a/fortaleza-llm/llm/README.md
+++ b/fortaleza-llm/llm/README.md
@@ -1,5 +1,8 @@
 # Fortaleza LLM — Núcleo (engine/backends)
 
 ## O que é
 Camada mínima para gerar **UM** `diff` unificado a partir de logs/files, com:
 - perfis de decodificação (PATCH / PATCH_B) → A/B,
+- **SMOKE mode (offline)** para validação rápida da CLI sem rede.
```
"""
            return dummy, {"provider": "openai_compat", "model": self.model, "usage": {"mode": "smoke"}}
        # --------------------------------------------------------------------------
        url = self.base.rstrip("/") + "/chat/completions"
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ],
            "temperature": float(profile.get("temperature", 0.1)),
            "top_p": float(profile.get("top_p", 0.2)),
            "max_tokens": int(profile.get("max_tokens", 1200)),
        }
        # suportar stop tokens e seed se o backend aceitar
        if "stop" in profile:
            payload["stop"] = profile["stop"]
        if "seed" in profile:
            payload["seed"] = profile["seed"]
        if "repetition_penalty" in profile:
            payload["repetition_penalty"] = profile["repetition_penalty"]
        data = json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = resp.read().decode("utf-8", "ignore")
        obj = json.loads(raw)
        text = ""
        try:
            text = obj["choices"][0]["message"]["content"]
        except Exception:
            text = obj.get("choices",[{}])[0].get("text","")
        usage = obj.get("usage", {})
        return text, {"provider": "openai_compat", "model": self.model, "usage": usage}
