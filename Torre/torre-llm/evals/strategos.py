from __future__ import annotations
import re, time
from typing import Dict, Any, List, Tuple
from enum import Enum

class ErrorType(Enum):
    BUILD = "build"
    TYPES = "types"
    TESTS = "tests"
    STYLE = "style"
    UNKNOWN = "unknown"

class Strategos:
    """
    Sistema de estratégia básica para Fase 1.2
    Objetivo: Ordem de ataque = build→types→tests→style ajustada por risco
    """
    
    def __init__(self):
        self.error_patterns = {
            ErrorType.BUILD: [
                r"ModuleNotFoundError",
                r"ImportError",
                r"SyntaxError",
                r"ReferenceError",
                r"cannot find module",
                r"module not found",
                r"build failed",
                r"compilation error"
            ],
            ErrorType.TYPES: [
                r"TypeError",
                r"TS\d+",
                r"type.*error",
                r"cannot find name",
                r"property.*missing",
                r"type.*mismatch",
                r"interface.*not.*implemented"
            ],
            ErrorType.TESTS: [
                r"AssertionError",
                r"test.*failed",
                r"expect.*to.*be",
                r"coverage.*drop",
                r"test.*timeout",
                r"test.*error"
            ],
            ErrorType.STYLE: [
                r"ESLint",
                r"lint.*error",
                r"no-unused-vars",
                r"prefer-const",
                r"no-console",
                r"style.*error"
            ]
        }
        
        self.risk_scores = {
            ErrorType.BUILD: 10,    # Mais crítico
            ErrorType.TYPES: 8,
            ErrorType.TESTS: 6,
            ErrorType.STYLE: 4      # Menos crítico
        }
    
    def analyze_logs(self, logs: Dict[str, str]) -> List[Tuple[ErrorType, str, int]]:
        """Analisa logs e retorna erros ordenados por risco"""
        errors = []
        
        for log_type, log_content in logs.items():
            for error_type, patterns in self.error_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, log_content, re.IGNORECASE):
                        risk_score = self.risk_scores[error_type]
                        errors.append((error_type, log_content, risk_score))
                        break  # Só conta uma vez por tipo de erro
        
        # Ordena por risco (maior primeiro)
        errors.sort(key=lambda x: x[2], reverse=True)
        return errors
    
    def generate_attack_plan(self, logs: Dict[str, str]) -> Dict[str, Any]:
        """Gera plano de ataque baseado nos logs"""
        errors = self.analyze_logs(logs)
        
        if not errors:
            return {
                "strategy": "no_errors",
                "priority_order": [],
                "risk_assessment": "low",
                "estimated_time": 0
            }
        
        # Agrupa erros por tipo
        error_groups = {}
        for error_type, content, risk in errors:
            if error_type not in error_groups:
                error_groups[error_type] = []
            error_groups[error_type].append((content, risk))
        
        # Define ordem de ataque baseada em risco
        priority_order = []
        total_risk = 0
        
        for error_type in [ErrorType.BUILD, ErrorType.TYPES, ErrorType.TESTS, ErrorType.STYLE]:
            if error_type in error_groups:
                priority_order.append({
                    "type": error_type.value,
                    "count": len(error_groups[error_type]),
                    "risk_score": self.risk_scores[error_type],
                    "examples": [content[:100] for content, _ in error_groups[error_type][:3]]
                })
                total_risk += self.risk_scores[error_type] * len(error_groups[error_type])
        
        # Calcula tempo estimado baseado no risco
        estimated_time = total_risk * 2  # 2 minutos por ponto de risco
        
        return {
            "strategy": "risk_based_attack",
            "priority_order": priority_order,
            "risk_assessment": self._assess_risk_level(total_risk),
            "estimated_time": estimated_time,
            "total_errors": len(errors),
            "error_distribution": {et.value: len(eg) for et, eg in error_groups.items()}
        }
    
    def _assess_risk_level(self, total_risk: int) -> str:
        """Avalia nível de risco"""
        if total_risk >= 50:
            return "critical"
        elif total_risk >= 30:
            return "high"
        elif total_risk >= 15:
            return "medium"
        else:
            return "low"
    
    def should_apply_patch(self, logs: Dict[str, str], patch_size: int) -> bool:
        """Decide se deve aplicar o patch baseado em risco"""
        errors = self.analyze_logs(logs)
        total_risk = sum(risk for _, _, risk in errors)
        
        # Se risco crítico, aplica sempre
        if total_risk >= 50:
            return True
        
        # Se patch muito grande e risco baixo, não aplica
        if patch_size > 50 and total_risk < 10:
            return False
        
        # Se risco médio-alto, aplica
        if total_risk >= 15:
            return True
        
        # Caso contrário, não aplica
        return False
    
    def generate_report(self, attack_plan: Dict[str, Any]) -> str:
        """Gera relatório da estratégia"""
        if attack_plan["strategy"] == "no_errors":
            return """
# Relatório de Estratégia - Sem Erros

✅ **Status**: Nenhum erro detectado
✅ **Ação**: Nenhuma ação necessária
✅ **Risco**: Baixo
"""
        
        report = f"""
# Relatório de Estratégia - Plano de Ataque

## Resumo
- **Estratégia**: {attack_plan['strategy']}
- **Total de Erros**: {attack_plan['total_errors']}
- **Nível de Risco**: {attack_plan['risk_assessment']}
- **Tempo Estimado**: {attack_plan['estimated_time']} minutos

## Ordem de Prioridade
"""
        
        for i, priority in enumerate(attack_plan['priority_order'], 1):
            report += f"""
### {i}. {priority['type'].upper()} (Risco: {priority['risk_score']})
- **Quantidade**: {priority['count']} erros
- **Exemplos**: {', '.join(priority['examples'])}
"""
        
        report += f"""
## Distribuição de Erros
"""
        for error_type, count in attack_plan['error_distribution'].items():
            report += f"- **{error_type}**: {count} erros\n"
        
        return report
