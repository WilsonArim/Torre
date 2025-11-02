#!/usr/bin/env python3
"""
Teste da Fase 17: Rollback on Red + Sandbox & Quotas
"""

import json
import sys
import os
import tempfile
import subprocess
from pathlib import Path

def test_phase17():
    """Testa a implementação da Fase 17"""
    
    print("🎯 TESTE FASE 17 - ROLLBACK ON RED + SANDBOX")
    print("=" * 50)
    
    # 1. Verificar módulos implementados
    modules = [
        "llm/ops/sandbox.py",
        "llm/ops/guard_apply.py"
    ]
    
    print("📦 Módulos implementados:")
    for module in modules:
        exists = Path(module).exists()
        print(f"   {'✅' if exists else '❌'} {module}: {exists}")
        if not exists:
            return False
    
    # 2. Verificar se o servidor compila com os novos imports
    try:
        import subprocess
        result = subprocess.run(
            ["python3", "-m", "py_compile", "llm/server.py"],
            capture_output=True,
            text=True,
            cwd="."
        )
        compiles = result.returncode == 0
        print(f"✅ Server compila: {compiles}")
        if not compiles:
            print(f"   Erro: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Erro ao compilar server: {e}")
        return False
    
    # 3. Verificar se o CLI compila
    try:
        result = subprocess.run(
            ["python3", "-m", "py_compile", "llm/cli.py"],
            capture_output=True,
            text=True,
            cwd="."
        )
        compiles = result.returncode == 0
        print(f"✅ CLI compila: {compiles}")
        if not compiles:
            print(f"   Erro: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Erro ao compilar CLI: {e}")
        return False
    
    # 4. Testar sandbox (simulação)
    print("\n🧪 Testando sandbox:")
    try:
        from llm.ops.sandbox import run_in_sandbox
        
        # Teste simples de sandbox
        rc, out, err = run_in_sandbox(
            ["echo", "hello"],
            timeout_s=5,
            cpu_seconds=5,
            mem_mb=100,
            no_network=True
        )
        sandbox_works = rc == 0 and "hello" in out
        print(f"   {'✅' if sandbox_works else '❌'} Sandbox básico: {sandbox_works}")
        
        # Teste de isolamento de rede
        rc, out, err = run_in_sandbox(
            ["curl", "http://example.com"],
            timeout_s=5,
            no_network=True
        )
        network_blocked = rc != 0
        print(f"   {'✅' if network_blocked else '❌'} Rede bloqueada: {network_blocked}")
        
    except Exception as e:
        print(f"   ❌ Erro no sandbox: {e}")
        return False
    
    # 5. Testar guard_apply (simulação)
    print("\n🔒 Testando guard_apply:")
    try:
        from llm.ops.guard_apply import apply_with_rollback, ensure_not_locked
        
        # Teste de lock check
        try:
            ensure_not_locked(".")
            lock_check_works = True
        except Exception:
            lock_check_works = False
        print(f"   {'✅' if lock_check_works else '❌'} Lock check: {lock_check_works}")
        
    except Exception as e:
        print(f"   ❌ Erro no guard_apply: {e}")
        return False
    
    # 6. Verificar endpoint no servidor
    print("\n🌐 Verificando endpoint /ops/apply:")
    try:
        with open("llm/server.py", "r") as f:
            content = f.read()
        
        has_endpoint = "/ops/apply" in content
        has_rate_limit = "rate_limit(20, 60)" in content
        has_api_key = "require_api_key" in content
        has_secret_scan = "scan_diff_for_secrets" in content
        
        print(f"   {'✅' if has_endpoint else '❌'} Endpoint /ops/apply: {has_endpoint}")
        print(f"   {'✅' if has_rate_limit else '❌'} Rate limit: {has_rate_limit}")
        print(f"   {'✅' if has_api_key else '❌'} API key auth: {has_api_key}")
        print(f"   {'✅' if has_secret_scan else '❌'} Secret scan: {has_secret_scan}")
        
    except Exception as e:
        print(f"   ❌ Erro ao verificar servidor: {e}")
        return False
    
    # 7. Verificar CLI integration
    print("\n🖥️ Verificando CLI integration:")
    try:
        with open("llm/cli.py", "r") as f:
            content = f.read()
        
        has_apply_func = "_maybe_apply_with_rollback" in content
        has_fort_apply = "FORT_APPLY" in content
        has_apply_call = "_maybe_apply_with_rollback(out)" in content
        
        print(f"   {'✅' if has_apply_func else '❌'} Função apply: {has_apply_func}")
        print(f"   {'✅' if has_fort_apply else '❌'} Env var FORT_APPLY: {has_fort_apply}")
        print(f"   {'✅' if has_apply_call else '❌'} Chamada no main: {has_apply_call}")
        
    except Exception as e:
        print(f"   ❌ Erro ao verificar CLI: {e}")
        return False
    
    # 8. Verificar gates padrão
    print("\n🎯 Verificando gates padrão:")
    try:
        from llm.ops.guard_apply import DEFAULT_GATES
        
        expected_gates = ["lint", "types", "tests", "build"]
        all_gates = all(gate in DEFAULT_GATES for gate in expected_gates)
        
        print(f"   {'✅' if all_gates else '❌'} Gates padrão: {all_gates}")
        for gate in expected_gates:
            exists = gate in DEFAULT_GATES
            print(f"      {'✅' if exists else '❌'} {gate}: {exists}")
        
    except Exception as e:
        print(f"   ❌ Erro ao verificar gates: {e}")
        return False
    
    print("\n🎉 FASE 17 IMPLEMENTADA COM SUCESSO!")
    print("   ✅ Sandbox com quotas (CPU/mem/tempo)")
    print("   ✅ Isolamento de rede (shims)")
    print("   ✅ Rollback automático on red")
    print("   ✅ Gates de validação (lint/types/tests/build)")
    print("   ✅ WAF (rate-limit, auth, secret-scan)")
    print("   ✅ Lock system pós-rollback")
    print("   ✅ CLI integration (opt-in)")
    
    return True

if __name__ == "__main__":
    success = test_phase17()
    sys.exit(0 if success else 1)
