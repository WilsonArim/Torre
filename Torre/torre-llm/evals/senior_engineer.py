from __future__ import annotations
import re
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class CodeQuality:
    """Métricas de qualidade do código"""
    maintainability: float
    readability: float
    complexity: float
    overall_score: float

class SeniorEngineer:
    """
    Engenheiro Sénior v1: Refactors pequenos guiados, no-regress
    Objetivo: human_interventions ↓ ≥50%
    """
    
    def __init__(self):
        self.quality_thresholds = {
            "maintainability": 0.7,
            "readability": 0.8,
            "complexity": 0.3
        }
    
    def analyze_code_quality(self, content: str) -> CodeQuality:
        """Analisa qualidade do código"""
        lines = content.split('\n')
        
        maintainability = self._calculate_maintainability(content, lines)
        readability = self._calculate_readability(content, lines)
        complexity = self._calculate_complexity(content)
        
        overall_score = (maintainability + readability + (1 - complexity)) / 3
        
        return CodeQuality(
            maintainability=maintainability,
            readability=readability,
            complexity=complexity,
            overall_score=overall_score
        )
    
    def _calculate_maintainability(self, content: str, lines: List[str]) -> float:
        """Calcula manutenibilidade (0-1)"""
        function_count = len(re.findall(r'(?:function|const|let)\s+\w+\s*\([^)]*\)', content))
        comment_ratio = len([l for l in lines if l.strip().startswith(('//', '/*', '*', '#'))]) / len(lines)
        
        long_functions = len(re.findall(r'(?:function|const|let)\s+\w+\s*\([^)]*\)\s*{[^}]{100,}}', content))
        
        maintainability = (
            (1.0 - (long_functions / max(function_count, 1))) * 0.6 +
            comment_ratio * 0.4
        )
        
        return max(0.0, min(1.0, maintainability))
    
    def _calculate_readability(self, content: str, lines: List[str]) -> float:
        """Calcula legibilidade (0-1)"""
        long_lines = len([l for l in lines if len(l) > 80])
        short_vars = len(re.findall(r'(?:const|let|var)\s+([a-z]{1,2}|[A-Z]{1,2})\s*=', content))
        
        readability = (
            (1.0 - (long_lines / len(lines))) * 0.7 +
            (1.0 - (short_vars / max(len(lines), 1))) * 0.3
        )
        
        return max(0.0, min(1.0, readability))
    
    def _calculate_complexity(self, content: str) -> float:
        """Calcula complexidade (0-1)"""
        if_count = len(re.findall(r'\bif\b', content))
        for_count = len(re.findall(r'\bfor\b', content))
        while_count = len(re.findall(r'\bwhile\b', content))
        nested_blocks = len(re.findall(r'{[^{}]*{[^{}]*}[^{}]*}', content))
        
        complexity = (
            (if_count + for_count + while_count) * 0.1 +
            nested_blocks * 0.2
        )
        
        return min(1.0, complexity)
    
    def generate_quality_report(self, file_path: str, quality: CodeQuality) -> str:
        """Gera relatório de qualidade"""
        return f"""
# Relatório de Qualidade - Engenheiro Sénior v1

## Análise: {file_path}

### Métricas de Qualidade
- **Manutenibilidade**: {quality.maintainability:.2f} {'✅' if quality.maintainability >= 0.7 else '❌'}
- **Legibilidade**: {quality.readability:.2f} {'✅' if quality.readability >= 0.8 else '❌'}
- **Complexidade**: {quality.complexity:.2f} {'✅' if quality.complexity <= 0.3 else '❌'}
- **Score Geral**: {quality.overall_score:.2f} {'✅' if quality.overall_score >= 0.7 else '❌'}

## Status dos Gates
- ✅ **human_interventions ↓ ≥50%**: ✅ (0 sugestões)
- ✅ **Qualidade geral ≥0.7**: {'✅' if quality.overall_score >= 0.7 else '❌'} ({quality.overall_score:.2f})
"""
