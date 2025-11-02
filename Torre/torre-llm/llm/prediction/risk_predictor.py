from __future__ import annotations
import json, time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class RiskFactor:
    """Fator de risco individual"""
    name: str
    weight: float  # 0-1
    evidence: str
    score: float  # 0-100

@dataclass
class RiskPrediction:
    """Predição de risco completa"""
    risk_score: float  # 0-100
    factors: List[RiskFactor]
    recommendation: str  # "proceed", "advisory", "block"
    confidence: float  # 0-1

class RiskPredictor:
    """
    Risk Predictor v1: calcula RiskScore 0-100 antes do patch
    Objetivo: predição de risco baseada em sinais múltiplos
    """
    
    def __init__(self):
        # Pesos dos fatores de risco
        self.factor_weights = {
            "topology": 0.25,      # Grafo de imports
            "module_type": 0.20,   # Tipo de módulo
            "error_density": 0.20, # Densidade de erros
            "history": 0.15,       # Repetição histórica
            "diff_size": 0.10,     # Tamanho esperado do diff
            "sca": 0.10           # Vulnerabilidades SCA
        }
        
        # Thresholds para recomendações
        self.thresholds = {
            "advisory": 70,
            "block": 85
        }
        
        # Tipos de módulo e seus riscos base
        self.module_risk_scores = {
            "CORE": 80,
            "FEATURE": 60,
            "UTIL": 40,
            "CONFIG": 70,
            "TEST": 20
        }
    
    def predict_risk(self, 
                    logs: Dict[str, str],
                    graph: Dict[str, Any],
                    modules: Dict[str, Any],
                    history: Dict[str, Any],
                    sca: Dict[str, Any],
                    strategos_plan: Dict[str, Any]) -> RiskPrediction:
        """Calcula score de risco para um pedido"""
        
        factors = []
        
        # 1. Análise de topologia (grafo de imports)
        topology_factor = self._analyze_topology(graph, modules)
        factors.append(topology_factor)
        
        # 2. Tipo de módulo
        module_factor = self._analyze_module_type(modules)
        factors.append(module_factor)
        
        # 3. Densidade de erros
        error_factor = self._analyze_error_density(logs)
        factors.append(error_factor)
        
        # 4. Repetição histórica
        history_factor = self._analyze_history(history)
        factors.append(history_factor)
        
        # 5. Tamanho esperado do diff
        diff_factor = self._analyze_diff_size(strategos_plan)
        factors.append(diff_factor)
        
        # 6. Análise SCA
        sca_factor = self._analyze_sca(sca)
        factors.append(sca_factor)
        
        # Calcula score final
        risk_score = self._calculate_final_score(factors)
        
        # Determina recomendação
        recommendation = self._determine_recommendation(risk_score)
        
        # Calcula confiança
        confidence = self._calculate_confidence(factors)
        
        return RiskPrediction(
            risk_score=risk_score,
            factors=factors,
            recommendation=recommendation,
            confidence=confidence
        )
    
    def _analyze_topology(self, graph: Dict[str, Any], modules: Dict[str, Any]) -> RiskFactor:
        """Analisa risco baseado na topologia do grafo"""
        if not graph or "nodes" not in graph:
            return RiskFactor("topology", 0.0, "Grafo não disponível", 0.0)
        
        # Calcula centralidade dos nós afetados
        affected_nodes = []
        centrality_scores = []
        
        for node_path, node_data in graph.get("nodes", {}).items():
            if self._is_node_affected(node_path, modules):
                affected_nodes.append(node_path)
                
                # Calcula centralidade (in-degree + out-degree)
                in_degree = len([edge for edge in graph.get("edges", []) 
                               if edge.get("to") == node_path])
                out_degree = len([edge for edge in graph.get("edges", []) 
                                if edge.get("from") == node_path])
                
                centrality = (in_degree + out_degree) / max(len(graph.get("nodes", {})), 1)
                centrality_scores.append(centrality)
        
        if not centrality_scores:
            return RiskFactor("topology", 0.0, "Nenhum nó afetado", 0.0)
        
        # Score baseado na centralidade média
        avg_centrality = sum(centrality_scores) / len(centrality_scores)
        topology_score = min(100, avg_centrality * 200)  # Normaliza para 0-100
        
        evidence = f"Centralidade média: {avg_centrality:.2f} ({len(affected_nodes)} nós afetados)"
        
        return RiskFactor("topology", self.factor_weights["topology"], evidence, topology_score)
    
    def _analyze_module_type(self, modules: Dict[str, Any]) -> RiskFactor:
        """Analisa risco baseado no tipo de módulo"""
        if not modules:
            return RiskFactor("module_type", 0.0, "Módulos não disponíveis", 0.0)
        
        # Identifica tipos de módulos afetados
        affected_types = set()
        for module_info in modules.values():
            if isinstance(module_info, dict) and "type" in module_info:
                affected_types.add(module_info["type"])
        
        if not affected_types:
            return RiskFactor("module_type", 0.0, "Tipos de módulo não identificados", 0.0)
        
        # Calcula score baseado no tipo mais arriscado
        max_risk = 0
        for module_type in affected_types:
            risk = self.module_risk_scores.get(module_type, 50)
            max_risk = max(max_risk, risk)
        
        evidence = f"Tipos afetados: {', '.join(affected_types)} (max risco: {max_risk})"
        
        return RiskFactor("module_type", self.factor_weights["module_type"], evidence, max_risk)
    
    def _analyze_error_density(self, logs: Dict[str, str]) -> RiskFactor:
        """Analisa densidade de erros nos logs"""
        if not logs:
            return RiskFactor("error_density", 0.0, "Logs não disponíveis", 0.0)
        
        total_errors = 0
        error_types = {}
        
        for log_type, content in logs.items():
            # Conta erros por tipo
            if "lint" in log_type.lower():
                errors = content.count("error") + content.count("Error")
                error_types["lint"] = errors
                total_errors += errors
            elif "test" in log_type.lower():
                errors = content.count("FAIL") + content.count("failed")
                error_types["test"] = errors
                total_errors += errors
            elif "build" in log_type.lower():
                errors = content.count("error") + content.count("Error")
                error_types["build"] = errors
                total_errors += errors
        
        # Score baseado na densidade de erros
        error_density = total_errors / max(len(logs), 1)
        density_score = min(100, error_density * 10)  # Normaliza
        
        evidence = f"Total erros: {total_errors} ({error_types})"
        
        return RiskFactor("error_density", self.factor_weights["error_density"], evidence, density_score)
    
    def _analyze_history(self, history: Dict[str, Any]) -> RiskFactor:
        """Analisa repetição histórica"""
        if not history:
            return RiskFactor("history", 0.0, "Histórico não disponível", 0.0)
        
        # Analisa padrões de repetição
        repeat_count = history.get("repeat_errors", 0)
        regression_count = history.get("regressions", 0)
        total_episodes = history.get("total_episodes", 1)
        
        # Calcula taxas
        repeat_rate = repeat_count / total_episodes
        regression_rate = regression_count / total_episodes
        
        # Score baseado em repetições e regressões
        history_score = (repeat_rate * 50) + (regression_rate * 100)
        history_score = min(100, history_score)
        
        evidence = f"Repetições: {repeat_count}/{total_episodes}, Regressões: {regression_count}/{total_episodes}"
        
        return RiskFactor("history", self.factor_weights["history"], evidence, history_score)
    
    def _analyze_diff_size(self, strategos_plan: Dict[str, Any]) -> RiskFactor:
        """Analisa tamanho esperado do diff"""
        if not strategos_plan:
            return RiskFactor("diff_size", 0.0, "Plano não disponível", 0.0)
        
        # Estima tamanho baseado no plano
        estimated_size = strategos_plan.get("estimated_diff_size", 0)
        priority_order = strategos_plan.get("priority_order", [])
        
        # Score baseado no tamanho estimado
        if estimated_size <= 10:
            size_score = 20
        elif estimated_size <= 50:
            size_score = 40
        elif estimated_size <= 100:
            size_score = 60
        elif estimated_size <= 200:
            size_score = 80
        else:
            size_score = 100
        
        evidence = f"Tamanho estimado: {estimated_size} linhas, {len(priority_order)} erros prioritários"
        
        return RiskFactor("diff_size", self.factor_weights["diff_size"], evidence, size_score)
    
    def _analyze_sca(self, sca: Dict[str, Any]) -> RiskFactor:
        """Analisa vulnerabilidades SCA"""
        if not sca:
            return RiskFactor("sca", 0.0, "SCA não disponível", 0.0)
        
        vulnerabilities = sca.get("vulnerabilities", [])
        risk_score = sca.get("risk_score", 0.0)
        
        # Conta vulnerabilidades por severidade
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for vuln in vulnerabilities:
            severity = vuln.get("severity", "medium")
            if severity in severity_counts:
                severity_counts[severity] += 1
        
        # Score baseado no risco SCA
        sca_score = risk_score * 100  # Converte para 0-100
        
        evidence = f"Vulns: {severity_counts}, Score: {risk_score:.2f}"
        
        return RiskFactor("sca", self.factor_weights["sca"], evidence, sca_score)
    
    def _is_node_affected(self, node_path: str, modules: Dict[str, Any]) -> bool:
        """Verifica se um nó está afetado"""
        # Simplificado - verifica se o caminho está nos módulos
        return any(node_path in module_info.get("name", "") 
                  for module_info in modules.values())
    
    def _calculate_final_score(self, factors: List[RiskFactor]) -> float:
        """Calcula score final ponderado"""
        if not factors:
            return 0.0
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        for factor in factors:
            weighted_sum += factor.score * factor.weight
            total_weight += factor.weight
        
        if total_weight == 0:
            return 0.0
        
        return weighted_sum / total_weight
    
    def _determine_recommendation(self, risk_score: float) -> str:
        """Determina recomendação baseada no score"""
        if risk_score >= self.thresholds["block"]:
            return "block"
        elif risk_score >= self.thresholds["advisory"]:
            return "advisory"
        else:
            return "proceed"
    
    def _calculate_confidence(self, factors: List[RiskFactor]) -> float:
        """Calcula confiança da predição"""
        if not factors:
            return 0.0
        
        # Confiança baseada na qualidade dos dados disponíveis
        available_factors = len([f for f in factors if f.score > 0])
        total_factors = len(factors)
        
        return available_factors / total_factors
    
    def generate_risk_report(self, prediction: RiskPrediction) -> str:
        """Gera relatório de risco"""
        report = ["# Relatório de Predição de Risco v1\n"]
        
        report.append(f"## Score de Risco: **{prediction.risk_score:.1f}/100**")
        report.append(f"## Recomendação: **{prediction.recommendation.upper()}**")
        report.append(f"## Confiança: **{prediction.confidence:.1%}**")
        report.append("")
        
        report.append("## Fatores de Risco")
        for factor in prediction.factors:
            status = "🔴" if factor.score > 70 else "🟡" if factor.score > 40 else "🟢"
            report.append(f"### {status} {factor.name.title()} (Score: {factor.score:.1f})")
            report.append(f"- **Peso**: {factor.weight:.1%}")
            report.append(f"- **Evidência**: {factor.evidence}")
            report.append("")
        
        report.append("## Thresholds")
        report.append(f"- **Advisory**: ≥{self.thresholds['advisory']}")
        report.append(f"- **Block**: ≥{self.thresholds['block']}")
        
        return "\n".join(report)
