from __future__ import annotations
import time, subprocess, tempfile
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from .episodic_store import EpisodicStore, Lesson
from .lesson_engine import LessonEngine, LessonResult

class CandidateType(Enum):
    BASE = "base"
    BASE_LESSON = "base_lesson"
    BASE_LESSON_CODEMOD = "base_lesson_codemod"

@dataclass
class Candidate:
    """Candidato de patch"""
    candidate_type: CandidateType
    diff_content: str
    prompt: str
    lessons_applied: List[str]
    confidence: float
    execution_time_ms: int
    lint_score: float
    test_score: float
    build_score: float
    total_score: float

@dataclass
class BanditResult:
    """Resultado do bandit orchestrator"""
    winner: Candidate
    candidates: List[Candidate]
    execution_summary: Dict[str, Any]
    lesson_updates: List[Dict[str, Any]]

class BanditOrchestrator:
    """
    Bandit Orchestrator: compara candidatos e reranker por execução
    Objetivo: escolher o melhor candidato baseado em execução real
    """
    
    def __init__(self, episodic_store: EpisodicStore, lesson_engine: LessonEngine):
        self.episodic_store = episodic_store
        self.lesson_engine = lesson_engine
        
        # Configurações
        self.config = {
            "max_candidates": 3,
            "execution_timeout": 30,  # segundos
            "enable_lint_check": True,
            "enable_test_check": True,
            "enable_build_check": True,
            "score_weights": {
                "lint": 0.3,
                "test": 0.4,
                "build": 0.3
            }
        }
        
        # Algoritmos de bandit
        self.bandit_algorithms = {
            "thompson": self._thompson_sampling,
            "ucb": self._ucb_selection,
            "epsilon_greedy": self._epsilon_greedy
        }
    
    def generate_candidates(self, 
                          base_prompt: str,
                          error_signature: str,
                          context: Dict[str, Any]) -> List[Candidate]:
        """Gera candidatos de patch"""
        
        candidates = []
        
        # Candidato 1: Base (sem lições)
        base_candidate = Candidate(
            candidate_type=CandidateType.BASE,
            diff_content="",
            prompt=base_prompt,
            lessons_applied=[],
            confidence=0.5,
            execution_time_ms=0,
            lint_score=0.0,
            test_score=0.0,
            build_score=0.0,
            total_score=0.0
        )
        candidates.append(base_candidate)
        
        # Candidato 2: Base + Lições
        lessons = self.lesson_engine.find_applicable_lessons(error_signature, context)
        if lessons:
            lesson_result = self.lesson_engine.apply_lessons(lessons, base_prompt, context)
            
            base_lesson_candidate = Candidate(
                candidate_type=CandidateType.BASE_LESSON,
                diff_content="",
                prompt=lesson_result.modified_prompt or base_prompt,
                lessons_applied=[lesson.lesson_id for lesson in lessons],
                confidence=lesson_result.total_confidence,
                execution_time_ms=0,
                lint_score=0.0,
                test_score=0.0,
                build_score=0.0,
                total_score=0.0
            )
            candidates.append(base_lesson_candidate)
            
            # Candidato 3: Base + Lições + Codemod
            if lesson_result.pre_codemod_diff:
                base_lesson_codemod_candidate = Candidate(
                    candidate_type=CandidateType.BASE_LESSON_CODEMOD,
                    diff_content=lesson_result.pre_codemod_diff,
                    prompt=lesson_result.modified_prompt or base_prompt,
                    lessons_applied=[lesson.lesson_id for lesson in lessons],
                    confidence=lesson_result.total_confidence * 1.1,  # Boost para codemod
                    execution_time_ms=0,
                    lint_score=0.0,
                    test_score=0.0,
                    build_score=0.0,
                    total_score=0.0
                )
                candidates.append(base_lesson_codemod_candidate)
        
        return candidates[:self.config["max_candidates"]]
    
    def evaluate_candidates(self, candidates: List[Candidate], context: Dict[str, Any]) -> List[Candidate]:
        """Avalia candidatos através de execução real"""
        
        for candidate in candidates:
            # Simula execução (em produção, aplicaria o diff e executaria checks)
            candidate.execution_time_ms = self._simulate_execution(candidate, context)
            
            # Executa checks
            if self.config["enable_lint_check"]:
                candidate.lint_score = self._run_lint_check(candidate, context)
            
            if self.config["enable_test_check"]:
                candidate.test_score = self._run_test_check(candidate, context)
            
            if self.config["enable_build_check"]:
                candidate.build_score = self._run_build_check(candidate, context)
            
            # Calcula score total
            candidate.total_score = self._calculate_total_score(candidate)
        
        return candidates
    
    def _simulate_execution(self, candidate: Candidate, context: Dict[str, Any]) -> int:
        """Simula tempo de execução"""
        # Base time
        base_time = 100  # ms
        
        # Adiciona overhead baseado no tipo de candidato
        if candidate.candidate_type == CandidateType.BASE_LESSON:
            base_time += 50  # Overhead das lições
        elif candidate.candidate_type == CandidateType.BASE_LESSON_CODEMOD:
            base_time += 100  # Overhead do codemod
        
        # Adiciona variação aleatória
        import random
        variation = random.randint(-20, 20)
        
        return max(50, base_time + variation)
    
    def _run_lint_check(self, candidate: Candidate, context: Dict[str, Any]) -> float:
        """Executa check de lint"""
        # Simula lint check
        base_score = 0.8
        
        # Penaliza baseado no tipo de candidato
        if candidate.candidate_type == CandidateType.BASE:
            base_score = 0.7
        elif candidate.candidate_type == CandidateType.BASE_LESSON:
            base_score = 0.85
        elif candidate.candidate_type == CandidateType.BASE_LESSON_CODEMOD:
            base_score = 0.9
        
        # Adiciona variação baseada na confiança
        confidence_boost = candidate.confidence * 0.2
        
        return min(1.0, base_score + confidence_boost)
    
    def _run_test_check(self, candidate: Candidate, context: Dict[str, Any]) -> float:
        """Executa check de testes"""
        # Simula test check
        base_score = 0.75
        
        # Penaliza baseado no tipo de candidato
        if candidate.candidate_type == CandidateType.BASE:
            base_score = 0.65
        elif candidate.candidate_type == CandidateType.BASE_LESSON:
            base_score = 0.8
        elif candidate.candidate_type == CandidateType.BASE_LESSON_CODEMOD:
            base_score = 0.85
        
        # Adiciona variação baseada na confiança
        confidence_boost = candidate.confidence * 0.25
        
        return min(1.0, base_score + confidence_boost)
    
    def _run_build_check(self, candidate: Candidate, context: Dict[str, Any]) -> float:
        """Executa check de build"""
        # Simula build check
        base_score = 0.9
        
        # Penaliza baseado no tipo de candidato
        if candidate.candidate_type == CandidateType.BASE:
            base_score = 0.85
        elif candidate.candidate_type == CandidateType.BASE_LESSON:
            base_score = 0.9
        elif candidate.candidate_type == CandidateType.BASE_LESSON_CODEMOD:
            base_score = 0.95
        
        # Adiciona variação baseada na confiança
        confidence_boost = candidate.confidence * 0.1
        
        return min(1.0, base_score + confidence_boost)
    
    def _calculate_total_score(self, candidate: Candidate) -> float:
        """Calcula score total ponderado"""
        weights = self.config["score_weights"]
        
        total_score = (
            candidate.lint_score * weights["lint"] +
            candidate.test_score * weights["test"] +
            candidate.build_score * weights["build"]
        )
        
        # Bonus por confiança
        confidence_bonus = candidate.confidence * 0.1
        
        # Penalty por tempo de execução
        time_penalty = min(0.1, candidate.execution_time_ms / 1000)
        
        return max(0.0, min(1.0, total_score + confidence_bonus - time_penalty))
    
    def select_winner(self, candidates: List[Candidate], algorithm: str = "ucb") -> Candidate:
        """Seleciona vencedor usando algoritmo de bandit"""
        
        if not candidates:
            raise ValueError("No candidates provided")
        
        if len(candidates) == 1:
            return candidates[0]
        
        # Usa algoritmo especificado
        if algorithm in self.bandit_algorithms:
            winner_idx = self.bandit_algorithms[algorithm](candidates)
            return candidates[winner_idx]
        else:
            # Fallback: seleciona por score total
            return max(candidates, key=lambda c: c.total_score)
    
    def _thompson_sampling(self, candidates: List[Candidate]) -> int:
        """Thompson Sampling para seleção"""
        import random
        
        # Simula distribuição beta para cada candidato
        best_score = 0.0
        best_idx = 0
        
        for i, candidate in enumerate(candidates):
            # Simula amostra da distribuição beta
            alpha = candidate.total_score * 10 + 1
            beta = (1 - candidate.total_score) * 10 + 1
            
            sample = random.betavariate(alpha, beta)
            
            if sample > best_score:
                best_score = sample
                best_idx = i
        
        return best_idx
    
    def _ucb_selection(self, candidates: List[Candidate]) -> int:
        """Upper Confidence Bound para seleção"""
        import math
        
        # UCB = score + sqrt(2 * log(total_plays) / plays)
        # Simplificado para este contexto
        best_ucb = 0.0
        best_idx = 0
        
        for i, candidate in enumerate(candidates):
            # UCB = score + exploration bonus
            exploration_bonus = math.sqrt(2 * math.log(len(candidates)) / (i + 1))
            ucb = candidate.total_score + exploration_bonus
            
            if ucb > best_ucb:
                best_ucb = ucb
                best_idx = i
        
        return best_idx
    
    def _epsilon_greedy(self, candidates: List[Candidate], epsilon: float = 0.1) -> int:
        """Epsilon-Greedy para seleção"""
        import random
        
        # Com probabilidade epsilon, explora aleatoriamente
        if random.random() < epsilon:
            return random.randint(0, len(candidates) - 1)
        
        # Caso contrário, explora o melhor
        return max(range(len(candidates)), key=lambda i: candidates[i].total_score)
    
    def update_lesson_confidence(self, 
                                winner: Candidate,
                                success: bool,
                                context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Atualiza confiança das lições aplicadas"""
        
        updates = []
        
        for lesson_id in winner.lessons_applied:
            lesson = self.episodic_store.get_lesson_by_id(lesson_id)
            if lesson:
                # Calcula novo delta de sucesso
                success_delta = 1.0 if success else -1.0
                
                # Atualiza lição
                self.episodic_store.store_episode(
                    error_signature=lesson.error_signature,
                    context=context,
                    tactic_applied=lesson.tactic_applied,
                    success=success,
                    diff_size=len(winner.diff_content),
                    ttg_ms=winner.execution_time_ms,
                    metadata={
                        "candidate_type": winner.candidate_type.value,
                        "total_score": winner.total_score,
                        "confidence": winner.confidence
                    }
                )
                
                updates.append({
                    "lesson_id": lesson_id,
                    "success": success,
                    "score": winner.total_score,
                    "candidate_type": winner.candidate_type.value
                })
        
        return updates
    
    def run_bandit_experiment(self, 
                            base_prompt: str,
                            error_signature: str,
                            context: Dict[str, Any],
                            algorithm: str = "ucb") -> BanditResult:
        """Executa experimento completo do bandit"""
        
        # 1. Gera candidatos
        candidates = self.generate_candidates(base_prompt, error_signature, context)
        
        # 2. Avalia candidatos
        evaluated_candidates = self.evaluate_candidates(candidates, context)
        
        # 3. Seleciona vencedor
        winner = self.select_winner(evaluated_candidates, algorithm)
        
        # 4. Simula resultado (em produção, aplicaria o patch)
        success = winner.total_score > 0.7  # Threshold de sucesso
        
        # 5. Atualiza lições
        lesson_updates = self.update_lesson_confidence(winner, success, context)
        
        return BanditResult(
            winner=winner,
            candidates=evaluated_candidates,
            execution_summary={
                "total_candidates": len(evaluated_candidates),
                "algorithm_used": algorithm,
                "success": success,
                "execution_time_ms": sum(c.execution_time_ms for c in evaluated_candidates)
            },
            lesson_updates=lesson_updates
        )
    
    def generate_bandit_report(self, result: BanditResult) -> str:
        """Gera relatório do experimento bandit"""
        
        report = ["# Bandit Orchestrator Report\n"]
        
        # Resumo executivo
        report.append("## Executive Summary")
        report.append(f"**Winner**: {result.winner.candidate_type.value}")
        report.append(f"**Total Score**: {result.winner.total_score:.1%}")
        report.append(f"**Success**: {'✅' if result.execution_summary['success'] else '❌'}")
        report.append(f"**Algorithm**: {result.execution_summary['algorithm_used']}")
        report.append("")
        
        # Comparação de candidatos
        report.append("## Candidate Comparison")
        for i, candidate in enumerate(result.candidates, 1):
            status = "🏆 WINNER" if candidate == result.winner else ""
            report.append(f"### Candidate {i}: {candidate.candidate_type.value} {status}")
            report.append(f"- **Total Score**: {candidate.total_score:.1%}")
            report.append(f"- **Confidence**: {candidate.confidence:.1%}")
            report.append(f"- **Execution Time**: {candidate.execution_time_ms}ms")
            report.append(f"- **Lint Score**: {candidate.lint_score:.1%}")
            report.append(f"- **Test Score**: {candidate.test_score:.1%}")
            report.append(f"- **Build Score**: {candidate.build_score:.1%}")
            report.append(f"- **Lessons Applied**: {len(candidate.lessons_applied)}")
            report.append("")
        
        # Atualizações de lições
        if result.lesson_updates:
            report.append("## Lesson Updates")
            for update in result.lesson_updates:
                status = "✅" if update["success"] else "❌"
                report.append(f"- {status} **{update['lesson_id']}**: {update['candidate_type']} (score: {update['score']:.1%})")
            report.append("")
        
        # Métricas de execução
        report.append("## Execution Metrics")
        report.append(f"- **Total Candidates**: {result.execution_summary['total_candidates']}")
        report.append(f"- **Total Execution Time**: {result.execution_summary['execution_time_ms']}ms")
        report.append(f"- **Algorithm Used**: {result.execution_summary['algorithm_used']}")
        
        return "\n".join(report)
