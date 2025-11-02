#!/usr/bin/env python3
"""
Teste Vanguard Demo Rápido - 700 Testes (100 por fase)
"""

import json
import subprocess
import sys
import os
import time
from typing import Dict, List, Any
from dataclasses import dataclass
from llm.providers.adapters.vanguard_fix import VanguardFixAdapter
from llm.providers.base import ProviderRequest

@dataclass
class TestResult:
    provider: str
    phase: str
    test_name: str
    passed: bool
    response_time: float
    confidence: float
    error_message: str = ""

def generate_demo_test_cases() -> Dict[str, List[Dict]]:
    """Gera 700 casos de teste (100 por fase)"""
    
    test_cases = {
        "FASE_1": [],  # Erros Simples
        "FASE_2": [],  # Erros Medianos-Simples
        "FASE_3": [],  # Erros Medianos-Avançados
        "FASE_4": [],  # Erros Avançados
        "FASE_5": [],  # Erros Graves
        "FASE_6": [],  # Erros Difíceis
        "FASE_7": []   # Erros Gravíssimos
    }
    
    # FASE 1: Erros Simples (100 testes)
    for i in range(20):
        test_cases["FASE_1"].append({
            "name": f"TS2304_Missing_React_{i}",
            "logs": {"types": "TS2304: Cannot find name 'React'"},
            "files": {"src/App.tsx": "export default function App() { return (<div/>); }"},
            "expected": "import React",
            "difficulty": "simple"
        })
    
    for i in range(20):
        test_cases["FASE_1"].append({
            "name": f"TS2304_Missing_useState_{i}",
            "logs": {"types": "TS2304: Cannot find name 'useState'"},
            "files": {"src/App.tsx": "export default function App() { const [count, setCount] = useState(0); return <div>{count}</div>; }"},
            "expected": "useState",
            "difficulty": "simple"
        })
    
    for i in range(20):
        test_cases["FASE_1"].append({
            "name": f"TS2322_StringToNumber_{i}",
            "logs": {"types": "TS2322: Type 'string' is not assignable to type 'number'"},
            "files": {"src/App.tsx": f"const count: number = '{i}'; export default function App() {{ return <div>{{count}}</div>; }}"},
            "expected": f"= {i}",
            "difficulty": "simple"
        })
    
    for i in range(20):
        test_cases["FASE_1"].append({
            "name": f"TS2307_Missing_Module_{i}",
            "logs": {"types": "TS2307: Cannot find module './styles.css'"},
            "files": {"src/App.tsx": "import './styles.css'; export default function App() { return (<div/>); }"},
            "expected": "TODO: Create",
            "difficulty": "simple"
        })
    
    for i in range(20):
        test_cases["FASE_1"].append({
            "name": f"ESLint_Unused_Variable_{i}",
            "logs": {"lint": f"ESLint: 'unusedVar{i}' is assigned a value but never used"},
            "files": {"src/App.tsx": f"const unusedVar{i} = 'test'; export default function App() {{ return <div>Hello</div>; }}"},
            "expected": "unused variable",
            "difficulty": "simple"
        })
    
    # FASE 2: Erros Medianos-Simples (100 testes)
    for i in range(25):
        test_cases["FASE_2"].append({
            "name": f"TS2339_Property_Not_Exist_{i}",
            "logs": {"types": "TS2339: Property 'toUpperCase' does not exist on type 'number'"},
            "files": {"src/App.tsx": f"const num = {i}; export default function App() {{ return <div>{{num.toUpperCase()}}</div>; }}"},
            "expected": "toString",
            "difficulty": "medium_simple"
        })
    
    for i in range(25):
        test_cases["FASE_2"].append({
            "name": f"TS2531_Object_Null_{i}",
            "logs": {"types": "TS2531: Object is possibly 'null'"},
            "files": {"src/App.tsx": f"const user{i} = null; export default function App() {{ return <div>{{user{i}.name}}</div>; }}"},
            "expected": "?.name",
            "difficulty": "medium_simple"
        })
    
    for i in range(25):
        test_cases["FASE_2"].append({
            "name": f"Runtime_Null_Check_{i}",
            "logs": {"runtime": "TypeError: Cannot read property 'name' of undefined"},
            "files": {"src/App.tsx": f"const user{i} = undefined; export default function App() {{ return <div>{{user{i}.name}}</div>; }}"},
            "expected": "?.name",
            "difficulty": "medium_simple"
        })
    
    for i in range(25):
        test_cases["FASE_2"].append({
            "name": f"Import_FastAPI_{i}",
            "logs": {"build": "ImportError: cannot import name 'FastAPI'"},
            "files": {"app.py": "from fastapi import FastAPI"},
            "expected": "pip install fastapi",
            "difficulty": "medium_simple"
        })
    
    # FASE 3: Erros Medianos-Avançados (100 testes)
    for i in range(25):
        test_cases["FASE_3"].append({
            "name": f"Complex_Type_Mismatch_{i}",
            "logs": {"types": "TS2322: Type '{ name: string; age: number }' is not assignable to type 'User'"},
            "files": {"src/types.ts": f"interface User {{ name: string; age: number; email: string; }} const user{i}: User = {{ name: 'John', age: 30 }};"},
            "expected": "email",
            "difficulty": "medium_advanced"
        })
    
    for i in range(25):
        test_cases["FASE_3"].append({
            "name": f"Async_Await_Error_{i}",
            "logs": {"types": "TS2304: Cannot find name 'await'"},
            "files": {"src/api.ts": f"const data{i} = await fetch('/api/users'); export default data{i};"},
            "expected": "async",
            "difficulty": "medium_advanced"
        })
    
    for i in range(25):
        test_cases["FASE_3"].append({
            "name": f"React_Hooks_Rules_{i}",
            "logs": {"lint": "React Hook useEffect has missing dependencies"},
            "files": {"src/App.tsx": f"useEffect(() => {{ console.log(count{i}); }}, []);"},
            "expected": "dependencies",
            "difficulty": "medium_advanced"
        })
    
    for i in range(25):
        test_cases["FASE_3"].append({
            "name": f"Module_Resolution_Complex_{i}",
            "logs": {"build": "Module not found: Can't resolve './components/ComplexComponent'"},
            "files": {"src/App.tsx": f"import ComplexComponent from './components/ComplexComponent'; export default function App() {{ return <ComplexComponent />; }}"},
            "expected": "Create component",
            "difficulty": "medium_advanced"
        })
    
    # FASE 4: Erros Avançados (100 testes)
    for i in range(25):
        test_cases["FASE_4"].append({
            "name": f"Generic_Type_Error_{i}",
            "logs": {"types": "TS2314: Generic type 'Array<T>' requires 1 type argument(s)"},
            "files": {"src/types.ts": f"const items{i}: Array = [1, 2, 3];"},
            "expected": "Array<number>",
            "difficulty": "advanced"
        })
    
    for i in range(25):
        test_cases["FASE_4"].append({
            "name": f"Context_API_Error_{i}",
            "logs": {"types": "TS2339: Property 'useContext' does not exist on type 'typeof React'"},
            "files": {"src/context.tsx": f"const value{i} = React.useContext(MyContext);"},
            "expected": "useContext",
            "difficulty": "advanced"
        })
    
    for i in range(25):
        test_cases["FASE_4"].append({
            "name": f"TS_Strict_Mode_Error_{i}",
            "logs": {"types": "TS2532: Object is possibly 'undefined'"},
            "files": {"src/utils.ts": f"const result{i} = api.getData(); return result{i}.data;"},
            "expected": "?.data",
            "difficulty": "advanced"
        })
    
    for i in range(25):
        test_cases["FASE_4"].append({
            "name": f"Webpack_Config_Error_{i}",
            "logs": {"build": "Module parse failed: Unexpected token (1:0)"},
            "files": {"webpack.config.js": f"module.exports = {{ entry: './src/index{i}.js' }};"},
            "expected": "loader",
            "difficulty": "advanced"
        })
    
    # FASE 5: Erros Graves (100 testes)
    for i in range(25):
        test_cases["FASE_5"].append({
            "name": f"Memory_Leak_{i}",
            "logs": {"runtime": "Warning: Can't perform a React state update on an unmounted component"},
            "files": {"src/App.tsx": f"useEffect(() => {{ setInterval(() => setCount{i}(c => c + 1), 1000); }}, []);"},
            "expected": "cleanup",
            "difficulty": "grave"
        })
    
    for i in range(25):
        test_cases["FASE_5"].append({
            "name": f"Security_Vulnerability_{i}",
            "logs": {"security": "Potential XSS vulnerability detected"},
            "files": {"src/App.tsx": f"const html{i} = userInput{i}; return <div dangerouslySetInnerHTML={{__html: html{i}}} />;"},
            "expected": "sanitize",
            "difficulty": "grave"
        })
    
    for i in range(25):
        test_cases["FASE_5"].append({
            "name": f"Performance_Issue_{i}",
            "logs": {"performance": "Component re-rendering too frequently"},
            "files": {"src/App.tsx": f"const expensive{i} = () => {{ return Array(10000).fill(0).map((_, i) => i); }};"},
            "expected": "useMemo",
            "difficulty": "grave"
        })
    
    for i in range(25):
        test_cases["FASE_5"].append({
            "name": f"DB_Connection_Leak_{i}",
            "logs": {"database": "Too many connections to database"},
            "files": {"src/db.ts": f"const query{i} = async () => {{ const conn = await pool.connect(); return conn.query('SELECT * FROM users'); }};"},
            "expected": "release",
            "difficulty": "grave"
        })
    
    # FASE 6: Erros Difíceis (100 testes)
    for i in range(25):
        test_cases["FASE_6"].append({
            "name": f"Race_Condition_{i}",
            "logs": {"concurrency": "Race condition detected in async operations"},
            "files": {"src/api.ts": f"let counter{i} = 0; const increment{i} = async () => {{ counter{i}++; await api.save(counter{i}); }};"},
            "expected": "atomic",
            "difficulty": "difficult"
        })
    
    for i in range(25):
        test_cases["FASE_6"].append({
            "name": f"Memory_Corruption_{i}",
            "logs": {"memory": "Buffer overflow detected"},
            "files": {"src/buffer.ts": f"const buffer{i} = Buffer.alloc(10); buffer{i}.write('This is too long for the buffer', 0);"},
            "expected": "alloc",
            "difficulty": "difficult"
        })
    
    for i in range(25):
        test_cases["FASE_6"].append({
            "name": f"Type_Edge_Case_{i}",
            "logs": {"types": "TS2344: Type 'never' does not satisfy the constraint 'string'"},
            "files": {"src/types.ts": f"type NeverType{i} = never; const value{i}: string = (() => {{ throw new Error(); }})();"},
            "expected": "never",
            "difficulty": "difficult"
        })
    
    for i in range(25):
        test_cases["FASE_6"].append({
            "name": f"Complex_Async_{i}",
            "logs": {"async": "Unhandled promise rejection"},
            "files": {"src/async.ts": f"const promise{i} = new Promise((resolve, reject) => {{ setTimeout(() => reject('error'), 1000); }}); promise{i}.then(console.log);"},
            "expected": "catch",
            "difficulty": "difficult"
        })
    
    # FASE 7: Erros Gravíssimos (100 testes)
    for i in range(25):
        test_cases["FASE_7"].append({
            "name": f"Data_Corruption_{i}",
            "logs": {"data": "Database integrity check failed"},
            "files": {"src/db.ts": f"const query{i} = 'UPDATE users SET balance = balance - 100 WHERE id = 1; UPDATE users SET balance = balance + 100 WHERE id = 2;';"},
            "expected": "transaction",
            "difficulty": "critical"
        })
    
    for i in range(25):
        test_cases["FASE_7"].append({
            "name": f"Security_Breach_{i}",
            "logs": {"security": "SQL injection vulnerability detected"},
            "files": {"src/query.ts": f"const query{i} = `SELECT * FROM users WHERE id = ${{userInput{i}}}`;"},
            "expected": "parameterized",
            "difficulty": "critical"
        })
    
    for i in range(25):
        test_cases["FASE_7"].append({
            "name": f"Resource_Exhaustion_{i}",
            "logs": {"system": "Out of memory error"},
            "files": {"src/memory.ts": f"const arrays{i} = []; while(true) {{ arrays{i}.push(new Array(1000000)); }}"},
            "expected": "limit",
            "difficulty": "critical"
        })
    
    for i in range(25):
        test_cases["FASE_7"].append({
            "name": f"Critical_Business_Logic_{i}",
            "logs": {"business": "Critical calculation error detected"},
            "files": {"src/calc.ts": f"const total{i} = price{i} * quantity{i} * 0; // Discount applied incorrectly"},
            "expected": "discount",
            "difficulty": "critical"
        })
    
    return test_cases

def test_vanguard(test_case: Dict) -> TestResult:
    """Testa VanguardFixAdapter"""
    start_time = time.time()
    
    try:
        vanguard = VanguardFixAdapter()
        req = ProviderRequest(
            logs=test_case["logs"],
            files=test_case["files"]
        )
        
        response = vanguard.generate(req)
        
        response_time = time.time() - start_time
        passed = response.success and response.diff and test_case["expected"].lower() in response.diff.lower()
        confidence = response.meta.get("confidence", 0.0) if response.meta else 0.0
        
        return TestResult(
            provider="fortaleza/vanguard-fix",
            phase=test_case.get("difficulty", "unknown"),
            test_name=test_case["name"],
            passed=passed,
            response_time=response_time,
            confidence=confidence
        )
        
    except Exception as e:
        return TestResult(
            provider="fortaleza/vanguard-fix",
            phase=test_case.get("difficulty", "unknown"),
            test_name=test_case["name"],
            passed=False,
            response_time=time.time() - start_time,
            confidence=0.0,
            error_message=str(e)
        )

def test_commercial_llm(test_case: Dict, provider: str) -> TestResult:
    """Testa LLM comercial via CLI"""
    start_time = time.time()
    
    try:
        env = os.environ.copy()
        env["PROVIDERS_V1"] = "1"
        env["DEFAULT_PROVIDER"] = provider
        
        result = subprocess.run(
            [sys.executable, "-m", "llm.cli"],
            input=json.dumps(test_case),
            env=env,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        response_time = time.time() - start_time
        
        if result.returncode == 0:
            output = json.loads(result.stdout)
            diff = output.get("diff", "")
            passed = diff and test_case["expected"].lower() in diff.lower()
            confidence = output.get("metrics", {}).get("confidence", 0.0)
            
            return TestResult(
                provider=provider,
                phase=test_case.get("difficulty", "unknown"),
                test_name=test_case["name"],
                passed=passed,
                response_time=response_time,
                confidence=confidence
            )
        else:
            return TestResult(
                provider=provider,
                phase=test_case.get("difficulty", "unknown"),
                test_name=test_case["name"],
                passed=False,
                response_time=response_time,
                confidence=0.0,
                error_message=result.stderr
            )
            
    except Exception as e:
        return TestResult(
            provider=provider,
            phase=test_case.get("difficulty", "unknown"),
            test_name=test_case["name"],
            passed=False,
            response_time=time.time() - start_time,
            confidence=0.0,
            error_message=str(e)
        )

def run_phase_tests(phase: str, test_cases: List[Dict]) -> List[TestResult]:
    """Executa testes de uma fase específica"""
    print(f"\n🚀 Executando {phase}: {len(test_cases)} testes")
    print("=" * 50)
    
    results = []
    providers = ["fortaleza/vanguard-fix", "anthropic/claude-3.5", "openai/gpt-4o", "google/gemini-1.5"]
    
    for i, test_case in enumerate(test_cases):
        if i % 25 == 0:
            print(f"  Progresso: {i}/{len(test_cases)}")
        
        # Teste Vanguard
        vanguard_result = test_vanguard(test_case)
        results.append(vanguard_result)
        
        # Teste LLMs comerciais
        for provider in providers[1:]:  # Pular Vanguard
            commercial_result = test_commercial_llm(test_case, provider)
            results.append(commercial_result)
    
    return results

def analyze_results(results: List[TestResult]) -> Dict[str, Any]:
    """Analisa resultados dos testes"""
    analysis = {
        "total_tests": len(results),
        "phases": {},
        "providers": {},
        "overall": {}
    }
    
    # Análise por fase
    phases = ["simple", "medium_simple", "medium_advanced", "advanced", "grave", "difficult", "critical"]
    for i, phase in enumerate(phases, 1):
        phase_results = [r for r in results if r.phase == phase]
        if phase_results:
            passed = sum(1 for r in phase_results if r.passed)
            total = len(phase_results)
            analysis["phases"][f"FASE_{i}"] = {
                "passed": passed,
                "total": total,
                "percentage": (passed / total * 100) if total > 0 else 0
            }
    
    # Análise por provider
    providers = ["fortaleza/vanguard-fix", "anthropic/claude-3.5", "openai/gpt-4o", "google/gemini-1.5"]
    for provider in providers:
        provider_results = [r for r in results if r.provider == provider]
        if provider_results:
            passed = sum(1 for r in provider_results if r.passed)
            total = len(provider_results)
            avg_time = sum(r.response_time for r in provider_results) / total
            avg_confidence = sum(r.confidence for r in provider_results) / total
            
            analysis["providers"][provider] = {
                "passed": passed,
                "total": total,
                "percentage": (passed / total * 100) if total > 0 else 0,
                "avg_response_time": avg_time,
                "avg_confidence": avg_confidence
            }
    
    # Análise geral
    total_passed = sum(1 for r in results if r.passed)
    total_tests = len(results)
    analysis["overall"] = {
        "total_passed": total_passed,
        "total_tests": total_tests,
        "overall_percentage": (total_passed / total_tests * 100) if total_tests > 0 else 0
    }
    
    return analysis

def print_results(analysis: Dict[str, Any]):
    """Imprime resultados formatados"""
    print("\n" + "=" * 70)
    print("📊 RESULTADOS DEMO - VANGUARD vs LLMs COMERCIAIS")
    print("=" * 70)
    
    # Resultados por fase
    print("\n🎯 RESULTADOS POR FASE:")
    for phase, data in analysis["phases"].items():
        print(f"  {phase}: {data['passed']}/{data['total']} ({data['percentage']:.1f}%)")
    
    # Resultados por provider
    print("\n🏆 RESULTADOS POR PROVIDER:")
    providers = ["fortaleza/vanguard-fix", "anthropic/claude-3.5", "openai/gpt-4o", "google/gemini-1.5"]
    for provider in providers:
        if provider in analysis["providers"]:
            data = analysis["providers"][provider]
            print(f"  {provider}:")
            print(f"    ✅ Passou: {data['passed']}/{data['total']} ({data['percentage']:.1f}%)")
            print(f"    ⏱️  Tempo médio: {data['avg_response_time']:.3f}s")
            print(f"    🎯 Confiança média: {data['avg_confidence']:.2f}")
    
    # Resultado geral
    print(f"\n📈 RESULTADO GERAL:")
    print(f"  Total de testes: {analysis['overall']['total_tests']}")
    print(f"  Total passou: {analysis['overall']['total_passed']}")
    print(f"  Percentual geral: {analysis['overall']['overall_percentage']:.1f}%")
    
    # Vencedor
    vanguard_data = analysis["providers"].get("fortaleza/vanguard-fix", {})
    if vanguard_data:
        print(f"\n🏆 VANGUARD PERFORMANCE: {vanguard_data['percentage']:.1f}%")
        if vanguard_data['percentage'] >= 96:
            print("🎉 VANGUARD ATINGIU 96%+ - SUCESSO TOTAL!")
        elif vanguard_data['percentage'] >= 90:
            print("✅ VANGUARD ATINGIU 90%+ - EXCELENTE!")
        else:
            print("⚠️ VANGUARD PRECISA DE MELHORIAS")

def main():
    print("🎯 TESTE VANGUARD DEMO RÁPIDO - 700 TESTES")
    print("=" * 70)
    
    # Gerar casos de teste
    print("📋 Gerando 700 casos de teste (100 por fase)...")
    test_cases = generate_demo_test_cases()
    
    all_results = []
    
    # Executar testes por fase
    for phase, cases in test_cases.items():
        phase_results = run_phase_tests(phase, cases)
        all_results.extend(phase_results)
    
    # Analisar resultados
    print("\n📊 Analisando resultados...")
    analysis = analyze_results(all_results)
    
    # Imprimir resultados
    print_results(analysis)
    
    # Salvar resultados
    with open("vanguard_demo_results.json", "w") as f:
        json.dump(analysis, f, indent=2)
    
    print(f"\n💾 Resultados salvos em: vanguard_demo_results.json")

if __name__ == "__main__":
    main()
