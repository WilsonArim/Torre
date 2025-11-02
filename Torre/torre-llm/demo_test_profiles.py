#!/usr/bin/env python3
"""
Demo dos dois perfis de teste: Smoke (rápido) vs Contrato (estrito)
"""

import subprocess
import sys
import os

def run_test(profile: str, test_file: str) -> bool:
    """Executa teste com perfil específico"""
    print(f"\n🔍 Executando {profile.upper()}: {test_file}")
    print("=" * 60)
    
    env = os.environ.copy()
    if profile == "strict":
        env["TEST_PROFILE"] = "strict"
    
    try:
        if test_file == "tests/test_fastapi_simple.py":
            # Script standalone
            result = subprocess.run(
                [sys.executable, test_file],
                env=env,
                cwd=".",
                capture_output=True,
                text=True
            )
        else:
            # Teste pytest
            result = subprocess.run(
                [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"],
                env=env,
                cwd=".",
                capture_output=True,
                text=True
            )
        
        print(result.stdout)
        if result.stderr:
            print("⚠️  Warnings:")
            print(result.stderr)
        
        success = result.returncode == 0
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"\n{status} - Perfil: {profile.upper()}")
        return success
        
    except Exception as e:
        print(f"❌ Erro ao executar teste: {e}")
        return False

def main():
    print("🚀 DEMO: Dois Perfis de Teste FastAPI")
    print("=" * 60)
    
    # Teste Smoke (rápido)
    smoke_ok = run_test("smoke", "tests/test_fastapi_simple.py")
    
    # Teste Contrato (estrito)
    contract_ok = run_test("strict", "tests/test_fastapi_contract.py")
    
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS RESULTADOS:")
    print(f"Smoke (rápido): {'✅ PASSOU' if smoke_ok else '❌ FALHOU'}")
    print(f"Contrato (estrito): {'✅ PASSOU' if contract_ok else '❌ FALHOU'}")
    
    if smoke_ok and contract_ok:
        print("\n🎉 AMBOS OS PERFIS PASSARAM!")
        print("✅ Infraestrutura básica funcionando")
        print("✅ Contratos e validações funcionando")
    elif smoke_ok:
        print("\n⚠️  APENAS SMOKE PASSOU")
        print("✅ Infraestrutura básica funcionando")
        print("❌ Contratos precisam de ajustes")
    else:
        print("\n❌ PROBLEMAS DETECTADOS")
        print("❌ Infraestrutura básica com problemas")

if __name__ == "__main__":
    main()
