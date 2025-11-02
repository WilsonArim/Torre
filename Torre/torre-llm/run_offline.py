"""
Runner OFFLINE para a LLM-Engenheira.
Simula validate/dry_run/apply e grava os diffs em .fortaleza/outbox/.
Não altera o comportamento do orquestrador normal (com API).
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
from datetime import datetime

# Importa o orquestrador depois de definirmos helpers locais.
try:
    from . import orchestrator as orch
except ImportError:
    # Fallback para quando executado diretamente
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    import orchestrator as orch

OUTBOX = Path(".fortaleza/outbox")
OUTBOX.mkdir(parents=True, exist_ok=True)

_last_payload: str | None = None

def _ts() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")

def offline_ingest_report(ws: str, mode: str, payload: str, content_type: str = "text/plain") -> bool:
    """
    Simula o endpoint de ingest:
    * Grava o payload (diff) em .fortaleza/outbox/patch-<mode>-<timestamp>.diff
    * Retorna True para que o orquestrador continue o fluxo (validate/dry_run/apply)
    """
    global _last_payload
    _last_payload = payload
    fname = OUTBOX / f"patch-{mode}-{_ts()}.diff"
    # Garante texto (o orquestrador envia text/plain)
    data = payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False)
    fname.write_text(data, encoding="utf-8")
    return True

def offline_get_pipeline_state(ws: str):
    return {"workspace": ws, "mode": "offline", "state": "unknown"}

def offline_write_pipeline_state(state):
    p = Path(".fortaleza")
    p.mkdir(exist_ok=True)
    (p / "pipeline_state.json").write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

def main() -> None:
    # Injeção (monkeypatch) das funções usadas pelo orquestrador
    orch.ingest_report = offline_ingest_report  # type: ignore[attr-defined]
    orch.get_pipeline_state = offline_get_pipeline_state  # type: ignore[attr-defined]
    orch.write_pipeline_state = offline_write_pipeline_state  # type: ignore[attr-defined]
    
    try:
        orch.main()
    except Exception as e:
        # Produz JSON de erro para consumo pelo pipeline
        print(json.dumps({"offline": True, "error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main()
