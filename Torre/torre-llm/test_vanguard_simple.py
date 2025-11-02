#!/usr/bin/env python3
"""
Teste Vanguard Simples - Demonstração do Sistema
"""

import json
import subprocess
import sys
import os
from llm.providers.adapters.vanguard_fix import VanguardFixAdapter
from llm.providers.base import ProviderRequest

def test_vanguard_simple():
    """Teste simples do VanguardFixAdapter"""
    print("🎯 TESTE VANGUARD SIMPLES")
    print("=" * 40)
    
    adapter = VanguardFixAdapter()
    
    # Testes simples e diretos
    test_cases = [
        {
            "name": "TS2304 - Missing React",
            "logs": {"types": "TS2304: Cannot find name 'React'"},
            "files": {"src/App.tsx": "export default function App() { return (<div/>); }"},
            "expected": "import React"
        },
        {
            "name": "TS2304 - Missing useState",
            "logs": {"types": "TS2304: Cannot find name 'useState'"},
            "files": {"src/App.tsx": "export default function App() { const [count, setCount] = useState(0); return <div>{count}</div>; }"},
            "expected": "useState"
        },
        {
            "name": "TS2322 - Type Mismatch",
            "logs": {"types": "TS2322: Type 'string' is not assignable to type 'number'"},
            "files": {"src/App.tsx": "const count: number = '5'; export default function App() { return <div>{count}</div>; }"},
            "expected": "= 5"
        },
        {
            "name": "ESLint - Unused Variable",
            "logs": {"lint": "ESLint: 'unusedVar' is assigned a value but never used"},
            "files": {"src/App.tsx": "const unusedVar = 'test'; export default function App() { return <div>Hello</div>; }"},
            "expected": "unused variable"
        },
        {
            "name": "Prettier - Formatting",
            "logs": {"lint": "Prettier: Code style issues found"},
            "files": {"src/App.tsx": "export default function App(){return(<div>Hello</div>)}"},
            "expected": "function App() {"
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
            if case["expected"].lower() in response.diff.lower():
                print(f"     ✅ Correção aplicada: {case['expected']}")
                passed += 1
            else:
                print(f"     ❌ Correção não abordou: {case['expected']}")
                print(f"        Diff gerado: {response.diff[:100]}...")
        else:
            print(f"     ❌ Falha na geração")
    
    percentage = (passed / total * 100) if total > 0 else 0
    print(f"\n📊 RESULTADO: {passed}/{total} ({percentage:.1f}%)")
    
    if percentage >= 80:
        print("🎉 VANGUARD FUNCIONANDO BEM!")
        return True
    else:
        print("⚠️ VANGUARD PRECISA DE AJUSTES")
        return False

def test_cli_vanguard():
    """Testa CLI com Vanguard"""
    print("\n🚀 Testando CLI com Vanguard")
    
    test_case = {
        "logs": {"types": "TS2304: Cannot find name 'React'"},
        "files": {"src/App.tsx": "export default function App() { return (<div/>); }"}
    }
    
    try:
        env = os.environ.copy()
        env["PROVIDERS_V1"] = "1"
        
        result = subprocess.run(
            [sys.executable, "-m", "llm.cli"],
            input=json.dumps(test_case),
            env=env,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            output = json.loads(result.stdout)
            print(f"    ✅ CLI funcionou")
            print(f"    📊 Output: {output.get('mode', 'N/A')}")
            return True
        else:
            print(f"    ❌ CLI falhou: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"    ❌ Erro: {e}")
        return False

def main():
    print("🎯 TESTE VANGUARD SIMPLES - DEMONSTRAÇÃO")
    print("=" * 50)
    
    # Teste direto
    adapter_test = test_vanguard_simple()
    
    # Teste CLI
    cli_test = test_cli_vanguard()
    
    print("\n" + "=" * 50)
    print("📊 RESUMO VANGUARD")
    print("=" * 50)
    
    if adapter_test and cli_test:
        print("🎉 VANGUARD IMPLEMENTADO COM SUCESSO!")
        print("✅ Sistema vanguard: Operacional")
        print("✅ Integração CLI: Funcionando")
        print("\n🏆 FORTALEZA LLM TEM SISTEMA VANGUARD!")
    else:
        print("⚠️ VANGUARD PRECISA DE AJUSTES")
        if not adapter_test:
            print("❌ Teste do adapter falhou")
        if not cli_test:
            print("❌ Teste da CLI falhou")

if __name__ == "__main__":
    main()
