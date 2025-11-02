from __future__ import annotations
import time, json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from .deterministic_brain import DeterministicBrain, DeterministicOutput, OutputMode
from .post_processor import PostProcessor, PostProcessResult, ValidationResult
from .circuit_breaker import CircuitBreaker, CircuitState

@dataclass
class AutonomyResult:
    """Resultado da orquestração de autonomia"""
    success: bool
    output_mode: OutputMode
    diff_content: str
    confidence: float
    reasoning: str
    validation_result: ValidationResult
    circuit_state: CircuitState
    metadata: Dict[str, Any]

class AutonomyOrchestrator:
    """
    Orquestrador de Autonomia: coordena cérebro determinista + pós-processamento + circuit breaker
    Objetivo: garantir ≥99% outputs com apenas um bloco ```diff``` válido
    """
    
    def __init__(self):
        self.deterministic_brain = DeterministicBrain()
        self.post_processor = PostProcessor()
        self.circuit_breaker = CircuitBreaker()
        
        # Configurações de autonomia
        self.autonomy_config = {
            "min_confidence": 0.6,
            "max_retries": 3,
            "retry_delay": 1.0,  # segundos
            "enable_auto_degradation": True,
            "enable_advice_mode": True
        }
    
    def process_request(self, 
                       raw_llm_response: str,
                       context: Dict[str, Any],
                       force_mode: Optional[OutputMode] = None) -> AutonomyResult:
        """Processa um request completo através do pipeline de autonomia"""
        
        start_time = time.time()
        
        # 1. Verifica circuit breaker
        if not self.circuit_breaker.should_allow_request():
            return AutonomyResult(
                success=False,
                output_mode=OutputMode.ADVICE,
                diff_content="",
                confidence=0.0,
                reasoning="Circuit breaker OPEN - request blocked",
                validation_result=ValidationResult.BLOCKED,
                circuit_state=self.circuit_breaker.state,
                metadata={"blocked": True, "reason": "circuit_breaker_open"}
            )
        
        # 2. Determina modo de operação
        current_mode = self._determine_operation_mode(force_mode)
        
        # 3. Processa com cérebro determinista
        brain_result = self.deterministic_brain.process_llm_response(
            raw_llm_response, context, current_mode
        )
        
        # 4. Pós-processamento
        post_result = self.post_processor.process_output(
            brain_result.diff_content, context
        )
        
        # 5. Validação final
        final_validation = self._validate_final_output(brain_result, post_result)
        
        # 6. Atualiza circuit breaker
        success = (final_validation == ValidationResult.VALID and 
                  brain_result.confidence >= self.autonomy_config["min_confidence"])
        
        self.circuit_breaker.record_request(success, {
            "mode": brain_result.mode.value,
            "confidence": brain_result.confidence,
            "validation": post_result.validation.value,
            "processing_time": time.time() - start_time
        })
        
        # 7. Determina output final
        final_output_mode = self._determine_final_output_mode(brain_result, post_result, success)
        
        return AutonomyResult(
            success=success,
            output_mode=final_output_mode,
            diff_content=post_result.cleaned_content,
            confidence=brain_result.confidence,
            reasoning=brain_result.reasoning,
            validation_result=post_result.validation,
            circuit_state=self.circuit_breaker.state,
            metadata={
                "processing_time": time.time() - start_time,
                "brain_metadata": brain_result.metadata,
                "post_metadata": post_result.metadata,
                "violations": post_result.violations
            }
        )
    
    def _determine_operation_mode(self, force_mode: Optional[OutputMode]) -> OutputMode:
        """Determina modo de operação baseado no estado do sistema"""
        
        if force_mode:
            return force_mode
        
        # Verifica se deve degradar
        if self.circuit_breaker.should_degrade_to_patch_b():
            return OutputMode.PATCH_B
        
        # Verifica se deve ir para advice mode
        if self.circuit_breaker.should_switch_to_advice_mode():
            return OutputMode.ADVICE
        
        # Modo normal
        return OutputMode.PATCH
    
    def _validate_final_output(self, 
                              brain_result: DeterministicOutput,
                              post_result: PostProcessResult) -> ValidationResult:
        """Validação final do output"""
        
        # Se o cérebro bloqueou, é bloqueado
        if brain_result.mode == OutputMode.ADVICE and brain_result.confidence == 0.0:
            return ValidationResult.BLOCKED
        
        # Se o pós-processamento bloqueou, é bloqueado
        if post_result.validation == ValidationResult.BLOCKED:
            return ValidationResult.BLOCKED
        
        # Se tem violações de segurança, é bloqueado
        if any("sensitive" in v.lower() or "dangerous" in v.lower() for v in post_result.violations):
            return ValidationResult.BLOCKED
        
        # Se não tem diff válido, é inválido
        if not brain_result.diff_content.strip():
            return ValidationResult.INVALID
        
        # Se confiança muito baixa, é inválido
        if brain_result.confidence < 0.3:
            return ValidationResult.INVALID
        
        return post_result.validation
    
    def _determine_final_output_mode(self,
                                   brain_result: DeterministicOutput,
                                   post_result: PostProcessResult,
                                   success: bool) -> OutputMode:
        """Determina modo de output final"""
        
        # Se falhou completamente, vai para advice
        if not success:
            return OutputMode.ADVICE
        
        # Se foi bloqueado, vai para advice
        if post_result.validation == ValidationResult.BLOCKED:
            return OutputMode.ADVICE
        
        # Se confiança baixa, degrada
        if brain_result.confidence < 0.6:
            return OutputMode.PATCH_B
        
        # Se tem violações, degrada
        if post_result.violations:
            return OutputMode.PATCH_B
        
        # Modo normal
        return brain_result.mode
    
    def generate_engineer_only_prompt(self, context: Dict[str, Any]) -> str:
        """Gera prompt engenharia-only refinado"""
        return self.deterministic_brain.generate_engineer_only_prompt(context)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Retorna status completo do sistema"""
        
        circuit_metrics = self.circuit_breaker.get_metrics()
        current_config = self.circuit_breaker.get_current_config()
        
        return {
            "circuit_breaker": {
                "state": self.circuit_breaker.state.value,
                "metrics": {
                    "success_count": circuit_metrics.success_count,
                    "failure_count": circuit_metrics.failure_count,
                    "total_requests": circuit_metrics.total_requests,
                    "success_rate": (circuit_metrics.success_count / 
                                   max(circuit_metrics.total_requests, 1))
                }
            },
            "current_config": current_config,
            "autonomy_config": self.autonomy_config,
            "should_degrade": self.circuit_breaker.should_degrade_to_patch_b(),
            "should_advice": self.circuit_breaker.should_switch_to_advice_mode()
        }
    
    def generate_autonomy_report(self, result: AutonomyResult) -> str:
        """Gera relatório completo de autonomia"""
        
        report = ["# Autonomy Orchestrator Report\n"]
        
        # Status geral
        status_emoji = "✅" if result.success else "❌"
        report.append(f"## Status: {status_emoji} {'SUCCESS' if result.success else 'FAILED'}")
        report.append("")
        
        # Modo de operação
        mode_emoji = {
            OutputMode.PATCH: "🟢",
            OutputMode.PATCH_B: "🟡",
            OutputMode.ADVICE: "🔴"
        }
        
        report.append(f"## Modo de Operação: {mode_emoji[result.output_mode]} {result.output_mode.value.upper()}")
        report.append("")
        
        # Métricas de qualidade
        report.append("## Métricas de Qualidade")
        report.append(f"- **Confiança**: {result.confidence:.1%}")
        report.append(f"- **Validação**: {result.validation_result.value}")
        report.append(f"- **Circuit State**: {result.circuit_state.value}")
        report.append(f"- **Tempo de processamento**: {result.metadata['processing_time']:.2f}s")
        report.append("")
        
        # Reasoning
        report.append("## Reasoning")
        report.append(result.reasoning)
        report.append("")
        
        # Violações (se houver)
        if result.metadata.get("violations"):
            report.append("## Violações Detectadas")
            for violation in result.metadata["violations"]:
                report.append(f"- ❌ {violation}")
            report.append("")
        
        # Recomendações
        report.append("## Recomendações")
        if result.success:
            if result.output_mode == OutputMode.PATCH:
                report.append("- ✅ **Aplicar**: Patch de alta qualidade, aplicação automática segura")
            elif result.output_mode == OutputMode.PATCH_B:
                report.append("- ⚠️ **Revisar**: Patch conservador, revisão recomendada antes da aplicação")
            else:
                report.append("- 🔴 **Aconselhar**: Modo advice - não aplicar automaticamente")
        else:
            report.append("- 🚫 **Bloqueado**: Não aplicar - falhas detectadas no processamento")
        
        return "\n".join(report)
    
    def reset_system(self) -> None:
        """Reseta o sistema de autonomia"""
        self.circuit_breaker.reset()
    
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """Atualiza configurações de autonomia"""
        self.autonomy_config.update(new_config)
    
    def export_state(self) -> Dict[str, Any]:
        """Exporta estado completo do sistema"""
        return {
            "autonomy_config": self.autonomy_config,
            "circuit_breaker_state": self.circuit_breaker.export_state(),
            "timestamp": time.time()
        }
    
    def import_state(self, state_data: Dict[str, Any]) -> None:
        """Importa estado do sistema"""
        if "autonomy_config" in state_data:
            self.autonomy_config.update(state_data["autonomy_config"])
        
        if "circuit_breaker_state" in state_data:
            self.circuit_breaker.import_state(state_data["circuit_breaker_state"])
