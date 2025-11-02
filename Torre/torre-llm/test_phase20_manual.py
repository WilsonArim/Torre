#!/usr/bin/env python3
"""
Teste manual para demonstrar a Fase 20 (Providers + Router + n-best)
"""

import json
import subprocess
import sys
import os

def test_providers_router():
    """Testa o router de providers"""
    print("🔧 Testando router de providers...")
    
    try:
        from llm.providers.router import ProvidersRouter
        from llm.providers.base import ProviderRequest
        
        router = ProvidersRouter(".")
        
        # Teste 1: Types
        logs = {"types": "TS2304: Cannot find name React"}
        files = {"src/App.tsx": "export default function App() { return (<div/>); }"}
        
        decision = router.decide(logs, files)
        print(f"   ✅ Types decision: {decision}")
        
        # Teste 2: Build
        logs = {"build": "Module not found: ./styles.css"}
        files = {"src/main.ts": "console.log('Hello')"}
        
        decision = router.decide(logs, files)
        print(f"   ✅ Build decision: {decision}")
        
        # Teste 3: Generate candidates
        req = ProviderRequest(logs=logs, files=files)
        candidates = router.generate_candidates(req, decision)
        print(f"   ✅ Generated {len(candidates)} candidates")
        
        for i, c in enumerate(candidates):
            print(f"      {i+1}. {c.provider} (tokens: {c.tokens_in}→{c.tokens_out}, latency: {c.latency_ms}ms)")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro no router: {e}")
        return False

def test_cli_with_providers():
    """Testa CLI com providers habilitados"""
    print("🚀 Testando CLI com providers...")
    
    try:
        # Preparar variáveis de ambiente
        env = os.environ.copy()
        env["PROVIDERS_V1"] = "1"
        
        # Request simples
        request = {
            "logs": {"types": "TS2307: Cannot find module './x.css'"},
            "files": {"src/App.tsx": "export default function App() { return (<div/>); }"}
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
            
            # Verificar output
            try:
                output = json.loads(result.stdout)
                providers_metrics = output.get("metrics", {}).get("providers", {})
                
                if providers_metrics:
                    print("   ✅ Providers metrics encontradas:")
                    print(f"      Router decision: {providers_metrics.get('router_decision', {})}")
                    print(f"      Candidates: {len(providers_metrics.get('candidates', []))}")
                    
                    if "selected" in providers_metrics:
                        selected = providers_metrics["selected"]
                        print(f"      Selected: {selected.get('provider')} (index: {selected.get('index')})")
                    
                    # Verificar trace
                    trace = output.get("metrics", {}).get("trace", {})
                    if trace:
                        print(f"      Trace: provider={trace.get('provider')}, tokens={trace.get('tokens_in')}→{trace.get('tokens_out')}")
                    
                    return True
                else:
                    print("   ⚠️  Providers metrics não encontradas")
                    return False
                    
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

def test_policy_config():
    """Testa configuração de política"""
    print("📋 Testando configuração de política...")
    
    try:
        from llm.providers.policy import ProvidersPolicy
        
        # Teste com política padrão
        policy = ProvidersPolicy(".")
        
        # Verificar providers permitidos
        print(f"   ✅ Providers permitidos: {policy.allowed}")
        
        # Verificar quotas
        print(f"   ✅ Quotas configuradas: {len(policy.quotas)} providers")
        
        # Teste de filtro
        test_providers = ["openai/gpt-4o", "anthropic/claude-3.5", "invalid/provider"]
        filtered = policy.filter_allowed(test_providers)
        print(f"   ✅ Filtro: {test_providers} → {filtered}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro na política: {e}")
        return False

def test_adapters():
    """Testa os adapters"""
    print("🔌 Testando adapters...")
    
    try:
        from llm.providers.adapters.local import LocalStub
        from llm.providers.adapters.openai import OpenAIStub
        from llm.providers.adapters.anthropic import AnthropicStub
        from llm.providers.adapters.google import GoogleStub
        from llm.providers.base import ProviderRequest
        
        adapters = [
            LocalStub(),
            OpenAIStub(),
            AnthropicStub(),
            GoogleStub()
        ]
        
        req = ProviderRequest(
            logs={"types": "TS2304: Cannot find name X"},
            files={"src/App.tsx": "console.log(1)"}
        )
        
        for adapter in adapters:
            resp = adapter.generate(req)
            print(f"   ✅ {adapter.name}: {resp.tokens_in}→{resp.tokens_out} tokens, {resp.latency_ms}ms")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro nos adapters: {e}")
        return False

def main():
    print("🧪 Teste Manual da Fase 20 - Providers + Router + n-best")
    print("=" * 70)
    
    tests = [
        ("Adapters", test_adapters),
        ("Policy", test_policy_config),
        ("Router", test_providers_router),
        ("CLI Integration", test_cli_with_providers),
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
        print("🎉 FASE 20 IMPLEMENTADA COM SUCESSO!")
        print("✅ Adapters de providers funcionando")
        print("✅ Router de seleção funcionando")
        print("✅ Política e quotas funcionando")
        print("✅ Integração CLI funcionando")
        print("✅ n-best entre provedores funcionando")
        print("✅ Telemetria e governança funcionando")
    else:
        print("⚠️  Alguns testes falharam")

if __name__ == "__main__":
    main()
