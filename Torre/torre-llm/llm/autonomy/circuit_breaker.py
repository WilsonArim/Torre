from __future__ import annotations
import time, json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
from collections import deque

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Blocked
    HALF_OPEN = "half_open"  # Testing recovery

@dataclass
class CircuitMetrics:
    """Métricas do circuit breaker"""
    success_count: int
    failure_count: int
    total_requests: int
    last_failure_time: float
    last_success_time: float
    current_state: CircuitState

class CircuitBreaker:
    """
    Circuit Breaker: degradação automática de qualidade
    Objetivo: proteger contra falhas em cascata e degradar graciosamente
    """
    
    def __init__(self, 
                 failure_threshold: float = 0.1,
                 recovery_timeout: int = 300,
                 success_threshold: int = 5,
                 window_size: int = 100):
        
        # Configurações
        self.failure_threshold = failure_threshold  # 10% falhas = abrir
        self.recovery_timeout = recovery_timeout    # 5 minutos para tentar recuperar
        self.success_threshold = success_threshold  # 5 sucessos para fechar
        self.window_size = window_size              # Janela de 100 requests
        
        # Estado atual
        self.state = CircuitState.CLOSED
        self.last_state_change = time.time()
        
        # Métricas
        self.request_history = deque(maxlen=window_size)
        self.success_count = 0
        self.failure_count = 0
        
        # Configurações de degradação
        self.degradation_configs = {
            "patch": {
                "normal": {
                    "max_diff_size": 500,
                    "confidence_threshold": 0.8,
                    "quality_level": "high"
                },
                "degraded": {
                    "max_diff_size": 300,
                    "confidence_threshold": 0.6,
                    "quality_level": "conservative"
                },
                "emergency": {
                    "max_diff_size": 100,
                    "confidence_threshold": 0.4,
                    "quality_level": "minimal"
                }
            }
        }
    
    def record_request(self, success: bool, metadata: Dict[str, Any] = None) -> None:
        """Regista um request e atualiza métricas"""
        
        timestamp = time.time()
        request_data = {
            "success": success,
            "timestamp": timestamp,
            "metadata": metadata or {}
        }
        
        self.request_history.append(request_data)
        
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1
        
        # Atualiza estado do circuit breaker
        self._update_state()
    
    def _update_state(self) -> None:
        """Atualiza estado do circuit breaker"""
        
        current_time = time.time()
        total_requests = len(self.request_history)
        
        if total_requests == 0:
            return
        
        # Calcula taxa de falha
        recent_failures = sum(1 for req in self.request_history if not req["success"])
        failure_rate = recent_failures / total_requests
        
        # Transições de estado
        if self.state == CircuitState.CLOSED:
            if failure_rate >= self.failure_threshold:
                self._open_circuit()
        
        elif self.state == CircuitState.OPEN:
            if current_time - self.last_state_change >= self.recovery_timeout:
                self._half_open_circuit()
        
        elif self.state == CircuitState.HALF_OPEN:
            recent_successes = sum(1 for req in list(self.request_history)[-self.success_threshold:] 
                                 if req["success"])
            if recent_successes >= self.success_threshold:
                self._close_circuit()
            elif failure_rate >= self.failure_threshold:
                self._open_circuit()
    
    def _open_circuit(self) -> None:
        """Abre o circuit breaker"""
        self.state = CircuitState.OPEN
        self.last_state_change = time.time()
    
    def _half_open_circuit(self) -> None:
        """Coloca o circuit breaker em half-open"""
        self.state = CircuitState.HALF_OPEN
        self.last_state_change = time.time()
    
    def _close_circuit(self) -> None:
        """Fecha o circuit breaker"""
        self.state = CircuitState.CLOSED
        self.last_state_change = time.time()
    
    def should_allow_request(self) -> bool:
        """Verifica se deve permitir o request"""
        return self.state != CircuitState.OPEN
    
    def get_current_config(self, config_type: str = "patch") -> Dict[str, Any]:
        """Retorna configuração atual baseada no estado"""
        
        if self.state == CircuitState.CLOSED:
            return self.degradation_configs[config_type]["normal"]
        elif self.state == CircuitState.HALF_OPEN:
            return self.degradation_configs[config_type]["degraded"]
        else:  # OPEN
            return self.degradation_configs[config_type]["emergency"]
    
    def get_metrics(self) -> CircuitMetrics:
        """Retorna métricas atuais"""
        
        total_requests = len(self.request_history)
        recent_successes = sum(1 for req in self.request_history if req["success"])
        recent_failures = total_requests - recent_successes
        
        last_failure = None
        last_success = None
        
        for req in reversed(self.request_history):
            if req["success"] and last_success is None:
                last_success = req["timestamp"]
            elif not req["success"] and last_failure is None:
                last_failure = req["timestamp"]
            
            if last_success is not None and last_failure is not None:
                break
        
        return CircuitMetrics(
            success_count=recent_successes,
            failure_count=recent_failures,
            total_requests=total_requests,
            last_failure_time=last_failure or 0,
            last_success_time=last_success or 0,
            current_state=self.state
        )
    
    def should_degrade_to_patch_b(self) -> bool:
        """Decide se deve degradar para PATCH_B"""
        metrics = self.get_metrics()
        
        if metrics.total_requests < 10:
            return False
        
        failure_rate = metrics.failure_count / metrics.total_requests
        return failure_rate >= 0.15  # 15% falhas = degradar
    
    def should_switch_to_advice_mode(self) -> bool:
        """Decide se deve mudar para ADVICE mode"""
        return self.state == CircuitState.OPEN
    
    def generate_status_report(self) -> str:
        """Gera relatório de status do circuit breaker"""
        
        metrics = self.get_metrics()
        
        report = ["# Circuit Breaker Status Report\n"]
        
        # Estado atual
        state_emoji = {
            CircuitState.CLOSED: "🟢",
            CircuitState.HALF_OPEN: "🟡",
            CircuitState.OPEN: "🔴"
        }
        
        report.append(f"## Estado: {state_emoji[self.state]} {self.state.value.upper()}")
        report.append(f"**Última mudança**: {time.strftime('%H:%M:%S', time.localtime(self.last_state_change))}")
        report.append("")
        
        # Métricas
        report.append("## Métricas")
        report.append(f"- **Total de requests**: {metrics.total_requests}")
        report.append(f"- **Sucessos**: {metrics.success_count}")
        report.append(f"- **Falhas**: {metrics.failure_count}")
        
        if metrics.total_requests > 0:
            success_rate = metrics.success_count / metrics.total_requests
            failure_rate = metrics.failure_count / metrics.total_requests
            report.append(f"- **Taxa de sucesso**: {success_rate:.1%}")
            report.append(f"- **Taxa de falha**: {failure_rate:.1%}")
        
        report.append("")
        
        # Configuração atual
        current_config = self.get_current_config()
        report.append("## Configuração Atual")
        report.append(f"- **Qualidade**: {current_config['quality_level']}")
        report.append(f"- **Tamanho máximo diff**: {current_config['max_diff_size']} linhas")
        report.append(f"- **Threshold confiança**: {current_config['confidence_threshold']:.1%}")
        report.append("")
        
        # Recomendações
        report.append("## Recomendações")
        if self.state == CircuitState.CLOSED:
            report.append("- ✅ **Normal**: Operação em modo normal")
        elif self.state == CircuitState.HALF_OPEN:
            report.append("- ⚠️ **Degradado**: Testando recuperação - monitorizar de perto")
        else:
            report.append("- 🚫 **Bloqueado**: Circuit breaker aberto - aguardar recuperação")
        
        return "\n".join(report)
    
    def reset(self) -> None:
        """Reseta o circuit breaker"""
        self.state = CircuitState.CLOSED
        self.last_state_change = time.time()
        self.request_history.clear()
        self.success_count = 0
        self.failure_count = 0
    
    def export_state(self) -> Dict[str, Any]:
        """Exporta estado para persistência"""
        return {
            "state": self.state.value,
            "last_state_change": self.last_state_change,
            "request_history": list(self.request_history),
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "config": {
                "failure_threshold": self.failure_threshold,
                "recovery_timeout": self.recovery_timeout,
                "success_threshold": self.success_threshold,
                "window_size": self.window_size
            }
        }
    
    def import_state(self, state_data: Dict[str, Any]) -> None:
        """Importa estado de persistência"""
        self.state = CircuitState(state_data["state"])
        self.last_state_change = state_data["last_state_change"]
        self.request_history = deque(state_data["request_history"], maxlen=self.window_size)
        self.success_count = state_data["success_count"]
        self.failure_count = state_data["failure_count"]
