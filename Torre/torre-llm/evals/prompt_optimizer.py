from __future__ import annotations
import json
from typing import Dict, Any

class PromptOptimizer:
    """
    Otimizador de prompts para reduzir TTG
    Objetivo: Prompt ainda mais curto, decodificação PATCH com top_p 0.15, max_tokens ~900
    """
    
    def __init__(self):
        self.max_tokens = 900
        self.top_p = 0.15
        self.temperature = 0.1
        
    def optimize_prompt(self, episode: Dict[str, Any], tree: Dict[str, str]) -> Dict[str, Any]:
        """Otimiza prompt para ser mais conciso e eficiente"""
        
        # Extrai apenas os erros mais críticos
        critical_logs = self._extract_critical_errors(episode.get("logs", {}))
        
        # Seleciona apenas ficheiros relevantes
        relevant_files = self._select_relevant_files(tree, critical_logs)
        
        # Cria prompt otimizado
        optimized_prompt = {
            "logs": critical_logs,
            "files": relevant_files,
            "objective": episode.get("objective", "Corrigir erros críticos"),
            "constraints": {
                "max_tokens": self.max_tokens,
                "top_p": self.top_p,
                "temperature": self.temperature,
                "format": "diff_only"
            }
        }
        
        return optimized_prompt
    
    def _extract_critical_errors(self, logs: Dict[str, str]) -> Dict[str, str]:
        """Extrai apenas os erros mais críticos"""
        critical_patterns = [
            "Cannot find name",
            "ModuleNotFoundError",
            "ImportError",
            "SyntaxError",
            "TypeError",
            "TS2304",
            "TS2307",
            "TS2339"
        ]
        
        critical_logs = {}
        for log_type, content in logs.items():
            # Verifica se contém erros críticos
            if any(pattern in content for pattern in critical_patterns):
                # Trunca para apenas a primeira linha de erro
                lines = content.split('\n')
                critical_lines = []
                for line in lines:
                    if any(pattern in line for pattern in critical_patterns):
                        critical_lines.append(line)
                        break  # Só pega o primeiro erro crítico
                
                if critical_lines:
                    critical_logs[log_type] = '\n'.join(critical_lines)
        
        return critical_logs
    
    def _select_relevant_files(self, tree: Dict[str, str], logs: Dict[str, str]) -> Dict[str, str]:
        """Seleciona apenas ficheiros relevantes para o erro"""
        relevant_files = {}
        
        # Extrai nomes de ficheiros mencionados nos logs
        mentioned_files = set()
        for content in logs.values():
            # Procura por padrões de ficheiros nos logs
            import re
            file_patterns = [
                r'([a-zA-Z0-9_/]+\.(ts|tsx|js|jsx))',
                r'Cannot find name \'([^\']+)\'',
                r'Module \'([^\']+)\''
            ]
            
            for pattern in file_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    if isinstance(match, tuple):
                        mentioned_files.add(match[0])
                    else:
                        mentioned_files.add(match)
        
        # Adiciona ficheiros mencionados
        for file_path, content in tree.items():
            file_name = file_path.split('/')[-1]
            if any(mentioned in file_name for mentioned in mentioned_files):
                relevant_files[file_path] = content
        
        # Se não encontrou ficheiros específicos, adiciona os principais
        if not relevant_files:
            main_files = [k for k in tree.keys() if k.endswith(('.ts', '.tsx'))][:3]
            for file_path in main_files:
                relevant_files[file_path] = tree[file_path]
        
        return relevant_files
    
    def get_optimization_stats(self, original_prompt: str, optimized_prompt: Dict[str, Any]) -> Dict[str, Any]:
        """Retorna estatísticas de otimização do prompt"""
        original_size = len(original_prompt)
        optimized_size = len(json.dumps(optimized_prompt))
        
        reduction = original_size - optimized_size
        reduction_percent = (reduction / original_size * 100) if original_size > 0 else 0
        
        return {
            "original_size": original_size,
            "optimized_size": optimized_size,
            "reduction_bytes": reduction,
            "reduction_percent": round(reduction_percent, 2),
            "max_tokens": self.max_tokens,
            "top_p": self.top_p
        }
