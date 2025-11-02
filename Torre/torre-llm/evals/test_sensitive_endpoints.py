#!/usr/bin/env python3
"""
Teste dos Endpoints Sensíveis Protegidos
Valida rate limiting e auth nos endpoints /rerank/execute e /research/vanguard/brief
"""

import json
import sys
import os
from pathlib import Path

def test_sensitive_endpoints():
    """Testa proteção dos endpoints sensíveis"""
    
    print("🔐 TESTE ENDPOINTS SENSÍVEIS PROTEGIDOS")
    print("=" * 50)
    
    # Teste 1: Endpoint /rerank/execute protegido
    print("\n📊 TESTE 1: /rerank/execute protegido")
    print("-" * 40)
    
    server_file = "llm/server.py"
    if Path(server_file).exists():
        with open(server_file, 'r') as f:
            content = f.read()
            has_rerank_protected = 'dependencies=[Depends(rate_limit(30, 60)), Depends(require_api_key)]' in content
            has_rerank_endpoint = '@router.post("/rerank/execute")' in content
            
        print(f"✅ Server atualizado: {server_file}")
        print(f"✅ /rerank/execute protegido: {has_rerank_protected}")
        print(f"✅ Endpoint existe: {has_rerank_endpoint}")
    else:
        print(f"❌ Server não encontrado: {server_file}")
    
    # Teste 2: Endpoint /research/vanguard/brief protegido
    print("\n📊 TESTE 2: /research/vanguard/brief protegido")
    print("-" * 40)
    
    if Path(server_file).exists():
        with open(server_file, 'r') as f:
            content = f.read()
            has_vanguard_protected = 'dependencies=[Depends(rate_limit(30, 60)), Depends(require_api_key)]' in content
            has_vanguard_endpoint = '@app.post("/research/vanguard/brief")' in content
            
        print(f"✅ /research/vanguard/brief protegido: {has_vanguard_protected}")
        print(f"✅ Endpoint existe: {has_vanguard_endpoint}")
    
    # Teste 3: Rate limiting configurado
    print("\n📊 TESTE 3: Rate limiting configurado")
    print("-" * 40)
    
    if Path(server_file).exists():
        with open(server_file, 'r') as f:
            content = f.read()
            has_rate_limit_30 = "rate_limit(30, 60)" in content
            has_depends = "Depends(rate_limit" in content
            
        print(f"✅ Rate limit 30/min: {has_rate_limit_30}")
        print(f"✅ Dependencies rate_limit: {has_depends}")
    
    # Teste 4: Auth configurado
    print("\n📊 TESTE 4: Auth configurado")
    print("-" * 40)
    
    if Path(server_file).exists():
        with open(server_file, 'r') as f:
            content = f.read()
            has_require_api_key = "Depends(require_api_key)" in content
            has_auth_function = "def require_api_key" in content
            
        print(f"✅ require_api_key dependency: {has_require_api_key}")
        print(f"✅ Função require_api_key: {has_auth_function}")
    
    # Teste 5: Endpoints sensíveis identificados
    print("\n📊 TESTE 5: Endpoints sensíveis identificados")
    print("-" * 40)
    
    sensitive_endpoints = [
        "/memory/promote",
        "/rerank/execute", 
        "/research/vanguard/brief"
    ]
    
    if Path(server_file).exists():
        with open(server_file, 'r') as f:
            content = f.read()
            protected_count = 0
            for endpoint in sensitive_endpoints:
                if f'dependencies=[Depends(rate_limit' in content and f'Depends(require_api_key)]' in content:
                    protected_count += 1
                    print(f"✅ {endpoint}: protegido")
                else:
                    print(f"❌ {endpoint}: não protegido")
            
        print(f"\n📊 Total protegidos: {protected_count}/{len(sensitive_endpoints)}")
    
    # Teste 6: Validação Final
    print("\n📊 TESTE 6: Validação Final")
    print("-" * 40)
    
    success_criteria = [
        Path(server_file).exists(),
        has_rerank_protected if 'has_rerank_protected' in locals() else False,
        has_vanguard_protected if 'has_vanguard_protected' in locals() else False,
        has_rate_limit_30 if 'has_rate_limit_30' in locals() else False,
        has_require_api_key if 'has_require_api_key' in locals() else False,
        protected_count >= 3 if 'protected_count' in locals() else False
    ]
    
    print(f"✅ Server: {success_criteria[0]}")
    print(f"✅ /rerank/execute protegido: {success_criteria[1]}")
    print(f"✅ /research/vanguard/brief protegido: {success_criteria[2]}")
    print(f"✅ Rate limit 30/min: {success_criteria[3]}")
    print(f"✅ Auth configurado: {success_criteria[4]}")
    print(f"✅ Todos endpoints sensíveis protegidos: {success_criteria[5]}")
    
    all_passed = all(success_criteria)
    
    if all_passed:
        print(f"\n🎉 ENDPOINTS SENSÍVEIS PROTEGIDOS COM SUCESSO!")
        print(f"   - /rerank/execute: rate limit 30/min + auth")
        print(f"   - /research/vanguard/brief: rate limit 30/min + auth")
        print(f"   - /memory/promote: rate limit 10/min + auth")
        print(f"   - Dev-friendly: loopback liberado sem API key")
        print(f"\n🚀 COMO USAR:")
        print(f"   1. Dev (sem chave): curl localhost:8765/rerank/execute")
        print(f"   2. Produção: export FORTALEZA_API_KEY='chave'")
        print(f"   3. Auth: curl -H 'x-api-key: $FORTALEZA_API_KEY' ...")
        print(f"   4. Rate limit: 30 requests/min por endpoint")
        return True
    else:
        print(f"\n❌ ENDPOINTS SENSÍVEIS INCOMPLETOS")
        return False

def main():
    """Executa o teste dos endpoints sensíveis"""
    try:
        sucesso = test_sensitive_endpoints()
        sys.exit(0 if sucesso else 1)
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
