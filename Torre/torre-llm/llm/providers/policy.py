from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, List, Tuple
import json, os, time

DEFAULT_ALLOWED = [
    "fortaleza/vanguard-fix",
    "fortaleza/smart-fix",
    "openai/gpt-4o",
    "anthropic/claude-3.5",
    "google/gemini-1.5",
    "local/qwen2.5-7b",
]

DEFAULT_QUOTAS = {
    # por provedor: rpm e daily budget (USD simbólico, não cobramos de fato)
    "fortaleza/vanguard-fix": {"rpm": 2000, "daily_usd": 0},  # Máxima prioridade, sem custo
    "fortaleza/smart-fix": {"rpm": 1000, "daily_usd": 0},  # Sem custo, alta prioridade
    "openai/gpt-4o": {"rpm": 60, "daily_usd": 100},
    "anthropic/claude-3.5": {"rpm": 40, "daily_usd": 100},
    "google/gemini-1.5": {"rpm": 60, "daily_usd": 100},
    "local/qwen2.5-7b": {"rpm": 600, "daily_usd": 0},
}

class ProvidersPolicy:
    def __init__(self, root: str | Path = "."):
        self.root = Path(root)
        self.allowed = list(DEFAULT_ALLOWED)
        self.quotas = dict(DEFAULT_QUOTAS)
        self._counters: Dict[str, Dict[str, Any]] = {}
        self._load_yaml()

    def _load_yaml(self):
        try:
            import yaml  # type: ignore
        except Exception:
            yaml = None
        cfg = self.root / ".fortaleza" / "providers.yaml"
        if yaml and cfg.exists():
            try:
                data = yaml.safe_load(cfg.read_text()) or {}
                self.allowed = data.get("allowed", self.allowed)
                self.quotas.update(data.get("quotas", {}))
            except Exception:
                pass

    def filter_allowed(self, providers: List[str]) -> List[str]:
        allowed = {p for p in self.allowed}
        return [p for p in providers if p in allowed]

    def check_quota(self, provider: str) -> bool:
        q = self.quotas.get(provider, {})
        rpm = int(q.get("rpm", 999999))
        day = time.strftime("%Y-%m-%d")
        c = self._counters.setdefault(provider, {"rpm": [], "day": day, "day_count": 0})
        now = time.time()
        # limpa janela de 60s
        c["rpm"] = [t for t in c["rpm"] if now - t < 60]
        if len(c["rpm"]) >= rpm:
            return False
        # dia
        if c["day"] != day:
            c["day"] = day
            c["day_count"] = 0
        # não medimos $ real, apenas número de chamadas/dia como proxy
        daily_cap = int(q.get("daily_calls", 999999))
        if c["day_count"] >= daily_cap:
            return False
        return True

    def mark_use(self, provider: str):
        c = self._counters.setdefault(provider, {"rpm": [], "day": time.strftime("%Y-%m-%d"), "day_count": 0})
        c["rpm"].append(time.time())
        c["day_count"] += 1
