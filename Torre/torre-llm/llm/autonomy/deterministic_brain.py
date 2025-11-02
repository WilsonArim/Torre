from __future__ import annotations
import re, json, time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class OutputMode(Enum):
    PATCH = "patch"
    PATCH_B = "patch_b"
    ADVICE = "advice"

@dataclass
class DeterministicOutput:
    """Saída determinista do cérebro"""
    mode: OutputMode
    diff_content: str
    confidence: float  # 0-1
    reasoning: str
    metadata: Dict[str, Any]

class DeterministicBrain:
    """
    Cérebro determinista: garante saídas engenharia-only → 1 diff unificado → idempotente
    Objetivo: ≥99% outputs com apenas um bloco ```diff``` válido
    """
    
    def __init__(self):
        # Protocolo de saída unificado
        self.output_protocol = {
            "format": "```diff\n{content}\n```",
            "max_lines": 1200,
            "required_fields": ["diff", "reasoning", "confidence"]
        }
        
        # Perfis de patch
        self.patch_profiles = {
            OutputMode.PATCH: {
                "max_diff_size": 500,
                "confidence_threshold": 0.8,
                "quality_requirements": ["surgical", "minimal", "safe"]
            },
            OutputMode.PATCH_B: {
                "max_diff_size": 300,
                "confidence_threshold": 0.6,
                "quality_requirements": ["conservative", "safe", "review_required"]
            }
        }
        
        # Circuit breaker
        self.circuit_breaker = {
            "success_rate_threshold": 0.9,
            "window_minutes": 30,
            "degradation_threshold": 0.85
        }
        
        # Paths sensíveis (hard-deny)
        self.sensitive_paths = [
            r"\.env",
            r"\.ssh",
            r"\.pem$",
            r"id_rsa",
            r"secrets\.",
            r"\.key$",
            r"\.cert$",
            r"\.p12$",
            r"\.pfx$"
        ]
    
    def process_llm_response(self, 
                           raw_response: str,
                           context: Dict[str, Any],
                           current_mode: OutputMode = OutputMode.PATCH) -> DeterministicOutput:
        """Processa resposta da LLM de forma determinista"""
        
        # 1. Extrai e valida diff
        diff_content = self._extract_diff(raw_response)
        
        # 2. Valida paths sensíveis
        if self._contains_sensitive_paths(diff_content):
            return DeterministicOutput(
                mode=OutputMode.ADVICE,
                diff_content="",
                confidence=0.0,
                reasoning="BLOCKED: Tentativa de modificar paths sensíveis",
                metadata={"blocked": True, "reason": "sensitive_paths"}
            )
        
        # 3. Valida tamanho do diff
        if self._exceeds_size_limit(diff_content, current_mode):
            diff_content = self._auto_shrink_diff(diff_content, current_mode)
        
        # 4. Determina confiança
        confidence = self._calculate_confidence(diff_content, context)
        
        # 5. Determina modo de saída
        output_mode = self._determine_output_mode(confidence, current_mode)
        
        # 6. Gera reasoning
        reasoning = self._generate_reasoning(diff_content, confidence, output_mode)
        
        return DeterministicOutput(
            mode=output_mode,
            diff_content=diff_content,
            confidence=confidence,
            reasoning=reasoning,
            metadata={
                "original_size": len(raw_response),
                "processed_size": len(diff_content),
                "mode": output_mode.value,
                "timestamp": time.time()
            }
        )
    
    def _extract_diff(self, raw_response: str) -> str:
        """Extrai diff unificado da resposta"""
        
        # Procura por blocos ```diff
        diff_pattern = r"```diff\s*\n(.*?)\n```"
        matches = re.findall(diff_pattern, raw_response, re.DOTALL)
        
        if not matches:
            # Fallback: procura por blocos ``` sem especificador
            fallback_pattern = r"```\s*\n(.*?)\n```"
            matches = re.findall(fallback_pattern, raw_response, re.DOTALL)
        
        if not matches:
            # Fallback: procura por linhas que começam com + ou -
            diff_lines = []
            lines = raw_response.split('\n')
            for line in lines:
                if line.startswith(('+', '-', ' ')):
                    diff_lines.append(line)
            
            if diff_lines:
                return '\n'.join(diff_lines)
            
            return ""
        
        # Retorna o primeiro diff encontrado (unificado)
        return matches[0].strip()
    
    def _contains_sensitive_paths(self, diff_content: str) -> bool:
        """Verifica se o diff contém paths sensíveis"""
        for pattern in self.sensitive_paths:
            if re.search(pattern, diff_content, re.IGNORECASE):
                return True
        return False
    
    def _exceeds_size_limit(self, diff_content: str, mode: OutputMode) -> bool:
        """Verifica se o diff excede o limite de tamanho"""
        max_lines = self.patch_profiles[mode]["max_diff_size"]
        actual_lines = len(diff_content.split('\n'))
        return actual_lines > max_lines
    
    def _auto_shrink_diff(self, diff_content: str, mode: OutputMode) -> str:
        """Reduz automaticamente o tamanho do diff de forma segura"""
        max_lines = self.patch_profiles[mode]["max_diff_size"]
        lines = diff_content.split('\n')
        
        if len(lines) <= max_lines:
            return diff_content
        
        # Estratégia: mantém o início e fim, remove o meio
        keep_lines = max_lines // 2
        
        # Mantém as primeiras linhas
        first_part = lines[:keep_lines]
        
        # Adiciona indicador de truncamento
        truncation_indicator = [f"# ... (truncated {len(lines) - max_lines} lines) ..."]
        
        # Mantém as últimas linhas
        last_part = lines[-(keep_lines - 1):]
        
        return '\n'.join(first_part + truncation_indicator + last_part)
    
    def _calculate_confidence(self, diff_content: str, context: Dict[str, Any]) -> float:
        """Calcula confiança da saída"""
        
        if not diff_content:
            return 0.0
        
        confidence = 0.5  # Base
        
        # Fatores de confiança
        factors = {
            "diff_validity": self._validate_diff_structure(diff_content),
            "context_alignment": self._check_context_alignment(diff_content, context),
            "safety_score": self._calculate_safety_score(diff_content),
            "complexity_score": self._calculate_complexity_score(diff_content)
        }
        
        # Pondera fatores
        weights = {
            "diff_validity": 0.4,
            "context_alignment": 0.3,
            "safety_score": 0.2,
            "complexity_score": 0.1
        }
        
        for factor, value in factors.items():
            confidence += value * weights[factor]
        
        return min(1.0, confidence)
    
    def _validate_diff_structure(self, diff_content: str) -> float:
        """Valida estrutura do diff"""
        lines = diff_content.split('\n')
        
        if not lines:
            return 0.0
        
        # Verifica se tem linhas válidas de diff
        valid_lines = 0
        total_lines = len(lines)
        
        for line in lines:
            if line.startswith(('+', '-', ' ')) or line.startswith('@@'):
                valid_lines += 1
        
        return valid_lines / max(total_lines, 1)
    
    def _check_context_alignment(self, diff_content: str, context: Dict[str, Any]) -> float:
        """Verifica alinhamento com o contexto"""
        if not context:
            return 0.5
        
        # Verifica se os arquivos mencionados no diff estão no contexto
        files_in_context = context.get("files", [])
        files_in_diff = self._extract_files_from_diff(diff_content)
        
        if not files_in_diff:
            return 0.5
        
        aligned_files = 0
        for file in files_in_diff:
            if any(file in ctx_file for ctx_file in files_in_context):
                aligned_files += 1
        
        return aligned_files / len(files_in_diff)
    
    def _extract_files_from_diff(self, diff_content: str) -> List[str]:
        """Extrai nomes de arquivos do diff"""
        file_pattern = r"^\+\+\+ b/(.+)$|^--- a/(.+)$"
        matches = re.findall(file_pattern, diff_content, re.MULTILINE)
        
        files = []
        for match in matches:
            file_path = match[0] or match[1]
            if file_path:
                files.append(file_path)
        
        return list(set(files))
    
    def _calculate_safety_score(self, diff_content: str) -> float:
        """Calcula score de segurança"""
        safety_score = 1.0
        
        # Penaliza operações perigosas
        dangerous_patterns = [
            r"rm\s+-rf",
            r"del\s+/s",
            r"format\s+c:",
            r"dd\s+if=",
            r"eval\(",
            r"exec\(",
            r"system\("
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, diff_content, re.IGNORECASE):
                safety_score -= 0.3
        
        return max(0.0, safety_score)
    
    def _calculate_complexity_score(self, diff_content: str) -> float:
        """Calcula score de complexidade (menor = melhor)"""
        lines = diff_content.split('\n')
        
        if not lines:
            return 1.0
        
        # Conta mudanças complexas
        complex_changes = 0
        for line in lines:
            if line.startswith('+') and len(line) > 100:
                complex_changes += 1
            elif line.startswith('-') and len(line) > 100:
                complex_changes += 1
        
        # Score baseado na proporção de mudanças complexas
        complexity_ratio = complex_changes / len(lines)
        return max(0.0, 1.0 - complexity_ratio)
    
    def _determine_output_mode(self, confidence: float, current_mode: OutputMode) -> OutputMode:
        """Determina modo de saída baseado na confiança"""
        
        threshold = self.patch_profiles[current_mode]["confidence_threshold"]
        
        if confidence >= threshold:
            return current_mode
        elif confidence >= 0.3:
            return OutputMode.PATCH_B
        else:
            return OutputMode.ADVICE
    
    def _generate_reasoning(self, diff_content: str, confidence: float, mode: OutputMode) -> str:
        """Gera reasoning para a saída"""
        
        if mode == OutputMode.ADVICE:
            return "ADVICE MODE: Confiança insuficiente para aplicar patch automaticamente"
        
        reasoning_parts = []
        
        # Adiciona informações sobre o diff
        if diff_content:
            lines = diff_content.split('\n')
            added_lines = len([l for l in lines if l.startswith('+')])
            removed_lines = len([l for l in lines if l.startswith('-')])
            
            reasoning_parts.append(f"Patch: +{added_lines} -{removed_lines} linhas")
        
        # Adiciona confiança
        reasoning_parts.append(f"Confiança: {confidence:.1%}")
        
        # Adiciona modo
        reasoning_parts.append(f"Modo: {mode.value.upper()}")
        
        # Adiciona qualidade
        if mode == OutputMode.PATCH:
            reasoning_parts.append("Qualidade: Alta (aplicação automática)")
        elif mode == OutputMode.PATCH_B:
            reasoning_parts.append("Qualidade: Conservadora (revisão recomendada)")
        
        return " | ".join(reasoning_parts)
    
    def should_degrade_to_patch_b(self, recent_success_rate: float) -> bool:
        """Decide se deve degradar para PATCH_B"""
        return recent_success_rate < self.circuit_breaker["degradation_threshold"]
    
    def should_switch_to_advice_mode(self, recent_success_rate: float) -> bool:
        """Decide se deve mudar para ADVICE mode"""
        return recent_success_rate < self.circuit_breaker["success_rate_threshold"]
    
    def generate_engineer_only_prompt(self, context: Dict[str, Any]) -> str:
        """Gera prompt engenharia-only refinado"""
        
        prompt = """# ENGINEER-ONLY PATCH GENERATION

## CONTEXT
{context_summary}

## TASK
Generate a minimal, surgical patch to fix the identified issues.

## CONSTRAINTS
- ONE unified ```diff``` block only
- Maximum 1200 lines
- NO sensitive paths (.env, .ssh, *.pem, id_rsa, secrets.*)
- Surgical changes only
- NO prose, NO explanations outside the diff

## OUTPUT FORMAT
```diff
{minimal_patch_here}
```

## VALIDATION
- Diff must be valid git format
- Only one diff block
- No sensitive file modifications
- Minimal and safe changes only

Generate the patch:"""
        
        # Substitui placeholders
        context_summary = self._summarize_context(context)
        prompt = prompt.replace("{context_summary}", context_summary)
        
        return prompt
    
    def _summarize_context(self, context: Dict[str, Any]) -> str:
        """Resume o contexto para o prompt"""
        summary_parts = []
        
        if "error_logs" in context:
            summary_parts.append(f"Errors: {len(context['error_logs'])} issues")
        
        if "files" in context:
            summary_parts.append(f"Files: {len(context['files'])} affected")
        
        if "priority" in context:
            summary_parts.append(f"Priority: {context['priority']}")
        
        return " | ".join(summary_parts) if summary_parts else "No specific context provided"
