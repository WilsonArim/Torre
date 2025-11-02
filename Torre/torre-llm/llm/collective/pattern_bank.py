from __future__ import annotations
import json, hashlib, time
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
from enum import Enum

class PatternType(Enum):
    ERROR_FIX = "error_fix"
    PERFORMANCE = "performance"
    SECURITY = "security"
    ARCHITECTURE = "architecture"

@dataclass
class ProblemSignature:
    """Assinatura anónima de um problema"""
    error_type: str
    error_code: str
    context_hash: str  # Hash do contexto (sem código)
    framework: str
    language: str

@dataclass
class SolutionSignature:
    """Assinatura anónima de uma solução"""
    fix_type: str
    diff_size: int
    success_rate: float
    avg_ttg_ms: int
    preconditions: List[str]
    postconditions: List[str]

@dataclass
class Pattern:
    """Padrão reutilizável"""
    id: str
    problem: ProblemSignature
    solution: SolutionSignature
    frequency: int
    last_seen: float
    reuse_hit_rate: float
    time_saved_ms: int

class PatternBank:
    """
    Pattern Bank: inteligência coletiva sem PII/código bruto
    Objetivo: aprender padrões reutilizáveis entre repositórios
    """
    
    def __init__(self, storage_path: str = ".fortaleza/patterns"):
        self.storage_path = storage_path
        self.patterns: Dict[str, Pattern] = {}
        self.pattern_index: Dict[str, List[str]] = {}  # error_type -> pattern_ids
        
        # Métricas de reuso
        self.reuse_stats = {
            "total_episodes": 0,
            "reuse_hits": 0,
            "time_saved_total_ms": 0,
            "repositories_seen": set()
        }
        
        self.load_patterns()
    
    def extract_pattern(self, 
                       error_logs: Dict[str, str],
                       solution_diff: str,
                       success: bool,
                       ttg_ms: int,
                       repo_context: Dict[str, Any]) -> Optional[Pattern]:
        """Extrai padrão de um episódio"""
        
        # Cria assinatura do problema
        problem_sig = self._create_problem_signature(error_logs, repo_context)
        
        # Cria assinatura da solução
        solution_sig = self._create_solution_signature(solution_diff, success, ttg_ms)
        
        # Gera ID único do padrão
        pattern_id = self._generate_pattern_id(problem_sig, solution_sig)
        
        # Verifica se já existe
        if pattern_id in self.patterns:
            # Atualiza padrão existente
            pattern = self.patterns[pattern_id]
            pattern.frequency += 1
            pattern.last_seen = time.time()
            
            # Atualiza métricas de sucesso
            if success:
                pattern.solution.success_rate = (
                    (pattern.solution.success_rate * (pattern.frequency - 1)) + 1.0
                ) / pattern.frequency
            else:
                pattern.solution.success_rate = (
                    pattern.solution.success_rate * (pattern.frequency - 1)
                ) / pattern.frequency
            
            pattern.solution.avg_ttg_ms = (
                (pattern.solution.avg_ttg_ms * (pattern.frequency - 1)) + ttg_ms
            ) / pattern.frequency
            
            return pattern
        else:
            # Cria novo padrão
            pattern = Pattern(
                id=pattern_id,
                problem=problem_sig,
                solution=solution_sig,
                frequency=1,
                last_seen=time.time(),
                reuse_hit_rate=0.0,
                time_saved_ms=0
            )
            
            self.patterns[pattern_id] = pattern
            self._index_pattern(pattern)
            
            return pattern
    
    def find_matching_pattern(self, 
                             error_logs: Dict[str, str],
                             repo_context: Dict[str, Any]) -> Optional[Pattern]:
        """Encontra padrão que corresponde ao problema atual"""
        
        # Cria assinatura do problema atual
        current_problem = self._create_problem_signature(error_logs, repo_context)
        
        # Procura por padrões similares
        candidates = self._find_candidates(current_problem)
        
        if not candidates:
            return None
        
        # Ordena por similaridade e reuso
        scored_candidates = []
        for pattern in candidates:
            similarity = self._calculate_similarity(current_problem, pattern.problem)
            reuse_score = pattern.reuse_hit_rate * pattern.frequency
            
            # Score composto: similaridade + histórico de reuso
            composite_score = (similarity * 0.7) + (reuse_score * 0.3)
            
            scored_candidates.append((pattern, composite_score))
        
        # Retorna o melhor candidato
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        
        if scored_candidates and scored_candidates[0][1] > 0.8:
            return scored_candidates[0][0]
        
        return None
    
    def record_reuse(self, pattern: Pattern, success: bool, time_saved_ms: int, repo_id: str):
        """Regista reuso de um padrão"""
        
        # Atualiza estatísticas
        self.reuse_stats["total_episodes"] += 1
        self.reuse_stats["repositories_seen"].add(repo_id)
        
        if success:
            self.reuse_stats["reuse_hits"] += 1
            self.reuse_stats["time_saved_total_ms"] += time_saved_ms
        
        # Atualiza padrão
        pattern.reuse_hit_rate = self.reuse_stats["reuse_hits"] / self.reuse_stats["total_episodes"]
        pattern.time_saved_ms = time_saved_ms
    
    def get_reuse_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de reuso"""
        total_repos = len(self.reuse_stats["repositories_seen"])
        
        return {
            "total_patterns": len(self.patterns),
            "total_episodes": self.reuse_stats["total_episodes"],
            "reuse_hit_rate": self.reuse_stats["reuse_hits"] / max(self.reuse_stats["total_episodes"], 1),
            "time_saved_total_ms": self.reuse_stats["time_saved_total_ms"],
            "repositories_seen": total_repos,
            "avg_time_saved_per_episode": (
                self.reuse_stats["time_saved_total_ms"] / max(self.reuse_stats["total_episodes"], 1)
            )
        }
    
    def _create_problem_signature(self, error_logs: Dict[str, str], repo_context: Dict[str, Any]) -> ProblemSignature:
        """Cria assinatura anónima do problema"""
        
        # Extrai tipo de erro
        error_type = "unknown"
        error_code = "unknown"
        
        for log_type, content in error_logs.items():
            if "typescript" in log_type.lower() or "ts" in log_type.lower():
                # Procura por códigos de erro TypeScript
                import re
                ts_errors = re.findall(r"TS(\d+)", content)
                if ts_errors:
                    error_type = "typescript"
                    error_code = f"TS{ts_errors[0]}"
                    break
            elif "lint" in log_type.lower():
                error_type = "lint"
                error_code = "lint_error"
                break
            elif "build" in log_type.lower():
                error_type = "build"
                error_code = "build_error"
                break
        
        # Cria hash do contexto (sem código)
        context_str = f"{repo_context.get('framework', 'unknown')}:{repo_context.get('language', 'unknown')}:{error_type}"
        context_hash = hashlib.sha256(context_str.encode()).hexdigest()[:16]
        
        return ProblemSignature(
            error_type=error_type,
            error_code=error_code,
            context_hash=context_hash,
            framework=repo_context.get("framework", "unknown"),
            language=repo_context.get("language", "unknown")
        )
    
    def _create_solution_signature(self, solution_diff: str, success: bool, ttg_ms: int) -> SolutionSignature:
        """Cria assinatura anónima da solução"""
        
        # Determina tipo de fix
        fix_type = "unknown"
        if "import" in solution_diff.lower():
            fix_type = "import_fix"
        elif "type" in solution_diff.lower():
            fix_type = "type_fix"
        elif "syntax" in solution_diff.lower():
            fix_type = "syntax_fix"
        elif "lint" in solution_diff.lower():
            fix_type = "lint_fix"
        
        # Calcula tamanho do diff
        diff_size = len(solution_diff.split('\n'))
        
        # Pré e pós condições (simplificadas)
        preconditions = ["error_present"]
        postconditions = ["error_resolved"]
        
        if fix_type == "import_fix":
            preconditions.append("missing_import")
            postconditions.append("import_added")
        elif fix_type == "type_fix":
            preconditions.append("type_error")
            postconditions.append("type_correct")
        
        return SolutionSignature(
            fix_type=fix_type,
            diff_size=diff_size,
            success_rate=1.0 if success else 0.0,
            avg_ttg_ms=ttg_ms,
            preconditions=preconditions,
            postconditions=postconditions
        )
    
    def _generate_pattern_id(self, problem: ProblemSignature, solution: SolutionSignature) -> str:
        """Gera ID único do padrão"""
        pattern_str = f"{problem.error_type}:{problem.error_code}:{problem.context_hash}:{solution.fix_type}"
        return hashlib.sha256(pattern_str.encode()).hexdigest()[:16]
    
    def _find_candidates(self, problem: ProblemSignature) -> List[Pattern]:
        """Encontra candidatos para um problema"""
        candidates = []
        
        # Procura por padrões do mesmo tipo de erro
        if problem.error_type in self.pattern_index:
            for pattern_id in self.pattern_index[problem.error_type]:
                if pattern_id in self.patterns:
                    candidates.append(self.patterns[pattern_id])
        
        # Procura por padrões do mesmo framework
        for pattern in self.patterns.values():
            if pattern.problem.framework == problem.framework:
                candidates.append(pattern)
        
        return candidates
    
    def _calculate_similarity(self, problem1: ProblemSignature, problem2: ProblemSignature) -> float:
        """Calcula similaridade entre dois problemas"""
        similarity = 0.0
        
        # Mesmo tipo de erro
        if problem1.error_type == problem2.error_type:
            similarity += 0.4
        
        # Mesmo código de erro
        if problem1.error_code == problem2.error_code:
            similarity += 0.3
        
        # Mesmo framework
        if problem1.framework == problem2.framework:
            similarity += 0.2
        
        # Mesma linguagem
        if problem1.language == problem2.language:
            similarity += 0.1
        
        return similarity
    
    def _index_pattern(self, pattern: Pattern) -> None:
        """Indexa padrão para busca rápida"""
        error_type = pattern.problem.error_type
        if error_type not in self.pattern_index:
            self.pattern_index[error_type] = []
        
        if pattern.id not in self.pattern_index[error_type]:
            self.pattern_index[error_type].append(pattern.id)
    
    def save_patterns(self) -> None:
        """Salva padrões em ficheiro"""
        import pathlib
        
        path = pathlib.Path(self.storage_path)
        path.mkdir(parents=True, exist_ok=True)
        
        # Converte para formato serializável
        patterns_data = {}
        for pattern_id, pattern in self.patterns.items():
            patterns_data[pattern_id] = {
                "id": pattern.id,
                "problem": {
                    "error_type": pattern.problem.error_type,
                    "error_code": pattern.problem.error_code,
                    "context_hash": pattern.problem.context_hash,
                    "framework": pattern.problem.framework,
                    "language": pattern.problem.language
                },
                "solution": {
                    "fix_type": pattern.solution.fix_type,
                    "diff_size": pattern.solution.diff_size,
                    "success_rate": pattern.solution.success_rate,
                    "avg_ttg_ms": pattern.solution.avg_ttg_ms,
                    "preconditions": pattern.solution.preconditions,
                    "postconditions": pattern.solution.postconditions
                },
                "frequency": pattern.frequency,
                "last_seen": pattern.last_seen,
                "reuse_hit_rate": pattern.reuse_hit_rate,
                "time_saved_ms": pattern.time_saved_ms
            }
        
        # Salva padrões
        patterns_file = path / "patterns.json"
        with open(patterns_file, 'w') as f:
            json.dump(patterns_data, f, indent=2)
        
        # Salva estatísticas
        stats_file = path / "stats.json"
        stats_data = {
            "total_episodes": self.reuse_stats["total_episodes"],
            "reuse_hits": self.reuse_stats["reuse_hits"],
            "time_saved_total_ms": self.reuse_stats["time_saved_total_ms"],
            "repositories_seen": list(self.reuse_stats["repositories_seen"])
        }
        
        with open(stats_file, 'w') as f:
            json.dump(stats_data, f, indent=2)
    
    def load_patterns(self) -> None:
        """Carrega padrões do ficheiro"""
        import pathlib
        
        path = pathlib.Path(self.storage_path)
        patterns_file = path / "patterns.json"
        stats_file = path / "stats.json"
        
        if patterns_file.exists():
            try:
                with open(patterns_file, 'r') as f:
                    patterns_data = json.load(f)
                
                for pattern_id, data in patterns_data.items():
                    problem = ProblemSignature(**data["problem"])
                    solution = SolutionSignature(**data["solution"])
                    
                    pattern = Pattern(
                        id=data["id"],
                        problem=problem,
                        solution=solution,
                        frequency=data["frequency"],
                        last_seen=data["last_seen"],
                        reuse_hit_rate=data["reuse_hit_rate"],
                        time_saved_ms=data["time_saved_ms"]
                    )
                    
                    self.patterns[pattern_id] = pattern
                    self._index_pattern(pattern)
            
            except Exception as e:
                print(f"⚠️ Erro ao carregar padrões: {e}")
        
        if stats_file.exists():
            try:
                with open(stats_file, 'r') as f:
                    stats_data = json.load(f)
                
                self.reuse_stats["total_episodes"] = stats_data.get("total_episodes", 0)
                self.reuse_stats["reuse_hits"] = stats_data.get("reuse_hits", 0)
                self.reuse_stats["time_saved_total_ms"] = stats_data.get("time_saved_total_ms", 0)
                self.reuse_stats["repositories_seen"] = set(stats_data.get("repositories_seen", []))
            
            except Exception as e:
                print(f"⚠️ Erro ao carregar estatísticas: {e}")
    
    def generate_pattern_report(self) -> str:
        """Gera relatório dos padrões"""
        stats = self.get_reuse_stats()
        
        report = ["# Relatório Pattern Bank - Inteligência Coletiva\n"]
        
        report.append("## Estatísticas Gerais")
        report.append(f"- **Total de Padrões**: {stats['total_patterns']}")
        report.append(f"- **Total de Episódios**: {stats['total_episodes']}")
        report.append(f"- **Taxa de Reuso**: {stats['reuse_hit_rate']:.1%}")
        report.append(f"- **Tempo Poupado Total**: {stats['time_saved_total_ms']}ms")
        report.append(f"- **Repositórios Vistos**: {stats['repositories_seen']}")
        report.append(f"- **Tempo Poupado Médio**: {stats['avg_time_saved_per_episode']:.1f}ms/episódio")
        report.append("")
        
        report.append("## Padrões Mais Frequentes")
        top_patterns = sorted(self.patterns.values(), key=lambda p: p.frequency, reverse=True)[:5]
        
        for i, pattern in enumerate(top_patterns, 1):
            report.append(f"### {i}. {pattern.problem.error_type.upper()} - {pattern.solution.fix_type}")
            report.append(f"- **Frequência**: {pattern.frequency} vezes")
            report.append(f"- **Sucesso**: {pattern.solution.success_rate:.1%}")
            report.append(f"- **TTG Médio**: {pattern.solution.avg_ttg_ms}ms")
            report.append(f"- **Reuso**: {pattern.reuse_hit_rate:.1%}")
            report.append("")
        
        report.append("## Status dos Gates")
        gate_status = "✅ ATINGIDO" if stats['reuse_hit_rate'] >= 0.3 else "❌ NÃO ATINGIDO"
        report.append(f"- **Reuse Hit Rate ≥30%**: {gate_status} ({stats['reuse_hit_rate']:.1%})")
        
        return "\n".join(report)
