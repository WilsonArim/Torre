from __future__ import annotations
from typing import Dict, Any, List, Tuple
import os
from .base import ProviderRequest, ProviderResponse
from .adapters.local import LocalStub
from .adapters.openai import OpenAIStub
from .adapters.anthropic import AnthropicStub
from .adapters.google import GoogleStub
from .adapters.smart_fix import SmartFixAdapter
from .adapters.vanguard_fix import VanguardFixAdapter
from .policy import ProvidersPolicy

ALL_ADAPTERS = {
    "openai/gpt-4o": OpenAIStub(),
    "anthropic/claude-3.5": AnthropicStub(),
    "google/gemini-1.5": GoogleStub(),
    "local/qwen2.5-7b": LocalStub(),
    "fortaleza/smart-fix": SmartFixAdapter(),
    "fortaleza/vanguard-fix": VanguardFixAdapter(),
}

def _classify(logs: Dict[str, str], files: Dict[str, str]) -> str:
    msg = " ".join((logs or {}).values()).lower()
    if "ts2304" in msg or "ts2307" in msg or "type" in msg:
        return "types"
    if "build" in msg or "module not found" in msg or "vite" in msg:
        return "build"
    if "test" in msg or "jest" in msg or "vitest" in msg or "pytest" in msg:
        return "tests"
    if "style" in msg or "eslint" in msg or "prettier" in msg:
        return "style"
    return "general"

def _providers_for_stage(stage: str) -> List[str]:
    # regra simples e auditável
    if stage in ("build", "types"):
        return ["fortaleza/vanguard-fix", "fortaleza/smart-fix", "anthropic/claude-3.5", "openai/gpt-4o"]
    if stage in ("tests", "style", "docs", "general"):
        return ["fortaleza/vanguard-fix", "fortaleza/smart-fix", "openai/gpt-4o", "local/qwen2.5-7b"]
    return ["fortaleza/vanguard-fix", "fortaleza/smart-fix", "openai/gpt-4o", "local/qwen2.5-7b"]

class ProvidersRouter:
    """
    Seleciona provedores por regra simples + aplica quotas/política,
    e gera candidatos (um por provedor) para n-best (F13).
    """
    def __init__(self, root: str = "."):
        self.policy = ProvidersPolicy(root=root)

    def decide(self, logs: Dict[str, str], files: Dict[str, str]) -> Dict[str, Any]:
        stage = _classify(logs, files)
        wanted = _providers_for_stage(stage)
        allowed = self.policy.filter_allowed(wanted)
        # aplica quotas (filtra indisponíveis agora)
        eligible = [p for p in allowed if self.policy.check_quota(p)]
        fallback = allowed or wanted
        final = eligible or fallback[:1]
        reason = f"{stage}: {'+'.join(final)}"
        return {"stage": stage, "providers": final, "reason": reason}

    def generate_candidates(self, req: ProviderRequest, decision: Dict[str, Any]) -> List[ProviderResponse]:
        candidates: List[ProviderResponse] = []
        for pid in decision.get("providers", []):
            adapter = ALL_ADAPTERS.get(pid)
            if not adapter:
                continue
            if not self.policy.check_quota(pid):
                continue
            resp = adapter.generate(req)
            self.policy.mark_use(pid)
            candidates.append(resp)
        return candidates
