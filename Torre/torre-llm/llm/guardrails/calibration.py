from __future__ import annotations
import json, pathlib, re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class ThresholdConfig:
    """Configuração de thresholds por módulo/repositório"""
    module_pattern: str
    security_strictness: float  # 0-1 (mais alto = mais restritivo)
    arch_strictness: float      # 0-1
    perf_strictness: float      # 0-1
    duplication_strictness: float  # 0-1

class GuardrailCalibration:
    """
    Sistema de calibração para endurecer guardrails
    Objetivo: thresholds adaptativos baseados em 5-10 repositórios reais
    """
    
    def __init__(self, config_path: str = ".fortaleza/guardrails/config.json"):
        self.config_path = pathlib.Path(config_path)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Configurações padrão por tipo de projeto
        self.default_configs = {
            "web-app": {
                "security_strictness": 0.9,
                "arch_strictness": 0.8,
                "perf_strictness": 0.7,
                "duplication_strictness": 0.6
            },
            "library": {
                "security_strictness": 0.7,
                "arch_strictness": 0.9,
                "perf_strictness": 0.8,
                "duplication_strictness": 0.8
            },
            "backend": {
                "security_strictness": 0.95,
                "arch_strictness": 0.7,
                "perf_strictness": 0.8,
                "duplication_strictness": 0.7
            },
            "infrastructure": {
                "security_strictness": 0.98,
                "arch_strictness": 0.6,
                "perf_strictness": 0.9,
                "duplication_strictness": 0.5
            }
        }
        
        # Thresholds específicos por módulo
        self.module_thresholds = {
            "src/core/": ThresholdConfig("src/core/", 0.95, 0.9, 0.8, 0.8),
            "src/components/": ThresholdConfig("src/components/", 0.8, 0.7, 0.6, 0.7),
            "src/utils/": ThresholdConfig("src/utils/", 0.7, 0.8, 0.8, 0.9),
            "src/infra/": ThresholdConfig("src/infra/", 0.98, 0.6, 0.9, 0.5),
            "src/db/": ThresholdConfig("src/db/", 0.95, 0.7, 0.8, 0.6),
            "tests/": ThresholdConfig("tests/", 0.6, 0.5, 0.5, 0.8),
            "config/": ThresholdConfig("config/", 0.9, 0.5, 0.5, 0.5)
        }
        
        self.load_config()
    
    def detect_project_type(self, repo_path: str) -> str:
        """Detecta tipo de projeto baseado na estrutura"""
        repo_files = list(pathlib.Path(repo_path).rglob("*"))
        
        # Indicadores de tipo
        web_indicators = ["package.json", "vite.config", "next.config", "react"]
        lib_indicators = ["setup.py", "pyproject.toml", "Cargo.toml", "go.mod"]
        backend_indicators = ["requirements.txt", "Dockerfile", "docker-compose"]
        infra_indicators = ["terraform", "kubernetes", "helm", "ansible"]
        
        file_names = [f.name.lower() for f in repo_files if f.is_file()]
        
        if any(indicator in " ".join(file_names) for indicator in infra_indicators):
            return "infrastructure"
        elif any(indicator in " ".join(file_names) for indicator in web_indicators):
            return "web-app"
        elif any(indicator in " ".join(file_names) for indicator in lib_indicators):
            return "library"
        elif any(indicator in " ".join(file_names) for indicator in backend_indicators):
            return "backend"
        
        return "web-app"  # Default
    
    def get_thresholds_for_file(self, file_path: str, project_type: str) -> ThresholdConfig:
        """Retorna thresholds específicos para um ficheiro"""
        # Procura por padrão de módulo
        for pattern, config in self.module_thresholds.items():
            if pattern in file_path:
                return config
        
        # Fallback para configuração do tipo de projeto
        default = self.default_configs.get(project_type, self.default_configs["web-app"])
        return ThresholdConfig(
            module_pattern="default",
            security_strictness=default["security_strictness"],
            arch_strictness=default["arch_strictness"],
            perf_strictness=default["perf_strictness"],
            duplication_strictness=default["duplication_strictness"]
        )
    
    def calibrate_from_repos(self, repo_paths: List[str]) -> None:
        """Calibra thresholds baseado em análise de repositórios reais"""
        calibration_data = {}
        
        for repo_path in repo_paths:
            repo_name = pathlib.Path(repo_path).name
            project_type = self.detect_project_type(repo_path)
            
            # Analisa repositório
            analysis = self._analyze_repo(repo_path)
            
            calibration_data[repo_name] = {
                "project_type": project_type,
                "analysis": analysis,
                "recommended_thresholds": self._calculate_recommended_thresholds(analysis)
            }
        
        # Salva calibração
        self.save_calibration(calibration_data)
        
        # Atualiza configurações
        self._update_configs_from_calibration(calibration_data)
    
    def _analyze_repo(self, repo_path: str) -> Dict[str, Any]:
        """Analisa um repositório para calibração"""
        repo_files = list(pathlib.Path(repo_path).rglob("*.{ts,tsx,js,jsx,py,go,rs}"))
        
        analysis = {
            "total_files": len(repo_files),
            "security_issues": 0,
            "arch_violations": 0,
            "perf_issues": 0,
            "duplications": 0,
            "module_distribution": {}
        }
        
        for file_path in repo_files:
            rel_path = str(file_path.relative_to(repo_path))
            
            # Categoriza por módulo
            module = self._categorize_module(rel_path)
            analysis["module_distribution"][module] = analysis["module_distribution"].get(module, 0) + 1
            
            # Análise básica do ficheiro
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                file_analysis = self._analyze_file_content(content, rel_path)
                
                analysis["security_issues"] += file_analysis["security_issues"]
                analysis["arch_violations"] += file_analysis["arch_violations"]
                analysis["perf_issues"] += file_analysis["perf_issues"]
                analysis["duplications"] += file_analysis["duplications"]
            except Exception as e:
                print(f"⚠️ Erro ao analisar {file_path}: {e}")
        
        return analysis
    
    def _categorize_module(self, file_path: str) -> str:
        """Categoriza ficheiro por módulo"""
        if "src/core/" in file_path:
            return "core"
        elif "src/components/" in file_path or "src/ui/" in file_path:
            return "components"
        elif "src/utils/" in file_path or "src/helpers/" in file_path:
            return "utils"
        elif "src/infra/" in file_path or "src/infrastructure/" in file_path:
            return "infra"
        elif "src/db/" in file_path or "database/" in file_path:
            return "db"
        elif "test" in file_path or "spec" in file_path:
            return "tests"
        elif "config" in file_path or "conf" in file_path:
            return "config"
        else:
            return "other"
    
    def _analyze_file_content(self, content: str, file_path: str) -> Dict[str, int]:
        """Análise básica do conteúdo de um ficheiro"""
        analysis = {
            "security_issues": 0,
            "arch_violations": 0,
            "perf_issues": 0,
            "duplications": 0
        }
        
        # Detecção de problemas de segurança
        security_patterns = [
            r"api[_-]?key\s*[:=]\s*['\"][^'\"]+['\"]",
            r"secret\s*[:=]\s*['\"][^'\"]+['\"]",
            r"password\s*[:=]\s*['\"][^'\"]+['\"]",
            r"token\s*[:=]\s*['\"][^'\"]+['\"]"
        ]
        
        for pattern in security_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                analysis["security_issues"] += 1
        
        # Detecção de violações arquiteturais
        if "src/components/" in file_path or "src/ui/" in file_path:
            if re.search(r"import.*from.*['\"]\.\./infra", content) or \
               re.search(r"import.*from.*['\"]\.\./db", content):
                analysis["arch_violations"] += 1
        
        # Detecção de problemas de performance
        nested_loops = re.findall(r"for\s*\(.*\).{0,100}for\s*\(", content, re.DOTALL)
        analysis["perf_issues"] += len(nested_loops)
        
        # Detecção de duplicações (simplificada)
        function_defs = re.findall(r"(?:function|const|let)\s+(\w+)", content)
        if len(function_defs) != len(set(function_defs)):
            analysis["duplications"] += 1
        
        return analysis
    
    def _calculate_recommended_thresholds(self, analysis: Dict[str, Any]) -> Dict[str, float]:
        """Calcula thresholds recomendados baseado na análise"""
        total_files = max(analysis["total_files"], 1)
        
        # Calcula taxas de problemas
        security_rate = analysis["security_issues"] / total_files
        arch_rate = analysis["arch_violations"] / total_files
        perf_rate = analysis["perf_issues"] / total_files
        dup_rate = analysis["duplications"] / total_files
        
        # Ajusta thresholds baseado nas taxas
        return {
            "security_strictness": min(0.98, 0.7 + security_rate * 2),
            "arch_strictness": min(0.95, 0.6 + arch_rate * 2),
            "perf_strictness": min(0.9, 0.5 + perf_rate * 2),
            "duplication_strictness": min(0.85, 0.4 + dup_rate * 2)
        }
    
    def _update_configs_from_calibration(self, calibration_data: Dict[str, Any]) -> None:
        """Atualiza configurações baseado na calibração"""
        for repo_name, data in calibration_data.items():
            project_type = data["project_type"]
            thresholds = data["recommended_thresholds"]
            
            # Atualiza configuração padrão para este tipo de projeto
            if project_type in self.default_configs:
                self.default_configs[project_type].update(thresholds)
        
        # Salva configurações atualizadas
        self.save_config()
    
    def save_calibration(self, calibration_data: Dict[str, Any]) -> None:
        """Salva dados de calibração"""
        calibration_file = self.config_path.parent / "calibration.json"
        with open(calibration_file, 'w') as f:
            json.dump(calibration_data, f, indent=2)
    
    def save_config(self) -> None:
        """Salva configuração atual"""
        config_data = {
            "default_configs": self.default_configs,
            "module_thresholds": {
                pattern: {
                    "security_strictness": config.security_strictness,
                    "arch_strictness": config.arch_strictness,
                    "perf_strictness": config.perf_strictness,
                    "duplication_strictness": config.duplication_strictness
                }
                for pattern, config in self.module_thresholds.items()
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(config_data, f, indent=2)
    
    def load_config(self) -> None:
        """Carrega configuração salva"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config_data = json.load(f)
                
                if "default_configs" in config_data:
                    self.default_configs.update(config_data["default_configs"])
                
                if "module_thresholds" in config_data:
                    for pattern, thresholds in config_data["module_thresholds"].items():
                        if pattern in self.module_thresholds:
                            config = self.module_thresholds[pattern]
                            config.security_strictness = thresholds.get("security_strictness", config.security_strictness)
                            config.arch_strictness = thresholds.get("arch_strictness", config.arch_strictness)
                            config.perf_strictness = thresholds.get("perf_strictness", config.perf_strictness)
                            config.duplication_strictness = thresholds.get("duplication_strictness", config.duplication_strictness)
            except Exception as e:
                print(f"⚠️ Erro ao carregar configuração: {e}")
    
    def generate_calibration_report(self) -> str:
        """Gera relatório de calibração"""
        calibration_file = self.config_path.parent / "calibration.json"
        
        if not calibration_file.exists():
            return "# Relatório de Calibração\n\nNenhuma calibração encontrada."
        
        with open(calibration_file, 'r') as f:
            calibration_data = json.load(f)
        
        report = ["# Relatório de Calibração - Guardrails Avançados\n"]
        
        for repo_name, data in calibration_data.items():
            report.append(f"## {repo_name}")
            report.append(f"- **Tipo**: {data['project_type']}")
            report.append(f"- **Ficheiros analisados**: {data['analysis']['total_files']}")
            report.append(f"- **Problemas encontrados**:")
            report.append(f"  - Segurança: {data['analysis']['security_issues']}")
            report.append(f"  - Arquitetura: {data['analysis']['arch_violations']}")
            report.append(f"  - Performance: {data['analysis']['perf_issues']}")
            report.append(f"  - Duplicação: {data['analysis']['duplications']}")
            report.append(f"- **Thresholds recomendados**:")
            for key, value in data['recommended_thresholds'].items():
                report.append(f"  - {key}: {value:.2f}")
            report.append("")
        
        return "\n".join(report)
