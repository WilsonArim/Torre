#!/usr/bin/env python3
"""
Teste rápido para validar o endpoint de memória episódica
"""

import requests
import json
import time

def test_memory_endpoint():
    """Testa o endpoint /memory/metrics"""
    
    print("🧠 TESTE ENDPOINT MEMÓRIA")
    print("=" * 40)
    
    # Aguardar servidor
    print("⏳ Aguardando servidor...")
    time.sleep(2)
    
    try:
        # Teste health
        print("📊 Testando /health...")
        health = requests.get("http://localhost:8765/health", timeout=5)
        print(f"✅ Health: {health.status_code} - {health.json()}")
        
        # Teste memory metrics
        print("📊 Testando /memory/metrics...")
        memory = requests.get("http://localhost:8765/memory/metrics", timeout=5)
        print(f"✅ Memory: {memory.status_code}")
        
        if memory.status_code == 200:
            data = memory.json()
            print("📈 Métricas:")
            print(f"   - Repeat error rate: {data.get('metrics', {}).get('repeat_error_rate', 0)}%")
            print(f"   - Rules promoted: {data.get('metrics', {}).get('rules_promoted', 0)}")
            print(f"   - Rules hit rate: {data.get('metrics', {}).get('rules_hit_rate', 0)}%")
            print(f"   - Avoidance saves: {data.get('metrics', {}).get('avoidance_saves', 0)}")
            print(f"   - Regras: {len(data.get('rules', []))}")
            
            if data.get('rules'):
                rule = data['rules'][0]
                print(f"   - Exemplo de regra: {rule.get('key', 'N/A')}")
            
            print("\n🎉 ENDPOINT FUNCIONANDO!")
            return True
        else:
            print(f"❌ Erro: {memory.status_code}")
            print(f"   {memory.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Servidor não está rodando em localhost:8765")
        print("   Execute: python3 -m llm.server")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    test_memory_endpoint()
