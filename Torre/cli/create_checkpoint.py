#!/usr/bin/env python3
"""
torre/cli/create_checkpoint.py - Criador de checkpoint manual

Agente: Engenheiro da TORRE
Função: Cria checkpoint do estado atual manualmente
Regras: ART-04 (Verificabilidade), ART-07 (Transparência)
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Caminhos absolutos
TORRE_ROOT = Path(__file__).resolve().parents[1]
CHECKPOINTS_DIR = TORRE_ROOT / "checkpoints"
RELATORIOS_DIR = TORRE_ROOT.parent / "relatorios"


def create_manual_checkpoint() -> Path:
    """Cria checkpoint manual do estado atual."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    checkpoint_name = f"checkpoint_manual_{timestamp}.ckpt"
    checkpoint_path = CHECKPOINTS_DIR / checkpoint_name
    
    checkpoint_data = {
        "type": "manual",
        "timestamp": datetime.now().isoformat(),
        "agent": "Engenheiro da TORRE",
        "conformidade": {
            "ART-04": True,  # Verificabilidade
            "ART-07": True,  # Transparência
            "ART-09": True,  # Evidência
        },
        "note": "Checkpoint criado manualmente via make torre_checkpoint",
    }
    
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    checkpoint_path.write_text(json.dumps(checkpoint_data, indent=2, ensure_ascii=False), encoding="utf-8")
    
    print(f"✅ Checkpoint criado: {checkpoint_path}")
    return checkpoint_path


if __name__ == "__main__":
    try:
        create_manual_checkpoint()
        sys.exit(0)
    except Exception as e:
        print(f"❌ ERRO ao criar checkpoint: {e}", file=sys.stderr)
        sys.exit(1)

