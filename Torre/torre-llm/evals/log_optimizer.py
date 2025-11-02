from __future__ import annotations
import re
from typing import Dict, List, Set, Any

class LogOptimizer:
    """
    Sistema de otimização de logs para reduzir TTG
    Objetivo: Trim de logs no pré-processamento, remover stack traces repetitivos
    """
    
    def __init__(self):
        # Padrões de stack traces repetitivos
        self.stack_patterns = [
            r'at\s+\w+\.\w+\s+\([^)]+\)',
            r'Error:\s+.*\n\s+at\s+.*',
            r'Traceback\s+\(most recent call last\):',
            r'File\s+"[^"]+",\s+line\s+\d+',
            r'^\s+.*\s+in\s+.*$',
        ]
        
        # Padrões de logs verbosos
        self.verbose_patterns = [
            r'DEBUG:.*',
            r'INFO:.*',
            r'Loading.*',
            r'Initializing.*',
            r'Starting.*',
            r'Finished.*',
        ]
        
        # Cache de logs já processados
        self.processed_logs: Set[str] = set()
        
    def optimize_logs(self, logs: Dict[str, str]) -> Dict[str, str]:
        """Otimiza logs removendo redundâncias e verbosidade"""
        optimized = {}
        
        for log_type, log_content in logs.items():
            # Remove stack traces repetitivos
            content = self._remove_stack_traces(log_content)
            
            # Remove logs verbosos
            content = self._remove_verbose_logs(content)
            
            # Remove linhas duplicadas
            content = self._remove_duplicates(content)
            
            # Trim de espaços e linhas vazias
            content = self._trim_content(content)
            
            # Só adiciona se não estiver vazio
            if content.strip():
                optimized[log_type] = content
        
        return optimized
    
    def _remove_stack_traces(self, content: str) -> str:
        """Remove stack traces repetitivos"""
        lines = content.split('\n')
        filtered_lines = []
        in_stack_trace = False
        
        for line in lines:
            # Detecta início de stack trace
            if any(re.search(pattern, line) for pattern in self.stack_patterns):
                in_stack_trace = True
                continue
            
            # Se está em stack trace, pula linhas de trace
            if in_stack_trace:
                if line.strip() == '' or not line.startswith(' '):
                    in_stack_trace = False
                else:
                    continue
            
            filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)
    
    def _remove_verbose_logs(self, content: str) -> str:
        """Remove logs verbosos"""
        lines = content.split('\n')
        filtered_lines = []
        
        for line in lines:
            # Verifica se é um log verboso
            if any(re.search(pattern, line, re.IGNORECASE) for pattern in self.verbose_patterns):
                continue
            
            filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)
    
    def _remove_duplicates(self, content: str) -> str:
        """Remove linhas duplicadas consecutivas"""
        lines = content.split('\n')
        filtered_lines = []
        prev_line = None
        
        for line in lines:
            if line != prev_line:
                filtered_lines.append(line)
                prev_line = line
        
        return '\n'.join(filtered_lines)
    
    def _trim_content(self, content: str) -> str:
        """Remove espaços excessivos e linhas vazias"""
        # Remove linhas vazias no início e fim
        lines = [line.rstrip() for line in content.split('\n')]
        
        # Remove linhas vazias consecutivas
        filtered_lines = []
        prev_empty = False
        
        for line in lines:
            if line.strip() == '':
                if not prev_empty:
                    filtered_lines.append(line)
                prev_empty = True
            else:
                filtered_lines.append(line)
                prev_empty = False
        
        return '\n'.join(filtered_lines).strip()
    
    def get_optimization_stats(self, original: Dict[str, str], optimized: Dict[str, str]) -> Dict[str, Any]:
        """Retorna estatísticas de otimização"""
        original_size = sum(len(content) for content in original.values())
        optimized_size = sum(len(content) for content in optimized.values())
        
        reduction = original_size - optimized_size
        reduction_percent = (reduction / original_size * 100) if original_size > 0 else 0
        
        return {
            "original_size": original_size,
            "optimized_size": optimized_size,
            "reduction_bytes": reduction,
            "reduction_percent": round(reduction_percent, 2),
            "log_types_removed": len(original) - len(optimized)
        }
