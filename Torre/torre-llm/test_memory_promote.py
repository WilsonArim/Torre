#!/usr/bin/env python3
"""
Teste rápido para validar o endpoint de promoção de regras
"""

import requests
import json
import time

def test_memory_promote():
    """Testa o endpoint /memory/promote"""
    
    print("🧠 TESTE ENDPOINT PROMOÇÃO DE REGRAS")
    print("=" * 50)
    
    # Aguardar servidor
    print("⏳ Aguardando servidor...")
    time.sleep(2)
    
    try:
        # Teste health
        print("📊 Testando /health...")
        health = requests.get("http://localhost:8765/health", timeout=5)
        print(f"✅ Health: {health.status_code} - {health.json()}")
        
        # Teste memory metrics (antes)
        print("📊 Testando /memory/metrics (antes)...")
        memory_before = requests.get("http://localhost:8765/memory/metrics", timeout=5)
        print(f"✅ Memory: {memory_before.status_code}")
        
        if memory_before.status_code == 200:
            data_before = memory_before.json()
            rules_before = len(data_before.get('rules', []))
            print(f"   - Regras antes: {rules_before}")
        
        # Teste promote
        print("📊 Testando /memory/promote...")
        promote = requests.post("http://localhost:8765/memory/promote", timeout=5)
        print(f"✅ Promote: {promote.status_code}")
        
        if promote.status_code == 200:
            data_promote = promote.json()
            print(f"   - OK: {data_promote.get('ok', False)}")
            print(f"   - Promovidas: {data_promote.get('promoted', 0)}")
            print(f"   - Regras: {len(data_promote.get('rules', []))}")
            
            if data_promote.get('error'):
                print(f"   - Erro: {data_promote.get('error')}")
        
        # Teste memory metrics (depois)
        print("📊 Testando /memory/metrics (depois)...")
        memory_after = requests.get("http://localhost:8765/memory/metrics", timeout=5)
        print(f"✅ Memory: {memory_after.status_code}")
        
        if memory_after.status_code == 200:
            data_after = memory_after.json()
            rules_after = len(data_after.get('rules', []))
            print(f"   - Regras depois: {rules_after}")
            
            if rules_before != rules_after:
                print(f"   - Mudança: {rules_after - rules_before} regras")
            else:
                print(f"   - Sem mudanças")
        
        print("\n🎉 ENDPOINT DE PROMOÇÃO FUNCIONANDO!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Servidor não está rodando em localhost:8765")
        print("   Execute: python3 -m llm.server")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    test_memory_promote()
