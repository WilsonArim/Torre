#!/usr/bin/env python3
"""
Teste Vanguard 96%+ - Validação de Alta Performance
"""

import json
import subprocess
import sys
import os
import time
from llm.providers.adapters.vanguard_fix import VanguardFixAdapter
from llm.providers.base import ProviderRequest

def test_vanguard_96_percent():
    """Testa VanguardFixAdapter para 96%+ de acerto"""
    print("🎯 TESTE VANGUARD 96%+")
    print("=" * 50)
    
    adapter = VanguardFixAdapter()
    
    # Testes abrangentes para 96%+ de cobertura
    test_cases = [
        # TypeScript Errors (Alta confiança)
        {
            "name": "TS2304 - Missing React",
            "logs": {"types": "TS2304: Cannot find name 'React'"},
            "files": {"src/App.tsx": "export default function App() { return (<div/>); }"},
            "expected": "import React",
            "category": "typescript_high_confidence"
        },
        {
            "name": "TS2304 - Missing useState",
            "logs": {"types": "TS2304: Cannot find name 'useState'"},
            "files": {"src/App.tsx": "export default function App() { const [count, setCount] = useState(0); return <div>{count}</div>; }"},
            "expected": "useState",
            "category": "typescript_high_confidence"
        },
        {
            "name": "TS2307 - Missing Module",
            "logs": {"types": "TS2307: Cannot find module './styles.css'"},
            "files": {"src/App.tsx": "import './styles.css'; export default function App() { return (<div/>); }"},
            "expected": "TODO: Create or fix module",
            "category": "typescript_high_confidence"
        },
        {
            "name": "TS2322 - Type Mismatch String to Number",
            "logs": {"types": "TS2322: Type 'string' is not assignable to type 'number'"},
            "files": {"src/App.tsx": "const count: number = '5'; export default function App() { return <div>{count}</div>; }"},
            "expected": "= 5",
            "category": "typescript_high_confidence"
        },
        {
            "name": "TS2322 - Type Mismatch Number to String",
            "logs": {"types": "TS2322: Type 'number' is not assignable to type 'string'"},
            "files": {"src/App.tsx": "const name: string = 42; export default function App() { return <div>{name}</div>; }"},
            "expected": "= '42'",
            "category": "typescript_high_confidence"
        },
        
        # Build Errors (Alta confiança)
        {
            "name": "Module Not Found - Local",
            "logs": {"build": "Module not found: Can't resolve './components/Button'"},
            "files": {"src/App.tsx": "import Button from './components/Button'; export default function App() { return <Button />; }"},
            "expected": "TODO: Create component",
            "category": "build_high_confidence"
        },
        {
            "name": "Import Error - FastAPI",
            "logs": {"build": "ImportError: cannot import name 'FastAPI'"},
            "files": {"app.py": "from fastapi import FastAPI"},
            "expected": "pip install fastapi",
            "category": "build_high_confidence"
        },
        
        # Linting Errors (Alta confiança)
        {
            "name": "ESLint - Unused Variable",
            "logs": {"lint": "ESLint: 'unusedVar' is assigned a value but never used"},
            "files": {"src/App.tsx": "const unusedVar = 'test'; export default function App() { return <div>Hello</div>; }"},
            "expected": "Unused variable",
            "category": "linting_high_confidence"
        },
        {
            "name": "Prettier - Formatting",
            "logs": {"lint": "Prettier: Code style issues found"},
            "files": {"src/App.tsx": "export default function App(){return(<div>Hello</div>)}"},
            "expected": "function App() {",
            "category": "linting_high_confidence"
        },
        
        # Runtime Errors (Alta confiança)
        {
            "name": "Runtime Error - Null Check",
            "logs": {"runtime": "TypeError: Cannot read property 'name' of undefined"},
            "files": {"src/App.tsx": "const user = null; export default function App() { return <div>{user.name}</div>; }"},
            "expected": "?.name || 'Guest'",
            "category": "runtime_high_confidence"
        },
        {
            "name": "Runtime Error - Array Length",
            "logs": {"runtime": "TypeError: Cannot read property 'length' of undefined"},
            "files": {"src/App.tsx": "const items = null; export default function App() { return <div>{items.length}</div>; }"},
            "expected": "?.length || 0",
            "category": "runtime_high_confidence"
        },
        
        # Advanced TypeScript Errors
        {
            "name": "TS2339 - Property Does Not Exist",
            "logs": {"types": "TS2339: Property 'toUpperCase' does not exist on type 'number'"},
            "files": {"src/App.tsx": "const num = 42; export default function App() { return <div>{num.toUpperCase()}</div>; }"},
            "expected": "toString",
            "category": "typescript_advanced"
        },
        {
            "name": "TS2345 - Argument Type",
            "logs": {"types": "TS2345: Argument of type 'string' is not assignable to parameter of type 'number'"},
            "files": {"src/App.tsx": "const num = parseInt('abc'); export default function App() { return <div>{num}</div>; }"},
            "expected": "parseInt",
            "category": "typescript_advanced"
        },
        
        # Edge Cases (Para 96%+)
        {
            "name": "TS2531 - Object Null",
            "logs": {"types": "TS2531: Object is possibly 'null'"},
            "files": {"src/App.tsx": "const user = null; export default function App() { return <div>{user.name}</div>; }"},
            "expected": "?.name",
            "category": "edge_cases"
        },
        {
            "name": "TS6133 - Unused Variable",
            "logs": {"types": "TS6133: 'unusedVar' is declared but its value is never read"},
            "files": {"src/App.tsx": "const unusedVar = 'test'; export default function App() { return <div>Hello</div>; }"},
            "expected": "unused variable",
            "category": "edge_cases"
        }
    ]
    
    passed = 0
    total = len(test_cases)
    category_results = {}
    
    for case in test_cases:
        print(f"\n  📋 {case['name']}")
        print(f"     Categoria: {case['category']}")
        
        req = ProviderRequest(
            logs=case["logs"],
            files=case["files"]
        )
        
        response = adapter.generate(req)
        
        if response.success and response.diff:
            # Verificar se a correção aborda o problema esperado
            if case["expected"].lower() in response.diff.lower():
                print(f"     ✅ Correção aplicada: {case['expected']}")
                passed += 1
                category = case["category"]
                if category not in category_results:
                    category_results[category] = {"passed": 0, "total": 0}
                category_results[category]["passed"] += 1
                category_results[category]["total"] += 1
            else:
                print(f"     ❌ Correção não abordou: {case['expected']}")
                print(f"        Diff gerado: {response.diff[:100]}...")
                category = case["category"]
                if category not in category_results:
                    category_results[category] = {"passed": 0, "total": 0}
                category_results[category]["total"] += 1
        else:
            print(f"     ❌ Falha na geração: {response.error}")
            category = case["category"]
            if category not in category_results:
                category_results[category] = {"passed": 0, "total": 0}
            category_results[category]["total"] += 1
    
    # Resultados por categoria
    print(f"\n📊 RESULTADOS POR CATEGORIA:")
    for category, results in category_results.items():
        percentage = (results["passed"] / results["total"] * 100) if results["total"] > 0 else 0
        print(f"   {category}: {results['passed']}/{results['total']} ({percentage:.1f}%)")
    
    # Resultado geral
    overall_percentage = (passed / total * 100) if total > 0 else 0
    print(f"\n📊 RESULTADO GERAL: {passed}/{total} ({overall_percentage:.1f}%)")
    
    # Validação de 96%+
    if overall_percentage >= 96:
        print("🎉 VANGUARD 96%+ ATINGIDO!")
        print("✅ Sistema vanguard funcionando perfeitamente")
        return True
    elif overall_percentage >= 90:
        print("✅ VANGUARD 90%+ ATINGIDO!")
        print("⚠️ Próximo objetivo: 96%+")
        return False
    else:
        print("❌ VANGUARD 96%+ NÃO ATINGIDO")
        print("⚠️ Sistema precisa de melhorias")
        return False

def test_cli_with_vanguard():
    """Testa CLI com VanguardFixAdapter"""
    print("\n🚀 Testando CLI com VanguardFixAdapter")
    
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
                    
                    # Verificar se Vanguard foi usado
                    vanguard_used = any(
                        c.get("provider") == "torre/vanguard-fix" 
                        for c in candidates
                    )
                    
                    if vanguard_used:
                        print(f"    ✅ Vanguard usado: {selected.get('provider')}")
                        passed += 1
                    else:
                        print(f"    ❌ Vanguard não usado")
                        print(f"       Candidatos: {[c.get('provider') for c in candidates]}")
                else:
                    print(f"    ❌ Métricas de providers não encontradas")
            else:
                print(f"    ❌ CLI falhou: {result.stderr}")
                
        except Exception as e:
            print(f"    ❌ Erro: {e}")
    
    print(f"\n📊 Resultado CLI: {passed}/{total} testes passaram")
    return passed == total

def main():
    print("🎯 TESTE VANGUARD 96%+ - VALIDAÇÃO DE ALTA PERFORMANCE")
    print("=" * 70)
    
    # Teste direto do adapter
    adapter_test = test_vanguard_96_percent()
    
    # Teste via CLI
    cli_test = test_cli_with_vanguard()
    
    print("\n" + "=" * 70)
    print("📊 RESUMO FINAL VANGUARD")
    print("=" * 70)
    
    if adapter_test and cli_test:
        print("🎉 VANGUARD 96%+ IMPLEMENTADO COM SUCESSO!")
        print("✅ Correção de erros: 96%+ de acerto")
        print("✅ Integração CLI: Funcionando")
        print("✅ Sistema vanguard: Operacional")
        print("\n🏆 TORRE LLM É AGORA VANGUARDA EM CORREÇÃO DE ERROS!")
    else:
        print("⚠️ VANGUARD 96%+ PRECISA DE AJUSTES")
        if not adapter_test:
            print("❌ Teste do adapter não atingiu 96%+")
        if not cli_test:
            print("❌ Teste da CLI falhou")

if __name__ == "__main__":
    main()
