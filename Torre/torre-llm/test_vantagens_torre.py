#!/usr/bin/env python3
"""
Teste das Vantagens Únicas da Torre LLM
Demonstra capacidades que outras LLMs não possuem
"""

import json
import subprocess
import sys
import os
import time
from pathlib import Path
from typing import Dict, Any, List, Tuple

class TorreAdvantagesTester:
    def __init__(self):
        self.results = {}
        
    def test_multi_provider_routing(self):
        """Testa roteamento inteligente entre múltiplos provedores"""
        print("🔧 Teste 1: Roteamento Inteligente Multi-Provider")
        print("   Capacidade: Seleciona provedor baseado no tipo de erro")
        
        test_cases = [
            {
                "name": "TypeScript Error",
                "logs": {"types": "TS2304: Cannot find name 'React'"},
                "files": {"src/App.tsx": "export default function App() { return (<div/>); }"},
                "expected_providers": ["anthropic/claude-3.5", "openai/gpt-4o"]
            },
            {
                "name": "Build Error",
                "logs": {"build": "Module not found: Can't resolve './Button'"},
                "files": {"src/App.tsx": "import Button from './Button';"},
                "expected_providers": ["anthropic/claude-3.5", "openai/gpt-4o"]
            },
            {
                "name": "Linting Error",
                "logs": {"lint": "ESLint: 'unusedVar' is assigned but never used"},
                "files": {"src/App.tsx": "const unusedVar = 'test';"},
                "expected_providers": ["openai/gpt-4o", "local/qwen2.5-7b"]
            }
        ]
        
        from llm.providers.router import ProvidersRouter
        
        router = ProvidersRouter(".")
        passed = 0
        
        for case in test_cases:
            decision = router.decide(case["logs"], case["files"])
            selected_providers = decision.get("providers", [])
            
            # Verificar se selecionou os provedores esperados
            if set(selected_providers) == set(case["expected_providers"]):
                print(f"   ✅ {case['name']}: Selecionou {selected_providers}")
                passed += 1
            else:
                print(f"   ❌ {case['name']}: Esperava {case['expected_providers']}, obteve {selected_providers}")
        
        print(f"   Resultado: {passed}/{len(test_cases)} casos corretos")
        return passed == len(test_cases)
    
    def test_provider_quotas_and_policy(self):
        """Testa sistema de quotas e política"""
        print("\n📋 Teste 2: Sistema de Quotas e Política")
        print("   Capacidade: Controle de uso por provedor")
        
        from llm.providers.policy import ProvidersPolicy
        
        policy = ProvidersPolicy(".")
        
        # Teste de filtro de provedores
        test_providers = ["openai/gpt-4o", "anthropic/claude-3.5", "invalid/provider"]
        filtered = policy.filter_allowed(test_providers)
        
        if filtered == ["openai/gpt-4o", "anthropic/claude-3.5"]:
            print("   ✅ Filtro de provedores funcionando")
            quota_test = True
        else:
            print(f"   ❌ Filtro falhou: {filtered}")
            quota_test = False
        
        # Teste de quotas
        if policy.check_quota("openai/gpt-4o"):
            print("   ✅ Verificação de quota funcionando")
            quota_test = quota_test and True
        else:
            print("   ❌ Verificação de quota falhou")
            quota_test = False
        
        return quota_test
    
    def test_n_best_selection(self):
        """Testa seleção n-best entre provedores"""
        print("\n🎯 Teste 3: Seleção N-Best entre Provedores")
        print("   Capacidade: Gera múltiplos candidatos e seleciona o melhor")
        
        from llm.providers.router import ProvidersRouter
        from llm.providers.base import ProviderRequest
        
        router = ProvidersRouter(".")
        logs = {"types": "TS2304: Cannot find name 'React'"}
        files = {"src/App.tsx": "export default function App() { return (<div/>); }"}
        
        decision = router.decide(logs, files)
        req = ProviderRequest(logs=logs, files=files)
        candidates = router.generate_candidates(req, decision)
        
        if len(candidates) >= 2:
            print(f"   ✅ Gerou {len(candidates)} candidatos de diferentes provedores")
            
            # Mostrar diferenças entre candidatos
            for i, candidate in enumerate(candidates):
                print(f"      {i+1}. {candidate.provider}: {candidate.tokens_in}→{candidate.tokens_out} tokens")
            
            return True
        else:
            print(f"   ❌ Gerou apenas {len(candidates)} candidatos")
            return False
    
    def test_telemetry_and_trace(self):
        """Testa telemetria e rastreabilidade"""
        print("\n📊 Teste 4: Telemetria e Rastreabilidade")
        print("   Capacidade: Trace completo com métricas detalhadas")
        
        try:
            # Executar CLI com providers
            request = {
                "logs": {"types": "TS2304: Cannot find name 'React'"},
                "files": {"src/App.tsx": "export default function App() { return (<div/>); }"}
            }
            
            env = os.environ.copy()
            env["PROVIDERS_V1"] = "1"
            
            result = subprocess.run(
                [sys.executable, "-m", "llm.cli"],
                input=json.dumps(request),
                env=env,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                output = json.loads(result.stdout)
                metrics = output.get("metrics", {})
                
                # Verificar telemetria
                telemetry_checks = []
                
                if "providers" in metrics:
                    telemetry_checks.append("✅ Métricas de providers")
                
                if "trace" in metrics:
                    telemetry_checks.append("✅ Trace com provider e tokens")
                
                if "router_decision" in metrics.get("providers", {}):
                    telemetry_checks.append("✅ Decisão do router")
                
                if "candidates" in metrics.get("providers", {}):
                    telemetry_checks.append("✅ Lista de candidatos")
                
                if "selected" in metrics.get("providers", {}):
                    telemetry_checks.append("✅ Provedor selecionado")
                
                print(f"   {' | '.join(telemetry_checks)}")
                return len(telemetry_checks) >= 4
            else:
                print("   ❌ CLI falhou")
                return False
                
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            return False
    
    def test_integration_with_existing_system(self):
        """Testa integração com sistema existente"""
        print("\n🔗 Teste 5: Integração com Sistema Existente")
        print("   Capacidade: Funciona com todas as fases anteriores")
        
        try:
            # Testar com diferentes flags
            request = {
                "logs": {"types": "TS2304: Cannot find name 'React'"},
                "files": {"src/App.tsx": "export default function App() { return (<div/>); }"}
            }
            
            env = os.environ.copy()
            env["PROVIDERS_V1"] = "1"
            env["STRATEGOS_V2"] = "1"
            env["LLM_RERANK"] = "1"
            
            result = subprocess.run(
                [sys.executable, "-m", "llm.cli"],
                input=json.dumps(request),
                env=env,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                output = json.loads(result.stdout)
                
                integration_checks = []
                
                # Verificar integração com F13 (rerank)
                if "rerank" in output.get("metrics", {}):
                    integration_checks.append("✅ F13 Rerank")
                
                # Verificar integração com F15 (strategos)
                if "strategos" in output.get("metrics", {}):
                    integration_checks.append("✅ F15 Strategos")
                
                # Verificar integração com F20 (providers)
                if "providers" in output.get("metrics", {}):
                    integration_checks.append("✅ F20 Providers")
                
                # Verificar integração com F16 (trace)
                if "trace" in output.get("metrics", {}):
                    integration_checks.append("✅ F16 Trace")
                
                print(f"   {' | '.join(integration_checks)}")
                return len(integration_checks) >= 3
            else:
                print("   ❌ Integração falhou")
                return False
                
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            return False
    
    def test_opt_in_behavior(self):
        """Testa comportamento opt-in"""
        print("\n⚙️ Teste 6: Comportamento Opt-In")
        print("   Capacidade: Não afeta sistema quando desabilitado")
        
        request = {
            "logs": {"types": "TS2304: Cannot find name 'React'"},
            "files": {"src/App.tsx": "export default function App() { return (<div/>); }"}
        }
        
        # Teste sem providers
        env_disabled = os.environ.copy()
        env_disabled["PROVIDERS_V1"] = "0"
        
        result_disabled = subprocess.run(
            [sys.executable, "-m", "llm.cli"],
            input=json.dumps(request),
            env=env_disabled,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Teste com providers
        env_enabled = os.environ.copy()
        env_enabled["PROVIDERS_V1"] = "1"
        
        result_enabled = subprocess.run(
            [sys.executable, "-m", "llm.cli"],
            input=json.dumps(request),
            env=env_enabled,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result_disabled.returncode == 0 and result_enabled.returncode == 0:
            output_disabled = json.loads(result_disabled.stdout)
            output_enabled = json.loads(result_enabled.stdout)
            
            # Verificar que providers só aparece quando habilitado
            has_providers_disabled = "providers" in output_disabled.get("metrics", {})
            has_providers_enabled = "providers" in output_enabled.get("metrics", {})
            
            if not has_providers_disabled and has_providers_enabled:
                print("   ✅ Opt-in funcionando corretamente")
                return True
            else:
                print("   ❌ Opt-in não funcionando")
                return False
        else:
            print("   ❌ Teste opt-in falhou")
            return False
    
    def run_advantages_test(self):
        """Executa todos os testes de vantagens"""
        print("🏆 TESTE DAS VANTAGENS ÚNICAS DA TORRE LLM")
        print("=" * 70)
        
        tests = [
            ("Roteamento Multi-Provider", self.test_multi_provider_routing),
            ("Quotas e Política", self.test_provider_quotas_and_policy),
            ("Seleção N-Best", self.test_n_best_selection),
            ("Telemetria e Trace", self.test_telemetry_and_trace),
            ("Integração com Sistema", self.test_integration_with_existing_system),
            ("Comportamento Opt-In", self.test_opt_in_behavior),
        ]
        
        results = []
        for name, test_func in tests:
            try:
                result = test_func()
                results.append((name, result))
                status = "✅ PASSOU" if result else "❌ FALHOU"
                print(f"\n{status}: {name}")
            except Exception as e:
                results.append((name, False))
                print(f"\n❌ FALHOU: {name} - Erro: {e}")
        
        # Resumo final
        print("\n" + "=" * 70)
        print("📊 RESUMO DAS VANTAGENS ÚNICAS")
        print("=" * 70)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        print(f"\n✅ Testes Passados: {passed}/{total}")
        
        if passed == total:
            print("🎉 TODAS AS VANTAGENS ÚNICAS FUNCIONANDO!")
        elif passed >= total * 0.8:
            print("✅ MAIORIA DAS VANTAGENS FUNCIONANDO!")
        else:
            print("⚠️ Algumas vantagens precisam de ajustes")
        
        print("\n🏆 VANTAGENS ÚNICAS DA TORRE LLM:")
        print("1. 🔧 Roteamento Inteligente: Seleciona provedor baseado no erro")
        print("2. 📋 Sistema de Quotas: Controle de uso por provedor")
        print("3. 🎯 Seleção N-Best: Múltiplos candidatos, melhor escolha")
        print("4. 📊 Telemetria Completa: Trace detalhado com métricas")
        print("5. 🔗 Integração Total: Funciona com todas as fases")
        print("6. ⚙️ Opt-In Seguro: Não quebra sistema existente")
        
        print("\n💡 DIFERENCIAL COMPETITIVO:")
        print("• Outras LLMs: Apenas um modelo, sem roteamento")
        print("• Torre LLM: Sistema completo com múltiplos provedores")
        print("• Outras LLMs: Sem controle de quotas ou política")
        print("• Torre LLM: Governança completa por workspace")
        print("• Outras LLMs: Sem telemetria detalhada")
        print("• Torre LLM: Trace completo com métricas")
        
        return passed == total

def main():
    tester = TorreAdvantagesTester()
    tester.run_advantages_test()

if __name__ == "__main__":
    main()
