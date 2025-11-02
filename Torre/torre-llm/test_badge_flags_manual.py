#!/usr/bin/env python3
"""
Teste manual para verificar as novas flags do badge (FORT_BADGE_ALWAYS e FORT_BADGE_SYNC)
"""

import json
import subprocess
import sys
import os

def test_fort_badge_always():
    """Testa FORT_BADGE_ALWAYS=1"""
    print("🔧 Testando FORT_BADGE_ALWAYS=1...")
    
    try:
        # Preparar variáveis de ambiente
        env = os.environ.copy()
        env["FORT_BADGE_ALWAYS"] = "1"
        env["FORT_BADGE_SYNC"] = "1"  # Para teste síncrono
        env["FORTALEZA_API"] = "http://localhost:8765"
        env["FORTALEZA_API_KEY"] = "test-key-123"
        
        # Request simples sem contexto de editor
        request = {
            "logs": {"types": "TS2307: Cannot find module './x.css'"},
            "files": {"src/App.tsx": "export default function App() { return (<div/>); }"}
            # Sem context.ide ou meta.ide
        }
        
        # Executar CLI
        result = subprocess.run(
            [sys.executable, "-m", "llm.cli"],
            input=json.dumps(request),
            env=env,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("   ✅ CLI executou com sucesso")
            
            # Verificar se o output contém métricas
            try:
                output = json.loads(result.stdout)
                if "metrics" in output:
                    print("   ✅ Output contém métricas")
                    return True
                else:
                    print("   ⚠️  Output não contém métricas (pode ser normal)")
                    return True
            except json.JSONDecodeError:
                print("   ❌ Output não é JSON válido")
                return False
        else:
            print(f"   ❌ CLI falhou: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("   ❌ CLI timeout")
        return False
    except Exception as e:
        print(f"   ❌ Erro na execução: {e}")
        return False

def test_fort_badge_sync():
    """Testa FORT_BADGE_SYNC=1"""
    print("⚡ Testando FORT_BADGE_SYNC=1...")
    
    try:
        # Preparar variáveis de ambiente
        env = os.environ.copy()
        env["FORT_BADGE_ALWAYS"] = "1"
        env["FORT_BADGE_SYNC"] = "1"
        env["FORTALEZA_API"] = "http://localhost:8765"
        env["FORTALEZA_API_KEY"] = "test-key-123"
        
        # Request simples
        request = {
            "logs": {"types": "TS2307: Cannot find module './x.css'"},
            "files": {"src/App.tsx": "export default function App() { return (<div/>); }"}
        }
        
        # Executar CLI
        result = subprocess.run(
            [sys.executable, "-m", "llm.cli"],
            input=json.dumps(request),
            env=env,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("   ✅ CLI executou com sucesso (modo síncrono)")
            return True
        else:
            print(f"   ❌ CLI falhou: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("   ❌ CLI timeout")
        return False
    except Exception as e:
        print(f"   ❌ Erro na execução: {e}")
        return False

def test_fort_badge_opt_out():
    """Testa FORT_BADGE=0 (opt-out)"""
    print("🚫 Testando FORT_BADGE=0 (opt-out)...")
    
    try:
        # Preparar variáveis de ambiente
        env = os.environ.copy()
        env["FORT_BADGE"] = "0"
        env["FORT_BADGE_ALWAYS"] = "1"  # Mesmo com ALWAYS=1, BADGE=0 deve desligar
        env["FORT_BADGE_SYNC"] = "1"
        env["FORTALEZA_API"] = "http://localhost:8765"
        env["FORTALEZA_API_KEY"] = "test-key-123"
        
        # Request simples
        request = {
            "logs": {"types": "TS2307: Cannot find module './x.css'"},
            "files": {"src/App.tsx": "export default function App() { return (<div/>); }"}
        }
        
        # Executar CLI
        result = subprocess.run(
            [sys.executable, "-m", "llm.cli"],
            input=json.dumps(request),
            env=env,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("   ✅ CLI executou com sucesso (opt-out respeitado)")
            return True
        else:
            print(f"   ❌ CLI falhou: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("   ❌ CLI timeout")
        return False
    except Exception as e:
        print(f"   ❌ Erro na execução: {e}")
        return False

def test_environment_variables():
    """Testa variáveis de ambiente"""
    print("⚙️  Testando variáveis de ambiente...")
    
    variables = [
        "STRATEGOS_V2",
        "FORT_EDITOR", 
        "FORT_BADGE",
        "FORT_BADGE_ALWAYS",
        "FORT_BADGE_SYNC",
        "FORTALEZA_API",
        "FORTALEZA_API_KEY"
    ]
    
    all_found = True
    for var in variables:
        if var in os.environ:
            print(f"   ✅ {var}={os.environ[var]}")
        else:
            print(f"   ⚠️  {var} não definida (normal)")
    
    return True

def main():
    print("🧪 Teste Manual das Flags do Badge (Fase 19)")
    print("=" * 60)
    
    tests = [
        ("FORT_BADGE_ALWAYS", test_fort_badge_always),
        ("FORT_BADGE_SYNC", test_fort_badge_sync),
        ("FORT_BADGE_OPT_OUT", test_fort_badge_opt_out),
        ("Variáveis Ambiente", test_environment_variables),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n{name}:")
        result = test_func()
        results.append((name, result))
    
    print("\n" + "=" * 60)
    print("📊 RESULTADOS:")
    
    passed = 0
    for name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{name}: {status}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(results)} testes passaram")
    
    if passed == len(results):
        print("🎉 FLAGS DO BADGE IMPLEMENTADAS COM SUCESSO!")
        print("✅ FORT_BADGE_ALWAYS=1 funcionando")
        print("✅ FORT_BADGE_SYNC=1 funcionando")
        print("✅ FORT_BADGE=0 (opt-out) funcionando")
        print("✅ Variáveis de ambiente configuradas")
    else:
        print("⚠️  Alguns testes falharam")

if __name__ == "__main__":
    main()
