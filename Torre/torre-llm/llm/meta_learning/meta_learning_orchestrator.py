from __future__ import annotations
import time, json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from .episodic_store import EpisodicStore, Lesson
from .lesson_engine import LessonEngine, LessonResult
from .bandit_orchestrator import BanditOrchestrator, BanditResult, Candidate

@dataclass
class MetaLearningResult:
    """Resultado da meta-aprendizagem"""
    success: bool
    error_signature: str
    lesson_result: Optional[LessonResult]
    bandit_result: Optional[BanditResult]
    final_candidate: Optional[Candidate]
    metrics: Dict[str, Any]

class MetaLearningOrchestrator:
    """
    Meta-Learning Orchestrator: coordena episodic store + lesson engine + bandit orchestrator
    Objetivo: reduzir erros repetidos e adaptar por workspace
    """
    
    def __init__(self, workspace_path: str = "."):
        self.episodic_store = EpisodicStore(workspace_path)
        self.lesson_engine = LessonEngine(self.episodic_store)
        self.bandit_orchestrator = BanditOrchestrator(self.episodic_store, self.lesson_engine)
        
        # Configurações
        self.config = {
            "enable_meta_learning": True,
            "enable_auto_apply": True,
            "min_lesson_confidence": 0.6,
            "max_lessons_per_request": 3,
            "bandit_algorithm": "ucb",
            "success_threshold": 0.7,
            "precision_threshold": 0.8
        }
        
        # Métricas de performance
        self.performance_metrics = {
            "total_episodes": 0,
            "successful_episodes": 0,
            "repeat_error_rate": 0.0,
            "lesson_precision": 0.0,
            "ttg_improvement": 0.0,
            "diff_size_improvement": 0.0
        }
    
    def process_request(self, 
                       error_logs: List[str],
                       context: Dict[str, Any],
                       base_prompt: str) -> MetaLearningResult:
        """Processa um request completo através da meta-aprendizagem"""
        
        start_time = time.time()
        
        if not self.config["enable_meta_learning"]:
            return MetaLearningResult(
                success=False,
                error_signature="meta_learning_disabled",
                lesson_result=None,
                bandit_result=None,
                final_candidate=None,
                metrics={"processing_time": time.time() - start_time}
            )
        
        # 1. Extrai assinatura de erro
        error_signature = self.lesson_engine.extract_error_signature(error_logs)
        
        # 2. Busca lições aplicáveis
        lessons = self.lesson_engine.find_applicable_lessons(error_signature, context)
        
        lesson_result = None
        bandit_result = None
        final_candidate = None
        
        if lessons:
            # 3. Aplica lições
            lesson_result = self.lesson_engine.apply_lessons(lessons, base_prompt, context)
            
            # 4. Executa experimento bandit
            bandit_result = self.bandit_orchestrator.run_bandit_experiment(
                base_prompt, error_signature, context, self.config["bandit_algorithm"]
            )
            
            final_candidate = bandit_result.winner
            
            # 5. Atualiza métricas
            self._update_performance_metrics(bandit_result, context)
        
        # 6. Calcula métricas finais
        processing_time = time.time() - start_time
        metrics = {
            "processing_time": processing_time,
            "error_signature": error_signature,
            "lessons_found": len(lessons) if lessons else 0,
            "final_confidence": final_candidate.confidence if final_candidate else 0.0,
            "success_prediction": final_candidate.total_score if final_candidate else 0.0
        }
        
        success = final_candidate and final_candidate.total_score > self.config["success_threshold"]
        
        return MetaLearningResult(
            success=success,
            error_signature=error_signature,
            lesson_result=lesson_result,
            bandit_result=bandit_result,
            final_candidate=final_candidate,
            metrics=metrics
        )
    
    def _update_performance_metrics(self, bandit_result: BanditResult, context: Dict[str, Any]) -> None:
        """Atualiza métricas de performance"""
        
        self.performance_metrics["total_episodes"] += 1
        
        if bandit_result and bandit_result.execution_summary["success"]:
            self.performance_metrics["successful_episodes"] += 1
        
        # Calcula taxa de erro repetido
        if self.performance_metrics["total_episodes"] > 0:
            success_rate = self.performance_metrics["successful_episodes"] / self.performance_metrics["total_episodes"]
            self.performance_metrics["repeat_error_rate"] = 1.0 - success_rate
        
        # Calcula precisão das lições
        if bandit_result and bandit_result.lesson_updates:
            successful_lessons = sum(1 for update in bandit_result.lesson_updates if update["success"])
            total_lessons = len(bandit_result.lesson_updates)
            if total_lessons > 0:
                self.performance_metrics["lesson_precision"] = successful_lessons / total_lessons
    
    def store_episode(self, 
                     error_signature: str,
                     context: Dict[str, Any],
                     tactic_applied: str,
                     success: bool,
                     diff_size: int,
                     ttg_ms: int,
                     metadata: Dict[str, Any] = None) -> str:
        """Armazena um episódio de aprendizagem"""
        
        return self.episodic_store.store_episode(
            error_signature=error_signature,
            context=context,
            tactic_applied=tactic_applied,
            success=success,
            diff_size=diff_size,
            ttg_ms=ttg_ms,
            metadata=metadata
        )
    
    def get_lessons_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas das lições"""
        return self.episodic_store.get_lessons_stats()
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Retorna métricas de performance"""
        return self.performance_metrics.copy()
    
    def check_gates(self) -> Dict[str, bool]:
        """Verifica se os gates da Fase 7 foram atingidos"""
        
        stats = self.episodic_store.get_lessons_stats()
        metrics = self.performance_metrics
        
        gates = {
            "repeat_error_rate": metrics["repeat_error_rate"] <= 0.4,  # ↓ ≥60%
            "lesson_precision": metrics["lesson_precision"] >= 0.8,   # ≥80%
            "total_episodes": self.performance_metrics["total_episodes"] >= 50,  # Mínimo de episódios
            "total_lessons": stats["total_lessons"] > 0  # Pelo menos uma lição
        }
        
        return gates
    
    def generate_meta_learning_report(self, result: MetaLearningResult) -> str:
        """Gera relatório completo de meta-aprendizagem"""
        
        report = ["# Meta-Learning Orchestrator Report\n"]
        
        # Status geral
        status_emoji = "✅" if result.success else "❌"
        report.append(f"## Status: {status_emoji} {'SUCCESS' if result.success else 'FAILED'}")
        report.append(f"**Error Signature**: {result.error_signature}")
        report.append(f"**Processing Time**: {result.metrics['processing_time']:.2f}s")
        report.append("")
        
        # Lições aplicadas
        if result.lesson_result:
            report.append("## Lesson Engine Results")
            report.append(f"**Lessons Found**: {result.metrics['lessons_found']}")
            report.append(f"**Total Confidence**: {result.lesson_result.total_confidence:.1%}")
            report.append("")
            
            # Adiciona relatório detalhado das lições
            lesson_report = self.lesson_engine.generate_lesson_report(result.lesson_result)
            report.append(lesson_report)
            report.append("")
        
        # Resultados do bandit
        if result.bandit_result:
            report.append("## Bandit Orchestrator Results")
            report.append(f"**Winner**: {result.bandit_result.winner.candidate_type.value}")
            report.append(f"**Total Score**: {result.bandit_result.winner.total_score:.1%}")
            report.append(f"**Success**: {'✅' if result.bandit_result.execution_summary['success'] else '❌'}")
            report.append("")
            
            # Adiciona relatório detalhado do bandit
            bandit_report = self.bandit_orchestrator.generate_bandit_report(result.bandit_result)
            report.append(bandit_report)
            report.append("")
        
        # Métricas de performance
        metrics = self.get_performance_metrics()
        report.append("## Performance Metrics")
        report.append(f"- **Total Episodes**: {metrics['total_episodes']}")
        report.append(f"- **Successful Episodes**: {metrics['successful_episodes']}")
        report.append(f"- **Repeat Error Rate**: {metrics['repeat_error_rate']:.1%}")
        report.append(f"- **Lesson Precision**: {metrics['lesson_precision']:.1%}")
        report.append("")
        
        # Verificação de gates
        gates = self.check_gates()
        report.append("## Gates Status")
        for gate_name, passed in gates.items():
            status = "✅" if passed else "❌"
            report.append(f"- {status} **{gate_name}**: {'PASSED' if passed else 'FAILED'}")
        report.append("")
        
        # Recomendações
        report.append("## Recommendations")
        if result.success:
            report.append("- ✅ **Proceed**: Meta-learning successfully applied")
            if result.final_candidate:
                report.append(f"- 🎯 **Strategy**: {result.final_candidate.candidate_type.value} approach selected")
        else:
            report.append("- ⚠️ **Review**: Meta-learning did not achieve desired results")
            report.append("- 🔍 **Investigate**: Check lesson quality and bandit configuration")
        
        return "\n".join(report)
    
    def cleanup_old_data(self, days_threshold: int = 90) -> int:
        """Remove dados antigos"""
        return self.episodic_store.cleanup_old_lessons(days_threshold)
    
    def purge_lessons_by_signature(self, error_signature: str) -> int:
        """Remove lições por assinatura de erro"""
        return self.episodic_store.purge_lessons_by_signature(error_signature)
    
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """Atualiza configurações"""
        self.config.update(new_config)
        
        # Propaga configurações para componentes
        if "min_lesson_confidence" in new_config:
            self.lesson_engine.config["min_confidence"] = new_config["min_lesson_confidence"]
        
        if "max_lessons_per_request" in new_config:
            self.lesson_engine.config["max_lessons_per_request"] = new_config["max_lessons_per_request"]
    
    def export_state(self) -> Dict[str, Any]:
        """Exporta estado completo"""
        return {
            "config": self.config,
            "performance_metrics": self.performance_metrics,
            "lessons_stats": self.get_lessons_stats(),
            "timestamp": time.time()
        }
    
    def import_state(self, state_data: Dict[str, Any]) -> None:
        """Importa estado"""
        if "config" in state_data:
            self.config.update(state_data["config"])
        
        if "performance_metrics" in state_data:
            self.performance_metrics.update(state_data["performance_metrics"])
