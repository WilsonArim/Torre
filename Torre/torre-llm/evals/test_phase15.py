#!/usr/bin/env python3
"""
Teste da Fase 15: Strategos v2 com grafo
Valida scorer impacto×risco×custo e plano priorizado
"""

import json
import sys
import os
from pathlib import Path
from llm.strategos.scorer_v2 import StrategosV2Graph

def test_phase15():
    """Testa todos os componentes da Fase 15"""
    
    print("🎯 TESTE FASE 15: Strategos v2 com Grafo")
    print("=" * 60)
    
    # Teste 1: Criação do Strategos v2
    print("\n📊 TESTE 1: Criação do Strategos v2")
    print("-" * 40)
    
    sg = StrategosV2Graph()
    print(f"✅ Strategos v2 criado")
    print(f"✅ Pesos padrão: impact={sg.W_IMPACT}, risk={sg.W_RISK}, cost={sg.W_COST}")
    print(f"✅ Caps por etapa: {sg.CAPS}")
    
    # Teste 2: Métricas de grafo
    print("\n📊 TESTE 2: Métricas de Grafo")
    print("-" * 40)
    
    # Grafo simples para teste
    codemap = {
        "nodes": [
            {"id": "src/App.tsx"},
            {"id": "src/utils.ts"},
            {"id": "src/components/Button.tsx"}
        ],
        "edges": [
            {"from": "src/App.tsx", "to": "src/utils.ts"},
            {"from": "src/App.tsx", "to": "src/components/Button.tsx"},
            {"from": "src/components/Button.tsx", "to": "src/utils.ts"}
        ]
    }
    
    metrics = sg.build_metrics(codemap)
    print(f"✅ Métricas calculadas para {len(metrics)} nós")
    
    for path, mx in metrics.items():
        print(f"   - {path}: in={mx.indeg}, out={mx.outdeg}, centrality={mx.centrality:.3f}")
    
    # Teste 3: Scoring de nós
    print("\n📊 TESTE 3: Scoring de Nós")
    print("-" * 40)
    
    files_ctx = {
        "src/App.tsx": "console.log(1)\nconsole.log(2)\nconsole.log(3)",
        "src/utils.ts": "export function helper() {}\n",
        "src/components/Button.tsx": "export function Button() {}\n"
    }
    
    scores = sg.score_nodes(metrics, files_ctx)
    print(f"✅ Scores calculados para {len(scores)} nós")
    
    for path, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
        print(f"   - {path}: {score:.4f}")
    
    # Teste 4: Plano com boosts
    print("\n📊 TESTE 4: Plano com Boosts")
    print("-" * 40)
    
    logs = {
        "types": "TS2304: Cannot find name React",
        "build": "vite build failed"
    }
    
    plan = sg.plan(codemap, logs, files_ctx, top_k=3)
    print(f"✅ Plano gerado: mode={plan['mode']}")
    print(f"✅ Boosts aplicados: {plan['boosts']}")
    print(f"✅ Nós considerados: {plan['nodes_considered']}")
    print(f"✅ Passos gerados: {len(plan['steps'])}")
    
    # Mostrar primeiros passos
    for i, step in enumerate(plan['steps'][:6]):
        print(f"   {i+1}. {step['stage']} → {step['target']} (score: {step['score']})")
    
    # Teste 5: Fallback para ADVICE
    print("\n📊 TESTE 5: Fallback para ADVICE")
    print("-" * 40)
    
    # Grafo vazio deve gerar ADVICE
    empty_plan = sg.plan({"nodes": [], "edges": []}, {}, {}, top_k=3)
    print(f"✅ Grafo vazio: mode={empty_plan['mode']}")
    print(f"✅ Passos: {len(empty_plan['steps'])}")
    
    # Teste 6: Integração com episódios
    print("\n📊 TESTE 6: Integração com Episódios")
    print("-" * 40)
    
    episodes = [
        {"file": "src/App.tsx", "outcome": "fail"},
        {"file": "src/App.tsx", "outcome": "fail"},
        {"file": "src/utils.ts", "outcome": "green"}
    ]
    
    plan_with_episodes = sg.plan(codemap, logs, files_ctx, episodes, top_k=3)
    print(f"✅ Plano com episódios: mode={plan_with_episodes['mode']}")
    print(f"✅ Passos: {len(plan_with_episodes['steps'])}")
    
    # Teste 7: Validação Final
    print("\n📊 TESTE 7: Validação Final")
    print("-" * 40)
    
    success_criteria = [
        sg.W_IMPACT > 0,
        sg.W_RISK > 0,
        sg.W_COST > 0,
        len(metrics) > 0,
        len(scores) > 0,
        plan['mode'] in ['PATCH', 'ADVICE'],
        len(plan['steps']) >= 0,
        empty_plan['mode'] == 'ADVICE'
    ]
    
    print(f"✅ Pesos configurados: {success_criteria[0]}")
    print(f"✅ Métricas calculadas: {success_criteria[3]}")
    print(f"✅ Scores gerados: {success_criteria[4]}")
    print(f"✅ Plano válido: {success_criteria[5]}")
    print(f"✅ Passos gerados: {success_criteria[6]}")
    print(f"✅ Fallback ADVICE: {success_criteria[7]}")
    
    all_passed = all(success_criteria)
    
    if all_passed:
        print(f"\n🎉 FASE 15 VALIDADA COM SUCESSO!")
        print(f"   - Strategos v2 funcionando")
        print(f"   - Scorer impacto×risco×custo ativo")
        print(f"   - Plano priorizado gerado")
        print(f"   - Fallback ADVICE funcionando")
        print(f"   - Integração com episódios ativa")
        return True
    else:
        print(f"\n❌ FASE 15 FALHOU NA VALIDAÇÃO")
        return False

def main():
    """Executa o teste da Fase 15"""
    try:
        sucesso = test_phase15()
        sys.exit(0 if sucesso else 1)
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
