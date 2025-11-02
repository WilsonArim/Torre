from __future__ import annotations
import json, time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

class ResearchTrigger(Enum):
    HIGH_UNCERTAINTY = "high_uncertainty"
    BREAKING_CHANGE = "breaking_change"
    STATE_OF_ART = "state_of_art"

@dataclass
class ResearchSource:
    """Fonte de pesquisa"""
    title: str
    url: str
    date: str
    type: str  # "official_doc", "rfc", "repo", "benchmark"

@dataclass
class VanguardBrief:
    """Brief de pesquisa Vanguard"""
    brief_md: str
    sources: List[ResearchSource]
    confidence: float  # 0-1
    trigger: ResearchTrigger
    admin_approval_required: bool

class VanguardRadar:
    """
    Vanguard Radar: pesquisa dirigida de referências de engenharia
    Objetivo: descoberta dirigida + admin gate para CANON
    """
    
    def __init__(self):
        # Domínios whitelist para pesquisa
        self.whitelist_domains = [
            "github.com", "gitlab.com", "docs.python.org", "nodejs.org",
            "react.dev", "vuejs.org", "angular.io", "typescriptlang.org",
            "developer.mozilla.org", "stackoverflow.com", "npmjs.com",
            "pypi.org", "crates.io", "go.dev", "rust-lang.org"
        ]
        
        # Triggers para pesquisa
        self.research_triggers = {
            "high_uncertainty": 0.8,  # Threshold de incerteza
            "breaking_change": 0.9,   # Threshold para breaking changes
            "state_of_art": 0.7       # Threshold para state-of-art
        }
        
        # Base de conhecimento local (simulada)
        self.local_knowledge = {
            "react": {
                "latest_version": "18.2.0",
                "breaking_changes": ["React 18", "Concurrent Features"],
                "best_practices": ["hooks", "functional_components"]
            },
            "typescript": {
                "latest_version": "5.0.0",
                "breaking_changes": ["TS 5.0", "Decorators"],
                "best_practices": ["strict_mode", "type_safety"]
            },
            "python": {
                "latest_version": "3.12.0",
                "breaking_changes": ["Python 3.12", "Type Hints"],
                "best_practices": ["type_hints", "async_await"]
            }
        }
    
    def should_research(self, 
                       topic: str,
                       repo_signals: Dict[str, Any],
                       questions: List[str]) -> bool:
        """Decide se deve fazer pesquisa"""
        
        # Verifica triggers
        uncertainty = repo_signals.get("uncertainty", 0.0)
        breaking_changes = repo_signals.get("breaking_changes", [])
        state_of_art_needed = repo_signals.get("state_of_art", False)
        
        # Trigger 1: Alta incerteza
        if uncertainty >= self.research_triggers["high_uncertainty"]:
            return True
        
        # Trigger 2: Breaking changes
        if breaking_changes and len(breaking_changes) > 0:
            return True
        
        # Trigger 3: State-of-art necessário
        if state_of_art_needed:
            return True
        
        # Trigger 4: Perguntas específicas que requerem pesquisa
        research_keywords = ["latest", "best practice", "performance", "security", "breaking"]
        for question in questions:
            if any(keyword in question.lower() for keyword in research_keywords):
                return True
        
        return False
    
    def research_topic(self, 
                      topic: str,
                      repo_signals: Dict[str, Any],
                      questions: List[str]) -> VanguardBrief:
        """Executa pesquisa sobre um tópico"""
        
        # Determina trigger
        trigger = self._determine_trigger(repo_signals, questions)
        
        # Simula pesquisa (em produção, faria web scraping/API calls)
        research_results = self._simulate_research(topic, trigger)
        
        # Gera brief
        brief_md = self._generate_brief(topic, research_results, questions)
        
        # Determina confiança
        confidence = self._calculate_confidence(research_results)
        
        # Verifica se precisa aprovação admin
        admin_approval_required = confidence < 0.6 or trigger == ResearchTrigger.BREAKING_CHANGE
        
        return VanguardBrief(
            brief_md=brief_md,
            sources=research_results["sources"],
            confidence=confidence,
            trigger=trigger,
            admin_approval_required=admin_approval_required
        )
    
    def _determine_trigger(self, repo_signals: Dict[str, Any], questions: List[str]) -> ResearchTrigger:
        """Determina trigger da pesquisa"""
        
        uncertainty = repo_signals.get("uncertainty", 0.0)
        breaking_changes = repo_signals.get("breaking_changes", [])
        state_of_art_needed = repo_signals.get("state_of_art", False)
        
        if breaking_changes and len(breaking_changes) > 0:
            return ResearchTrigger.BREAKING_CHANGE
        elif uncertainty >= self.research_triggers["high_uncertainty"]:
            return ResearchTrigger.HIGH_UNCERTAINTY
        elif state_of_art_needed:
            return ResearchTrigger.STATE_OF_ART
        else:
            return ResearchTrigger.HIGH_UNCERTAINTY  # Default
    
    def _simulate_research(self, topic: str, trigger: ResearchTrigger) -> Dict[str, Any]:
        """Simula pesquisa (em produção, faria pesquisa real)"""
        
        # Base de conhecimento simulada
        knowledge_base = {
            "react": {
                "title": "React Official Documentation",
                "url": "https://react.dev/reference/react",
                "date": "2024-01-15",
                "type": "official_doc",
                "content": "React 18 introduces concurrent features and automatic batching."
            },
            "typescript": {
                "title": "TypeScript Handbook",
                "url": "https://www.typescriptlang.org/docs/",
                "date": "2024-01-10",
                "type": "official_doc",
                "content": "TypeScript 5.0 brings improved performance and new decorators."
            },
            "performance": {
                "title": "Web Performance Best Practices",
                "url": "https://web.dev/performance/",
                "date": "2024-01-20",
                "type": "benchmark",
                "content": "Core Web Vitals and performance optimization techniques."
            },
            "security": {
                "title": "OWASP Top 10",
                "url": "https://owasp.org/www-project-top-ten/",
                "date": "2024-01-05",
                "type": "rfc",
                "content": "Most critical web application security risks."
            }
        }
        
        # Simula resultados baseados no tópico
        sources = []
        content_parts = []
        
        # Adiciona fontes relevantes
        for key, info in knowledge_base.items():
            if key.lower() in topic.lower():
                source = ResearchSource(
                    title=info["title"],
                    url=info["url"],
                    date=info["date"],
                    type=info["type"]
                )
                sources.append(source)
                content_parts.append(info["content"])
        
        # Adiciona fontes padrão se não encontrou específicas
        if not sources:
            default_source = ResearchSource(
                title="General Engineering Reference",
                url="https://github.com/engineering-best-practices",
                date=time.strftime("%Y-%m-%d"),
                type="repo"
            )
            sources.append(default_source)
            content_parts.append("General engineering best practices and patterns.")
        
        return {
            "sources": sources,
            "content": " ".join(content_parts),
            "topic": topic,
            "trigger": trigger
        }
    
    def _generate_brief(self, topic: str, research_results: Dict[str, Any], questions: List[str]) -> str:
        """Gera brief em markdown"""
        
        brief = [f"# Vanguard Brief: {topic}\n"]
        
        brief.append("## Resumo")
        brief.append(research_results["content"])
        brief.append("")
        
        brief.append("## Perguntas Respondidas")
        for i, question in enumerate(questions, 1):
            brief.append(f"{i}. {question}")
        brief.append("")
        
        brief.append("## Recomendações")
        brief.append("- Implementar seguindo as melhores práticas identificadas")
        brief.append("- Considerar impactos de breaking changes")
        brief.append("- Validar performance e segurança")
        brief.append("")
        
        brief.append("## Fontes")
        for source in research_results["sources"]:
            brief.append(f"- [{source.title}]({source.url}) ({source.date})")
        brief.append("")
        
        brief.append("## Nota")
        brief.append("Este brief foi gerado automaticamente. Verificar fontes antes de aplicar.")
        
        return "\n".join(brief)
    
    def _calculate_confidence(self, research_results: Dict[str, Any]) -> float:
        """Calcula confiança da pesquisa"""
        
        sources = research_results["sources"]
        if not sources:
            return 0.0
        
        # Confiança baseada na qualidade das fontes
        confidence = 0.0
        
        for source in sources:
            if source.type == "official_doc":
                confidence += 0.4
            elif source.type == "rfc":
                confidence += 0.3
            elif source.type == "repo":
                confidence += 0.2
            elif source.type == "benchmark":
                confidence += 0.3
        
        # Normaliza para 0-1
        return min(1.0, confidence / len(sources))
    
    def can_add_to_canon(self, brief: VanguardBrief, admin_approval: bool = False) -> bool:
        """Verifica se pode adicionar ao CANON"""
        
        # Precisa confiança alta
        if brief.confidence < 0.6:
            return False
        
        # Breaking changes precisam aprovação admin
        if brief.trigger == ResearchTrigger.BREAKING_CHANGE and not admin_approval:
            return False
        
        # Alta incerteza precisa aprovação admin
        if brief.trigger == ResearchTrigger.HIGH_UNCERTAINTY and not admin_approval:
            return False
        
        return True
    
    def generate_research_report(self, brief: VanguardBrief) -> str:
        """Gera relatório da pesquisa"""
        
        report = ["# Relatório Vanguard Radar\n"]
        
        report.append(f"## Tópico Pesquisado")
        report.append(f"- **Trigger**: {brief.trigger.value}")
        report.append(f"- **Confiança**: {brief.confidence:.1%}")
        report.append(f"- **Aprovação Admin**: {'Sim' if brief.admin_approval_required else 'Não'}")
        report.append("")
        
        report.append("## Fontes Encontradas")
        for source in brief.sources:
            report.append(f"- **{source.title}**")
            report.append(f"  - URL: {source.url}")
            report.append(f"  - Data: {source.date}")
            report.append(f"  - Tipo: {source.type}")
            report.append("")
        
        report.append("## Status CANON")
        can_add = self.can_add_to_canon(brief)
        status = "✅ PODE ADICIONAR" if can_add else "❌ NÃO PODE ADICIONAR"
        report.append(f"- **Status**: {status}")
        
        if not can_add:
            if brief.confidence < 0.6:
                report.append("- **Motivo**: Confiança muito baixa")
            elif brief.admin_approval_required:
                report.append("- **Motivo**: Precisa aprovação admin")
        
        return "\n".join(report)
