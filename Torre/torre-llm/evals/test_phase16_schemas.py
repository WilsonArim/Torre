#!/usr/bin/env python3
"""
Teste dos Schemas da Fase 16
"""

import json
import sys
from pathlib import Path

def test_schemas():
    """Testa apenas os schemas JSON"""
    
    print("🎯 TESTE SCHEMAS FASE 16")
    print("=" * 30)
    
    # Verificar schemas
    input_schema = Path("llm/contracts/input.schema.json")
    output_schema = Path("llm/contracts/output.schema.json")
    
    print(f"✅ Input schema existe: {input_schema.exists()}")
    print(f"✅ Output schema existe: {output_schema.exists()}")
    
    # Verificar se os schemas são JSON válido
    try:
        with open(input_schema, 'r') as f:
            input_data = json.load(f)
        print("✅ Input schema é JSON válido")
        print(f"   - Título: {input_data.get('title')}")
        print(f"   - ID: {input_data.get('$id')}")
        print(f"   - Required: {input_data.get('required')}")
    except Exception as e:
        print(f"❌ Input schema inválido: {e}")
        return False
    
    try:
        with open(output_schema, 'r') as f:
            output_data = json.load(f)
        print("✅ Output schema é JSON válido")
        print(f"   - Título: {output_data.get('title')}")
        print(f"   - ID: {output_data.get('$id')}")
        print(f"   - Required: {output_data.get('required')}")
    except Exception as e:
        print(f"❌ Output schema inválido: {e}")
        return False
    
    # Validar estrutura dos schemas
    input_has_trace_id = "trace_id" in input_data.get("properties", {})
    input_has_logs = "logs" in input_data.get("properties", {})
    input_has_files = "files" in input_data.get("properties", {})
    
    output_has_trace_id = "trace_id" in output_data.get("properties", {})
    output_has_cost = "cost" in output_data.get("properties", {}).get("metrics", {}).get("properties", {})
    
    print(f"✅ Input schema estrutura:")
    print(f"   - trace_id: {input_has_trace_id}")
    print(f"   - logs: {input_has_logs}")
    print(f"   - files: {input_has_files}")
    
    print(f"✅ Output schema estrutura:")
    print(f"   - trace_id: {output_has_trace_id}")
    print(f"   - cost metrics: {output_has_cost}")
    
    success = all([
        input_schema.exists(),
        output_schema.exists(),
        input_has_trace_id,
        input_has_logs,
        input_has_files,
        output_has_trace_id,
        output_has_cost
    ])
    
    if success:
        print("\n🎉 SCHEMAS FASE 16 VALIDADOS!")
        print("   - Input schema: Fortaleza LLM Request")
        print("   - Output schema: Fortaleza LLM Response")
        print("   - Trace ID em ambos")
        print("   - Cost metrics no output")
        return True
    else:
        print("\n❌ SCHEMAS FASE 16 INCOMPLETOS")
        return False

if __name__ == "__main__":
    success = test_schemas()
    sys.exit(0 if success else 1)
