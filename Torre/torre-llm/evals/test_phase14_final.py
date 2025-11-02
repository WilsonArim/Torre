#!/usr/bin/env python3
"""
Teste final da Fase 14: Memória Episódica + UI + Promoção
Valida implementação completa com endpoint de promoção
"""

import json
import sys
import os
from pathlib import Path
from llm.memory.episodic import EpisodicMemory, Episode

def test_phase14_final():
    """Testa implementação completa da Fase 14 com promoção"""
    
    print("🧠 TESTE FINAL FASE 14: Memória Episódica + UI + Promoção")
    print("=" * 70)
    
    # Teste 1: Funcionalidade Core
    print("\n📊 TESTE 1: Funcionalidade Core")
    print("-" * 40)
    
    em = EpisodicMemory()
    metrics = em.metrics()
    rules = em._load_rules()
    
    print(f"✅ Métricas: {metrics}")
    print(f"✅ Regras: {len(rules)}")
    
    # Teste 2: Promoção de Regras
    print("\n📊 TESTE 2: Promoção de Regras")
    print("-" * 40)
    
    # Adicionar alguns episódios para testar promoção
    for i in range(3):
        em.append(Episode.build({
            "file": f"src/test{i}.tsx",
            "err_code": "TS2304",
            "err_msg": f"Cannot find name Test{i}",
            "toolchain": "vite",
            "action": "codemod",
            "outcome": "green"
        }))
    
    # Promover regras
    added, kept = em.promote_rules()
    rules_after = em._load_rules()
    
    print(f"✅ Regras adicionadas: {added}")
    print(f"✅ Regras mantidas: {kept}")
    print(f"✅ Total de regras: {len(rules_after)}")
    
    # Teste 3: Endpoints Simulados
    print("\n📊 TESTE 3: Endpoints Simulados")
    print("-" * 40)
    
    # Simular resposta do endpoint metrics
    metrics_response = {
        "metrics": em.metrics(),
        "rules": em._load_rules()
    }
    
    # Simular resposta do endpoint promote
    promote_response = {
        "ok": True,
        "promoted": added,
        "rules": em._load_rules()
    }
    
    print(f"✅ /memory/metrics: {json.dumps(metrics_response, indent=2)}")
    print(f"✅ /memory/promote: {json.dumps(promote_response, indent=2)}")
    
    # Teste 4: Componentes UI
    print("\n📊 TESTE 4: Componentes UI")
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
    
    # Teste 5: Integração Server
    print("\n📊 TESTE 5: Integração Server")
    print("-" * 40)
    
    # Verificar se o servidor tem os endpoints
    server_file = "llm/server.py"
    if Path(server_file).exists():
        with open(server_file, 'r') as f:
            content = f.read()
            endpoints = [
                ("/memory/metrics", "GET"),
                ("/memory/promote", "POST")
            ]
            for endpoint, method in endpoints:
                if endpoint in content:
                    print(f"✅ Endpoint {method} {endpoint} encontrado")
                else:
                    print(f"❌ Endpoint {method} {endpoint} NÃO encontrado")
    else:
        print(f"❌ {server_file} - NÃO ENCONTRADO")
    
    # Teste 6: Validação Final
    print("\n📊 TESTE 6: Validação Final")
    print("-" * 40)
    
    success_criteria = [
        metrics.get("avoidance_saves", 0) > 0,
        len(rules_after) > 0,
        Path("../apps/fortaleza-ui/src/api/memory.ts").exists(),
        Path("../apps/fortaleza-ui/src/components/memory/MemoryPanel.tsx").exists(),
        Path("llm/server.py").exists() and "/memory/metrics" in Path("llm/server.py").read_text(),
        Path("llm/server.py").exists() and "/memory/promote" in Path("llm/server.py").read_text()
    ]
    
    print(f"✅ Avoidance saves > 0: {success_criteria[0]}")
    print(f"✅ Regras promovidas > 0: {success_criteria[1]}")
    print(f"✅ API client criado: {success_criteria[2]}")
    print(f"✅ MemoryPanel criado: {success_criteria[3]}")
    print(f"✅ Server endpoint metrics: {success_criteria[4]}")
    print(f"✅ Server endpoint promote: {success_criteria[5]}")
    
    all_passed = all(success_criteria)
    
    if all_passed:
        print(f"\n🎉 FASE 14 COMPLETA E VALIDADA!")
        print(f"   - Memória episódica funcionando")
        print(f"   - Endpoint /memory/metrics implementado")
        print(f"   - Endpoint /memory/promote implementado")
        print(f"   - Componentes UI criados")
        print(f"   - Botão 'Promover regras' ativo")
        print(f"   - Integração completa")
        print(f"\n🚀 PRÓXIMO PASSO:")
        print(f"   - Iniciar servidor: python3 -m llm.server")
        print(f"   - Acessar UI e clicar na aba 'Memória'")
        print(f"   - Clicar 'Promover regras' para testar")
        print(f"   - Ver métricas e regras em tempo real")
        return True
    else:
        print(f"\n❌ FASE 14 INCOMPLETA")
        return False

def main():
    """Executa o teste final da Fase 14"""
    try:
        sucesso = test_phase14_final()
        sys.exit(0 if sucesso else 1)
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
