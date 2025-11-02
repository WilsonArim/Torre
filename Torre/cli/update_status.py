#!/usr/bin/env python3
"""
torre/cli/update_status.py - Atualizador de status da TORRE

Agente: Engenheiro da TORRE
Função: Atualiza relatorios/torre_status.json automaticamente
Regras: ART-04 (Verificabilidade)
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Caminhos absolutos
TORRE_ROOT = Path(__file__).resolve().parents[1]
CHECKPOINTS_DIR = TORRE_ROOT / "checkpoints"
LOGS_DIR = TORRE_ROOT / "logs"
RELATORIOS_DIR = TORRE_ROOT.parent / "relatorios"


def update_status() -> None:
    """Atualiza status da TORRE em relatorios/torre_status.json."""
    status_file = RELATORIOS_DIR / "torre_status.json"
    
    # Carregar status existente
    current_status = {}
    if status_file.exists():
        try:
            current_status = json.loads(status_file.read_text(encoding="utf-8"))
        except Exception:
            pass
    
    # Contar checkpoints
    checkpoint_count = 0
    if CHECKPOINTS_DIR.exists():
        checkpoint_count = len(list(CHECKPOINTS_DIR.glob("*.ckpt")))
    
    # Contar logs
    log_count = 0
    if LOGS_DIR.exists():
        log_count = len(list(LOGS_DIR.glob("*.log")))
    
    # Atualizar status
    status_data = {
        "ultima_atualizacao": datetime.now().isoformat(),
        "agente": "Engenheiro da TORRE",
        "estatisticas": {
            "checkpoints": checkpoint_count,
            "logs": log_count,
        },
        **current_status,  # Preservar dados existentes
    }
    
    status_file.parent.mkdir(parents=True, exist_ok=True)
    status_file.write_text(json.dumps(status_data, indent=2, ensure_ascii=False), encoding="utf-8")
    
    print(f"✅ Status atualizado: {status_file}")


if __name__ == "__main__":
    try:
        update_status()
        sys.exit(0)
    except Exception as e:
        print(f"❌ ERRO ao atualizar status: {e}", file=sys.stderr)
        sys.exit(1)

