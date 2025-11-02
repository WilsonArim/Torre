#!/usr/bin/env python3
"""
Script de teste para Fase 2 - Inteligência Estratégica
Testa Strategos v2, Learning System e Senior Engineer
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from evals.strategos_v2 import StrategosV2
from evals.learning_system import LearningSystem
from evals.senior_engineer import SeniorEngineer

def test_strategos_v2():
    """Testa Strategos v2"""
    print("🧪 Testando Strategos v2...")
    
    s2 = StrategosV2()
    
    # Simula estrutura de projeto
    tree = {
        "src/core/main.ts": "export function main() { return 'hello'; }",
        "src/components/Button.tsx": "export function Button() { return <button>Click</button>; }",
        "src/utils/helpers.ts": "export function helper() { return true; }"
    }
    
    # Analisa estrutura
    modules = s2.analyze_project_structure(tree)
    
    # Testa plano de ataque
    logs = {
        'lint': 'TS2304: Cannot find name SettingsPage',
        'build': 'ModuleNotFoundError: No module named evals'
    }
    
    attack_plan = s2.generate_advanced_attack_plan(logs, modules)
    report = s2.generate_report(attack_plan)
    
    print(report)
    
    # Verifica se a estratégia está correta
    strategy_ok = (attack_plan['strategy'] == 'advanced_impact_risk_cost' and 
                   len(attack_plan['priority_order']) > 0 and
                   'module_analysis' in attack_plan)
    
    print(f"✅ Estratégia avançada correta: {'✅' if strategy_ok else '❌'}")
    
    return strategy_ok

def test_learning_system():
    """Testa Learning System"""
    print("\n🧪 Testando Learning System...")
    
    ls = LearningSystem()
    
    # Simula alguns episódios
    ls.record_episode(
        error_type="types",
        error_content="TS2304: Cannot find name SettingsPage",
        solution_applied="import { SettingsPage } from './SettingsPage';",
        success=True,
        ttg_ms=100,
        diff_size=5,
        violations=[],
        module_affected="src/components/Button.tsx"
    )
    
    ls.record_episode(
        error_type="build",
        error_content="ModuleNotFoundError: No module named evals",
        solution_applied="npm install evals",
        success=True,
        ttg_ms=200,
        diff_size=1,
        violations=[],
        module_affected="package.json"
    )
    
    # Testa sugestão de solução
    suggestion = ls.get_suggested_solution("TS2304: Cannot find name UserData", "types")
    
    # Gera relatório
    report = ls.generate_learning_report()
    print(report)
    
    # Verifica se o sistema está funcionando
    stats = ls.get_learning_stats()
    learning_ok = (stats['total_episodes'] == 2 and 
                   stats['total_lessons'] > 0 and
                   stats['success_rate'] == 100.0)
    
    print(f"✅ Sistema de aprendizagem correto: {'✅' if learning_ok else '❌'}")
    
    return learning_ok

def test_senior_engineer():
    """Testa Senior Engineer"""
    print("\n🧪 Testando Senior Engineer...")
    
    se = SeniorEngineer()
    
    # Testa análise de qualidade
    code_content = """
function processData(data) {
    if (data && data.items && data.items.length > 0) {
        const result = data.items.map(item => {
            if (item.value > 10) {
                return item.value * 2;
            } else {
                return item.value;
            }
        });
        return result;
    }
    return [];
}
"""
    
    quality = se.analyze_code_quality(code_content)
    report = se.generate_quality_report("test.ts", quality)
    
    print(report)
    
    # Verifica se a análise está correta
    quality_ok = (0.0 <= quality.maintainability <= 1.0 and
                  0.0 <= quality.readability <= 1.0 and
                  0.0 <= quality.complexity <= 1.0 and
                  0.0 <= quality.overall_score <= 1.0)
    
    print(f"✅ Análise de qualidade correta: {'✅' if quality_ok else '❌'}")
    
    return quality_ok

def main():
    """Executa todos os testes"""
    print("🚀 Iniciando testes da Fase 2 - Inteligência Estratégica\n")
    
    results = []
    
    # Testa cada componente
    results.append(("Strategos v2", test_strategos_v2()))
    results.append(("Learning System", test_learning_system()))
    results.append(("Senior Engineer", test_senior_engineer()))
    
    # Resumo
    print("\n📊 Resumo dos Testes:")
    for component, passed in results:
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"- {component}: {status}")
    
    all_passed = all(passed for _, passed in results)
    
    if all_passed:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Fase 2 - Inteligência Estratégica está pronta!")
    else:
        print("\n⚠️ ALGUNS TESTES FALHARAM!")
        print("❌ Fase 2 - Inteligência Estratégica precisa de correções!")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
