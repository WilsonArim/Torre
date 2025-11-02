from __future__ import annotations
import json, re
from pathlib import Path
from typing import Dict, Any, List, Tuple

TODO_RE = re.compile(r"\bTODO\b|\bFIXME\b", re.IGNORECASE)

class HotspotMiner:
    """
    Sinaliza hotspots por combinação simples:
    - tamanho do arquivo (proxy de complexidade)
    - grau no grafo (out/in)
    - densidade de TODO/FIXME
    - 'churn' aproximado por presença em episódios .fortaleza/evals
    """
    def __init__(self, repo_root: str = ".") -> None:
        self.root = Path(repo_root)

    def _file_size(self, rel: str) -> int:
        p = self.root / rel
        try:
            return p.stat().st_size
        except Exception:
            return 0

    def _todo_density(self, rel: str) -> float:
        p = self.root / rel
        try:
            t = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return 0.0
        if not t:
            return 0.0
        c = len(TODO_RE.findall(t))
        return c / max(1, t.count("\n") + 1)

    def _approx_churn(self, rel: str) -> int:
        # procura menções do ficheiro nos episódios de evals (se existirem)
        base = self.root / ".fortaleza" / "evals"
        if not base.exists():
            return 0
        hits = 0
        for j in base.glob("bakeoff-*.json"):
            try:
                data = json.loads(j.read_text(encoding="utf-8", errors="ignore"))
            except Exception:
                continue
            txt = json.dumps(data, ensure_ascii=False)
            if rel in txt:
                hits += 1
        return hits

    def rank(self, codemap: Dict[str, Any]) -> List[Dict[str, Any]]:
        indeg, outdeg = {}, {}
        for n in codemap.get("nodes", []):
            indeg[n] = 0
            outdeg[n] = 0
        for a, b in codemap.get("edges", []):
            outdeg[a] = outdeg.get(a, 0) + 1
            if b in indeg:
                indeg[b] = indeg.get(b, 0) + 1
        results: List[Dict[str, Any]] = []
        for n in codemap.get("nodes", []):
            size = self._file_size(n)
            todo = self._todo_density(n)
            churn = self._approx_churn(n)
            deg = indeg.get(n, 0) + outdeg.get(n, 0)
            # score simples normalizado por ordens de grandeza razoáveis
            score = (
                (size / 2048.0) * 0.35
                + (deg / 12.0) * 0.35
                + (todo * 10.0) * 0.20
                + (min(churn, 10) / 10.0) * 0.10
            )
            results.append({
                "file": n,
                "score": round(score, 4),
                "size": size,
                "deg": deg,
                "todo_density": round(todo, 4),
                "churn_hits": churn,
            })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
