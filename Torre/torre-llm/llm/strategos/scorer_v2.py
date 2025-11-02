from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple, Any
import math
import os

# Ordem canónica das etapas
STEPS = ["build", "types", "tests", "style"]

@dataclass
class NodeMetrics:
    path: str
    indeg: int = 0
    outdeg: int = 0
    centrality: float = 0.0  # aproximação: (in+out)/max_degree
    churn: float = 0.0       # episódios tocando este ficheiro (normalizado)
    coverage: float = 0.0    # opcional [0..1]
    is_core: bool = False    # heurística simples


def _safe_len_lines(s: str) -> int:
    if not isinstance(s, str):
        return 0
    return s.count("\n") + 1 if s else 0


class StrategosV2Graph:
    """
    Scorer impacto×risco×custo com consciência do grafo.
    Robusto a input parcial (funciona sem grafo ou sem memória).
    """
    def __init__(self, weights: Dict[str, float] | None = None):
        # pesos padrão (ajustáveis por workspace)
        w = weights or {}
        self.W_IMPACT = float(w.get("impact", 0.5))
        self.W_RISK   = float(w.get("risk",   0.3))
        self.W_COST   = float(w.get("cost",   0.2))
        # caps conservadores por etapa (influenciam score final)
        self.CAPS = {"build": 1.30, "types": 1.15, "tests": 1.05, "style": 1.00}

    # -------------------------- GRAFO → MÉTRICAS --------------------------
    def build_metrics(self, codemap: Dict[str, Any], episodes: List[Dict[str, Any]] | None = None) -> Dict[str, NodeMetrics]:
        """
        codemap: {'nodes': [{'id': 'src/a.ts', ...}, ...], 'edges': [{'from': 'src/a.ts','to':'src/b.ts'}]}
        episodes: lista de episódios (opcional) para calcular churn por ficheiro.
        """
        nodes = [n.get("id") or n.get("path") for n in (codemap.get("nodes") or [])]
        edges = [(e.get("from"), e.get("to")) for e in (codemap.get("edges") or [])]
        nodes = [n for n in nodes if isinstance(n, str)]
        m: Dict[str, NodeMetrics] = {p: NodeMetrics(path=p) for p in nodes}
        # graus
        for u, v in edges:
            if u in m:
                m[u].outdeg += 1
            if v in m:
                m[v].indeg += 1
        maxdeg = max([mx.indeg + mx.outdeg for mx in m.values()] or [1])
        for mx in m.values():
            mx.centrality = (mx.indeg + mx.outdeg) / maxdeg if maxdeg else 0.0
            # Heurística "core": diretórios comuns de domínio/infra
            p = mx.path.lower()
            mx.is_core = any(seg in p for seg in ("/core", "/domain", "/lib/", "/infra"))
        # churn por episódios
        if episodes:
            freq: Dict[str, int] = {}
            for ep in episodes:
                f = ep.get("file") or ep.get("path") or ""
                if isinstance(f, str) and f:
                    freq[f] = freq.get(f, 0) + 1
            maxf = max(freq.values() or [1])
            for path, cnt in freq.items():
                if path in m:
                    m[path].churn = cnt / maxf
        return m

    # ----------------------- SCORE IMPACTO/RISCO/CUSTO ---------------------
    def _impact(self, mx: NodeMetrics) -> float:
        # centralidade + ligeiro boost se "core"
        return mx.centrality * (1.0 + (0.15 if mx.is_core else 0.0))

    def _risk(self, mx: NodeMetrics) -> float:
        # churn (bugs recorrentes) + risco estrutural (fan-out=outdeg)
        # normalizamos fanout localmente (log2 para estabilizar)
        fanout = math.log2(1 + mx.outdeg) / 6.0  # ~[0..~0.3]
        return min(1.0, 0.7 * mx.churn + 0.3 * fanout)

    def _cost(self, path: str, files_ctx: Dict[str, str] | None) -> float:
        # custo ~ linhas a tocar (proxy: tamanho atual). Se desconhecido, neutro.
        if not files_ctx:
            return 0.5
        size = _safe_len_lines(files_ctx.get(path, ""))  # 0 se não existir
        # normaliza por um tamanho típico de arquivo (200 linhas)
        return min(1.0, size / 200.0) if size > 0 else 0.4

    def score_nodes(self, metrics: Dict[str, NodeMetrics], files_ctx: Dict[str, str] | None) -> Dict[str, float]:
        out: Dict[str, float] = {}
        for p, mx in metrics.items():
            s_impact = self._impact(mx)
            s_risk   = self._risk(mx)
            s_cost   = self._cost(p, files_ctx)
            # score final proporcional a (impacto×risco)/custo (evita alvo caro cedo)
            base = (s_impact * max(1e-3, s_risk)) / max(0.15, s_cost)
            out[p] = base
        return out

    # ----------------------- ORDEM POR ETAPA (GATES) -----------------------
    def _step_boosts(self, logs: Dict[str, str] | None) -> Dict[str, float]:
        msg = " ".join(str(v) for v in (logs or {}).values()).lower()
        boosts = {k: 1.0 for k in STEPS}
        if any(x in msg for x in ("module not found", "cannot find module", "enoent", "vite build failed", "import error")):
            boosts["build"] = 1.30
        if any(x in msg for x in ("ts", "ts2304", "cannot find name", "type error", "mypy")):
            boosts["types"] = max(boosts["types"], 1.15)
        if any(x in msg for x in ("fail", "assert", "pytest", "jest", "vitest")):
            boosts["tests"] = max(boosts["tests"], 1.05)
        return boosts

    def plan(self,
             codemap: Dict[str, Any] | None,
             logs: Dict[str, str] | None,
             files_ctx: Dict[str, str] | None,
             episodes: List[Dict[str, Any]] | None = None,
             top_k: int = 8) -> Dict[str, Any]:
        """
        Gera plano com etapas ordenadas build→types→tests→style,
        priorizando nós pelos scores (impacto×risco)/custo com boosts e caps.
        """
        codemap = codemap or {"nodes": [], "edges": []}
        metrics = self.build_metrics(codemap, episodes)
        node_scores = self.score_nodes(metrics, files_ctx)
        # ranking global por score
        ranked = sorted(node_scores.items(), key=lambda kv: kv[1], reverse=True)[: max(top_k, 1)]
        boosts = self._step_boosts(logs)

        steps: List[Dict[str, Any]] = []
        for step in STEPS:
            cap = self.CAPS.get(step, 1.0)
            for path, base in ranked:
                s = round(base * boosts.get(step, 1.0) * cap, 4)
                mx = metrics.get(path)
                steps.append({
                    "stage": step,
                    "target": path,
                    "score": s,
                    "impact": round(self._impact(mx), 4) if mx else 0.0,
                    "risk": round(self._risk(mx), 4) if mx else 0.0,
                    "cost": round(self._cost(path, files_ctx), 4),
                    "exit_criteria": self._exit_criteria(step)
                })
        # ordena: etapa na ordem canónica; depois score desc
        idx = {k: i for i, k in enumerate(STEPS)}
        steps.sort(key=lambda d: (idx.get(d["stage"], 99), -d["score"]))

        # fallback seguro: se todos empatam (sem grafo útil), retornar ADVICE
        all_same = len({(d["stage"], round(d["score"], 3)) for d in steps}) <= 2
        mode = "ADVICE" if all_same else "PATCH"
        return {
            "mode": mode,
            "weights": {"impact": self.W_IMPACT, "risk": self.W_RISK, "cost": self.W_COST},
            "boosts": boosts,
            "nodes_considered": [p for p, _ in ranked],
            "steps": steps[: max(top_k * len(STEPS), 8)]
        }

    @staticmethod
    def _exit_criteria(step: str) -> List[str]:
        if step == "build":
            return ["build seco OK", "sem erros de import", "git apply --check OK"]
        if step == "types":
            return ["tsc/mypy 0 erros", "sem TS2304/TS2307"]
        if step == "tests":
            return ["unit + contract verdes", "smoke vizinhança OK"]
        if step == "style":
            return ["lint OK", "sem duplicações críticas"]
        return []
