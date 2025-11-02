from __future__ import annotations
from typing import Dict, Any, List, Set, Tuple

class RefactorAdvisor:
    """
    Gera um plano de refactor **mínimo e reversível**:
      - Quebrar ciclos simples
      - Remover acoplamentos proibidos (via re-export/intermediário)
      - Sugerir extrações (quando grau/size altos)
    Saída é **advisory** (não aplica patch aqui). O motor principal gera o diff.
    """
    def __init__(self) -> None:
        pass

    def _cycles(self, codemap: Dict[str, Any]) -> List[List[str]]:
        # DFS simples para ciclos curtos (3 arestas no máx. para custo baixo)
        adj: Dict[str, List[str]] = {}
        for a, b in codemap.get("edges", []):
            if b.startswith("pkg:"):  # ignora externos
                continue
            adj.setdefault(a, []).append(b)
        max_depth = 3
        cycles: List[List[str]] = []

        def dfs(start: str, cur: List[str], seen: Set[str]):
            if len(cur) > max_depth:
                return
            u = cur[-1]
            for v in adj.get(u, []):
                if v == start and len(cur) >= 2:
                    cycles.append(cur + [start])
                elif v not in seen:
                    dfs(start, cur + [v], seen | {v})
        for n in codemap.get("nodes", []):
            dfs(n, [n], {n})
        # dedup aproximado
        uniq = []
        for c in cycles:
            if c not in uniq:
                uniq.append(c)
        return uniq[:20]

    def plan(self, codemap: Dict[str, Any], coupling_report: Dict[str, Any], hotspots: List[Dict[str, Any]]) -> Dict[str, Any]:
        actions: List[Dict[str, Any]] = []
        evidence: List[str] = []

        # 1) Resolver primeiros acoplamentos proibidos (prioridade)
        for v in coupling_report.get("violations", [])[:10]:
            actions.append({
                "type": "decouple_layers",
                "from": v["from"],
                "to": v["to"],
                "rule": v["rule"],
                "method": "introduce_service_boundary_or_reexport",
                "advice": "Mover acesso a infraestrutura para um serviço/porta; UI consome apenas o serviço.",
            })
            evidence.append(f"Coupling: {v['from_layer']}->{v['to_layer']} between {v['from']} -> {v['to']}")

        # 2) Ciclos curtos (quebra por re-export/intermediário)
        for cyc in self._cycles(codemap)[:5]:
            actions.append({
                "type": "break_cycle",
                "path": cyc,
                "method": "introduce_mediator_or_split_module",
                "advice": "Criar módulo intermediário (porta) ou mover símbolo para reduzir dependência circular.",
            })
            evidence.append(f"Cycle: {' -> '.join(cyc)}")

        # 3) Hotspots (sugestão de extração leve)
        for h in hotspots[:5]:
            if h["score"] >= 1.0 and h["deg"] >= 8:
                actions.append({
                    "type": "extract_module",
                    "file": h["file"],
                    "thresholds": {"deg": h["deg"], "size": h["size"]},
                    "advice": "Extrair submódulo para reduzir acoplamento e melhorar testabilidade.",
                })
                evidence.append(f"Hotspot: {h['file']} (score={h['score']})")

        proofs = [
            "git apply --check <patch>",
            "tsc --noEmit || pytest -q  # conforme o projeto",
            "eslint . -q || ruff . -q",
            "npm run build || vite build  # se frontend",
        ]
        return {
            "mode": "ADVISORY",
            "summary": "Plano de refactor mínimo e reversível (Fase 8).",
            "actions": actions,
            "proofs": proofs,
            "evidence": evidence,
        }
