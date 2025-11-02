#!/usr/bin/env python3
"""
Torre Battery Consolidator - Consolida relatórios de todos os blocos
"""

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

REPO_ROOT = Path(__file__).resolve().parents[2]


def consolidate_reports(artifacts_dir: Path) -> Dict[str, Any]:
    """Consolida todos os relatórios de blocos"""
    reports_dir = artifacts_dir / "reports"
    
    blocks = [
        "baseline",
        "agents_tools",
        "engineering",
        "security",
        "rag",
        "load_chaos",
        "finalization"
    ]
    
    consolidated = {
        "battery_id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat() + "Z",
        "status": "IN_PROGRESS",
        "blocks": {},
        "summary": {
            "total_blocks": len(blocks),
            "passed_blocks": 0,
            "failed_blocks": 0,
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "total_duration_seconds": 0
        },
        "gates": {}
    }
    
    for block_name in blocks:
        report_file = reports_dir / f"{block_name}_report.json"
        
        if report_file.exists():
            with open(report_file, "r", encoding="utf-8") as f:
                block_data = json.load(f)
            
            consolidated["blocks"][block_name] = block_data
            consolidated["summary"]["total_tests"] += block_data["metrics"]["total_tests"]
            consolidated["summary"]["passed_tests"] += (
                block_data["metrics"]["passed_tests"] + block_data["metrics"]["retried_tests"]
            )
            consolidated["summary"]["failed_tests"] += block_data["metrics"]["failed_tests"]
            consolidated["summary"]["total_duration_seconds"] += block_data["duration_seconds"]
            
            if block_data["status"] == "PASS":
                consolidated["summary"]["passed_blocks"] += 1
            else:
                consolidated["summary"]["failed_blocks"] += 1
            
            consolidated["gates"][block_data["gate"]] = block_data["status"]
        else:
            consolidated["blocks"][block_name] = {
                "status": "NOT_RUN",
                "error": "Report file not found"
            }
            consolidated["summary"]["failed_blocks"] += 1
    
    # Determinar status geral
    if consolidated["summary"]["failed_blocks"] == 0:
        consolidated["status"] = "PASS"
    elif consolidated["summary"]["passed_blocks"] > 0:
        consolidated["status"] = "PARTIAL"
    else:
        consolidated["status"] = "FAIL"
    
    return consolidated


def generate_markdown_report(consolidated: Dict[str, Any], output_file: Path):
    """Gera relatório Markdown consolidado"""
    md = f"""# Torre Battery - Relatório Consolidado de Stress/Auditoria

**Battery ID**: {consolidated['battery_id']}  
**Timestamp**: {consolidated['timestamp']}  
**Status Geral**: {consolidated['status']}

---

## 📊 Resumo Executivo

- **Blocos Totais**: {consolidated['summary']['total_blocks']}
- **Blocos Passados**: {consolidated['summary']['passed_blocks']}
- **Blocos Falhados**: {consolidated['summary']['failed_blocks']}
- **Testes Totais**: {consolidated['summary']['total_tests']}
- **Testes Passados**: {consolidated['summary']['passed_tests']}
- **Testes Falhados**: {consolidated['summary']['failed_tests']}
- **Duração Total**: {consolidated['summary']['total_duration_seconds']:.2f}s

---

## 🔋 Blocos Executados

"""
    
    for block_name, block_data in consolidated["blocks"].items():
        if isinstance(block_data, dict) and "status" in block_data:
            status_icon = "✅" if block_data["status"] == "PASS" else "❌" if block_data["status"] == "FAIL" else "⚠️"
            md += f"""### {status_icon} {block_data.get('block_display_name', block_name)}

- **Status**: {block_data.get('status', 'UNKNOWN')}
- **Gate**: {block_data.get('gate', 'N/A')}
- **Duração**: {block_data.get('duration_seconds', 0):.2f}s
- **Taxa de Sucesso**: {block_data.get('metrics', {}).get('success_rate', 0):.2f}%
- **Testes**: {block_data.get('metrics', {}).get('passed_tests', 0)}/{block_data.get('metrics', {}).get('total_tests', 0)} passados

"""
        else:
            md += f"""### ⚠️ {block_name}

- **Status**: NOT_RUN
- **Erro**: Relatório não encontrado

"""
    
    md += f"""
---

## 🛡️ Status dos Gates

"""
    for gate, status in consolidated["gates"].items():
        status_icon = "✅" if status == "PASS" else "❌"
        md += f"- {status_icon} **{gate}**: {status}\n"
    
    md += f"""
---

## 📈 Métricas de Performance

- **Taxa de Sucesso Geral**: {(consolidated['summary']['passed_tests'] / consolidated['summary']['total_tests'] * 100) if consolidated['summary']['total_tests'] > 0 else 0:.2f}%
- **Tempo Médio por Bloco**: {(consolidated['summary']['total_duration_seconds'] / consolidated['summary']['total_blocks']) if consolidated['summary']['total_blocks'] > 0 else 0:.2f}s

---

*Gerado automaticamente pelo Engenheiro da TORRE*
"""
    
    output_file.write_text(md, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Torre Battery Consolidator")
    parser.add_argument("--artifacts-dir", default="artifacts")
    parser.add_argument("--output", default="artifacts/torre_battery_report.md")
    parser.add_argument("--json-output", default="artifacts/torre_battery_report.json")
    
    args = parser.parse_args()
    
    artifacts_dir = Path(args.artifacts_dir)
    output_md = Path(args.output)
    output_json = Path(args.json_output)
    
    print("Consolidando relatórios da bateria de testes...")
    
    consolidated = consolidate_reports(artifacts_dir)
    
    # Salvar JSON
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(consolidated, f, indent=2, ensure_ascii=False)
    
    # Gerar Markdown
    generate_markdown_report(consolidated, output_md)
    
    print(f"✅ Relatório consolidado gerado:")
    print(f"   - {output_md}")
    print(f"   - {output_json}")
    print(f"\nStatus geral: {consolidated['status']}")
    print(f"Blocos passados: {consolidated['summary']['passed_blocks']}/{consolidated['summary']['total_blocks']}")


if __name__ == "__main__":
    import uuid
    main()

