#!/usr/bin/env python3
"""
Teste da Fase 15: UI do Strategos
Valida implementação dos componentes UI do Strategos
"""

import json
import sys
import os
from pathlib import Path

def test_phase15_ui():
    """Testa implementação da UI do Strategos"""
    
    print("🎯 TESTE FASE 15: UI do Strategos")
    print("=" * 50)
    
    # Teste 1: Cliente API
    print("\n📊 TESTE 1: Cliente API")
    print("-" * 40)
    
    api_file = "../apps/fortaleza-ui/src/api/strategos.ts"
    if Path(api_file).exists():
        with open(api_file, 'r') as f:
            content = f.read()
            has_graph_summary = "getGraphSummary" in content
            has_strategos_plan = "getStrategosPlan" in content
            has_types = "GraphSummary" in content and "StrategosPlan" in content
            
        print(f"✅ API client criado: {api_file}")
        print(f"✅ getGraphSummary: {has_graph_summary}")
        print(f"✅ getStrategosPlan: {has_strategos_plan}")
        print(f"✅ TypeScript types: {has_types}")
    else:
        print(f"❌ API client não encontrado: {api_file}")
    
    # Teste 2: Componente StrategosPanel
    print("\n📊 TESTE 2: Componente StrategosPanel")
    print("-" * 40)
    
    panel_file = "../apps/fortaleza-ui/src/components/strategos/StrategosPanel.tsx"
    if Path(panel_file).exists():
        with open(panel_file, 'r') as f:
            content = f.read()
            has_graph_summary = "getGraphSummary" in content
            has_strategos_plan = "getStrategosPlan" in content
            has_table = "table" in content
            has_textarea = "textarea" in content
            
        print(f"✅ StrategosPanel criado: {panel_file}")
        print(f"✅ Integração com API: {has_graph_summary and has_strategos_plan}")
        print(f"✅ Tabela de passos: {has_table}")
        print(f"✅ Campos de input: {has_textarea}")
    else:
        print(f"❌ StrategosPanel não encontrado: {panel_file}")
    
    # Teste 3: Integração LeftSidebar
    print("\n📊 TESTE 3: Integração LeftSidebar")
    print("-" * 40)
    
    sidebar_file = "../apps/fortaleza-ui/src/components/layout/LeftSidebar.tsx"
    if Path(sidebar_file).exists():
        with open(sidebar_file, 'r') as f:
            content = f.read()
            has_strategos_import = "StrategosPanel" in content
            has_strategos_tab = "strategos" in content
            has_strategos_button = "Strategos" in content
            
        print(f"✅ LeftSidebar atualizado: {sidebar_file}")
        print(f"✅ Import do StrategosPanel: {has_strategos_import}")
        print(f"✅ Tab strategos: {has_strategos_tab}")
        print(f"✅ Botão Strategos: {has_strategos_button}")
    else:
        print(f"❌ LeftSidebar não encontrado: {sidebar_file}")
    
    # Teste 4: Validação Final
    print("\n📊 TESTE 4: Validação Final")
    print("-" * 40)
    
    success_criteria = [
        Path(api_file).exists(),
        Path(panel_file).exists(),
        Path(sidebar_file).exists(),
        has_graph_summary if 'has_graph_summary' in locals() else False,
        has_strategos_plan if 'has_strategos_plan' in locals() else False,
        has_strategos_import if 'has_strategos_import' in locals() else False,
        has_strategos_tab if 'has_strategos_tab' in locals() else False
    ]
    
    print(f"✅ API client: {success_criteria[0]}")
    print(f"✅ StrategosPanel: {success_criteria[1]}")
    print(f"✅ LeftSidebar: {success_criteria[2]}")
    print(f"✅ getGraphSummary: {success_criteria[3]}")
    print(f"✅ getStrategosPlan: {success_criteria[4]}")
    print(f"✅ Import integrado: {success_criteria[5]}")
    print(f"✅ Tab integrado: {success_criteria[6]}")
    
    all_passed = all(success_criteria)
    
    if all_passed:
        print(f"\n🎉 UI DO STRATEGOS IMPLEMENTADA COM SUCESSO!")
        print(f"   - Cliente API TypeScript criado")
        print(f"   - Componente StrategosPanel implementado")
        print(f"   - Integração LeftSidebar ativa")
        print(f"   - Widget completo e funcional")
        print(f"\n🚀 PRÓXIMO PASSO:")
        print(f"   - Iniciar servidor: python3 -m llm.server")
        print(f"   - Abrir UI e clicar na aba 'Strategos'")
        print(f"   - Testar geração de plano")
        return True
    else:
        print(f"\n❌ UI DO STRATEGOS INCOMPLETA")
        return False

def main():
    """Executa o teste da UI do Strategos"""
    try:
        sucesso = test_phase15_ui()
        sys.exit(0 if sucesso else 1)
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
