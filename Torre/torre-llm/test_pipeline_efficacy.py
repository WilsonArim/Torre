#!/usr/bin/env python3
"""
Script para testar a eficácia da pipeline de correção de erros.
Gera casos de teste e mede a taxa de sucesso.
"""

import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Any

def generate_test_cases() -> List[Dict[str, Any]]:
    """Gera casos de teste comuns de TypeScript."""
    
    cases = []
    
    # Caso 1: TS2307 - Cannot find module
    cases.append({
        "name": "TS2307_missing_module",
        "file": "src/Component1.tsx",
        "content": """export default function Component1() {
  return <div>Hello</div>
}
import styles from './missing.module.css'
""",
        "expected_fixes": ["import moved to top", "React import added"]
    })
    
    # Caso 2: TS2304 - Cannot find name JSX
    cases.append({
        "name": "TS2304_jsx_no_react",
        "file": "src/Component2.tsx", 
        "content": """export default function Component2() {
  return <button>Click me</button>
}""",
        "expected_fixes": ["React import added"]
    })
    
    # Caso 3: TS2322 - Type assignment error
    cases.append({
        "name": "TS2322_type_error",
        "file": "src/Component3.tsx",
        "content": """const numberValue: number = "not a number"
export default function Component3() {
  return <div>{numberValue}</div>
}""",
        "expected_fixes": ["type correction"]
    })
    
    # Caso 4: Import order issues
    cases.append({
        "name": "import_order_issues",
        "file": "src/Component4.tsx",
        "content": """import { useState } from 'react'
export default function Component4() {
  const [count, setCount] = useState(0)
  return <div>{count}</div>
}
import './styles.css'""",
        "expected_fixes": ["imports reordered"]
    })
    
    return cases

def run_pipeline_on_case(case: Dict[str, Any], workdir: Path) -> Dict[str, Any]:
    """Executa a pipeline em um caso de teste."""
    
    # Criar arquivo de teste
    file_path = workdir / case["file"]
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, "w") as f:
        f.write(case["content"])
    
    # Executar pipeline
    try:
        result = subprocess.run(
            ["make", "pre-llm"],
            capture_output=True,
            text=True,
            cwd=workdir,
            timeout=60
        )
        
        # Ler arquivo após correção
        with open(file_path, "r") as f:
            corrected_content = f.read()
        
        return {
            "case": case["name"],
            "success": result.returncode == 0,
            "original": case["content"],
            "corrected": corrected_content,
            "pipeline_output": result.stdout,
            "pipeline_errors": result.stderr
        }
        
    except subprocess.TimeoutExpired:
        return {
            "case": case["name"],
            "success": False,
            "error": "timeout"
        }
    except Exception as e:
        return {
            "case": case["name"], 
            "success": False,
            "error": str(e)
        }

def analyze_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analisa os resultados dos testes."""
    
    total_cases = len(results)
    successful_cases = sum(1 for r in results if r.get("success", False))
    success_rate = (successful_cases / total_cases) * 100 if total_cases > 0 else 0
    
    # Análise detalhada
    fixes_applied = 0
    for result in results:
        if result.get("success") and result.get("corrected"):
            original = result.get("original", "")
            corrected = result.get("corrected", "")
            if original != corrected:
                fixes_applied += 1
    
    return {
        "total_cases": total_cases,
        "successful_cases": successful_cases,
        "success_rate": success_rate,
        "fixes_applied": fixes_applied,
        "fix_rate": (fixes_applied / total_cases) * 100 if total_cases > 0 else 0,
        "results": results
    }

def main():
    """Função principal."""
    
    print("🧪 Testando eficácia da pipeline de correção...")
    
    # Gerar casos de teste
    cases = generate_test_cases()
    print(f"📋 Gerados {len(cases)} casos de teste")
    
    # Criar diretório temporário
    with tempfile.TemporaryDirectory() as temp_dir:
        workdir = Path(temp_dir)
        
        # Copiar arquivos necessários
        for file in ["Makefile", "tsconfig.json", "eslint.config.js", "biome.json"]:
            if os.path.exists(file):
                subprocess.run(["cp", file, workdir])
        
        # Copiar diretório tools
        if os.path.exists("tools"):
            subprocess.run(["cp", "-r", "tools", workdir])
        
        # Executar pipeline em cada caso
        results = []
        for case in cases:
            print(f"🔧 Testando caso: {case['name']}")
            result = run_pipeline_on_case(case, workdir)
            results.append(result)
        
        # Analisar resultados
        analysis = analyze_results(results)
        
        # Salvar resultados
        output_file = ".fortaleza/out/pipeline_efficacy_test.json"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, "w") as f:
            json.dump(analysis, f, indent=2)
        
        # Mostrar resumo
        print("\n📊 RESULTADOS:")
        print(f"   Total de casos: {analysis['total_cases']}")
        print(f"   Casos bem-sucedidos: {analysis['successful_cases']}")
        print(f"   Taxa de sucesso: {analysis['success_rate']:.1f}%")
        print(f"   Correções aplicadas: {analysis['fixes_applied']}")
        print(f"   Taxa de correção: {analysis['fix_rate']:.1f}%")
        
        if analysis['success_rate'] >= 96:
            print("🎉 META ATINGIDA: 96%+ de sucesso!")
        else:
            print("⚠️  Meta não atingida. Verificar configurações.")
        
        print(f"\n📄 Resultados detalhados salvos em: {output_file}")

if __name__ == "__main__":
    main()
