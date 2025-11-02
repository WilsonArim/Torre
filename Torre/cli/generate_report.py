#!/usr/bin/env python3
"""
torre/cli/generate_report.py - Gerador de relatório técnico de treino

Agente: Engenheiro da TORRE
Função: Gera relatório técnico completo (train_summary.md)
Regras: ART-07 (Transparência), ART-09 (Evidência)
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

# Caminhos absolutos
TORRE_ROOT = Path(__file__).resolve().parents[1]
CHECKPOINTS_DIR = TORRE_ROOT / "checkpoints"
LOGS_DIR = TORRE_ROOT / "logs"
REPORTS_DIR = TORRE_ROOT / "reports"
RELATORIOS_DIR = TORRE_ROOT.parent / "relatorios"
PLAN_PATH = TORRE_ROOT / "curriculum" / "PLAN.md"


def get_latest_checkpoints() -> List[Dict[str, Any]]:
    """Obtém lista dos checkpoints mais recentes."""
    checkpoints = []
    
    if not CHECKPOINTS_DIR.exists():
        return checkpoints
    
    for ckpt_file in sorted(CHECKPOINTS_DIR.glob("*.ckpt"), reverse=True)[:10]:
        try:
            ckpt_data = json.loads(ckpt_file.read_text(encoding="utf-8"))
            checkpoints.append({
                "file": ckpt_file.name,
                "phase": ckpt_data.get("phase", "N/A"),
                "epoch": ckpt_data.get("epoch", "N/A"),
                "timestamp": ckpt_data.get("timestamp", "N/A"),
                "metrics": ckpt_data.get("metrics", {}),
            })
        except Exception:
            pass
    
    return checkpoints


def get_training_logs_summary() -> Dict[str, Any]:
    """Obtém resumo dos logs de treino."""
    logs_summary = {
        "total_logs": 0,
        "last_training": None,
        "errors": 0,
    }
    
    if not LOGS_DIR.exists():
        return logs_summary
    
    log_files = sorted(LOGS_DIR.glob("train_*.log"), reverse=True)
    logs_summary["total_logs"] = len(log_files)
    
    if log_files:
        # Ler último log
        try:
            last_log = log_files[0].read_text(encoding="utf-8")
            lines = last_log.strip().split("\n")
            if lines:
                logs_summary["last_training"] = lines[-1]
            
            # Contar erros
            logs_summary["errors"] = sum(1 for line in lines if "ERROR" in line.upper())
        except Exception:
            pass
    
    return logs_summary


def get_status() -> Dict[str, Any]:
    """Obtém status atual da TORRE."""
    status_file = RELATORIOS_DIR / "torre_status.json"
    
    if status_file.exists():
        try:
            return json.loads(status_file.read_text(encoding="utf-8"))
        except Exception:
            pass
    
    return {}


def generate_train_summary() -> Path:
    """Gera relatório técnico completo (train_summary.md)."""
    report_path = REPORTS_DIR / "train_summary.md"
    
    # Coletar dados
    checkpoints = get_latest_checkpoints()
    logs_summary = get_training_logs_summary()
    status = get_status()
    
    # Gerar relatório
    report_lines = [
        "# Relatório Técnico de Treino — LLM-Engenheira da FÁBRICA",
        "",
        f"**Agente**: Engenheiro da TORRE",
        f"**Data/Hora**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}",
        f"**Objetivo**: Relatório técnico de performance e métricas",
        "",
        "---",
        "",
        "## Status Atual",
    ]
    
    if status:
        report_lines.extend([
            f"- **Status**: {status.get('status', 'unknown')}",
            f"- **Última Fase**: {status.get('ultima_fase', 'N/A')}",
            f"- **Última Atualização**: {status.get('ultima_atualizacao', 'N/A')}",
        ])
    else:
        report_lines.append("- Status não disponível")
    
    report_lines.extend([
        "",
        "## Checkpoints Recentes",
        "",
    ])
    
    if checkpoints:
        for ckpt in checkpoints[:5]:  # Mostrar últimos 5
            report_lines.append(f"### {ckpt['file']}")
            report_lines.append(f"- **Fase**: {ckpt['phase']}")
            report_lines.append(f"- **Epoch**: {ckpt['epoch']}")
            report_lines.append(f"- **Timestamp**: {ckpt['timestamp']}")
            
            metrics = ckpt.get("metrics", {})
            if metrics:
                report_lines.append("- **Métricas**:")
                for key, value in metrics.items():
                    if isinstance(value, bool):
                        status_icon = "✅" if value else "❌"
                        report_lines.append(f"  - {key}: {status_icon}")
                    elif isinstance(value, (int, float)):
                        report_lines.append(f"  - {key}: {value}")
            report_lines.append("")
    else:
        report_lines.append("Nenhum checkpoint encontrado")
    
    report_lines.extend([
        "",
        "## Logs de Treino",
        "",
        f"- **Total de logs**: {logs_summary['total_logs']}",
        f"- **Erros encontrados**: {logs_summary['errors']}",
    ])
    
    if logs_summary.get("last_training"):
        report_lines.append(f"- **Última entrada**: `{logs_summary['last_training'][:100]}...`")
    
    report_lines.extend([
        "",
        "## Plano de Treino",
        "",
        f"- **Arquivo**: `{PLAN_PATH.relative_to(TORRE_ROOT.parent)}`",
        f"- **Status**: {'✅ Encontrado' if PLAN_PATH.exists() else '❌ Não encontrado'}",
        "",
        "## Artefactos Citados (ART-09)",
        "",
    ])
    
    # Listar artefactos
    artefactos = [
        str(PLAN_PATH.relative_to(TORRE_ROOT.parent)),
        str(RELATORIOS_DIR.relative_to(TORRE_ROOT.parent) / "torre_status.json"),
    ]
    
    for ckpt in checkpoints[:5]:
        artefactos.append(str(CHECKPOINTS_DIR.relative_to(TORRE_ROOT.parent) / ckpt["file"]))
    
    for artefacto in artefactos:
        report_lines.append(f"- `{artefacto}`")
    
    report_lines.extend([
        "",
        "## Regras Aplicadas (ART-07)",
        "",
        "- ART-04: Verificabilidade (logs e checkpoints rastreáveis)",
        "- ART-07: Transparência (metadados em todos os outputs)",
        "- ART-09: Evidência (artefactos citados)",
        "",
        "---",
        "",
        f"**Assinado**: Engenheiro da TORRE",
        f"**Data**: {datetime.now().strftime('%Y-%m-%d')}",
        "",
        "---",
        "",
        "## Comandos Úteis",
        "",
        "```bash",
        "# Executar treino de uma fase",
        "make torre_train PHASE=0",
        "",
        "# Criar checkpoint",
        "make torre_checkpoint",
        "",
        "# Avaliar checkpoint",
        "make torre_eval CHECKPOINT=checkpoint_phase0_epoch10_*.ckpt",
        "",
        "# Ver este relatório",
        "make torre_report",
        "```",
    ])
    
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(report_lines), encoding="utf-8")
    
    print(f"✅ Relatório gerado: {report_path}")
    return report_path


if __name__ == "__main__":
    try:
        generate_train_summary()
        sys.exit(0)
    except Exception as e:
        print(f"❌ ERRO ao gerar relatório: {e}", file=sys.stderr)
        sys.exit(1)

