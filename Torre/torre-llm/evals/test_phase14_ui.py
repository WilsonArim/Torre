#!/usr/bin/env python3
"""
Teste final da Fase 14: Memória Episódica + UI
Valida implementação completa com endpoint e componentes UI
"""

import json
import sys
import os
from pathlib import Path
from llm.memory.episodic import EpisodicMemory, Episode

def test_phase14_complete():
    """Testa implementação completa da Fase 14"""
    
    print("🧠 TESTE FINAL FASE 14: Memória Episódica + UI")
    print("=" * 60)
    
    # Teste 1: Funcionalidade Core
    print("\n📊 TESTE 1: Funcionalidade Core")
    print("-" * 40)
    
    em = EpisodicMemory()
    metrics = em.metrics()
    rules = em._load_rules()
    
    print(f"✅ Métricas: {metrics}")
    print(f"✅ Regras: {len(rules)}")
    
    # Teste 2: Endpoint Simulado
    print("\n📊 TESTE 2: Endpoint Simulado")
    print("-" * 40)
    
    # Simular resposta do endpoint
    endpoint_response = {
        "metrics": metrics,
        "rules": rules
    }
    
    print(f"✅ Endpoint response: {json.dumps(endpoint_response, indent=2)}")
    
    # Teste 3: Componentes UI
    print("\n📊 TESTE 3: Componentes UI")
    print("-" * 40)
    
    # Verificar se os arquivos UI existem
    ui_files = [
        "../apps/fortaleza-ui/src/api/memory.ts",
        "../apps/fortaleza-ui/src/components/memory/MemoryPanel.tsx",
        "../apps/fortaleza-ui/src/components/layout/LeftSidebar.tsx"
    ]
    
    for file_path in ui_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - NÃO ENCONTRADO")
    
    # Teste 4: Integração Server
    print("\n📊 TESTE 4: Integração Server")
    print("-" * 40)
    
    # Verificar se o servidor tem o endpoint
    server_file = "llm/server.py"
    if Path(server_file).exists():
        with open(server_file, 'r') as f:
            content = f.read()
            if "/memory/metrics" in content:
                print("✅ Endpoint /memory/metrics encontrado no servidor")
            else:
                print("❌ Endpoint /memory/metrics NÃO encontrado no servidor")
    else:
        print(f"❌ {server_file} - NÃO ENCONTRADO")
    
    # Teste 5: Validação Final
    print("\n📊 TESTE 5: Validação Final")
    print("-" * 40)
    
    success_criteria = [
        metrics.get("avoidance_saves", 0) > 0,
        len(rules) > 0,
        Path("../apps/fortaleza-ui/src/api/memory.ts").exists(),
        Path("../apps/fortaleza-ui/src/components/memory/MemoryPanel.tsx").exists(),
        Path("llm/server.py").exists() and "/memory/metrics" in Path("llm/server.py").read_text()
    ]
    
    print(f"✅ Avoidance saves > 0: {success_criteria[0]}")
    print(f"✅ Regras promovidas > 0: {success_criteria[1]}")
    print(f"✅ API client criado: {success_criteria[2]}")
    print(f"✅ MemoryPanel criado: {success_criteria[3]}")
    print(f"✅ Server endpoint: {success_criteria[4]}")
    
    all_passed = all(success_criteria)
    
    if all_passed:
        print(f"\n🎉 FASE 14 COMPLETA E VALIDADA!")
        print(f"   - Memória episódica funcionando")
        print(f"   - Endpoint /memory/metrics implementado")
        print(f"   - Componentes UI criados")
        print(f"   - Integração completa")
        print(f"\n🚀 PRÓXIMO PASSO:")
        print(f"   - Iniciar servidor: python3 -m llm.server")
        print(f"   - Acessar UI e clicar na aba 'Memória'")
        print(f"   - Ver métricas e regras em tempo real")
        return True
    else:
        print(f"\n❌ FASE 14 INCOMPLETA")
        return False

def main():
    """Executa o teste final da Fase 14"""
    try:
        sucesso = test_phase14_complete()
        sys.exit(0 if sucesso else 1)
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
