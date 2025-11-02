from __future__ import annotations
import re, ast
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from .episodic_store import EpisodicStore, Lesson

class LessonAction(Enum):
    NUDGE_PROMPT = "nudge_prompt"
    PRE_CODEMOD = "pre_codemod"
    ROUTING = "routing"

@dataclass
class LessonApplication:
    """Aplicação de uma lição"""
    lesson_id: str
    action: LessonAction
    tactic_applied: str
    confidence: float
    evidence: str
    success_prediction: float

@dataclass
class LessonResult:
    """Resultado da aplicação de lições"""
    applied_lessons: List[LessonApplication]
    modified_prompt: Optional[str]
    pre_codemod_diff: Optional[str]
    routing_suggestion: Optional[str]
    total_confidence: float

class LessonEngine:
    """
    Lesson Engine: aplica lições aprendidas
    Objetivo: match de lições por assinatura + contexto e aplicação de ações
    """
    
    def __init__(self, episodic_store: EpisodicStore):
        self.episodic_store = episodic_store
        
        # Configurações de aplicação
        self.config = {
            "min_confidence": 0.6,
            "max_lessons_per_request": 3,
            "enable_auto_apply": True,
            "enable_pre_codemod": True,
            "enable_routing": True
        }
        
        # Padrões de erro conhecidos
        self.error_patterns = {
            "TS2304": r"TS2304.*Cannot find name",
            "TS2307": r"TS2307.*Cannot find module",
            "TS2322": r"TS2322.*Type.*is not assignable",
            "TS2339": r"TS2339.*Property.*does not exist",
            "ESLint": r"ESLint.*error",
            "ImportError": r"ImportError.*No module named",
            "ModuleNotFoundError": r"ModuleNotFoundError.*No module named",
            "SyntaxError": r"SyntaxError.*invalid syntax"
        }
        
        # Táticas conhecidas
        self.known_tactics = {
            "add_import": "Adicionar import faltante",
            "fix_type": "Corrigir tipo TypeScript",
            "add_property": "Adicionar propriedade faltante",
            "fix_syntax": "Corrigir sintaxe",
            "update_dependency": "Atualizar dependência",
            "use_alternative": "Usar alternativa compatível"
        }
    
    def extract_error_signature(self, error_logs: List[str]) -> str:
        """Extrai assinatura de erro dos logs"""
        if not error_logs:
            return "unknown_error"
        
        # Procura por padrões conhecidos
        for pattern_name, pattern in self.error_patterns.items():
            for log in error_logs:
                if re.search(pattern, log, re.IGNORECASE):
                    # Adiciona contexto específico
                    context = self._extract_error_context(log)
                    return f"{pattern_name}:{context}"
        
        # Fallback: usa o primeiro erro
        first_error = error_logs[0]
        # Simplifica o erro
        simplified = re.sub(r'[\/\\][^\s\/\\]+\.(ts|js|py)', '/file.ext', first_error)
        simplified = re.sub(r'[A-Za-z0-9]{32,}', '[REDACTED]', simplified)
        return f"custom:{hash(simplified) % 10000}"
    
    def _extract_error_context(self, error_log: str) -> str:
        """Extrai contexto específico do erro"""
        # Procura por nomes de arquivo/componente
        file_match = re.search(r'([^\/\\]+)\.(ts|js|tsx|jsx|py)', error_log)
        if file_match:
            return file_match.group(1)
        
        # Procura por nomes de função/classe
        func_match = re.search(r'(?:function|class|const)\s+(\w+)', error_log)
        if func_match:
            return func_match.group(1)
        
        return "unknown"
    
    def find_applicable_lessons(self, 
                               error_signature: str,
                               context: Dict[str, Any]) -> List[Lesson]:
        """Encontra lições aplicáveis para um erro"""
        
        # Busca lições relevantes
        lessons = self.episodic_store.get_relevant_lessons(
            error_signature, context, self.config["max_lessons_per_request"]
        )
        
        # Filtra por confiança mínima
        applicable_lessons = [
            lesson for lesson in lessons 
            if lesson.confidence >= self.config["min_confidence"]
        ]
        
        return applicable_lessons
    
    def apply_lessons(self, 
                     lessons: List[Lesson],
                     original_prompt: str,
                     context: Dict[str, Any]) -> LessonResult:
        """Aplica lições encontradas"""
        
        applied_lessons = []
        modified_prompt = original_prompt
        pre_codemod_diff = None
        routing_suggestion = None
        total_confidence = 0.0
        
        for lesson in lessons:
            application = self._apply_single_lesson(lesson, context)
            applied_lessons.append(application)
            
            # Aplica ações baseadas no tipo de tática
            if application.action == LessonAction.NUDGE_PROMPT:
                modified_prompt = self._apply_prompt_nudge(
                    modified_prompt, lesson, application
                )
            elif application.action == LessonAction.PRE_CODEMOD:
                pre_codemod_diff = self._apply_pre_codemod(
                    lesson, application, context
                )
            elif application.action == LessonAction.ROUTING:
                routing_suggestion = self._apply_routing_suggestion(
                    lesson, application
                )
            
            total_confidence += application.confidence
        
        if applied_lessons:
            total_confidence /= len(applied_lessons)
        
        return LessonResult(
            applied_lessons=applied_lessons,
            modified_prompt=modified_prompt,
            pre_codemod_diff=pre_codemod_diff,
            routing_suggestion=routing_suggestion,
            total_confidence=total_confidence
        )
    
    def _apply_single_lesson(self, lesson: Lesson, context: Dict[str, Any]) -> LessonApplication:
        """Aplica uma lição individual"""
        
        # Determina ação baseada na tática
        action = self._determine_action(lesson.tactic_applied)
        
        # Gera evidência
        evidence = self._generate_evidence(lesson, context)
        
        # Prediz sucesso
        success_prediction = lesson.success_rate * lesson.confidence
        
        return LessonApplication(
            lesson_id=lesson.lesson_id,
            action=action,
            tactic_applied=lesson.tactic_applied,
            confidence=lesson.confidence,
            evidence=evidence,
            success_prediction=success_prediction
        )
    
    def _determine_action(self, tactic: str) -> LessonAction:
        """Determina ação baseada na tática"""
        
        if tactic in ["add_import", "fix_type", "add_property"]:
            return LessonAction.PRE_CODEMOD
        elif tactic in ["fix_syntax", "update_dependency"]:
            return LessonAction.NUDGE_PROMPT
        elif tactic in ["use_alternative"]:
            return LessonAction.ROUTING
        else:
            return LessonAction.NUDGE_PROMPT  # Default
    
    def _generate_evidence(self, lesson: Lesson, context: Dict[str, Any]) -> str:
        """Gera evidência para a aplicação da lição"""
        
        evidence_parts = []
        
        # Adiciona informações da lição
        evidence_parts.append(f"Lição {lesson.lesson_id}: {lesson.tactic_applied}")
        evidence_parts.append(f"Taxa de sucesso: {lesson.success_rate:.1%}")
        evidence_parts.append(f"Confiança: {lesson.confidence:.1%}")
        evidence_parts.append(f"Aplicações: {lesson.application_count}")
        
        # Adiciona contexto
        if "framework" in context:
            evidence_parts.append(f"Framework: {context['framework']}")
        
        if "stack" in context:
            evidence_parts.append(f"Stack: {context['stack']}")
        
        return " | ".join(evidence_parts)
    
    def _apply_prompt_nudge(self, prompt: str, lesson: Lesson, application: LessonApplication) -> str:
        """Aplica nudge no prompt baseado na lição"""
        
        nudge_templates = {
            "add_import": "\n\n## CONTEXT: Previous similar errors were resolved by adding missing imports. Consider checking import statements.",
            "fix_type": "\n\n## CONTEXT: Previous similar errors were resolved by fixing TypeScript types. Pay attention to type definitions.",
            "fix_syntax": "\n\n## CONTEXT: Previous similar errors were resolved by fixing syntax issues. Check for missing brackets, semicolons, etc.",
            "update_dependency": "\n\n## CONTEXT: Previous similar errors were resolved by updating dependencies. Consider version compatibility.",
            "use_alternative": "\n\n## CONTEXT: Previous similar errors were resolved by using alternative approaches. Consider different patterns."
        }
        
        nudge = nudge_templates.get(lesson.tactic_applied, "")
        if nudge:
            # Insere nudge antes da seção de output
            if "## OUTPUT FORMAT" in prompt:
                prompt = prompt.replace("## OUTPUT FORMAT", nudge + "\n\n## OUTPUT FORMAT")
            else:
                prompt += nudge
        
        return prompt
    
    def _apply_pre_codemod(self, lesson: Lesson, application: LessonApplication, context: Dict[str, Any]) -> Optional[str]:
        """Aplica codemod prévio baseado na lição"""
        
        if not self.config["enable_pre_codemod"]:
            return None
        
        # Gera diff baseado na tática
        if lesson.tactic_applied == "add_import":
            return self._generate_import_fix(context)
        elif lesson.tactic_applied == "fix_type":
            return self._generate_type_fix(context)
        elif lesson.tactic_applied == "add_property":
            return self._generate_property_fix(context)
        
        return None
    
    def _generate_import_fix(self, context: Dict[str, Any]) -> Optional[str]:
        """Gera fix para imports faltantes"""
        files = context.get("files", [])
        if not files:
            return None
        
        # Simplificado - em produção seria mais inteligente
        target_file = files[0]
        if target_file.endswith(('.ts', '.tsx')):
            return f"""```diff
--- a/{target_file}
+++ b/{target_file}
@@ -1,1 +1,2 @@
+import {{ useState, useEffect }} from 'react';
 // ... existing code ...
```"""
        
        return None
    
    def _generate_type_fix(self, context: Dict[str, Any]) -> Optional[str]:
        """Gera fix para tipos TypeScript"""
        files = context.get("files", [])
        if not files:
            return None
        
        target_file = files[0]
        if target_file.endswith(('.ts', '.tsx')):
            return f"""```diff
--- a/{target_file}
+++ b/{target_file}
@@ -1,1 +1,1 @@
-const data: any = {{}};
+const data: Record<string, unknown> = {{}};
 // ... existing code ...
```"""
        
        return None
    
    def _generate_property_fix(self, context: Dict[str, Any]) -> Optional[str]:
        """Gera fix para propriedades faltantes"""
        files = context.get("files", [])
        if not files:
            return None
        
        target_file = files[0]
        if target_file.endswith(('.ts', '.tsx')):
            return f"""```diff
--- a/{target_file}
+++ b/{target_file}
@@ -1,1 +1,1 @@
-interface Props {{
+interface Props {{
+  className?: string;
 }}
 // ... existing code ...
```"""
        
        return None
    
    def _apply_routing_suggestion(self, lesson: Lesson, application: LessonApplication) -> Optional[str]:
        """Aplica sugestão de routing"""
        
        if not self.config["enable_routing"]:
            return None
        
        routing_suggestions = {
            "use_alternative": "Consider using alternative approach (PATCH_B mode)",
            "high_complexity": "High complexity detected (14B model recommended)",
            "low_confidence": "Low confidence scenario (ADVICE mode recommended)"
        }
        
        return routing_suggestions.get(lesson.tactic_applied, None)
    
    def generate_lesson_report(self, result: LessonResult) -> str:
        """Gera relatório de aplicação de lições"""
        
        report = ["# Lesson Engine Report\n"]
        
        if not result.applied_lessons:
            report.append("## Status: No lessons applied")
            report.append("No applicable lessons found for this error.")
            return "\n".join(report)
        
        report.append("## Status: Lessons Applied")
        report.append(f"**Total confidence**: {result.total_confidence:.1%}")
        report.append(f"**Lessons applied**: {len(result.applied_lessons)}")
        report.append("")
        
        report.append("## Applied Lessons")
        for i, application in enumerate(result.applied_lessons, 1):
            report.append(f"### Lesson {i}: {application.lesson_id}")
            report.append(f"- **Action**: {application.action.value}")
            report.append(f"- **Tactic**: {application.tactic_applied}")
            report.append(f"- **Confidence**: {application.confidence:.1%}")
            report.append(f"- **Success Prediction**: {application.success_prediction:.1%}")
            report.append(f"- **Evidence**: {application.evidence}")
            report.append("")
        
        if result.modified_prompt:
            report.append("## Prompt Modifications")
            report.append("Prompt was modified with lesson-based nudges.")
            report.append("")
        
        if result.pre_codemod_diff:
            report.append("## Pre-Codemod Applied")
            report.append("Pre-emptive code modification was applied:")
            report.append("```diff")
            report.append(result.pre_codemod_diff)
            report.append("```")
            report.append("")
        
        if result.routing_suggestion:
            report.append("## Routing Suggestion")
            report.append(f"**Suggestion**: {result.routing_suggestion}")
            report.append("")
        
        return "\n".join(report)
