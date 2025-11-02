from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Protocol, Optional
import time

def _est_tokens(s: str) -> int:
    # Heurística simples (≈ 4 chars/token)
    return max(0, len(s) // 4)

@dataclass
class ProviderRequest:
    logs: Dict[str, str]
    files: Dict[str, str]
    meta: Dict[str, Any] | None = None

@dataclass
class ProviderResponse:
    provider: str
    diff: str
    tokens_in: int = 0
    tokens_out: int = 0
    latency_ms: int = 0
    meta: Dict[str, Any] | None = None
    
    @property
    def success(self) -> bool:
        """Verifica se a resposta foi bem-sucedida"""
        return bool(self.diff and "---" in self.diff and "+++" in self.diff)
    
    @property
    def error(self) -> str | None:
        """Retorna erro se houver"""
        return self.meta.get("error") if self.meta else None

class Provider(Protocol):
    name: str
    def generate(self, req: ProviderRequest) -> ProviderResponse: ...

def make_noop_diff(filename: Optional[str] = None) -> str:
    # no-op compatível com unified diff
    target = filename or "IN_MEMORY"
    return f"--- a/{target}\n+++ b/{target}\n"
