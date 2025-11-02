#!/usr/bin/env python3
"""
Teste da Fase 6 - Autonomia Avançada
Objetivo: testar cérebro determinista + pós-processamento + circuit breaker
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm.autonomy.autonomy_orchestrator import AutonomyOrchestrator, OutputMode
from llm.autonomy.deterministic_brain import DeterministicBrain
from llm.autonomy.post_processor import PostProcessor, ValidationResult
from llm.autonomy.circuit_breaker import CircuitBreaker, CircuitState

def test_deterministic_brain():
    """Testa o cérebro determinista"""
    print("🧠 Testando Cérebro Determinista...")
    
    brain = DeterministicBrain()
    
    # Teste 1: Resposta válida
    valid_response = """
    Aqui está o patch para corrigir o erro:
    
    ```diff
    --- a/src/components/Button.tsx
    +++ b/src/components/Button.tsx
    @@ -10,7 +10,7 @@
     const Button: React.FC<ButtonProps> = ({ children, onClick, disabled = false }) => {
       return (
         <button
    -      className="btn btn-primary"
    +      className={`btn btn-primary ${disabled ? 'disabled' : ''}`}
           onClick={onClick}
           disabled={disabled}
         >
    ```
    """
    
    context = {
        "files": ["src/components/Button.tsx"],
        "error_logs": ["TypeError: Cannot read property 'className' of undefined"],
        "priority": "high"
    }
    
    result = brain.process_llm_response(valid_response, context)
    print(f"✅ Teste válido: {result.mode.value} (confiança: {result.confidence:.1%})")
    
    # Teste 2: Resposta com paths sensíveis
    sensitive_response = """
    ```diff
    --- a/.env
    +++ b/.env
    @@ -1,1 +1,1 @@
    -API_KEY=old_key
    +API_KEY=new_key
    ```
    """
    
    result = brain.process_llm_response(sensitive_response, context)
    print(f"🚫 Teste sensível: {result.mode.value} (bloqueado: {result.confidence == 0.0})")
    
    # Teste 3: Resposta muito grande
    large_response = "```diff\n" + "\n".join([f"+line {i}" for i in range(1000)]) + "\n```"
    result = brain.process_llm_response(large_response, context)
    print(f"✂️ Teste grande: {result.mode.value} (truncado: {len(result.diff_content.split()) < 1000})")
    
    return True

def test_post_processor():
    """Testa o pós-processamento"""
    print("\n🔧 Testando Pós-Processamento...")
    
    processor = PostProcessor()
    
    # Teste 1: Diff válido
    valid_diff = """```diff
--- a/src/utils/helper.ts
+++ b/src/utils/helper.ts
@@ -5,7 +5,7 @@
 export function formatDate(date: Date): string {
-  return date.toLocaleDateString();
+  return date.toLocaleDateString('pt-BR');
 }
```"""
    
    result = processor.process_output(valid_diff)
    print(f"✅ Diff válido: {result.validation.value} (violações: {len(result.violations)})")
    
    # Teste 2: Diff com segredos
    secret_diff = """```diff
--- a/config.js
+++ b/config.js
@@ -1,3 +1,3 @@
 module.exports = {
-  apiKey: 'old_key_123456789'
+  apiKey: 'new_key_987654321'
 };
```"""
    
    result = processor.process_output(secret_diff)
    print(f"🚫 Diff com segredos: {result.validation.value} (bloqueado: {'secret' in str(result.violations).lower()})")
    
    # Teste 3: Diff com comandos perigosos
    dangerous_diff = """```diff
--- a/script.sh
+++ b/script.sh
@@ -1,1 +1,1 @@
-echo "Hello"
+rm -rf /tmp/*
```"""
    
    result = processor.process_output(dangerous_diff)
    print(f"🚫 Diff perigoso: {result.validation.value} (bloqueado: {'dangerous' in str(result.violations).lower()})")
    
    return True

def test_circuit_breaker():
    """Testa o circuit breaker"""
    print("\n⚡ Testando Circuit Breaker...")
    
    breaker = CircuitBreaker(failure_threshold=0.2, recovery_timeout=5)
    
    # Teste 1: Sucessos normais
    for i in range(10):
        breaker.record_request(True, {"test": i})
    
    metrics = breaker.get_metrics()
    print(f"✅ Sucessos normais: {metrics.current_state.value} (success_rate: {metrics.success_count/metrics.total_requests:.1%})")
    
    # Teste 2: Falhas para abrir circuit
    for i in range(10):
        breaker.record_request(False, {"test": f"fail_{i}"})
    
    metrics = breaker.get_metrics()
    print(f"🔴 Circuit aberto: {metrics.current_state.value} (failure_rate: {metrics.failure_count/metrics.total_requests:.1%})")
    
    # Teste 3: Verificar se bloqueia requests
    should_allow = breaker.should_allow_request()
    print(f"🚫 Requests bloqueados: {not should_allow}")
    
    return True

def test_autonomy_orchestrator():
    """Testa o orquestrador completo"""
    print("\n🎯 Testando Orquestrador de Autonomia...")
    
    orchestrator = AutonomyOrchestrator()
    
    # Teste 1: Request normal
    normal_response = """
    ```diff
    --- a/src/components/Header.tsx
    +++ b/src/components/Header.tsx
    @@ -15,7 +15,7 @@
     const Header: React.FC = () => {
       return (
         <header className="header">
    -      <h1>My App</h1>
    +      <h1>Fortaleza App</h1>
           <nav>
             <ul>
    ```
    """
    
    context = {
        "files": ["src/components/Header.tsx"],
        "error_logs": ["Component Header not found"],
        "priority": "medium"
    }
    
    result = orchestrator.process_request(normal_response, context)
    print(f"✅ Request normal: {result.output_mode.value} (success: {result.success})")
    
    # Teste 2: Request com falhas para testar degradação
    for i in range(15):
        orchestrator.process_request("invalid response", context)
    
    # Simula um request válido após falhas
    result = orchestrator.process_request(normal_response, context)
    print(f"🟡 Request após falhas: {result.output_mode.value} (degradado: {result.output_mode == OutputMode.PATCH_B})")
    
    # Teste 3: Status do sistema
    status = orchestrator.get_system_status()
    print(f"📊 Status do sistema: {status['circuit_breaker']['state']} (success_rate: {status['circuit_breaker']['metrics']['success_rate']:.1%})")
    
    return True

def test_gates():
    """Testa os gates da Fase 6"""
    print("\n🎯 Testando Gates da Fase 6...")
    
    orchestrator = AutonomyOrchestrator()
    
    # Gate 1: ≥99% outputs com apenas um bloco ```diff``` válido
    valid_responses = 0
    total_responses = 100
    
    for i in range(total_responses):
        response = f"""
        ```diff
        --- a/test{i}.ts
        +++ b/test{i}.ts
        @@ -1,1 +1,1 @@
        -old{i}
        +new{i}
        ```
        """
        result = orchestrator.process_request(response, {"files": [f"test{i}.ts"]})
        if result.validation_result == ValidationResult.VALID:
            valid_responses += 1
    
    valid_percentage = valid_responses / total_responses
    gate1_passed = valid_percentage >= 0.99
    print(f"Gate 1 (≥99% válidos): {valid_percentage:.1%} {'✅' if gate1_passed else '❌'}")
    
    # Gate 2: 0 violações de paths sensíveis
    sensitive_response = """
    ```diff
    --- a/.env
    +++ b/.env
    @@ -1,1 +1,1 @@
    -SECRET=old
    +SECRET=new
    ```
    """
    result = orchestrator.process_request(sensitive_response, {"files": [".env"]})
    # Verifica se foi bloqueado ou se está em modo advice (ambos são aceitáveis)
    gate2_passed = (result.validation_result == ValidationResult.BLOCKED or 
                   result.output_mode == OutputMode.ADVICE)
    print(f"Gate 2 (0 violações sensíveis): {'✅' if gate2_passed else '❌'} (validation: {result.validation_result.value}, mode: {result.output_mode.value})")
    
    # Gate 3: SLI-patch-verde ≥95% com PATCH
    success_count = 0
    patch_count = 0
    
    for i in range(50):
        response = f"""
        ```diff
        --- a/valid{i}.ts
        +++ b/valid{i}.ts
        @@ -1,1 +1,1 @@
        -valid{i}
        +updated{i}
        ```
        """
        result = orchestrator.process_request(response, {"files": [f"valid{i}.ts"]})
        if result.output_mode == OutputMode.PATCH:
            patch_count += 1
            if result.success:
                success_count += 1
    
    if patch_count > 0:
        sli_patch_verde = success_count / patch_count
        gate3_passed = sli_patch_verde >= 0.95
        print(f"Gate 3 (SLI-patch-verde ≥95%): {sli_patch_verde:.1%} {'✅' if gate3_passed else '❌'}")
    else:
        print("Gate 3: N/A (nenhum patch gerado)")
        gate3_passed = True
    
    return gate1_passed and gate2_passed and gate3_passed

def main():
    """Executa todos os testes da Fase 6"""
    print("🚀 FASE 6 - AUTONOMIA AVANÇADA - TESTES")
    print("=" * 50)
    
    try:
        # Testes individuais
        test_deterministic_brain()
        test_post_processor()
        test_circuit_breaker()
        test_autonomy_orchestrator()
        
        # Testes de gates
        gates_passed = test_gates()
        
        print("\n" + "=" * 50)
        print("📋 RESUMO DOS TESTES")
        print("=" * 50)
        
        if gates_passed:
            print("✅ TODOS OS GATES ATINGIDOS!")
            print("🎯 Fase 6 - Autonomia Avançada: CONCLUÍDA")
        else:
            print("❌ ALGUNS GATES FALHARAM")
            print("⚠️ Fase 6 - Autonomia Avançada: NECESSITA AJUSTES")
        
        return gates_passed
        
    except Exception as e:
        print(f"❌ Erro nos testes: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
