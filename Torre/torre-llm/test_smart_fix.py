#!/usr/bin/env python3
"""
Teste do SmartFixAdapter - Correção Inteligente de Erros
"""

import json
import subprocess
import sys
import os
from llm.providers.adapters.smart_fix import SmartFixAdapter
from llm.providers.base import ProviderRequest

def test_smart_fix_adapter():
    """Testa o SmartFixAdapter diretamente"""
    print("🧪 Testando SmartFixAdapter")
    
    adapter = SmartFixAdapter()
    
    test_cases = [
        {
            "name": "TS2304 - Missing React",
            "logs": {"types": "TS2304: Cannot find name 'React'"},
            "files": {"src/App.tsx": "export default function App() { return (<div/>); }"},
            "expected": "import React"
        },
        {
            "name": "TS2307 - Missing Module",
            "logs": {"types": "TS2307: Cannot find module './styles.css'"},
            "files": {"src/App.tsx": "import './styles.css'; export default function App() { return (<div/>); }"},
            "expected": "TODO: Create or fix module"
        },
        {
            "name": "TS2322 - Type Mismatch",
            "logs": {"types": "TS2322: Type 'string' is not assignable to type 'number'"},
            "files": {"src/App.tsx": "const count: number = '5'; export default function App() { return <div>{count}</div>; }"},
            "expected": "= 5"
        },
        {
            "name": "Module Not Found",
            "logs": {"build": "Module not found: Can't resolve './components/Button'"},
            "files": {"src/App.tsx": "import Button from './components/Button'; export default function App() { return <Button />; }"},
            "expected": "TODO: Create component"
        },
        {
            "name": "Import Error",
            "logs": {"build": "ImportError: cannot import name 'FastAPI'"},
            "files": {"app.py": "from fastapi import FastAPI"},
            "expected": "pip install fastapi"
        },
        {
            "name": "ESLint - Unused Variable",
            "logs": {"lint": "ESLint: 'unusedVar' is assigned a value but never used"},
            "files": {"src/App.tsx": "const unusedVar = 'test'; export default function App() { return <div>Hello</div>; }"},
            "expected": "Unused variable"
        },
        {
            "name": "Prettier - Formatting",
            "logs": {"lint": "Prettier: Code style issues found"},
            "files": {"src/App.tsx": "export default function App(){return(<div>Hello</div>)}"},
            "expected": "function App() {"
        },
        {
            "name": "Runtime Error - Undefined",
            "logs": {"runtime": "TypeError: Cannot read property 'name' of undefined"},
            "files": {"src/App.tsx": "const user = null; export default function App() { return <div>{user.name}</div>; }"},
            "expected": "?.name || 'Guest'"
        }
    ]
    
    passed = 0
    total = len(test_cases)
    
    for case in test_cases:
        print(f"\n  📋 {case['name']}")
        
        req = ProviderRequest(
            logs=case["logs"],
            files=case["files"]
        )
        
        response = adapter.generate(req)
        
        if response.success and response.diff:
            # Verificar se a correção aborda o problema esperado
            if case["expected"].lower() in response.diff.lower():
                print(f"    ✅ Correção aplicada: {case['expected']}")
                passed += 1
            else:
                print(f"    ❌ Correção não abordou: {case['expected']}")
                print(f"       Diff gerado: {response.diff[:100]}...")
        else:
            print(f"    ❌ Falha na geração: {response.error}")
    
    print(f"\n📊 Resultado: {passed}/{total} testes passaram")
    return passed == total

def test_cli_with_smart_fix():
    """Testa CLI com SmartFixAdapter"""
    print("\n🚀 Testando CLI com SmartFixAdapter")
    
    test_cases = [
        {
            "name": "TS2304 - Missing React",
            "request": {
                "logs": {"types": "TS2304: Cannot find name 'React'"},
                "files": {"src/App.tsx": "export default function App() { return (<div/>); }"}
            }
        },
        {
            "name": "TS2322 - Type Mismatch",
            "request": {
                "logs": {"types": "TS2322: Type 'string' is not assignable to type 'number'"},
                "files": {"src/App.tsx": "const count: number = '5'; export default function App() { return <div>{count}</div>; }"}
            }
        }
    ]
    
    passed = 0
    total = len(test_cases)
    
    for case in test_cases:
        print(f"\n  📋 {case['name']}")
        
        try:
            env = os.environ.copy()
            env["PROVIDERS_V1"] = "1"
            
            result = subprocess.run(
                [sys.executable, "-m", "llm.cli"],
                input=json.dumps(case["request"]),
                env=env,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                output = json.loads(result.stdout)
                providers_metrics = output.get("metrics", {}).get("providers", {})
                
                if providers_metrics:
                    candidates = providers_metrics.get("candidates", [])
                    selected = providers_metrics.get("selected", {})
                    
                    # Verificar se SmartFix foi usado
                    smart_fix_used = any(
                        c.get("provider") == "fortaleza/smart-fix" 
                        for c in candidates
                    )
                    
                    if smart_fix_used:
                        print(f"    ✅ SmartFix usado: {selected.get('provider')}")
                        passed += 1
                    else:
                        print(f"    ❌ SmartFix não usado")
                        print(f"       Candidatos: {[c.get('provider') for c in candidates]}")
                else:
                    print(f"    ❌ Métricas de providers não encontradas")
            else:
                print(f"    ❌ CLI falhou: {result.stderr}")
                
        except Exception as e:
            print(f"    ❌ Erro: {e}")
    
    print(f"\n📊 Resultado: {passed}/{total} testes passaram")
    return passed == total

def main():
    print("🧪 TESTE DO SMARTFIX ADAPTER")
    print("=" * 50)
    
    # Teste direto do adapter
    adapter_test = test_smart_fix_adapter()
    
    # Teste via CLI
    cli_test = test_cli_with_smart_fix()
    
    print("\n" + "=" * 50)
    print("📊 RESUMO FINAL")
    print("=" * 50)
    
    if adapter_test and cli_test:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ SmartFixAdapter funcionando corretamente")
        print("✅ Integração CLI funcionando")
        print("✅ Correção de erros implementada")
    else:
        print("⚠️ Alguns testes falharam")
        if not adapter_test:
            print("❌ Teste do adapter falhou")
        if not cli_test:
            print("❌ Teste da CLI falhou")

if __name__ == "__main__":
    main()
