#!/usr/bin/env python3
"""
Torre Battery Reporter - Atualiza engineer.out.json com resultados da bateria
"""

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

REPO_ROOT = Path(__file__).resolve().parents[2]
ENGINEER_OUT = REPO_ROOT / "relatorios" / "para_estado_maior" / "engineer.out.json"


def update_engineer_out(battery_report_path: Path, engineer_out_path: Path):
    """Atualiza engineer.out.json com relatório da bateria"""
    # Ler relatório da bateria
    with open(battery_report_path, "r", encoding="utf-8") as f:
        battery_data = json.load(f)
    
    # Ler engineer.out.json existente
    existing_reports = []
    if engineer_out_path.exists():
        with open(engineer_out_path, "r", encoding="utf-8") as f:
            existing_reports = json.load(f)
    
    # Criar relatório no formato engineer.out.json
    battery_report = {
        "order_id": f"battery-stress-{datetime.now().strftime('%Y-%m-%dT%H-%M-%S')}",
        "report_id": battery_data["battery_id"],
        "version": 3,
        "from_role": "ENGENHEIRO",
        "to_role": "ESTADO-MAIOR",
        "project": "TORRE",
        "module": "BATTERY_STRESS",
        "gate": "BATTERY_ALL",
        "started_at": battery_data["timestamp"],
        "finished_at": datetime.now().isoformat() + "Z",
        "status": "PASS" if battery_data["status"] == "PASS" else "WARN" if battery_data["status"] == "PARTIAL" else "BLOCKED",
        "findings": [
            {
                "type": "info" if battery_data["status"] == "PASS" else "warning",
                "msg": f"Bateria de testes concluída: {battery_data['summary']['passed_blocks']}/{battery_data['summary']['total_blocks']} blocos passados"
            },
            {
                "type": "info",
                "msg": f"Total de testes: {battery_data['summary']['total_tests']}, Passados: {battery_data['summary']['passed_tests']}, Falhados: {battery_data['summary']['failed_tests']}"
            }
        ],
        "metrics": {
            "battery_id": battery_data["battery_id"],
            "total_blocks": battery_data["summary"]["total_blocks"],
            "passed_blocks": battery_data["summary"]["passed_blocks"],
            "failed_blocks": battery_data["summary"]["failed_blocks"],
            "total_tests": battery_data["summary"]["total_tests"],
            "passed_tests": battery_data["summary"]["passed_tests"],
            "failed_tests": battery_data["summary"]["failed_tests"],
            "total_duration_seconds": battery_data["summary"]["total_duration_seconds"],
            "success_rate": round(
                (battery_data["summary"]["passed_tests"] / battery_data["summary"]["total_tests"] * 100)
                if battery_data["summary"]["total_tests"] > 0 else 0,
                2
            )
        },
        "risks": [],
        "artifacts": [
            {"path": "artifacts/torre_battery_report.md", "type": "markdown"},
            {"path": "artifacts/torre_battery_report.json", "type": "json"}
        ],
        "references": [
            ".github/workflows/torre-battery.yml",
            "artifacts/torre_battery_report.json"
        ],
        "dataset_info": {}
    }
    
    # Adicionar relatório
    existing_reports.append(battery_report)
    
    # Salvar
    with open(engineer_out_path, "w", encoding="utf-8") as f:
        json.dump(existing_reports, f, indent=2, ensure_ascii=False)
    
    print(f"✅ engineer.out.json atualizado com relatório da bateria")
    print(f"   Status: {battery_report['status']}")
    print(f"   Blocos: {battery_data['summary']['passed_blocks']}/{battery_data['summary']['total_blocks']}")


def main():
    parser = argparse.ArgumentParser(description="Torre Battery Reporter")
    parser.add_argument("--battery-report", required=True)
    parser.add_argument("--output", default="relatorios/para_estado_maior/engineer.out.json")
    
    args = parser.parse_args()
    
    battery_report_path = Path(args.battery_report)
    engineer_out_path = Path(args.output)
    
    engineer_out_path.parent.mkdir(parents=True, exist_ok=True)
    
    update_engineer_out(battery_report_path, engineer_out_path)


if __name__ == "__main__":
    main()

