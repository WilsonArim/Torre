from __future__ import annotations
import re, time, json
from typing import Dict, Any, List, Tuple, Set
from enum import Enum
from dataclasses import dataclass

class ModuleType(Enum):
    CORE = "core"
    FEATURE = "feature"
    UTILITY = "utility"
    TEST = "test"
    CONFIG = "config"

@dataclass
class ModuleInfo:
    """Informação sobre um módulo"""
    name: str
    type: ModuleType
    dependencies: Set[str]
    dependents: Set[str]
    complexity: float  # 0-1
    criticality: float  # 0-1
    test_coverage: float  # 0-1

class StrategosV2:
    """
    Strategos v2 — priorização reforçada:
      1) Ordem canónica: BUILD > TYPES > TESTS > STYLE
      2) Boost por sinais de logs (build/type/test/lint)
      3) Tie-break: maior score, depois menor custo estimado
    """
    
    # Ordem canónica por fase
    _PHASE_ORDER: List[str] = ["build", "types", "tests", "style"]
    # Pesos por fase (multiplicadores suaves; não distorcem o score base)
    _PHASE_WEIGHTS: Dict[str, float] = {
        "build": 1.30,
        "types": 1.15,
        "tests": 1.05,
        "style": 1.00,
    }
    
    # Pistas simples por log → boost adicional (aditivo pequeno)
    _LOG_BOOSTS: List[Tuple[str, str, float]] = [
        ("build", "ModuleNotFoundError", 0.25),
        ("build", "ImportError", 0.20),
        ("types", "TS", 0.20),               # TS2304, TS2580, etc.
        ("tests", "FAIL", 0.10),             # Jest/Pytest failures
        ("style", "lint", 0.05),             # ESLint/Ruff
    ]
    
    def __init__(self):
        self.module_patterns = {
            ModuleType.CORE: [
                r"src/core/", r"src/lib/", r"src/shared/",
                r"main\.", r"app\.", r"index\.",
                r"utils/", r"helpers/", r"common/"
            ],
            ModuleType.FEATURE: [
                r"src/features/", r"src/components/",
                r"src/pages/", r"src/screens/"
            ],
            ModuleType.UTILITY: [
                r"src/utils/", r"src/helpers/",
                r"src/tools/", r"src/scripts/"
            ],
            ModuleType.TEST: [
                r"test/", r"tests/", r"__tests__/",
                r"\.test\.", r"\.spec\."
            ],
            ModuleType.CONFIG: [
                r"config/", r"\.config\.", r"\.json$",
                r"package\.json", r"tsconfig\.json"
            ]
        }
        
        # Pesos para cálculo de impacto
        self.impact_weights = {
            "module_criticality": 0.4,
            "dependency_count": 0.3,
            "complexity": 0.2,
            "test_coverage": 0.1
        }
        
        # Pesos para cálculo de risco
        self.risk_weights = {
            "error_severity": 0.5,
            "module_type": 0.3,
            "change_frequency": 0.2
        }
        
        # Pesos para cálculo de custo
        self.cost_weights = {
            "patch_size": 0.4,
            "estimated_time": 0.3,
            "human_intervention": 0.3
        }
    
    def analyze_project_structure(self, tree: Dict[str, str]) -> Dict[str, ModuleInfo]:
        """Analisa estrutura do projeto e identifica módulos"""
        modules = {}
        
        for file_path, content in tree.items():
            module_info = self._analyze_file(file_path, content, tree)
            if module_info:
                modules[file_path] = module_info
        
        # Calcula dependências entre módulos
        self._calculate_dependencies(modules)
        
        return modules
    
    def _analyze_file(self, file_path: str, content: str, tree: Dict[str, str]) -> ModuleInfo:
        """Analisa um ficheiro individual"""
        # Determina tipo do módulo
        module_type = self._determine_module_type(file_path)
        
        # Calcula complexidade
        complexity = self._calculate_complexity(content)
        
        # Calcula criticidade
        criticality = self._calculate_criticality(file_path, module_type)
        
        # Calcula cobertura de testes
        test_coverage = self._estimate_test_coverage(file_path, tree)
        
        return ModuleInfo(
            name=file_path,
            type=module_type,
            dependencies=set(),
            dependents=set(),
            complexity=complexity,
            criticality=criticality,
            test_coverage=test_coverage
        )
    
    def _determine_module_type(self, file_path: str) -> ModuleType:
        """Determina o tipo de módulo baseado no caminho"""
        for module_type, patterns in self.module_patterns.items():
            for pattern in patterns:
                if re.search(pattern, file_path, re.IGNORECASE):
                    return module_type
        return ModuleType.UTILITY  # Default
    
    def _calculate_complexity(self, content: str) -> float:
        """Calcula complexidade do código (0-1)"""
        lines = content.split('\n')
        if not lines:
            return 0.0
        
        # Métricas de complexidade
        function_count = len(re.findall(r'(?:function|def|const|let|var)\s+\w+', content))
        class_count = len(re.findall(r'class\s+\w+', content))
        import_count = len(re.findall(r'import|require', content))
        comment_ratio = len([l for l in lines if l.strip().startswith(('//', '/*', '*', '#'))]) / len(lines)
        
        # Fórmula de complexidade
        complexity = (
            (function_count * 0.1) +
            (class_count * 0.2) +
            (import_count * 0.05) +
            (1 - comment_ratio) * 0.3
        )
        
        return min(1.0, complexity)
    
    def _calculate_criticality(self, file_path: str, module_type: ModuleType) -> float:
        """Calcula criticidade do módulo (0-1)"""
        criticality = 0.0
        
        # Criticidade por tipo
        type_criticality = {
            ModuleType.CORE: 0.9,
            ModuleType.FEATURE: 0.7,
            ModuleType.UTILITY: 0.5,
            ModuleType.TEST: 0.3,
            ModuleType.CONFIG: 0.8
        }
        
        criticality += type_criticality.get(module_type, 0.5)
        
        # Criticidade por nome
        critical_names = ['main', 'app', 'index', 'core', 'shared', 'config']
        if any(name in file_path.lower() for name in critical_names):
            criticality += 0.2
        
        return min(1.0, criticality)
    
    def _estimate_test_coverage(self, file_path: str, tree: Dict[str, str]) -> float:
        """Estima cobertura de testes (0-1)"""
        # Procura por ficheiros de teste correspondentes
        base_name = file_path.replace('.ts', '').replace('.tsx', '').replace('.js', '').replace('.jsx', '')
        test_files = [
            f for f in tree.keys()
            if f.endswith(('.test.ts', '.test.tsx', '.spec.ts', '.spec.tsx')) and
            base_name in f
        ]
        
        if test_files:
            return 0.8  # Estimativa se tem testes
        else:
            return 0.2  # Estimativa se não tem testes
    
    def _calculate_dependencies(self, modules: Dict[str, ModuleInfo]) -> None:
        """Calcula dependências entre módulos"""
        for file_path, module in modules.items():
            # Extrai imports do conteúdo
            content = ""  # Seria o conteúdo real do ficheiro
            imports = self._extract_imports(content)
            
            for import_path in imports:
                if import_path in modules:
                    module.dependencies.add(import_path)
                    modules[import_path].dependents.add(file_path)
    
    def _extract_imports(self, content: str) -> List[str]:
        """Extrai imports do conteúdo"""
        # Implementação simplificada
        return []
    
    def generate_advanced_attack_plan(self, logs: Dict[str, str], modules: Dict[str, ModuleInfo]) -> Dict[str, Any]:
        """Gera plano de ataque avançado com impacto × risco × custo"""
        errors = self._analyze_errors(logs)
        
        if not errors:
            return {
                "strategy": "no_errors",
                "priority_order": [],
                "risk_assessment": "low",
                "estimated_time": 0,
                "impact_score": 0,
                "cost_score": 0
            }
        
        # Calcula scores para cada erro
        error_scores = []
        for error in errors:
            impact = self._calculate_impact_score(error, modules)
            risk = self._calculate_risk_score(error, modules)
            cost = self._calculate_cost_score(error)
            
            # Score composto: impacto × risco / custo
            composite_score = (impact * risk) / max(cost, 0.1)
            
            error_scores.append({
                "error": error,
                "impact": impact,
                "risk": risk,
                "cost": cost,
                "composite_score": composite_score
            })
        
        # 1) Ajuste de score por fase (peso multiplicativo)
        for score in error_scores:
            phase = str(score["error"].get("type", "")).lower()
            weight = self._PHASE_WEIGHTS.get(phase, 1.0)
            try:
                score["composite_score"] = float(score.get("composite_score", 0.0)) * weight
            except Exception:
                score["composite_score"] = 0.0

        # 2) Boost leve por sinais presentes nos logs
        joined_logs = " ".join(logs.values()).lower()
        for score in error_scores:
            phase = str(score["error"].get("type", "")).lower()
            boost = 0.0
            for ph, needle, inc in self._LOG_BOOSTS:
                if ph == phase and needle.lower() in joined_logs:
                    boost += inc
            score["composite_score"] = float(score.get("composite_score", 0.0)) + boost

        # 3) Reordenação final: ordem canónica > score desc > custo asc
        def _phase_rank(p: str) -> int:
            p = (p or "").lower()
            try:
                return self._PHASE_ORDER.index(p)
            except ValueError:
                return len(self._PHASE_ORDER) + 1

        def _key(score: Dict[str, Any]):
            return (
                _phase_rank(score["error"].get("type")),
                -float(score.get("composite_score", 0.0)),
                float(score.get("cost", 1.0)),
            )

        # Ordena por score composto com priorização canónica
        error_scores.sort(key=_key)
        
        # Calcula métricas agregadas
        total_impact = sum(score["impact"] for score in error_scores)
        total_risk = sum(score["risk"] for score in error_scores)
        total_cost = sum(score["cost"] for score in error_scores)
        
        return {
            "strategy": "advanced_impact_risk_cost",
            "priority_order": error_scores,
            "risk_assessment": self._assess_risk_level(total_risk),
            "estimated_time": total_cost * 2,  # 2 min por ponto de custo
            "impact_score": total_impact,
            "risk_score": total_risk,
            "cost_score": total_cost,
            "module_analysis": self._get_module_analysis(modules)
        }
    
    def _analyze_errors(self, logs: Dict[str, str]) -> List[Dict[str, Any]]:
        """Analisa erros dos logs"""
        errors = []
        
        for log_type, content in logs.items():
            # Padrões de erro mais sofisticados
            error_patterns = {
                "build": [r"ModuleNotFoundError", r"ImportError", r"SyntaxError"],
                "types": [r"TypeError", r"TS\d+", r"cannot find name"],
                "tests": [r"AssertionError", r"test.*failed", r"coverage.*drop"],
                "style": [r"ESLint", r"lint.*error", r"no-unused-vars"]
            }
            
            for error_category, patterns in error_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        errors.append({
                            "type": error_category,
                            "content": content,
                            "severity": self._get_error_severity(error_category)
                        })
                        break
        
        return errors
    
    def _get_error_severity(self, error_type: str) -> float:
        """Retorna severidade do erro (0-1)"""
        severity_map = {
            "build": 1.0,    # Mais crítico
            "types": 0.8,
            "tests": 0.6,
            "style": 0.4     # Menos crítico
        }
        return severity_map.get(error_type, 0.5)
    
    def _calculate_impact_score(self, error: Dict[str, Any], modules: Dict[str, ModuleInfo]) -> float:
        """Calcula score de impacto (0-1)"""
        # Implementação simplificada
        return error.get("severity", 0.5)
    
    def _calculate_risk_score(self, error: Dict[str, Any], modules: Dict[str, ModuleInfo]) -> float:
        """Calcula score de risco (0-1)"""
        # Implementação simplificada
        return error.get("severity", 0.5)
    
    def _calculate_cost_score(self, error: Dict[str, Any]) -> float:
        """Calcula score de custo (0-1)"""
        # Implementação simplificada
        return 0.3  # Custo médio
    
    def _assess_risk_level(self, total_risk: float) -> str:
        """Avalia nível de risco"""
        if total_risk >= 5.0:
            return "critical"
        elif total_risk >= 3.0:
            return "high"
        elif total_risk >= 1.5:
            return "medium"
        else:
            return "low"
    
    def _get_module_analysis(self, modules: Dict[str, ModuleInfo]) -> Dict[str, Any]:
        """Retorna análise dos módulos"""
        return {
            "total_modules": len(modules),
            "module_types": {t.value: len([m for m in modules.values() if m.type == t]) for t in ModuleType},
            "avg_complexity": sum(m.complexity for m in modules.values()) / len(modules) if modules else 0,
            "avg_criticality": sum(m.criticality for m in modules.values()) / len(modules) if modules else 0,
            "avg_test_coverage": sum(m.test_coverage for m in modules.values()) / len(modules) if modules else 0
        }
    
    def generate_report(self, attack_plan: Dict[str, Any]) -> str:
        """Gera relatório do plano de ataque avançado"""
        if attack_plan["strategy"] == "no_errors":
            return """
# Relatório Strategos v2 - Sem Erros

✅ **Status**: Nenhum erro detectado
✅ **Ação**: Nenhuma ação necessária
✅ **Risco**: Baixo
"""
        
        report = f"""
# Relatório Strategos v2 - Plano de Ataque Avançado

## Resumo
- **Estratégia**: {attack_plan['strategy']}
- **Impacto Total**: {attack_plan['impact_score']:.2f}
- **Risco Total**: {attack_plan['risk_score']:.2f}
- **Custo Total**: {attack_plan['cost_score']:.2f}
- **Nível de Risco**: {attack_plan['risk_assessment']}
- **Tempo Estimado**: {attack_plan['estimated_time']:.1f} minutos

## Ordem de Prioridade (Impacto × Risco / Custo)
"""
        
        for i, score in enumerate(attack_plan['priority_order'][:5], 1):
            report += f"""
### {i}. {score['error']['type'].upper()} (Score: {score['composite_score']:.2f})
- **Impacto**: {score['impact']:.2f}
- **Risco**: {score['risk']:.2f}
- **Custo**: {score['cost']:.2f}
- **Erro**: {score['error']['content'][:100]}...
"""
        
        if 'module_analysis' in attack_plan:
            ma = attack_plan['module_analysis']
            report += f"""
## Análise de Módulos
- **Total de Módulos**: {ma['total_modules']}
- **Tipos**: {', '.join([f'{k}: {v}' for k, v in ma['module_types'].items()])}
- **Complexidade Média**: {ma['avg_complexity']:.2f}
- **Criticidade Média**: {ma['avg_criticality']:.2f}
- **Cobertura de Testes Média**: {ma['avg_test_coverage']:.2f}
"""
        
        return report
