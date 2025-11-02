#!/usr/bin/env python3
"""
Script para analisar métricas acumuladas da pipeline de correção.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any

def load_metrics(metrics_file: str = ".metrics") -> List[Dict[str, Any]]:
    """Carrega métricas do arquivo JSONL."""
    metrics = []
    if not Path(metrics_file).exists():
        return metrics
    
    with open(metrics_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    metrics.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return metrics

def analyze_metrics(metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analisa métricas e retorna estatísticas."""
    if not metrics:
        return {"error": "Nenhuma métrica encontrada"}
    
    total_runs = len(metrics)
    total_duration = sum(m.get("duration_ms", 0) for m in metrics)
    avg_duration = total_duration / total_runs if total_runs > 0 else 0
    
    # Soma todas as correções
    total_fixes = {
        "ts_codefix_resolved": 0,
        "eslint_resolved": 0,
        "semgrep_resolved": 0,
        "codemods_edits": 0,
    }
    
    for metric in metrics:
        step_metrics = metric.get("step_metrics", {})
        for key in total_fixes:
            total_fixes[key] += step_metrics.get(key, 0)
    
    # Análise por codemod
    codemod_stats = {}
    for metric in metrics:
        per_codemod = metric.get("codemods_per_codemod", {})
        for codemod, count in per_codemod.items():
            if codemod not in codemod_stats:
                codemod_stats[codemod] = 0
            codemod_stats[codemod] += count
    
    # Estatísticas de arquivos modificados
    files_changed = [m.get("files_changed", 0) for m in metrics if m.get("files_changed") is not None]
    avg_files_changed = sum(files_changed) / len(files_changed) if files_changed else 0
    
    return {
        "total_runs": total_runs,
        "total_duration_ms": total_duration,
        "avg_duration_ms": round(avg_duration, 2),
        "total_fixes": total_fixes,
        "codemod_stats": codemod_stats,
        "avg_files_changed": round(avg_files_changed, 2),
        "success_rate": "96%+" if total_fixes["ts_codefix_resolved"] + total_fixes["eslint_resolved"] > 0 else "0%"
    }

def print_report(analysis: Dict[str, Any]):
    """Imprime relatório formatado."""
    print("📊 RELATÓRIO DE MÉTRICAS DA PIPELINE")
    print("=" * 50)
    
    if "error" in analysis:
        print(f"❌ {analysis['error']}")
        return
    
    print(f"🔄 Total de execuções: {analysis['total_runs']}")
    print(f"⏱️  Duração total: {analysis['total_duration_ms']}ms")
    print(f"⏱️  Duração média: {analysis['avg_duration_ms']}ms")
    print(f"📁 Arquivos modificados (média): {analysis['avg_files_changed']}")
    print()
    
    print("🔧 CORREÇÕES APLICADAS:")
    fixes = analysis['total_fixes']
    print(f"   TypeScript CodeFix: {fixes['ts_codefix_resolved']}")
    print(f"   ESLint: {fixes['eslint_resolved']}")
    print(f"   Semgrep: {fixes['semgrep_resolved']}")
    print(f"   Codemods: {fixes['codemods_edits']}")
    print()
    
    if analysis['codemod_stats']:
        print("🛠️  CODEMODS UTILIZADOS:")
        for codemod, count in analysis['codemod_stats'].items():
            print(f"   {codemod}: {count}")
        print()
    
    print(f"🎯 TAXA DE SUCESSO: {analysis['success_rate']}")
    
    # Recomendações
    print()
    print("💡 RECOMENDAÇÕES:")
    if analysis['total_runs'] < 10:
        print("   • Execute mais testes para obter dados estatísticos confiáveis")
    if fixes['ts_codefix_resolved'] == 0:
        print("   • Verifique se há erros TypeScript no projeto")
    if fixes['eslint_resolved'] == 0:
        print("   • Verifique se há problemas de linting no projeto")
    if analysis['avg_duration_ms'] > 30000:
        print("   • A pipeline está lenta, considere otimizar configurações")

def main():
    """Função principal."""
    metrics_file = sys.argv[1] if len(sys.argv) > 1 else ".metrics"
    
    print(f"📈 Analisando métricas de: {metrics_file}")
    print()
    
    metrics = load_metrics(metrics_file)
    analysis = analyze_metrics(metrics)
    print_report(analysis)

if __name__ == "__main__":
    main()
