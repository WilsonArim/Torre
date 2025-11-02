#!/usr/bin/env python3
"""
Teste Vanguard vs LLMs Comerciais - 7000 Testes em 7 Fases
"""

import json
import subprocess
import sys
import os
import time
import random
from typing import Dict, List, Any, Tuple
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

class VanguardVsCommercialTester:
    def __init__(self):
        self.vanguard = VanguardFixAdapter()
        self.results = []
        self.phases = {
            "FASE_1": "Erros Simples (1000 testes)",
            "FASE_2": "Erros Medianos-Simples (1000 testes)", 
            "FASE_3": "Erros Medianos-Avançados (1000 testes)",
            "FASE_4": "Erros Avançados (1000 testes)",
            "FASE_5": "Erros Graves (1000 testes)",
            "FASE_6": "Erros Difíceis (1000 testes)",
            "FASE_7": "Erros Gravíssimos (1000 testes)"
        }
        
    def generate_test_cases(self) -> Dict[str, List[Dict]]:
        """Gera 7000 casos de teste distribuídos em 7 fases"""
        
        test_cases = {
            "FASE_1": self._generate_simple_errors(),
            "FASE_2": self._generate_medium_simple_errors(),
            "FASE_3": self._generate_medium_advanced_errors(),
            "FASE_4": self._generate_advanced_errors(),
            "FASE_5": self._generate_grave_errors(),
            "FASE_6": self._generate_difficult_errors(),
            "FASE_7": self._generate_critical_errors()
        }
        
        return test_cases
    
    def _generate_simple_errors(self) -> List[Dict]:
        """Fase 1: 1000 erros simples"""
        cases = []
        
        # TS2304 - Missing imports
        for i in range(200):
            cases.append({
                "name": f"TS2304_Missing_React_{i}",
                "logs": {"types": "TS2304: Cannot find name 'React'"},
                "files": {"src/App.tsx": "export default function App() { return (<div/>); }"},
                "expected": "import React",
                "difficulty": "simple"
            })
        
        # TS2304 - Missing hooks
        hooks = ["useState", "useEffect", "useRef", "useCallback", "useMemo"]
        for hook in hooks:
            for i in range(40):
                cases.append({
                    "name": f"TS2304_Missing_{hook}_{i}",
                    "logs": {"types": f"TS2304: Cannot find name '{hook}'"},
                    "files": {"src/App.tsx": f"export default function App() {{ const [count, setCount] = {hook}(0); return <div>{{count}}</div>; }}"},
                    "expected": hook,
                    "difficulty": "simple"
                })
        
        # TS2322 - Type mismatches
        for i in range(200):
            cases.append({
                "name": f"TS2322_StringToNumber_{i}",
                "logs": {"types": "TS2322: Type 'string' is not assignable to type 'number'"},
                "files": {"src/App.tsx": f"const count: number = '{i}'; export default function App() {{ return <div>{{count}}</div>; }}"},
                "expected": f"= {i}",
                "difficulty": "simple"
            })
        
        # TS2307 - Missing modules
        modules = ["./styles.css", "./components/Button", "./utils/helpers"]
        for module in modules:
            for i in range(100):
                cases.append({
                    "name": f"TS2307_Missing_Module_{i}",
                    "logs": {"types": f"TS2307: Cannot find module '{module}'"},
                    "files": {"src/App.tsx": f"import '{module}'; export default function App() {{ return (<div/>); }}"},
                    "expected": "TODO: Create",
                    "difficulty": "simple"
                })
        
        # ESLint - Unused variables
        for i in range(200):
            cases.append({
                "name": f"ESLint_Unused_Variable_{i}",
                "logs": {"lint": f"ESLint: 'unusedVar{i}' is assigned a value but never used"},
                "files": {"src/App.tsx": f"const unusedVar{i} = 'test'; export default function App() {{ return <div>Hello</div>; }}"},
                "expected": "unused variable",
                "difficulty": "simple"
            })
        
        # Prettier - Formatting
        for i in range(100):
            cases.append({
                "name": f"Prettier_Formatting_{i}",
                "logs": {"lint": "Prettier: Code style issues found"},
                "files": {"src/App.tsx": f"export default function App{i}(){{return(<div>Hello</div>)}}"},
                "expected": "function App",
                "difficulty": "simple"
            })
        
        return cases[:1000]  # Garantir exatamente 1000
    
    def _generate_medium_simple_errors(self) -> List[Dict]:
        """Fase 2: 1000 erros medianos-simples"""
        cases = []
        
        # TS2339 - Property does not exist
        for i in range(200):
            cases.append({
                "name": f"TS2339_Property_Not_Exist_{i}",
                "logs": {"types": "TS2339: Property 'toUpperCase' does not exist on type 'number'"},
                "files": {"src/App.tsx": f"const num = {i}; export default function App() {{ return <div>{{num.toUpperCase()}}</div>; }}"},
                "expected": "toString",
                "difficulty": "medium_simple"
            })
        
        # TS2345 - Argument type mismatch
        for i in range(200):
            cases.append({
                "name": f"TS2345_Argument_Type_{i}",
                "logs": {"types": "TS2345: Argument of type 'string' is not assignable to parameter of type 'number'"},
                "files": {"src/App.tsx": f"const num = parseInt('abc{i}'); export default function App() {{ return <div>{{num}}</div>; }}"},
                "expected": "parseInt",
                "difficulty": "medium_simple"
            })
        
        # TS2531 - Object null
        for i in range(200):
            cases.append({
                "name": f"TS2531_Object_Null_{i}",
                "logs": {"types": "TS2531: Object is possibly 'null'"},
                "files": {"src/App.tsx": f"const user{i} = null; export default function App() {{ return <div>{{user{i}.name}}</div>; }}"},
                "expected": "?.name",
                "difficulty": "medium_simple"
            })
        
        # Runtime errors - Null checks
        for i in range(200):
            cases.append({
                "name": f"Runtime_Null_Check_{i}",
                "logs": {"runtime": "TypeError: Cannot read property 'name' of undefined"},
                "files": {"src/App.tsx": f"const user{i} = undefined; export default function App() {{ return <div>{{user{i}.name}}</div>; }}"},
                "expected": "?.name",
                "difficulty": "medium_simple"
            })
        
        # Import errors - FastAPI
        for i in range(200):
            cases.append({
                "name": f"Import_FastAPI_{i}",
                "logs": {"build": "ImportError: cannot import name 'FastAPI'"},
                "files": {"app.py": "from fastapi import FastAPI"},
                "expected": "pip install fastapi",
                "difficulty": "medium_simple"
            })
        
        return cases[:1000]
    
    def _generate_medium_advanced_errors(self) -> List[Dict]:
        """Fase 3: 1000 erros medianos-avançados"""
        cases = []
        
        # Complex type mismatches
        for i in range(200):
            cases.append({
                "name": f"Complex_Type_Mismatch_{i}",
                "logs": {"types": "TS2322: Type '{ name: string; age: number }' is not assignable to type 'User'"},
                "files": {"src/types.ts": f"interface User {{ name: string; age: number; email: string; }} const user{i}: User = {{ name: 'John', age: 30 }};"},
                "expected": "email",
                "difficulty": "medium_advanced"
            })
        
        # Async/await errors
        for i in range(200):
            cases.append({
                "name": f"Async_Await_Error_{i}",
                "logs": {"types": "TS2304: Cannot find name 'await'"},
                "files": {"src/api.ts": f"const data{i} = await fetch('/api/users'); export default data{i};"},
                "expected": "async",
                "difficulty": "medium_advanced"
            })
        
        # React hooks rules
        for i in range(200):
            cases.append({
                "name": f"React_Hooks_Rules_{i}",
                "logs": {"lint": "React Hook useEffect has missing dependencies"},
                "files": {"src/App.tsx": f"useEffect(() => {{ console.log(count{i}); }}, []);"},
                "expected": "dependencies",
                "difficulty": "medium_advanced"
            })
        
        # Module resolution complex
        for i in range(200):
            cases.append({
                "name": f"Module_Resolution_Complex_{i}",
                "logs": {"build": "Module not found: Can't resolve './components/ComplexComponent'"},
                "files": {"src/App.tsx": f"import ComplexComponent from './components/ComplexComponent'; export default function App() {{ return <ComplexComponent />; }}"},
                "expected": "Create component",
                "difficulty": "medium_advanced"
            })
        
        # State management errors
        for i in range(200):
            cases.append({
                "name": f"State_Management_Error_{i}",
                "logs": {"types": "TS2339: Property 'setState' does not exist on type 'number'"},
                "files": {"src/App.tsx": f"const [count{i}, setCount{i}] = useState(0); count{i}.setState(1);"},
                "expected": "setCount",
                "difficulty": "medium_advanced"
            })
        
        return cases[:1000]
    
    def _generate_advanced_errors(self) -> List[Dict]:
        """Fase 4: 1000 erros avançados"""
        cases = []
        
        # Generic type errors
        for i in range(200):
            cases.append({
                "name": f"Generic_Type_Error_{i}",
                "logs": {"types": "TS2314: Generic type 'Array<T>' requires 1 type argument(s)"},
                "files": {"src/types.ts": f"const items{i}: Array = [1, 2, 3];"},
                "expected": "Array<number>",
                "difficulty": "advanced"
            })
        
        # Context API errors
        for i in range(200):
            cases.append({
                "name": f"Context_API_Error_{i}",
                "logs": {"types": "TS2339: Property 'useContext' does not exist on type 'typeof React'"},
                "files": {"src/context.tsx": f"const value{i} = React.useContext(MyContext);"},
                "expected": "useContext",
                "difficulty": "advanced"
            })
        
        # Redux/state management
        for i in range(200):
            cases.append({
                "name": f"Redux_State_Error_{i}",
                "logs": {"types": "TS2339: Property 'dispatch' does not exist on type 'Store'"},
                "files": {"src/store.ts": f"const store{i} = createStore(reducer); store{i}.dispatch(action);"},
                "expected": "getState",
                "difficulty": "advanced"
            })
        
        # Webpack configuration
        for i in range(200):
            cases.append({
                "name": f"Webpack_Config_Error_{i}",
                "logs": {"build": "Module parse failed: Unexpected token (1:0)"},
                "files": {"webpack.config.js": f"module.exports = {{ entry: './src/index{i}.js' }};"},
                "expected": "loader",
                "difficulty": "advanced"
            })
        
        # TypeScript strict mode
        for i in range(200):
            cases.append({
                "name": f"TS_Strict_Mode_Error_{i}",
                "logs": {"types": "TS2532: Object is possibly 'undefined'"},
                "files": {"src/utils.ts": f"const result{i} = api.getData(); return result{i}.data;"},
                "expected": "?.data",
                "difficulty": "advanced"
            })
        
        return cases[:1000]
    
    def _generate_grave_errors(self) -> List[Dict]:
        """Fase 5: 1000 erros graves"""
        cases = []
        
        # Memory leaks
        for i in range(200):
            cases.append({
                "name": f"Memory_Leak_{i}",
                "logs": {"runtime": "Warning: Can't perform a React state update on an unmounted component"},
                "files": {"src/App.tsx": f"useEffect(() => {{ setInterval(() => setCount{i}(c => c + 1), 1000); }}, []);"},
                "expected": "cleanup",
                "difficulty": "grave"
            })
        
        # Infinite loops
        for i in range(200):
            cases.append({
                "name": f"Infinite_Loop_{i}",
                "logs": {"runtime": "Maximum call stack size exceeded"},
                "files": {"src/App.tsx": f"const render{i} = () => {{ setCount{i}(count{i} + 1); render{i}(); }};"},
                "expected": "base case",
                "difficulty": "grave"
            })
        
        # Security vulnerabilities
        for i in range(200):
            cases.append({
                "name": f"Security_Vulnerability_{i}",
                "logs": {"security": "Potential XSS vulnerability detected"},
                "files": {"src/App.tsx": f"const html{i} = userInput{i}; return <div dangerouslySetInnerHTML={{__html: html{i}}} />;"},
                "expected": "sanitize",
                "difficulty": "grave"
            })
        
        # Performance issues
        for i in range(200):
            cases.append({
                "name": f"Performance_Issue_{i}",
                "logs": {"performance": "Component re-rendering too frequently"},
                "files": {"src/App.tsx": f"const expensive{i} = () => {{ return Array(10000).fill(0).map((_, i) => i); }};"},
                "expected": "useMemo",
                "difficulty": "grave"
            })
        
        # Database connection leaks
        for i in range(200):
            cases.append({
                "name": f"DB_Connection_Leak_{i}",
                "logs": {"database": "Too many connections to database"},
                "files": {"src/db.ts": f"const query{i} = async () => {{ const conn = await pool.connect(); return conn.query('SELECT * FROM users'); }};"},
                "expected": "release",
                "difficulty": "grave"
            })
        
        return cases[:1000]
    
    def _generate_difficult_errors(self) -> List[Dict]:
        """Fase 6: 1000 erros difíceis"""
        cases = []
        
        # Race conditions
        for i in range(200):
            cases.append({
                "name": f"Race_Condition_{i}",
                "logs": {"concurrency": "Race condition detected in async operations"},
                "files": {"src/api.ts": f"let counter{i} = 0; const increment{i} = async () => {{ counter{i}++; await api.save(counter{i}); }};"},
                "expected": "atomic",
                "difficulty": "difficult"
            })
        
        # Deadlocks
        for i in range(200):
            cases.append({
                "name": f"Deadlock_{i}",
                "logs": {"concurrency": "Potential deadlock detected"},
                "files": {"src/locks.ts": f"const lock1{i} = new Mutex(); const lock2{i} = new Mutex(); await lock1{i}.acquire(); await lock2{i}.acquire();"},
                "expected": "order",
                "difficulty": "difficult"
            })
        
        # Memory corruption
        for i in range(200):
            cases.append({
                "name": f"Memory_Corruption_{i}",
                "logs": {"memory": "Buffer overflow detected"},
                "files": {"src/buffer.ts": f"const buffer{i} = Buffer.alloc(10); buffer{i}.write('This is too long for the buffer', 0);"},
                "expected": "alloc",
                "difficulty": "difficult"
            })
        
        # Type system edge cases
        for i in range(200):
            cases.append({
                "name": f"Type_Edge_Case_{i}",
                "logs": {"types": "TS2344: Type 'never' does not satisfy the constraint 'string'"},
                "files": {"src/types.ts": f"type NeverType{i} = never; const value{i}: string = (() => {{ throw new Error(); }})();"},
                "expected": "never",
                "difficulty": "difficult"
            })
        
        # Complex async patterns
        for i in range(200):
            cases.append({
                "name": f"Complex_Async_{i}",
                "logs": {"async": "Unhandled promise rejection"},
                "files": {"src/async.ts": f"const promise{i} = new Promise((resolve, reject) => {{ setTimeout(() => reject('error'), 1000); }}); promise{i}.then(console.log);"},
                "expected": "catch",
                "difficulty": "difficult"
            })
        
        return cases[:1000]
    
    def _generate_critical_errors(self) -> List[Dict]:
        """Fase 7: 1000 erros gravíssimos"""
        cases = []
        
        # System crashes
        for i in range(200):
            cases.append({
                "name": f"System_Crash_{i}",
                "logs": {"system": "Segmentation fault detected"},
                "files": {"src/crash.ts": f"const ptr{i} = process.binding('buffer').createUnsafeBuffer(1000000000); ptr{i}[0] = 0xDEADBEEF;"},
                "expected": "safe",
                "difficulty": "critical"
            })
        
        # Data corruption
        for i in range(200):
            cases.append({
                "name": f"Data_Corruption_{i}",
                "logs": {"data": "Database integrity check failed"},
                "files": {"src/db.ts": f"const query{i} = 'UPDATE users SET balance = balance - 100 WHERE id = 1; UPDATE users SET balance = balance + 100 WHERE id = 2;';"},
                "expected": "transaction",
                "difficulty": "critical"
            })
        
        # Security breaches
        for i in range(200):
            cases.append({
                "name": f"Security_Breach_{i}",
                "logs": {"security": "SQL injection vulnerability detected"},
                "files": {"src/query.ts": f"const query{i} = `SELECT * FROM users WHERE id = ${userInput{i}}`;"},
                "expected": "parameterized",
                "difficulty": "critical"
            })
        
        # Resource exhaustion
        for i in range(200):
            cases.append({
                "name": f"Resource_Exhaustion_{i}",
                "logs": {"system": "Out of memory error"},
                "files": {"src/memory.ts": f"const arrays{i} = []; while(true) {{ arrays{i}.push(new Array(1000000)); }}"},
                "expected": "limit",
                "difficulty": "critical"
            })
        
        # Critical business logic
        for i in range(200):
            cases.append({
                "name": f"Critical_Business_Logic_{i}",
                "logs": {"business": "Critical calculation error detected"},
                "files": {"src/calc.ts": f"const total{i} = price{i} * quantity{i} * 0; // Discount applied incorrectly"},
                "expected": "discount",
                "difficulty": "critical"
            })
        
        return cases[:1000]
    
    def test_vanguard(self, test_case: Dict) -> TestResult:
        """Testa VanguardFixAdapter"""
        start_time = time.time()
        
        try:
            req = ProviderRequest(
                logs=test_case["logs"],
                files=test_case["files"]
            )
            
            response = self.vanguard.generate(req)
            
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
    
    def test_commercial_llm(self, test_case: Dict, provider: str) -> TestResult:
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
    
    def run_phase_tests(self, phase: str, test_cases: List[Dict]) -> List[TestResult]:
        """Executa testes de uma fase específica"""
        print(f"\n🚀 Executando {phase}: {len(test_cases)} testes")
        print("=" * 60)
        
        results = []
        providers = ["fortaleza/vanguard-fix", "anthropic/claude-3.5", "openai/gpt-4o", "google/gemini-1.5"]
        
        for i, test_case in enumerate(test_cases):
            if i % 100 == 0:
                print(f"  Progresso: {i}/{len(test_cases)}")
            
            # Teste Vanguard
            vanguard_result = self.test_vanguard(test_case)
            results.append(vanguard_result)
            
            # Teste LLMs comerciais
            for provider in providers[1:]:  # Pular Vanguard
                commercial_result = self.test_commercial_llm(test_case, provider)
                results.append(commercial_result)
        
        return results
    
    def analyze_results(self, results: List[TestResult]) -> Dict[str, Any]:
        """Analisa resultados dos testes"""
        analysis = {
            "total_tests": len(results),
            "phases": {},
            "providers": {},
            "overall": {}
        }
        
        # Análise por fase
        for phase in self.phases.keys():
            phase_results = [r for r in results if r.phase in phase.lower()]
            if phase_results:
                passed = sum(1 for r in phase_results if r.passed)
                total = len(phase_results)
                analysis["phases"][phase] = {
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
    
    def print_results(self, analysis: Dict[str, Any]):
        """Imprime resultados formatados"""
        print("\n" + "=" * 80)
        print("📊 RESULTADOS COMPLETOS - VANGUARD vs LLMs COMERCIAIS")
        print("=" * 80)
        
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
    print("🎯 TESTE VANGUARD vs LLMs COMERCIAIS - 7000 TESTES")
    print("=" * 80)
    
    tester = VanguardVsCommercialTester()
    
    # Gerar casos de teste
    print("📋 Gerando 7000 casos de teste...")
    test_cases = tester.generate_test_cases()
    
    all_results = []
    
    # Executar testes por fase
    for phase, cases in test_cases.items():
        phase_results = tester.run_phase_tests(phase, cases)
        all_results.extend(phase_results)
    
    # Analisar resultados
    print("\n📊 Analisando resultados...")
    analysis = tester.analyze_results(all_results)
    
    # Imprimir resultados
    tester.print_results(analysis)
    
    # Salvar resultados
    with open("vanguard_vs_commercial_results.json", "w") as f:
        json.dump(analysis, f, indent=2)
    
    print(f"\n💾 Resultados salvos em: vanguard_vs_commercial_results.json")

if __name__ == "__main__":
    main()
