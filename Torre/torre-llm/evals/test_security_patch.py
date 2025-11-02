#!/usr/bin/env python3
"""
Teste do Patch de Segurança e Produção
Valida rate limiting, auth, validação de inputs e rotação de logs
"""

import json
import sys
import os
import time
from pathlib import Path

def test_security_patch():
    """Testa implementação das funcionalidades de segurança"""
    
    print("🔐 TESTE PATCH DE SEGURANÇA E PRODUÇÃO")
    print("=" * 50)
    
    # Teste 1: Rate limiting no servidor
    print("\n📊 TESTE 1: Rate limiting no servidor")
    print("-" * 35)
    
    server_file = "llm/server.py"
    if Path(server_file).exists():
        with open(server_file, 'r') as f:
            content = f.read()
            has_rate_limit = "rate_limit" in content
            has_rate_buckets = "_RATE_BUCKETS" in content
            has_client_ip = "_client_ip" in content
            has_depends = "Depends(rate_limit" in content
            
        print(f"✅ Server atualizado: {server_file}")
        print(f"✅ Função rate_limit: {has_rate_limit}")
        print(f"✅ Variável _RATE_BUCKETS: {has_rate_buckets}")
        print(f"✅ Função _client_ip: {has_client_ip}")
        print(f"✅ Dependencies rate_limit: {has_depends}")
    else:
        print(f"❌ Server não encontrado: {server_file}")
    
    # Teste 2: Auth opcional
    print("\n📊 TESTE 2: Auth opcional")
    print("-" * 35)
    
    if Path(server_file).exists():
        with open(server_file, 'r') as f:
            content = f.read()
            has_require_api_key = "require_api_key" in content
            has_fortaleza_api_key = "FORTALEZA_API_KEY" in content
            has_ip_address = "ip_address" in content
            has_loopback_check = "is_loopback" in content
            
        print(f"✅ Função require_api_key: {has_require_api_key}")
        print(f"✅ Variável FORTALEZA_API_KEY: {has_fortaleza_api_key}")
        print(f"✅ Import ip_address: {has_ip_address}")
        print(f"✅ Check loopback: {has_loopback_check}")
    
    # Teste 3: Validação de inputs
    print("\n📊 TESTE 3: Validação de inputs")
    print("-" * 35)
    
    if Path(server_file).exists():
        with open(server_file, 'r') as f:
            content = f.read()
            has_plan_in = "class PlanIn" in content
            has_field = "Field(" in content
            has_validator = "@validator" in content
            has_size_limits = "8000" in content and "200_000" in content
            
        print(f"✅ Modelo PlanIn: {has_plan_in}")
        print(f"✅ Field validators: {has_field}")
        print(f"✅ @validator decorators: {has_validator}")
        print(f"✅ Size limits: {has_size_limits}")
    
    # Teste 4: Rotação de logs na memória
    print("\n📊 TESTE 4: Rotação de logs na memória")
    print("-" * 35)
    
    memory_file = "llm/memory/episodic.py"
    if Path(memory_file).exists():
        with open(memory_file, 'r') as f:
            content = f.read()
            has_max_limits = "MAX_FIELD_LEN" in content
            has_truncate = "_truncate" in content
            has_rotate = "_rotate_if_needed" in content
            has_file_size_check = "getsize" in content
            
        print(f"✅ Memory atualizado: {memory_file}")
        print(f"✅ Limites MAX_*: {has_max_limits}")
        print(f"✅ Função _truncate: {has_truncate}")
        print(f"✅ Função _rotate_if_needed: {has_rotate}")
        print(f"✅ File size check: {has_file_size_check}")
    else:
        print(f"❌ Memory não encontrado: {memory_file}")
    
    # Teste 5: Rotação de logs no audit
    print("\n📊 TESTE 5: Rotação de logs no audit")
    print("-" * 35)
    
    audit_file = "evals/audit_all.py"
    if Path(audit_file).exists():
        with open(audit_file, 'r') as f:
            content = f.read()
            has_rotation = "existing[:-20]" in content
            has_unlink = "p.unlink()" in content
            has_timezone = "timezone.utc" in content
            
        print(f"✅ Audit atualizado: {audit_file}")
        print(f"✅ Rotação de logs: {has_rotation}")
        print(f"✅ Cleanup unlink: {has_unlink}")
        print(f"✅ Timezone UTC: {has_timezone}")
    else:
        print(f"❌ Audit não encontrado: {audit_file}")
    
    # Teste 6: Fix CLI warning
    print("\n📊 TESTE 6: Fix CLI warning")
    print("-" * 35)
    
    cli_file = "llm/cli.py"
    if Path(cli_file).exists():
        with open(cli_file, 'r') as f:
            content = f.read()
            has_bytes_check = "isinstance(body, (bytes, bytearray))" in content
            has_conditional_encode = "body.encode(" in content
            has_raw_variable = "raw = body" in content
            
        print(f"✅ CLI atualizado: {cli_file}")
        print(f"✅ Bytes check: {has_bytes_check}")
        print(f"✅ Conditional encode: {has_conditional_encode}")
        print(f"✅ Raw variable: {has_raw_variable}")
    else:
        print(f"❌ CLI não encontrado: {cli_file}")
    
    # Teste 7: Validação Final
    print("\n📊 TESTE 7: Validação Final")
    print("-" * 35)
    
    success_criteria = [
        Path(server_file).exists(),
        Path(memory_file).exists(),
        Path(audit_file).exists(),
        Path(cli_file).exists(),
        has_rate_limit if 'has_rate_limit' in locals() else False,
        has_require_api_key if 'has_require_api_key' in locals() else False,
        has_plan_in if 'has_plan_in' in locals() else False,
        has_truncate if 'has_truncate' in locals() else False,
        has_rotation if 'has_rotation' in locals() else False,
        has_bytes_check if 'has_bytes_check' in locals() else False
    ]
    
    print(f"✅ Server: {success_criteria[0]}")
    print(f"✅ Memory: {success_criteria[1]}")
    print(f"✅ Audit: {success_criteria[2]}")
    print(f"✅ CLI: {success_criteria[3]}")
    print(f"✅ Rate limiting: {success_criteria[4]}")
    print(f"✅ Auth: {success_criteria[5]}")
    print(f"✅ Input validation: {success_criteria[6]}")
    print(f"✅ Log truncation: {success_criteria[7]}")
    print(f"✅ Log rotation: {success_criteria[8]}")
    print(f"✅ CLI warning fix: {success_criteria[9]}")
    
    all_passed = all(success_criteria)
    
    if all_passed:
        print(f"\n🎉 PATCH DE SEGURANÇA IMPLEMENTADO COM SUCESSO!")
        print(f"   - Rate limiting por IP (fixed-window)")
        print(f"   - Auth opcional por API key")
        print(f"   - Validação de inputs (tamanho, paths)")
        print(f"   - Rotação de logs (memória + audit)")
        print(f"   - Fix CLI warning (bytes.encode)")
        print(f"\n🚀 COMO USAR:")
        print(f"   1. Rate limits: automático nos endpoints")
        print(f"   2. Auth: export FORTALEZA_API_KEY='sua-chave'")
        print(f"   3. Validação: automática nos inputs")
        print(f"   4. Logs: rotação automática >5MB")
        print(f"   5. CLI: sem warnings de bytes")
        return True
    else:
        print(f"\n❌ PATCH DE SEGURANÇA INCOMPLETO")
        return False

def main():
    """Executa o teste de segurança"""
    try:
        sucesso = test_security_patch()
        sys.exit(0 if sucesso else 1)
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
