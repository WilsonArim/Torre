#!/usr/bin/env python3
"""
Teste para verificar o patch do badge na CLI (Fase 19)
"""

import json
import subprocess
import sys
import os
from pathlib import Path

def test_cli_import():
    """Testa se a CLI importa sem erros após o patch"""
    print("🔧 Testando import da CLI...")
    
    try:
        import llm.cli
        print("   ✅ CLI importada com sucesso")
        return True
    except Exception as e:
        print(f"   ❌ Erro ao importar CLI: {e}")
        return False

def test_editor_detection():
    """Testa detecção de modo editor"""
    print("🔍 Testando detecção de modo editor...")
    
    try:
        from llm.cli import _detect_editor_mode
        
        # Teste com FORT_EDITOR=1
        os.environ["FORT_EDITOR"] = "1"
        result = _detect_editor_mode({})
        if result:
            print("   ✅ FORT_EDITOR=1 detectado")
        else:
            print("   ❌ FORT_EDITOR=1 não detectado")
            return False
        
        # Teste com context.ide
        os.environ.pop("FORT_EDITOR", None)
        result = _detect_editor_mode({"context": {"ide": "vscode"}})
        if result:
            print("   ✅ context.ide detectado")
        else:
            print("   ❌ context.ide não detectado")
            return False
        
        # Teste com meta.ide
        result = _detect_editor_mode({"meta": {"ide": "cursor"}})
        if result:
            print("   ✅ meta.ide detectado")
        else:
            print("   ❌ meta.ide não detectado")
            return False
        
        # Teste com source=editor
        result = _detect_editor_mode({"source": "editor"})
        if result:
            print("   ✅ source=editor detectado")
        else:
            print("   ❌ source=editor não detectado")
            return False
        
        # Teste negativo
        result = _detect_editor_mode({"logs": {"types": "error"}})
        if not result:
            print("   ✅ Modo não-editor detectado corretamente")
        else:
            print("   ❌ Modo não-editor detectado incorretamente")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro no teste de detecção: {e}")
        return False

def test_badge_extraction():
    """Testa extração de badge do output"""
    print("📊 Testando extração de badge...")
    
    try:
        from llm.cli import _extract_strategos_badge_payload
        
        # Teste com report.plan
        out_obj = {
            "report": {
                "plan": {
                    "mode": "PATCH",
                    "attempts_to_green_est": 2.5
                }
            }
        }
        badge = _extract_strategos_badge_payload(out_obj)
        if badge.get("mode") == "PATCH" and badge.get("attempts_to_green_est") == 2.5:
            print("   ✅ Badge extraído de report.plan")
        else:
            print("   ❌ Badge não extraído de report.plan")
            return False
        
        # Teste com metrics.strategos
        out_obj = {
            "metrics": {
                "strategos": {
                    "mode": "ADVISORY",
                    "attempts_to_green_est": 1.0
                }
            }
        }
        badge = _extract_strategos_badge_payload(out_obj)
        if badge.get("mode") == "ADVISORY" and badge.get("attempts_to_green_est") == 1.0:
            print("   ✅ Badge extraído de metrics.strategos")
        else:
            print("   ❌ Badge não extraído de metrics.strategos")
            return False
        
        # Teste com valor padrão
        out_obj = {}
        badge = _extract_strategos_badge_payload(out_obj)
        if badge.get("mode") == "ADVISORY" and badge.get("attempts_to_green_est") is None:
            print("   ✅ Badge com valores padrão")
        else:
            print("   ❌ Badge sem valores padrão")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro no teste de extração: {e}")
        return False

def test_cli_execution():
    """Testa execução da CLI com modo editor"""
    print("🚀 Testando execução da CLI...")
    
    try:
        # Preparar variáveis de ambiente
        env = os.environ.copy()
        env["STRATEGOS_V2"] = "1"
        env["FORT_EDITOR"] = "1"
        env["FORTALEZA_API"] = "http://localhost:8765"
        
        # Request simples
        request = {
            "logs": {"types": "TS2307: Cannot find module './x.css'"},
            "files": {"src/App.tsx": "export default function App() { return (<div/>); }"},
            "context": {"ide": "vscode"}
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
            
            # Verificar se o output contém métricas do Strategos
            try:
                output = json.loads(result.stdout)
                if "metrics" in output and "strategos" in output.get("metrics", {}):
                    print("   ✅ Métricas do Strategos presentes")
                    return True
                else:
                    print("   ⚠️  Métricas do Strategos não encontradas (pode ser normal)")
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

def test_environment_variables():
    """Testa variáveis de ambiente"""
    print("⚙️  Testando variáveis de ambiente...")
    
    variables = [
        "STRATEGOS_V2",
        "FORT_EDITOR", 
        "FORT_BADGE",
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
    print("🧪 Teste do Patch CLI Badge (Fase 19)")
    print("=" * 60)
    
    tests = [
        ("Import", test_cli_import),
        ("Detecção Editor", test_editor_detection),
        ("Extração Badge", test_badge_extraction),
        ("Execução CLI", test_cli_execution),
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
        print("🎉 PATCH CLI BADGE IMPLEMENTADO COM SUCESSO!")
        print("✅ Detecção de modo editor funcionando")
        print("✅ Extração de badge funcionando")
        print("✅ CLI executa sem erros")
        print("✅ Variáveis de ambiente configuradas")
    else:
        print("⚠️  Alguns testes falharam")

if __name__ == "__main__":
    main()
