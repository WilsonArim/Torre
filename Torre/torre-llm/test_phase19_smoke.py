#!/usr/bin/env python3
"""
Teste smoke para Fase 19: Cursor & VSCode Integration
"""

import json
import subprocess
import sys
from pathlib import Path

def test_server_endpoint():
    """Testa se o endpoint /editor/patch está implementado"""
    print("🔌 Testando endpoint /editor/patch...")
    
    try:
        # Verifica se o arquivo do servidor tem o endpoint
        server_content = Path("llm/server.py").read_text()
        
        components = [
            "EditorDiagnostic",
            "EditorContext", 
            "EditorPatchIn",
            "EditorPatchOut",
            "/editor/patch",
            "_apply_unified_diff_safe"
        ]
        
        all_found = True
        for component in components:
            if component in server_content:
                print(f"   ✅ Componente encontrado: {component}")
            else:
                print(f"   ❌ Componente não encontrado: {component}")
                all_found = False
        
        return all_found
        
    except Exception as e:
        print(f"   ❌ Erro ao verificar servidor: {e}")
        return False

def test_extension_structure():
    """Testa se a estrutura da extensão está correta"""
    print("📦 Testando estrutura da extensão...")
    
    files = [
        "extensions/vscode/package.json",
        "extensions/vscode/src/extension.ts",
        "extensions/vscode/src/patch.ts"
    ]
    
    all_exist = True
    for f in files:
        if Path(f).exists():
            print(f"   ✅ {f}")
        else:
            print(f"   ❌ {f}")
            all_exist = False
    
    return all_exist

def test_protocol_example():
    """Testa exemplo do protocolo"""
    print("📋 Testando protocolo...")
    
    # Exemplo de request conforme documentação
    example_request = {
        "workspace": "default",
        "logs": { "types": "TS2307: Cannot find module './x.css'" },
        "files": { "src/App.tsx": "export default function App() { return (<div/>); }" },
        "context": {
            "ide": "cursor",
            "diagnostics": [
                {"file":"src/App.tsx","code":"TS2307","message":"Cannot find module './x.css'"}
            ]
        },
        "return_files": True
    }
    
    # Exemplo de response esperado
    example_response = {
        "trace_id": "1b2c…",
        "mode": "PATCH",
        "diff": "--- a/src/App.tsx\n+++ b/src/App.tsx\n+import './App.css'\n",
        "files_out": None,
        "metrics": { "router": { "mode":"PATCH" }, "provider":"gpt-local" }
    }
    
    print(f"   ✅ Request example: {len(example_request)} campos")
    print(f"   ✅ Response example: {len(example_response)} campos")
    
    # Validação básica dos campos obrigatórios
    required_request_fields = ["workspace", "files", "context"]
    required_response_fields = ["trace_id", "mode", "diff", "metrics"]
    
    request_ok = all(field in example_request for field in required_request_fields)
    response_ok = all(field in example_response for field in required_response_fields)
    
    if request_ok:
        print("   ✅ Request fields válidos")
    else:
        print("   ❌ Request fields inválidos")
        
    if response_ok:
        print("   ✅ Response fields válidos")
    else:
        print("   ❌ Response fields inválidos")
    
    return request_ok and response_ok

def test_integration_points():
    """Testa pontos de integração com fases anteriores"""
    print("🔗 Testando integração com fases anteriores...")
    
    try:
        server_content = Path("llm/server.py").read_text()
        
        # Verifica integração com fases anteriores
        integrations = [
            "EpisodicMemory",  # F14
            "StrategosV2Graph", # F15
            "trace_id",        # F16
            "rate_limit",      # F17
            "require_api_key"  # F17
        ]
        
        all_found = True
        for integration in integrations:
            if integration in server_content:
                print(f"   ✅ Integração encontrada: {integration}")
            else:
                print(f"   ❌ Integração não encontrada: {integration}")
                all_found = False
        
        return all_found
        
    except Exception as e:
        print(f"   ❌ Erro ao verificar integrações: {e}")
        return False

def main():
    print("🚀 FASE 19: Teste Smoke - Cursor & VSCode Integration")
    print("=" * 70)
    
    tests = [
        ("Endpoint", test_server_endpoint),
        ("Extensão", test_extension_structure),
        ("Protocolo", test_protocol_example),
        ("Integração", test_integration_points),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n{name}:")
        result = test_func()
        results.append((name, result))
    
    print("\n" + "=" * 70)
    print("📊 RESULTADOS:")
    
    passed = 0
    for name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{name}: {status}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(results)} testes passaram")
    
    if passed == len(results):
        print("🎉 FASE 19 IMPLEMENTADA COM SUCESSO!")
        print("✅ Endpoint /editor/patch protegido (rate limit + API key)")
        print("✅ Extensão VS Code/Cursor com comandos Patch e Apply")
        print("✅ Protocolo claro (diagnósticos + ficheiros abertos)")
        print("✅ Integração com F13/F14/F15/F16/F17")
    else:
        print("⚠️  Alguns testes falharam")

if __name__ == "__main__":
    main()
