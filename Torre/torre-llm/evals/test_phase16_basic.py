#!/usr/bin/env python3
"""
Teste Básico da Fase 16 — Validação Simples
"""

import json
import sys
from pathlib import Path

def test_phase16_basic():
    """Teste básico da Fase 16"""
    
    print("🎯 TESTE BÁSICO FASE 16")
    print("=" * 30)
    
    # Verificar schemas
    input_schema = Path("llm/contracts/input.schema.json")
    output_schema = Path("llm/contracts/output.schema.json")
    
    print(f"✅ Input schema existe: {input_schema.exists()}")
    print(f"✅ Output schema existe: {output_schema.exists()}")
    
    # Verificar se os arquivos compilam
    try:
        import llm.server
        print("✅ Server compila")
    except Exception as e:
        print(f"❌ Server não compila: {e}")
        return False
    
    try:
        import llm.cli
        print("✅ CLI compila")
    except Exception as e:
        print(f"❌ CLI não compila: {e}")
        return False
    
    # Verificar se os schemas são JSON válido
    try:
        with open(input_schema, 'r') as f:
            json.load(f)
        print("✅ Input schema é JSON válido")
    except Exception as e:
        print(f"❌ Input schema inválido: {e}")
        return False
    
    try:
        with open(output_schema, 'r') as f:
            json.load(f)
        print("✅ Output schema é JSON válido")
    except Exception as e:
        print(f"❌ Output schema inválido: {e}")
        return False
    
    print("\n🎉 FASE 16 BÁSICA FUNCIONANDO!")
    return True

if __name__ == "__main__":
    success = test_phase16_basic()
    sys.exit(0 if success else 1)
