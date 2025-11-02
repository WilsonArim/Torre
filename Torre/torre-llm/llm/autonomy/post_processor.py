from __future__ import annotations
import re, json, time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class ValidationResult(Enum):
    VALID = "valid"
    INVALID = "invalid"
    BLOCKED = "blocked"
    TRUNCATED = "truncated"

@dataclass
class PostProcessResult:
    """Resultado do pós-processamento"""
    validation: ValidationResult
    cleaned_content: str
    violations: List[str]
    metadata: Dict[str, Any]

class PostProcessor:
    """
    Pós-processamento blindado: validação e limpeza de saídas
    Objetivo: garantir que toda saída é segura e válida
    """
    
    def __init__(self):
        # Configurações de validação
        self.validation_config = {
            "max_lines": 1200,
            "max_file_size_kb": 100,
            "allowed_extensions": [".py", ".js", ".ts", ".jsx", ".tsx", ".json", ".md", ".txt"],
            "blocked_extensions": [".exe", ".dll", ".so", ".dylib", ".bin"]
        }
        
        # Padrões de segurança
        self.security_patterns = {
            "secrets": [
                r"api[_-]?key\s*[:=]\s*['\"][A-Za-z0-9_\-]{16,}['\"]",
                r"secret\s*[:=]\s*['\"][A-Za-z0-9_\-]{16,}['\"]",
                r"password\s*[:=]\s*['\"][A-Za-z0-9_\-]{8,}['\"]",
                r"token\s*[:=]\s*['\"][A-Za-z0-9_\-]{16,}['\"]",
                r"private[_-]?key\s*[:=]\s*['\"][A-Za-z0-9_\-]{32,}['\"]"
            ],
            "dangerous_commands": [
                r"rm\s+-rf",
                r"del\s+/s",
                r"format\s+c:",
                r"dd\s+if=",
                r"mkfs\.",
                r"fdisk\s+/dev/",
                r"chmod\s+777"
            ],
            "eval_patterns": [
                r"eval\(",
                r"exec\(",
                r"system\(",
                r"subprocess\.",
                r"os\.system\(",
                r"eval\s*\("
            ]
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
            r"\.pfx$",
            r"\.keystore$",
            r"\.jks$"
        ]
    
    def process_output(self, raw_output: str, context: Dict[str, Any] = None) -> PostProcessResult:
        """Processa e valida uma saída"""
        
        violations = []
        cleaned_content = raw_output
        
        # 1. Validação básica de estrutura
        structure_validation = self._validate_structure(raw_output)
        if structure_validation != ValidationResult.VALID:
            violations.append(f"Structure validation failed: {structure_validation.value}")
        
        # 2. Verificação de segurança
        security_violations = self._check_security(raw_output)
        violations.extend(security_violations)
        
        # 3. Verificação de paths sensíveis
        if self._contains_sensitive_paths(raw_output) or self._check_sensitive_paths_in_diff(raw_output):
            violations.append("Contains sensitive paths")
        
        # 4. Limpeza de ruído
        cleaned_content = self._remove_noise(raw_output)
        
        # 5. Truncamento se necessário
        if len(cleaned_content.split('\n')) > self.validation_config["max_lines"]:
            cleaned_content = self._truncate_content(cleaned_content)
            violations.append("Content truncated due to size limit")
        
        # 6. Determina resultado final
        if any("sensitive" in v.lower() or "dangerous" in v.lower() for v in violations):
            validation = ValidationResult.BLOCKED
        elif any("truncated" in v.lower() for v in violations):
            validation = ValidationResult.TRUNCATED
        elif violations:
            validation = ValidationResult.INVALID
        else:
            validation = ValidationResult.VALID
        
        return PostProcessResult(
            validation=validation,
            cleaned_content=cleaned_content,
            violations=violations,
            metadata={
                "original_size": len(raw_output),
                "cleaned_size": len(cleaned_content),
                "violation_count": len(violations),
                "timestamp": time.time()
            }
        )
    
    def _validate_structure(self, content: str) -> ValidationResult:
        """Valida estrutura básica do conteúdo"""
        
        if not content or not content.strip():
            return ValidationResult.INVALID
        
        # Verifica se tem pelo menos um diff válido
        diff_pattern = r"```diff\s*\n(.*?)\n```"
        if not re.search(diff_pattern, content, re.DOTALL):
            # Fallback: verifica se tem linhas de diff
            lines = content.split('\n')
            diff_lines = [l for l in lines if l.startswith(('+', '-', ' '))]
            if len(diff_lines) < 2:
                return ValidationResult.INVALID
        
        return ValidationResult.VALID
    
    def _check_security(self, content: str) -> List[str]:
        """Verifica violações de segurança"""
        violations = []
        
        # Verifica padrões de segredos
        for pattern in self.security_patterns["secrets"]:
            if re.search(pattern, content, re.IGNORECASE):
                violations.append(f"Potential secret detected: {pattern}")
        
        # Verifica comandos perigosos
        for pattern in self.security_patterns["dangerous_commands"]:
            if re.search(pattern, content, re.IGNORECASE):
                violations.append(f"Dangerous command detected: {pattern}")
        
        # Verifica padrões eval
        for pattern in self.security_patterns["eval_patterns"]:
            if re.search(pattern, content, re.IGNORECASE):
                violations.append(f"Code execution pattern detected: {pattern}")
        
        return violations
    
    def _contains_sensitive_paths(self, content: str) -> bool:
        """Verifica se contém paths sensíveis"""
        for pattern in self.sensitive_paths:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False
    
    def _check_sensitive_paths_in_diff(self, diff_content: str) -> bool:
        """Verifica paths sensíveis especificamente em diffs"""
        # Extrai nomes de arquivos do diff
        file_pattern = r"^\+\+\+ b/(.+)$|^--- a/(.+)$"
        matches = re.findall(file_pattern, diff_content, re.MULTILINE)
        
        for match in matches:
            file_path = match[0] or match[1]
            if file_path:
                # Verifica se o arquivo é sensível
                for pattern in self.sensitive_paths:
                    if re.search(pattern, file_path, re.IGNORECASE):
                        return True
        
        return False
    
    def _remove_noise(self, content: str) -> str:
        """Remove ruído do conteúdo"""
        
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Remove linhas vazias excessivas
            if not line.strip() and len(cleaned_lines) > 0 and not cleaned_lines[-1].strip():
                continue
            
            # Remove comentários desnecessários
            if line.strip().startswith('#') and not line.strip().startswith('# '):
                continue
            
            # Remove linhas de debug
            if any(debug_word in line.lower() for debug_word in ["debug:", "console.log", "print(", "echo"]):
                continue
            
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _truncate_content(self, content: str) -> str:
        """Trunca conteúdo de forma segura"""
        
        max_lines = self.validation_config["max_lines"]
        lines = content.split('\n')
        
        if len(lines) <= max_lines:
            return content
        
        # Estratégia: mantém início e fim, remove meio
        keep_lines = max_lines // 2
        
        # Mantém as primeiras linhas
        first_part = lines[:keep_lines]
        
        # Adiciona indicador de truncamento
        truncation_indicator = [f"# ... (truncated {len(lines) - max_lines} lines) ..."]
        
        # Mantém as últimas linhas
        last_part = lines[-(keep_lines - 1):]
        
        return '\n'.join(first_part + truncation_indicator + last_part)
    
    def validate_diff_format(self, diff_content: str) -> Tuple[bool, List[str]]:
        """Valida formato específico de diff"""
        
        errors = []
        lines = diff_content.split('\n')
        
        # Verifica se tem pelo menos uma linha de diff
        if not lines:
            errors.append("Empty diff content")
            return False, errors
        
        # Verifica formato de diff
        valid_diff_lines = 0
        for line in lines:
            if line.startswith(('+', '-', ' ')) or line.startswith('@@'):
                valid_diff_lines += 1
        
        if valid_diff_lines == 0:
            errors.append("No valid diff lines found")
        
        # Verifica se tem headers de arquivo
        has_file_header = False
        for line in lines:
            if line.startswith('+++') or line.startswith('---'):
                has_file_header = True
                break
        
        if not has_file_header:
            errors.append("Missing file headers (+++ or ---)")
        
        # Verifica balanceamento de + e -
        added_lines = len([l for l in lines if l.startswith('+')])
        removed_lines = len([l for l in lines if l.startswith('-')])
        
        if added_lines == 0 and removed_lines == 0:
            errors.append("No changes detected (+ or - lines)")
        
        return len(errors) == 0, errors
    
    def extract_files_from_diff(self, diff_content: str) -> List[str]:
        """Extrai nomes de arquivos do diff"""
        
        files = []
        file_pattern = r"^\+\+\+ b/(.+)$|^--- a/(.+)$"
        matches = re.findall(file_pattern, diff_content, re.MULTILINE)
        
        for match in matches:
            file_path = match[0] or match[1]
            if file_path and file_path not in files:
                files.append(file_path)
        
        return files
    
    def validate_file_extensions(self, files: List[str]) -> Tuple[bool, List[str]]:
        """Valida extensões de arquivos"""
        
        errors = []
        for file_path in files:
            # Verifica extensões bloqueadas
            for blocked_ext in self.validation_config["blocked_extensions"]:
                if file_path.endswith(blocked_ext):
                    errors.append(f"Blocked file extension: {file_path}")
            
            # Verifica se tem extensão permitida
            has_allowed_ext = any(file_path.endswith(ext) for ext in self.validation_config["allowed_extensions"])
            if not has_allowed_ext and '.' in file_path:
                errors.append(f"Unsupported file extension: {file_path}")
        
        return len(errors) == 0, errors
    
    def generate_validation_report(self, result: PostProcessResult) -> str:
        """Gera relatório de validação"""
        
        report = ["# Post-Processing Validation Report\n"]
        
        # Status
        status_emoji = {
            ValidationResult.VALID: "✅",
            ValidationResult.INVALID: "❌",
            ValidationResult.BLOCKED: "🚫",
            ValidationResult.TRUNCATED: "✂️"
        }
        
        report.append(f"## Status: {status_emoji[result.validation]} {result.validation.value.upper()}")
        report.append("")
        
        # Métricas
        report.append("## Métricas")
        report.append(f"- **Tamanho original**: {result.metadata['original_size']} chars")
        report.append(f"- **Tamanho limpo**: {result.metadata['cleaned_size']} chars")
        report.append(f"- **Violações**: {result.metadata['violation_count']}")
        report.append("")
        
        # Violações
        if result.violations:
            report.append("## Violações Detectadas")
            for violation in result.violations:
                report.append(f"- ❌ {violation}")
            report.append("")
        
        # Recomendações
        report.append("## Recomendações")
        if result.validation == ValidationResult.BLOCKED:
            report.append("- 🚫 **BLOQUEADO**: Não aplicar - violações de segurança detectadas")
        elif result.validation == ValidationResult.INVALID:
            report.append("- ⚠️ **INVÁLIDO**: Revisar e corrigir antes de aplicar")
        elif result.validation == ValidationResult.TRUNCATED:
            report.append("- ✂️ **TRUNCADO**: Conteúdo reduzido - verificar se está completo")
        else:
            report.append("- ✅ **VÁLIDO**: Pode ser aplicado com segurança")
        
        return "\n".join(report)
