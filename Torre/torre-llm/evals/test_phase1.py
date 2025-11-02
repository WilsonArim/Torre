#!/usr/bin/env python3
"""
Script de teste para Fase 1 - Fundação
Testa Omni-Contexto, Strategos e Dashboard de Métricas
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from evals.omni_context import OmniContext
from evals.strategos import Strategos
from evals.metrics_dashboard import MetricsDashboard

def test_omni_context():
    """Testa Omni-Contexto"""
    print("🧪 Testando Omni-Contexto...")
    
    oc = OmniContext('.')
    result = oc.analyze_project()
    report = oc.generate_report(result)
    
    print(report)
    
    # Verifica gates
    metrics = result["metrics"]
    coverage_ok = metrics['file_coverage'] >= 90
    imports_ok = metrics['import_resolution_rate'] >= 95
    
    print(f"✅ Cobertura ≥90%: {'✅' if coverage_ok else '❌'}")
    print(f"✅ Imports ≥95%: {'✅' if imports_ok else '❌'}")
    
    return coverage_ok and imports_ok

def test_strategos():
    """Testa Strategos"""
    print("\n🧪 Testando Strategos...")
    
    s = Strategos()
    
    # Teste 1: Erros de build e types
    logs1 = {
        'lint': 'TS2304: Cannot find name SettingsPage',
        'build': 'ModuleNotFoundError: No module named evals'
    }
    plan1 = s.generate_attack_plan(logs1)
    report1 = s.generate_report(plan1)
    
    print("Teste 1 - Build + Types:")
    print(report1)
    
    # Teste 2: Sem erros
    logs2 = {'info': 'All tests passing'}
    plan2 = s.generate_attack_plan(logs2)
    report2 = s.generate_report(plan2)
    
    print("Teste 2 - Sem erros:")
    print(report2)
    
    # Verifica se a estratégia está correta
    strategy_ok = (plan1['strategy'] == 'risk_based_attack' and 
                   plan2['strategy'] == 'no_errors' and
                   len(plan1['priority_order']) > 0)
    
    print(f"✅ Estratégia correta: {'✅' if strategy_ok else '❌'}")
    
    return strategy_ok

def test_metrics_dashboard():
    """Testa Dashboard de Métricas"""
    print("\n🧪 Testando Dashboard de Métricas...")
    
    md = MetricsDashboard()
    
    # Simula alguns episódios
    md.record_episode(True, 100, 5, 50)
    md.record_episode(False, 200, 10, 75)
    md.record_episode(True, 150, 3, 60)
    md.record_episode(True, 80, 2, 40)
    
    report = md.generate_dashboard_report()
    print(report)
    
    # Verifica se as métricas estão corretas
    metrics = md.get_current_metrics()
    success_rate_ok = metrics['success_rate'] == 75.0  # 3/4 episódios
    episodes_ok = metrics['episodes_count'] == 4
    
    print(f"✅ Success Rate correto: {'✅' if success_rate_ok else '❌'}")
    print(f"✅ Episódios contados: {'✅' if episodes_ok else '❌'}")
    
    return success_rate_ok and episodes_ok

def main():
    """Executa todos os testes"""
    print("🚀 Iniciando testes da Fase 1 - Fundação\n")
    
    results = []
    
    # Testa cada componente
    results.append(("Omni-Contexto", test_omni_context()))
    results.append(("Strategos", test_strategos()))
    results.append(("Dashboard de Métricas", test_metrics_dashboard()))
    
    # Resumo
    print("\n📊 Resumo dos Testes:")
    for component, passed in results:
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"- {component}: {status}")
    
    all_passed = all(passed for _, passed in results)
    
    if all_passed:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Fase 1 - Fundação está pronta!")
    else:
        print("\n⚠️ ALGUNS TESTES FALHARAM!")
        print("❌ Fase 1 - Fundação precisa de correções!")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
