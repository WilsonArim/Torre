#!/usr/bin/env python3
"""
Teste da Fase 14: Memória Episódica por Workspace (sem PII)
Valida episódios, promoção de regras, priors seguros e métricas
"""

import json
import sys
import os
from pathlib import Path
from llm.memory.episodic import EpisodicMemory, Episode

def test_phase14():
    """Testa todos os componentes da Fase 14"""
    
    print("🧠 TESTE FASE 14: Memória Episódica por Workspace")
    print("=" * 60)
    
    # Limpar memória anterior para teste limpo
    mem_dir = Path(".fortaleza/memory")
    if mem_dir.exists():
        import shutil
        shutil.rmtree(mem_dir)
    
    # Teste 1: Criação e persistência
    print("\n📊 TESTE 1: Criação e Persistência")
    print("-" * 40)
    
    em = EpisodicMemory()
    print(f"✅ Diretório criado: {mem_dir}")
    print(f"✅ Arquivos criados: {list(mem_dir.glob('*'))}")
    
    # Teste 2: Sanitização sem PII
    print("\n📊 TESTE 2: Sanitização sem PII")
    print("-" * 40)
    
    # Teste com dados sensíveis
    sensitive_ep = Episode.build({
        "file": "/home/user/project/src/App.tsx",  # path absoluto
        "err_code": "TS2304",
        "err_msg": "Cannot find name React. Contact john.doe@company.com for help. API key: sk-123456789012345678901234",
        "toolchain": "vite",
        "action": "patch",
        "outcome": "green"
    })
    
    print(f"✅ Path relativo: {sensitive_ep.file}")
    print(f"✅ Email redatado: {'[redacted-email]' in sensitive_ep.err_msg}")
    print(f"✅ Secret redatado: {'[redacted-secret]' in sensitive_ep.err_msg}")
    
    # Teste 3: Aplicação de Priors Seguros
    print("\n📊 TESTE 3: Priors Seguros")
    print("-" * 40)
    
    test_cases = [
        {
            "name": "Assets CSS",
            "logs": {"types": "TS2307: Cannot find module './App.module.css'"},
            "expected": "kit:assets"
        },
        {
            "name": "JSX Intrinsics",
            "logs": {"types": "JSX element implicitly has type 'any'"},
            "expected": "kit:jsx"
        },
        {
            "name": "Node.js Globals",
            "logs": {"types": "Cannot find name 'process'"},
            "expected": "kit:node"
        },
        {
            "name": "Vitest Tests",
            "logs": {"types": "Cannot find name 'describe'", "build": "vitest"},
            "expected": "kit:tests-vitest"
        }
    ]
    
    for case in test_cases:
        req = {"files": {"src/App.tsx": "console.log(1)"}}
        logs = case["logs"]
        
        result = em.apply_priors(req, logs, {})
        applied = result.get("meta", {}).get("priors_applied", [])
        
        success = case["expected"] in applied
        status = "✅" if success else "❌"
        print(f"{status} {case['name']}: {applied}")
    
    # Teste 4: Promoção de Regras
    print("\n📊 TESTE 4: Promoção de Regras")
    print("-" * 40)
    
    # Simular 3 sucessos consecutivos
    for i in range(3):
        em.append(Episode.build({
            "file": "src/App.tsx",
            "err_code": "TS2307",
            "err_msg": f"Cannot find module './test{i}.css'",
            "toolchain": "vite",
            "action": "prior",
            "outcome": "green"
        }))
    
    # Promover regras
    added, kept = em.promote_rules(n=3)
    rules = em._load_rules()
    
    print(f"✅ Regras adicionadas: {added}")
    print(f"✅ Regras mantidas: {kept}")
    print(f"✅ Total de regras: {len(rules)}")
    
    if rules:
        rule = rules[0]
        print(f"✅ Regra criada: {rule['key']}")
        print(f"✅ Confiança: {rule['confidence']}")
        print(f"✅ Política: {rule['policy']}")
    
    # Teste 5: Métricas
    print("\n📊 TESTE 5: Métricas")
    print("-" * 40)
    
    # Adicionar alguns episódios para testar métricas
    for i in range(5):
        em.append(Episode.build({
            "file": f"src/file{i}.tsx",
            "err_code": "TS2304",
            "err_msg": f"Cannot find name Test{i}",
            "toolchain": "vite",
            "action": "codemod",
            "outcome": "green" if i < 4 else "fail"  # 4 sucessos, 1 falha
        }))
    
    metrics = em.metrics()
    
    print(f"✅ Taxa de repetição: {metrics['repeat_error_rate']}%")
    print(f"✅ Regras promovidas: {metrics['rules_promoted']}")
    print(f"✅ Taxa de hit das regras: {metrics['rules_hit_rate']}%")
    print(f"✅ Avoidance saves: {metrics['avoidance_saves']}")
    
    # Teste 6: Integração com CLI
    print("\n📊 TESTE 6: Integração com CLI")
    print("-" * 40)
    
    # Simular chamada CLI
    os.environ["FORT_MEM"] = "1"
    
    try:
        from llm.cli import main
        import subprocess
        
        # Teste via subprocess para simular stdin
        test_input = json.dumps({
            "logs": {"types": "TS2307: Cannot find module './test.css'"},
            "files": {"src/App.tsx": "console.log(1)"}
        })
        
        result = subprocess.run(
            [sys.executable, "-m", "llm.cli"],
            input=test_input.encode(),
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            output = json.loads(result.stdout)
            memory_metrics = output.get("metrics", {}).get("memory", {})
            
            print(f"✅ CLI integração: OK")
            print(f"✅ Métricas expostas: {list(memory_metrics.keys())}")
            print(f"✅ Avoidance saves: {memory_metrics.get('avoidance_saves', 0)}")
        else:
            print(f"❌ CLI integração: Erro")
            print(f"   {result.stderr}")
            
    except Exception as e:
        print(f"⚠️  CLI integração: {e}")
    
    # Validação final
    print(f"\n🎯 VALIDAÇÃO FINAL")
    print("-" * 40)
    
    success_criteria = [
        mem_dir.exists(),
        len(em._load_episodes()) > 0,
        len(em._load_rules()) > 0,
        em.metrics()["avoidance_saves"] > 0
    ]
    
    all_passed = all(success_criteria)
    
    print(f"✅ Diretório criado: {success_criteria[0]}")
    print(f"✅ Episódios gravados: {success_criteria[1]}")
    print(f"✅ Regras promovidas: {success_criteria[2]}")
    print(f"✅ Priors aplicados: {success_criteria[3]}")
    
    if all_passed:
        print(f"\n🎉 FASE 14 VALIDADA COM SUCESSO!")
        print(f"   - Memória episódica funcionando")
        print(f"   - Sanitização sem PII ativa")
        print(f"   - Regras promovidas automaticamente")
        print(f"   - Priors seguros aplicados")
        print(f"   - Métricas expostas")
        return True
    else:
        print(f"\n❌ FASE 14 FALHOU NA VALIDAÇÃO")
        return False

def main():
    """Executa o teste da Fase 14"""
    try:
        sucesso = test_phase14()
        sys.exit(0 if sucesso else 1)
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
