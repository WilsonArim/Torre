from __future__ import annotations
import json, time, sqlite3
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class PolicyType(Enum):
    TEMPERATURE = "temperature"
    TOP_P = "top_p"
    STOP_SEQUENCES = "stop_sequences"
    MAX_TOKENS = "max_tokens"

@dataclass
class DecodePolicy:
    """Política de decodificação"""
    temperature: float
    top_p: float
    stop_sequences: List[str]
    max_tokens: int
    success_rate: float
    avg_ttg_ms: int
    avg_diff_size: int

@dataclass
class OptimizationResult:
    """Resultado da otimização"""
    policy: DecodePolicy
    improvement: float  # % de melhoria
    rollback_needed: bool
    metrics: Dict[str, float]

class AutoOptimizer:
    """
    Auto-Otimizador: autotuning de políticas de decode + reranker
    Objetivo: reduzir TTG e diff_size sem perder success rate
    """
    
    def __init__(self, db_path: str = ".fortaleza/optimization/policy.db"):
        self.db_path = db_path
        self.current_policies: Dict[str, DecodePolicy] = {}
        self.baseline_metrics: Dict[str, float] = {}
        
        # Configurações de otimização
        self.optimization_config = {
            "temperature_range": (0.1, 0.9),
            "top_p_range": (0.8, 0.99),
            "max_tokens_range": (100, 500),
            "improvement_threshold": 0.1,  # 10% de melhoria
            "rollback_threshold": -0.005,  # -0.5pp de success rate
            "exploration_rate": 0.2  # 20% de exploração
        }
        
        # Algoritmos de bandit
        self.bandit_algorithms = {
            "ucb": self._ucb_selection,
            "epsilon_greedy": self._epsilon_greedy_selection
        }
        
        self.init_database()
        self.load_current_policies()
    
    def get_optimized_policy(self, 
                           error_type: str,
                           project_context: Dict[str, Any]) -> DecodePolicy:
        """Retorna política otimizada para o contexto"""
        
        # Identifica contexto
        context_key = self._create_context_key(error_type, project_context)
        
        # Verifica se já tem política para este contexto
        if context_key in self.current_policies:
            policy = self.current_policies[context_key]
            
            # Decide se deve explorar nova política
            if self._should_explore():
                new_policy = self._generate_exploratory_policy(policy)
                return new_policy
            
            return policy
        
        # Cria política inicial
        initial_policy = self._create_initial_policy(error_type)
        self.current_policies[context_key] = initial_policy
        self.save_policy(context_key, initial_policy)
        
        return initial_policy
    
    def update_policy_performance(self,
                                 context_key: str,
                                 policy: DecodePolicy,
                                 success: bool,
                                 ttg_ms: int,
                                 diff_size: int) -> None:
        """Atualiza performance de uma política"""
        
        # Atualiza métricas da política
        if context_key in self.current_policies:
            current_policy = self.current_policies[context_key]
            
            # Atualiza success rate
            if success:
                current_policy.success_rate = (
                    (current_policy.success_rate * 0.9) + 0.1
                )
            else:
                current_policy.success_rate = (
                    current_policy.success_rate * 0.9
                )
            
            # Atualiza TTG médio
            current_policy.avg_ttg_ms = (
                (current_policy.avg_ttg_ms * 0.9) + (ttg_ms * 0.1)
            )
            
            # Atualiza diff size médio
            current_policy.avg_diff_size = (
                (current_policy.avg_diff_size * 0.9) + (diff_size * 0.1)
            )
        
        # Salva atualização
        self.save_policy(context_key, policy)
        
        # Verifica se precisa rollback
        if self._needs_rollback(context_key, policy):
            self._rollback_policy(context_key)
    
    def optimize_policies(self) -> List[OptimizationResult]:
        """Executa otimização de todas as políticas"""
        
        results = []
        
        for context_key, policy in self.current_policies.items():
            # Gera política candidata
            candidate_policy = self._generate_candidate_policy(policy)
            
            # Avalia candidata
            improvement = self._evaluate_improvement(policy, candidate_policy)
            
            # Decide se aplica
            if improvement > self.optimization_config["improvement_threshold"]:
                self.current_policies[context_key] = candidate_policy
                self.save_policy(context_key, candidate_policy)
                
                results.append(OptimizationResult(
                    policy=candidate_policy,
                    improvement=improvement,
                    rollback_needed=False,
                    metrics=self._calculate_metrics(candidate_policy)
                ))
            else:
                results.append(OptimizationResult(
                    policy=policy,
                    improvement=0.0,
                    rollback_needed=False,
                    metrics=self._calculate_metrics(policy)
                ))
        
        return results
    
    def _create_context_key(self, error_type: str, project_context: Dict[str, Any]) -> str:
        """Cria chave única para o contexto"""
        framework = project_context.get("framework", "unknown")
        language = project_context.get("language", "unknown")
        complexity = project_context.get("complexity", "medium")
        
        return f"{error_type}:{framework}:{language}:{complexity}"
    
    def _create_initial_policy(self, error_type: str) -> DecodePolicy:
        """Cria política inicial baseada no tipo de erro"""
        
        # Políticas base por tipo de erro
        base_policies = {
            "typescript": DecodePolicy(
                temperature=0.3,
                top_p=0.9,
                stop_sequences=["\n\n", "```"],
                max_tokens=200,
                success_rate=0.0,
                avg_ttg_ms=0,
                avg_diff_size=0
            ),
            "lint": DecodePolicy(
                temperature=0.2,
                top_p=0.95,
                stop_sequences=["\n", ";"],
                max_tokens=100,
                success_rate=0.0,
                avg_ttg_ms=0,
                avg_diff_size=0
            ),
            "build": DecodePolicy(
                temperature=0.4,
                top_p=0.85,
                stop_sequences=["\n\n", "error"],
                max_tokens=300,
                success_rate=0.0,
                avg_ttg_ms=0,
                avg_diff_size=0
            )
        }
        
        return base_policies.get(error_type, base_policies["typescript"])
    
    def _should_explore(self) -> bool:
        """Decide se deve explorar nova política"""
        import random
        return random.random() < self.optimization_config["exploration_rate"]
    
    def _generate_exploratory_policy(self, base_policy: DecodePolicy) -> DecodePolicy:
        """Gera política exploratória baseada na atual"""
        
        import random
        
        # Varia temperatura
        temp_range = self.optimization_config["temperature_range"]
        new_temp = max(temp_range[0], min(temp_range[1], 
                    base_policy.temperature + random.uniform(-0.1, 0.1)))
        
        # Varia top_p
        top_p_range = self.optimization_config["top_p_range"]
        new_top_p = max(top_p_range[0], min(top_p_range[1],
                    base_policy.top_p + random.uniform(-0.05, 0.05)))
        
        # Varia max_tokens
        max_tokens_range = self.optimization_config["max_tokens_range"]
        new_max_tokens = max(max_tokens_range[0], min(max_tokens_range[1],
                           base_policy.max_tokens + random.randint(-50, 50)))
        
        return DecodePolicy(
            temperature=new_temp,
            top_p=new_top_p,
            stop_sequences=base_policy.stop_sequences,
            max_tokens=new_max_tokens,
            success_rate=base_policy.success_rate,
            avg_ttg_ms=base_policy.avg_ttg_ms,
            avg_diff_size=base_policy.avg_diff_size
        )
    
    def _generate_candidate_policy(self, current_policy: DecodePolicy) -> DecodePolicy:
        """Gera política candidata para otimização"""
        
        # Usa algoritmo UCB para seleção
        return self._ucb_selection(current_policy)
    
    def _ucb_selection(self, current_policy: DecodePolicy) -> DecodePolicy:
        """Seleção usando Upper Confidence Bound"""
        
        import random
        import math
        
        # Calcula UCB para diferentes variações
        variations = []
        
        for i in range(5):
            # Varia temperatura
            temp_variation = current_policy.temperature + random.uniform(-0.2, 0.2)
            temp_variation = max(0.1, min(0.9, temp_variation))
            
            # Varia top_p
            top_p_variation = current_policy.top_p + random.uniform(-0.1, 0.1)
            top_p_variation = max(0.8, min(0.99, top_p_variation))
            
            # Calcula UCB score
            exploration_bonus = math.sqrt(math.log(1 + current_policy.success_rate))
            ucb_score = current_policy.success_rate + exploration_bonus
            
            variations.append({
                "policy": DecodePolicy(
                    temperature=temp_variation,
                    top_p=top_p_variation,
                    stop_sequences=current_policy.stop_sequences,
                    max_tokens=current_policy.max_tokens,
                    success_rate=current_policy.success_rate,
                    avg_ttg_ms=current_policy.avg_ttg_ms,
                    avg_diff_size=current_policy.avg_diff_size
                ),
                "ucb_score": ucb_score
            })
        
        # Retorna variação com maior UCB
        best_variation = max(variations, key=lambda x: x["ucb_score"])
        return best_variation["policy"]
    
    def _epsilon_greedy_selection(self, current_policy: DecodePolicy) -> DecodePolicy:
        """Seleção usando ε-greedy"""
        
        import random
        
        epsilon = 0.1  # 10% de exploração
        
        if random.random() < epsilon:
            # Exploração: política aleatória
            return self._generate_exploratory_policy(current_policy)
        else:
            # Exploitação: política atual
            return current_policy
    
    def _evaluate_improvement(self, current: DecodePolicy, candidate: DecodePolicy) -> float:
        """Avalia melhoria da política candidata"""
        
        # Score composto: success_rate + TTG + diff_size
        current_score = (
            current.success_rate * 0.5 +
            (1 - current.avg_ttg_ms / 1000) * 0.3 +  # Normaliza TTG
            (1 - current.avg_diff_size / 100) * 0.2   # Normaliza diff_size
        )
        
        candidate_score = (
            candidate.success_rate * 0.5 +
            (1 - candidate.avg_ttg_ms / 1000) * 0.3 +
            (1 - candidate.avg_diff_size / 100) * 0.2
        )
        
        return candidate_score - current_score
    
    def _needs_rollback(self, context_key: str, policy: DecodePolicy) -> bool:
        """Verifica se precisa rollback"""
        
        # Verifica se success rate caiu muito
        if context_key in self.current_policies:
            baseline = self.current_policies[context_key].success_rate
            current = policy.success_rate
            
            if (baseline - current) > abs(self.optimization_config["rollback_threshold"]):
                return True
        
        return False
    
    def _rollback_policy(self, context_key: str) -> None:
        """Faz rollback para política anterior"""
        
        # Carrega política anterior da base de dados
        previous_policy = self.load_policy_from_db(context_key)
        
        if previous_policy:
            self.current_policies[context_key] = previous_policy
            print(f"🔄 Rollback da política para {context_key}")
    
    def _calculate_metrics(self, policy: DecodePolicy) -> Dict[str, float]:
        """Calcula métricas da política"""
        
        return {
            "success_rate": policy.success_rate,
            "avg_ttg_ms": policy.avg_ttg_ms,
            "avg_diff_size": policy.avg_diff_size,
            "temperature": policy.temperature,
            "top_p": policy.top_p
        }
    
    def init_database(self) -> None:
        """Inicializa base de dados"""
        
        import pathlib
        
        db_dir = pathlib.Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS policies (
                context_key TEXT PRIMARY KEY,
                temperature REAL,
                top_p REAL,
                stop_sequences TEXT,
                max_tokens INTEGER,
                success_rate REAL,
                avg_ttg_ms INTEGER,
                avg_diff_size INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                context_key TEXT,
                success BOOLEAN,
                ttg_ms INTEGER,
                diff_size INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_policy(self, context_key: str, policy: DecodePolicy) -> None:
        """Salva política na base de dados"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO policies 
            (context_key, temperature, top_p, stop_sequences, max_tokens, 
             success_rate, avg_ttg_ms, avg_diff_size, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            context_key,
            policy.temperature,
            policy.top_p,
            json.dumps(policy.stop_sequences),
            policy.max_tokens,
            policy.success_rate,
            policy.avg_ttg_ms,
            policy.avg_diff_size
        ))
        
        conn.commit()
        conn.close()
    
    def load_policy_from_db(self, context_key: str) -> Optional[DecodePolicy]:
        """Carrega política da base de dados"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT temperature, top_p, stop_sequences, max_tokens,
                   success_rate, avg_ttg_ms, avg_diff_size
            FROM policies WHERE context_key = ?
        """, (context_key,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return DecodePolicy(
                temperature=row[0],
                top_p=row[1],
                stop_sequences=json.loads(row[2]),
                max_tokens=row[3],
                success_rate=row[4],
                avg_ttg_ms=row[5],
                avg_diff_size=row[6]
            )
        
        return None
    
    def load_current_policies(self) -> None:
        """Carrega políticas atuais da base de dados"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT context_key, temperature, top_p, stop_sequences, max_tokens,
                   success_rate, avg_ttg_ms, avg_diff_size
            FROM policies
        """)
        
        for row in cursor.fetchall():
            context_key = row[0]
            policy = DecodePolicy(
                temperature=row[1],
                top_p=row[2],
                stop_sequences=json.loads(row[3]),
                max_tokens=row[4],
                success_rate=row[5],
                avg_ttg_ms=row[6],
                avg_diff_size=row[7]
            )
            
            self.current_policies[context_key] = policy
        
        conn.close()
    
    def generate_optimization_report(self) -> str:
        """Gera relatório de otimização"""
        
        report = ["# Relatório Auto-Otimizador - Turbo I&D\n"]
        
        report.append("## Políticas Ativas")
        for context_key, policy in self.current_policies.items():
            report.append(f"### {context_key}")
            report.append(f"- **Success Rate**: {policy.success_rate:.1%}")
            report.append(f"- **TTG Médio**: {policy.avg_ttg_ms}ms")
            report.append(f"- **Diff Size Médio**: {policy.avg_diff_size} linhas")
            report.append(f"- **Temperature**: {policy.temperature:.2f}")
            report.append(f"- **Top-p**: {policy.top_p:.2f}")
            report.append("")
        
        # Calcula métricas agregadas
        total_policies = len(self.current_policies)
        avg_success_rate = sum(p.success_rate for p in self.current_policies.values()) / max(total_policies, 1)
        avg_ttg = sum(p.avg_ttg_ms for p in self.current_policies.values()) / max(total_policies, 1)
        
        report.append("## Métricas Agregadas")
        report.append(f"- **Total de Políticas**: {total_policies}")
        report.append(f"- **Success Rate Médio**: {avg_success_rate:.1%}")
        report.append(f"- **TTG Médio**: {avg_ttg:.1f}ms")
        report.append("")
        
        report.append("## Status dos Gates")
        ttg_improvement = (self.baseline_metrics.get("ttg", 100) - avg_ttg) / self.baseline_metrics.get("ttg", 100)
        gate_status = "✅ ATINGIDO" if ttg_improvement >= 0.1 else "❌ NÃO ATINGIDO"
        report.append(f"- **TTG p95 melhora ≥10%**: {gate_status} ({ttg_improvement:.1%})")
        
        success_gate = "✅ ATINGIDO" if avg_success_rate >= 0.97 else "❌ NÃO ATINGIDO"
        report.append(f"- **Success Rate não cai**: {success_gate} ({avg_success_rate:.1%})")
        
        return "\n".join(report)
