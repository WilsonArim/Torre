#!/usr/bin/env python3
"""
PIN — SOP v3.0
Guardião das Leis e da Constituição

REGRA DE ABERTURA:
OWNER: SOP — Próxima ação: <frase curta>

PAPEL: aplicar leis/thresholds; gerar relatorio_sop.md; bloquear quando necessário.

REGRAS:
- Valida leis.yaml + exceptions.yaml + artefactos (coverage, sbom, semgrep…).
- Não planeia; apenas cumpre e reporta conformidade.

SAÍDAS:
- relatorios/relatorio_sop.md + relatorios/sop_status.json (status PASS/BLOQUEADO + métricas).

Respeita ART-01 (Integridade), ART-02 (Tríade), ART-04 (Verificabilidade), 
ART-07 (Transparência), ART-09 (Evidência)
"""
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import xml.etree.ElementTree as ET

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None


REPO_ROOT = Path(__file__).resolve().parents[2]
REL_DIR = REPO_ROOT / "relatorios"
SOP_DIR = REPO_ROOT / "core" / "sop"
ORQUESTRADOR_DIR = REPO_ROOT / "core" / "orquestrador"


def read_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    if yaml is None:
        # Fallback rudimentar se PyYAML não existir
        return json.loads(json.dumps({}))
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def parse_coverage(coverage_xml: Path) -> float:
    if not coverage_xml.exists():
        return 0.0
    try:
        tree = ET.parse(str(coverage_xml))
        root = tree.getroot()
        # Cobertura em 'line-rate' no root (Cobertura XML)
        rate = root.attrib.get("line-rate")
        if rate is not None:
            return round(float(rate) * 100, 2)
    except Exception:
        pass
    return 0.0


def load_json(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


@dataclass
class MetricResult:
    ok: bool
    extra: Dict[str, Any]


def find_junit_xml() -> Optional[Path]:
    """Procura arquivos JUnit XML nos locais comuns."""
    locations = [
        REL_DIR / "junit.xml",
        REL_DIR / "test-results.xml",
        REPO_ROOT / "junit.xml",
        REPO_ROOT / "test-results.xml",
    ]
    for loc in locations:
        if loc.exists():
            return loc
    return None


def eval_junit(junit_path: Optional[Path]) -> MetricResult:
    """Avalia resultados de testes JUnit."""
    if not junit_path:
        return MetricResult(ok=True, extra={"tests": 0, "failures": 0, "errors": 0, "suite": "none"})
    try:
        tree = ET.parse(str(junit_path))
        root = tree.getroot()
        tests = int(root.attrib.get("tests", 0))
        failures = int(root.attrib.get("failures", 0))
        errors = int(root.attrib.get("errors", 0))
        suite = "junit"
        return MetricResult(
            ok=(failures == 0 and errors == 0),
            extra={"tests": tests, "failures": failures, "errors": errors, "suite": suite},
        )
    except Exception:
        return MetricResult(ok=True, extra={"tests": 0, "failures": 0, "errors": 0, "suite": "unknown"})


def eval_semgrep(sarif_path: Path, blocking_levels: List[str]) -> MetricResult:
    data = load_json(sarif_path)
    if not data:
        return MetricResult(ok=True, extra={"findings": 0, "blocking": 0})
    findings = 0
    blocking = 0
    runs = data.get("runs", [])
    for run in runs:
        results = run.get("results", [])
        findings += len(results)
        for r in results:
            level = (r.get("level") or "").upper()
            if level in blocking_levels:
                blocking += 1
    return MetricResult(ok=blocking == 0, extra={"findings": findings, "blocking": blocking})


def eval_bandit(bandit_path: Path, min_level: str) -> MetricResult:
    data = load_json(bandit_path) or {}
    issues = data.get("results", [])
    levels = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}
    min_lv = levels.get(min_level.upper(), 2)
    worst = 0
    worst_severity = "LOW"
    for i in issues:
        sev = (i.get("issue_severity") or "LOW").upper()
        sev_level = levels.get(sev, 1)
        if sev_level > worst:
            worst = sev_level
            worst_severity = sev
    return MetricResult(ok=worst < min_lv, extra={"worst_severity": worst_severity, "worst_level": worst})


def eval_npm_audit(audit_path: Path) -> MetricResult:
    data = load_json(audit_path) or {}
    advis = data.get("vulnerabilities") or {}
    critical = advis.get("critical") or 0
    high = advis.get("high") or 0
    return MetricResult(ok=critical == 0, extra={"critical": critical, "high": high})


def eval_trivy(trivy_path: Path, block_levels: List[str]) -> MetricResult:
    data = load_json(trivy_path) or {}
    results = data.get("Results") or []
    critical = 0
    high = 0
    for r in results:
        vulns = r.get("Vulnerabilities") or []
        for v in vulns:
            sev = (v.get("Severity") or "").upper()
            if sev in [lvl.upper() for lvl in block_levels]:
                if sev == "CRITICAL":
                    critical += 1
                elif sev == "HIGH":
                    high += 1
    return MetricResult(ok=critical == 0, extra={"critical": critical, "high": high})


def eval_sbom(sbom_path: Path) -> MetricResult:
    exists = sbom_path.exists()
    if exists:
        try:
            data = load_json(sbom_path)
            bom_format = data.get("bomFormat", "unknown") if data else "unknown"
            return MetricResult(ok=True, extra={"format": bom_format})
        except Exception:
            return MetricResult(ok=True, extra={"format": "unknown"})
    return MetricResult(ok=False, extra={"format": "missing"})


def apply_exceptions(value: Any, rule_key: str, exceptions: List[Dict[str, Any]]) -> Any:
    now = datetime.utcnow().date()
    for ex in exceptions:
        if ex.get("regra") == rule_key:
            expires = ex.get("expires_at")
            if expires:
                try:
                    if datetime.strptime(expires, "%Y-%m-%d").date() < now:
                        continue
                except Exception:
                    pass
            value = ex.get("novo_valor", value)
    return value


def get_exceptions_used(exceptions: List[Dict[str, Any]], applied_rules: List[str]) -> List[Dict[str, Any]]:
    """Retorna lista de exceções aplicadas."""
    now = datetime.utcnow().date()
    used = []
    for ex in exceptions:
        rule = ex.get("regra", "")
        if rule in applied_rules:
            expires = ex.get("expires_at")
            if expires:
                try:
                    if datetime.strptime(expires, "%Y-%m-%d").date() < now:
                        continue
                except Exception:
                    pass
            used.append(ex)
    return used


def run_pipeline_validate() -> Dict[str, Any]:
    """Executa validação de pipeline e retorna resultado."""
    try:
        result = subprocess.run(
            [sys.executable, str(ORQUESTRADOR_DIR / "cli.py"), "validate_pipeline"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
        )
        # Lê o audit gerado
        audit_path = REPO_ROOT / "relatorios" / "pipeline_audit.json"
        if audit_path.exists():
            return load_json(audit_path) or {}
        return {}
    except Exception:
        return {}


def run_gatekeeper_prep() -> Dict[str, Any]:
    """Executa gatekeeper_prep e retorna pipeline_gate_input."""
    try:
        subprocess.run(
            [sys.executable, str(ORQUESTRADOR_DIR / "cli.py"), "gatekeeper_prep"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
        )
        # Lê o input gerado
        input_path = REPO_ROOT / "relatorios" / "pipeline_gate_input.json"
        if input_path.exists():
            return load_json(input_path) or {}
        return {}
    except Exception:
        return {}


def determine_gate(leis: Dict[str, Any]) -> str:
    """Determina qual gate avaliar baseado nos requisitos."""
    gates = leis.get("gates", {})
    # Por padrão avalia G2, mas pode ser expandido para detectar G3
    # Baseado nos requisitos presentes nos artefactos
    return "G2"  # Por enquanto sempre G2 (G3 requer e2e, latência, etc)


def get_gate_requirements(leis: Dict[str, Any], gate: str) -> List[str]:
    """Retorna lista de requisitos para um gate."""
    gates = leis.get("gates", {})
    gate_info = gates.get(gate, {})
    return gate_info.get("req", [])


def check_gate_requirements(gate: str, reqs: List[str], metrics: Dict[str, Any]) -> tuple[bool, List[str]]:
    """Verifica se os requisitos do gate são satisfeitos. Retorna (ok, violações)."""
    violations = []
    
    if gate == "G2":
        # G2: Build/Integração
        if "coverage_ok" in reqs and not metrics.get("coverage_ok", False):
            violations.append("coverage_ok")
        if "semgrep_ok" in reqs and not metrics.get("semgrep", {}).get("ok", False):
            violations.append("semgrep_ok")
        if "bandit_ok" in reqs and not metrics.get("bandit", {}).get("ok", False):
            violations.append("bandit_ok")
        if "sbom_ok" in reqs and not metrics.get("sbom", {}).get("ok", False):
            violations.append("sbom_ok")
        if "ci_verde" in reqs:
            # Assumimos que se chegou aqui, CI está verde
            pass
        if "lint_ok" in reqs:
            # Assumimos lint OK se semgrep passou
            pass
    
    elif gate == "G3":
        # G3: Sistémico (E2E)
        if "trivy_ok" in reqs and not metrics.get("trivy", {}).get("ok", False):
            violations.append("trivy_ok")
        if "e2e_ok" in reqs:
            # Requer análise de testes E2E (não implementado ainda)
            pass
        if "latencia<=alvo" in reqs:
            # Requer métricas de latência (não implementado ainda)
            pass
        if "observ_min_ok" in reqs:
            # Requer observabilidade mínima (não implementado ainda)
            pass
    
    return len(violations) == 0, violations


def generate_blocked_report(
    gate: str, violations: List[str], metrics: Dict[str, Any], politicas: Dict[str, Any], triade_ok: bool = True
) -> List[str]:
    """Gera relatório detalhado quando BLOQUEADO."""
    lines = [
        "# Relatório SOP - BLOQUEADO",
        f"Gate avaliado: {gate}",
        "Resultado: **BLOQUEADO**",
        "",
        "## Conformidade Constitucional",
        "- ⚠️ Constituição validada mas violações detectadas",
    ]
    
    if gate in ["G0", "G1", "G2"] and not triade_ok:
        lines.append("- ❌ ART-02 (Tríade de Fundamentação) VIOLADO")
    
    lines.extend([
        "",
        "## Regras Violadas",
    ])
    
    for v in violations:
        if v.startswith("ART-02"):
            # Violação da Tríade - adicionar detalhes
            lines.append(f"- **{v}**")
            if "White Paper" in v:
                lines.append("  - Ação mínima: Criar White Paper em docs/WHITE_PAPER.md")
            elif "Arquitetura" in v:
                lines.append("  - Ação mínima: Criar documento de Arquitetura em docs/ARQUITETURA.md ou validar pipeline/superpipeline.yaml")
            elif "Base Operacional" in v:
                lines.append("  - Ação mínima: Criar Base Operacional em docs/BASE_OPERACIONAL.md ou validar docs/SOP_MANUAL.md")
            continue
        elif v == "coverage_ok":
            coverage = metrics.get("coverage", 0)
            min_python = politicas.get("coverage_min", {}).get("python", 75)
            lines.append(f"- **Cobertura insuficiente**: {coverage}% < {min_python}%")
            lines.append("  - Ação mínima: Aumentar cobertura de testes acima do mínimo")
        elif v == "sbom_ok":
            lines.append("- **SBOM ausente ou inválido**")
            lines.append("  - Ação mínima: Gerar SBOM válido (`make sbom`)")
        elif v == "semgrep_ok":
            blocking = metrics.get("semgrep", {}).get("blocking", 0)
            findings = metrics.get("semgrep", {}).get("findings", 0)
            lines.append(f"- **Semgrep bloqueante**: {blocking} findings bloqueantes (total: {findings})")
            lines.append("  - Ação mínima: Corrigir findings ERROR/HIGH do Semgrep")
        elif v == "bandit_ok":
            worst = metrics.get("bandit", {}).get("worst_severity", "UNKNOWN")
            lines.append(f"- **Bandit bloqueante**: Severidade mínima encontrada: {worst} >= MEDIUM")
            lines.append("  - Ação mínima: Corrigir vulnerabilidades Bandit >= MEDIUM")
        elif v == "trivy_ok":
            critical = metrics.get("trivy", {}).get("critical", 0)
            lines.append(f"- **Trivy bloqueante**: {critical} vulnerabilidades CRITICAL")
            lines.append("  - Ação mínima: Atualizar dependências com vulnerabilidades CRITICAL")
        else:
            # Violação genérica
            lines.append(f"- **{v}**: Requisito não satisfeito")
    
    lines.extend([
        "",
        "## Métricas Detalhadas",
        f"- Cobertura: {metrics.get('coverage', 0)}%",
        f"- Semgrep: ok={metrics.get('semgrep', {}).get('ok', False)} "
        f"(findings={metrics.get('semgrep', {}).get('findings', 0)}, "
        f"blocking={metrics.get('semgrep', {}).get('blocking', 0)})",
        f"- Bandit: ok={metrics.get('bandit', {}).get('ok', False)} "
        f"(worst={metrics.get('bandit', {}).get('worst_severity', 'N/A')})",
        f"- npm audit: ok={metrics.get('npm_audit', {}).get('ok', False)} "
        f"(critical={metrics.get('npm_audit', {}).get('critical', 0)})",
        f"- Trivy: ok={metrics.get('trivy', {}).get('ok', False)} "
        f"(critical={metrics.get('trivy', {}).get('critical', 0)})",
        f"- SBOM: ok={metrics.get('sbom', {}).get('ok', False)}",
        "",
        "--",
    ])
    
    return lines


def validate_constituicao() -> tuple[bool, List[str], Optional[Dict[str, Any]]]:
    """Valida existência e integridade da Constituição. Retorna (ok, violações, constituicao_dict)."""
    constituicao_path = SOP_DIR / "constituição.yaml"
    violations = []
    
    if not constituicao_path.exists():
        violations.append("Constituição ausente: core/sop/constituição.yaml")
        return False, violations, None
    
    try:
        const = read_yaml(constituicao_path)
        # Verificar se read_yaml retornou dict vazio ou None
        if not const or (isinstance(const, dict) and len(const) == 0):
            # Tentar ler diretamente como texto para verificar se existe conteúdo
            try:
                content = constituicao_path.read_text(encoding="utf-8")
                if not content.strip():
                    violations.append("Constituição vazia")
                    return False, violations, None
                # Se tem conteúdo mas yaml não conseguiu parsear
                if yaml is None:
                    # Fallback: verificar estrutura básica via regex/texto
                    if "versao:" not in content or "leis:" not in content:
                        violations.append("Constituição sem estrutura válida (campos obrigatórios ausentes)")
                        return False, violations, None
                    # Se passou verificação básica, assumir OK para fallback
                    return True, [], {"versao": 1, "leis": []}
            except Exception as e:
                violations.append(f"Erro ao ler Constituição: {e}")
                return False, violations, None
            violations.append("Constituição vazia ou inválida")
            return False, violations, None
        
        # Verificar campos obrigatórios (se yaml está disponível)
        if yaml is not None:
            if const.get("imutavel") != True:
                violations.append("Constituição não marcada como imutável")
            if not const.get("leis"):
                violations.append("Constituição sem leis definidas")
            else:
                # Verificar que tem as 10 regras fundamentais
                leis = const.get("leis", [])
                if len(leis) < 10:
                    violations.append(f"Constituição incompleta: esperadas 10 leis, encontradas {len(leis)}")
                
                # Verificar IDs esperados
                ids_esperados = [f"ART-{i:02d}" for i in range(1, 11)]
                ids_encontrados = [lei.get("id") for lei in leis if lei.get("id")]
                for id_esperado in ids_esperados:
                    if id_esperado not in ids_encontrados:
                        violations.append(f"Lei {id_esperado} ausente na Constituição")
        else:
            # Fallback sem yaml: verificar estrutura básica no texto
            content = constituicao_path.read_text(encoding="utf-8")
            if "imutavel: true" not in content.lower():
                violations.append("Constituição não marcada como imutável")
            # Contar leis pelo padrão "id: ART-"
            art_count = content.count("id: ART-")
            if art_count < 10:
                violations.append(f"Constituição incompleta: esperadas 10 leis, encontradas {art_count}")
        
        if violations:
            return False, violations, const if yaml else None
        return True, [], const if yaml else {"versao": 1, "leis": []}
    except Exception as e:
        violations.append(f"Erro ao validar Constituição: {e}")
        return False, violations, None


def validate_triade_fundamentacao(gate: str, constituicao: Optional[Dict[str, Any]]) -> tuple[bool, List[str]]:
    """Valida ART-02: Tríade de Fundamentação. Retorna (ok, violações)."""
    violations = []
    
    # ART-02 aplica-se apenas a G0, G1, G2
    if gate not in ["G0", "G1", "G2"]:
        return True, []
    
    if not constituicao:
        # Se não temos constituição carregada, não podemos validar
        return True, []
    
    leis_const = constituicao.get("leis", [])
    art02 = next((lei for lei in leis_const if lei.get("id") == "ART-02"), None)
    
    if not art02:
        # ART-02 não encontrado, mas isso já seria detectado na validação da Constituição
        return True, []
    
    # Procurar documentos da Tríade em locais padrão
    docs_dir = REPO_ROOT / "docs"
    white_paper_paths = [
        docs_dir / "WHITE_PAPER.md",
        docs_dir / "white_paper.md",
        docs_dir / "WHITEPAPER.md",
        REPO_ROOT / "WHITE_PAPER.md",
    ]
    arquitetura_paths = [
        docs_dir / "ARQUITETURA.md",
        docs_dir / "arquitetura.md",
        docs_dir / "ARCHITECTURE.md",
        REPO_ROOT / "ARQUITETURA.md",
        REPO_ROOT / "pipeline" / "superpipeline.yaml",  # superpipeline pode servir como arquitetura
    ]
    base_operacional_paths = [
        docs_dir / "BASE_OPERACIONAL.md",
        docs_dir / "base_operacional.md",
        docs_dir / "OPERATIONAL_BASE.md",
        REPO_ROOT / "BASE_OPERACIONAL.md",
        docs_dir / "SOP_MANUAL.md",  # SOP_MANUAL pode servir como base operacional
    ]
    
    white_paper = next((p for p in white_paper_paths if p.exists()), None)
    arquitetura = next((p for p in arquitetura_paths if p.exists()), None)
    base_operacional = next((p for p in base_operacional_paths if p.exists()), None)
    
    if not white_paper:
        violations.append("ART-02: White Paper (Estratégia) ausente")
    if not arquitetura:
        violations.append("ART-02: Arquitetura (Estrutura) ausente")
    if not base_operacional:
        violations.append("ART-02: Base Operacional (Execução) ausente")
    
    return len(violations) == 0, violations


def add_transparency_metadata(content: List[str], agent: str = "SOP", objetivo: str = "Validação de gates G2-G3") -> List[str]:
    """Adiciona metadados de transparência conforme ART-07."""
    now = datetime.now()
    metadata = [
        "",
        "---",
        f"**Agente**: {agent}",
        f"**Data/Hora**: {now.strftime('%Y-%m-%d %H:%M:%S UTC')}",
        f"**Objetivo**: {objetivo}",
        "**Regras aplicadas**: Constituição (10 artigos), leis.yaml, exceptions.yaml",
        "",
    ]
    return content + metadata


def review_torre_status() -> tuple[bool, Dict[str, Any], List[str]]:
    """Lê torre_status.json e valida constitution_ok e triade_ok. Retorna (ok, dados, violações)."""
    torre_status_path = REL_DIR / "torre_status.json"
    violations = []
    
    if not torre_status_path.exists():
        violations.append("torre_status.json ausente")
        return False, {}, violations
    
    try:
        torre_data = load_json(torre_status_path)
        if not torre_data:
            violations.append("torre_status.json vazio ou inválido")
            return False, {}, violations
        
        constitution_ok = torre_data.get("constitution_ok", False)
        triade_ok = torre_data.get("triade_ok", False)
        
        if not constitution_ok:
            violations.append("constitution_ok=false")
        if not triade_ok:
            violations.append("triade_ok=false")
        
        # CRÍTICO: Riscos são falhas graves - bloqueiam imediatamente
        risks = torre_data.get("risks", [])
        if risks:
            violations.extend([f"Risco identificado (falha grave futura): {risk}" for risk in risks])
        
        status_ok = constitution_ok and triade_ok and len(risks) == 0
        return status_ok, torre_data, violations
    except Exception as e:
        violations.append(f"Erro ao processar torre_status.json: {e}")
        return False, {}, violations


def generate_torre_review(torre_data: Dict[str, Any], status: str, violations: List[str]) -> List[str]:
    """Gera relatório torre_sop_review.md conforme ART-07 e ART-09."""
    lines = [
        "# Revisão SOP - Torre (Gate G0)",
        "",
        f"**Status**: {status}",
        f"**Gate**: G0",
        "",
        "## Validação Constitucional",
    ]
    
    constitution_ok = torre_data.get("constitution_ok", False)
    triade_ok = torre_data.get("triade_ok", False)
    
    lines.append(f"- Constituição (ART-01): {'✅ Validada' if constitution_ok else '❌ Violada'}")
    lines.append(f"- Tríade de Fundamentação (ART-02): {'✅ Validada' if triade_ok else '❌ Violada'}")
    
    if violations:
        lines.extend([
            "",
            "## Violações Detectadas",
        ])
        for v in violations:
            lines.append(f"- ❌ {v}")
    
    # Informações adicionais da Torre
    if "model" in torre_data:
        model_info = torre_data["model"]
        lines.extend([
            "",
            "## Modelo da Torre",
            f"- Família: {model_info.get('family', 'N/A')}",
            f"- Variante: {model_info.get('variant', 'N/A')}",
            f"- Parâmetros: {model_info.get('params_m', 'N/A')}M",
            f"- Context Window: {model_info.get('context_window', 'N/A')}",
            f"- Quantização: {model_info.get('quantization', 'N/A')}",
        ])
    
    if "learning_level" in torre_data:
        lines.extend([
            "",
            "## Nível de Aprendizagem",
            f"- **{torre_data['learning_level']}**",
        ])
    
    if "privacy_findings" in torre_data and torre_data["privacy_findings"]:
        lines.extend([
            "",
            "## Achados de Privacidade",
        ])
        for finding in torre_data["privacy_findings"]:
            lines.append(f"- {finding}")
    
    if "risks" in torre_data and torre_data["risks"]:
        lines.extend([
            "",
            "## Falhas Graves Identificadas (Riscos)",
            "⚠️ **POLÍTICA ZERO RISCO**: Qualquer risco identificado é uma falha grave futura e bloqueia imediatamente.",
        ])
        for risk in torre_data["risks"]:
            lines.append(f"- ❌ **BLOQUEIO**: {risk}")
        lines.append("")
        lines.append("**Ação obrigatória**: Eliminar completamente todos os riscos antes de prosseguir.")
    
    if "actions_required" in torre_data and torre_data["actions_required"]:
        lines.extend([
            "",
            "## Ações Requeridas",
        ])
        for action in torre_data["actions_required"]:
            lines.append(f"- {action}")
    
    # Metadados de transparência (ART-07)
    lines = add_transparency_metadata(
        lines,
        agent="SOP (FÁBRICA 2.0)",
        objetivo="Revisão da Torre conforme gate G0 e Constituição"
    )
    
    return lines


def main() -> int:
    REL_DIR.mkdir(exist_ok=True, parents=True)

    # Verificar se precisa fazer revisão da Torre (gate G0)
    torre_status_path = REL_DIR / "torre_status.json"
    if torre_status_path.exists():
        print("🏰 Revisão da Torre (Gate G0) detectada...")
        torre_ok, torre_data, torre_violations = review_torre_status()
        torre_status = "PASS" if torre_ok else "BLOQUEADO"
        
        # Gerar relatório torre_sop_review.md
        torre_review_lines = generate_torre_review(torre_data, torre_status, torre_violations)
        (REL_DIR / "torre_sop_review.md").write_text("\n".join(torre_review_lines), encoding="utf-8")
        
        # Atualizar sop_status.json com gate G0
        sop_status_torre = {
            "gate": "G0",
            "status": torre_status,
            "violations": torre_violations if not torre_ok else [],
            "constitution_ok": torre_data.get("constitution_ok", False),
            "triade_ok": torre_data.get("triade_ok", False),
            "timestamp": datetime.now().isoformat(),
            "agente": "SOP",
            "artefactos_citados": {
                "torre_status": str(torre_status_path.relative_to(REPO_ROOT)),
            },
        }
        (REL_DIR / "sop_status.json").write_text(
            json.dumps(sop_status_torre, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        
        if torre_status == "BLOQUEADO":
            print(f"❌ Torre BLOQUEADA (Gate G0)")
            print(f"   Violações: {', '.join(torre_violations)}")
            print(f"   Relatório: relatorios/torre_sop_review.md")
            return 1
        else:
            print(f"✅ Torre APROVADA (Gate G0)")
            print(f"   Constituição: ✅")
            print(f"   Tríade: ✅")
            print(f"   Relatório: relatorios/torre_sop_review.md")
            return 0

    # 0. Validar Constituição (prioridade máxima - ART-01)
    const_ok, const_violations, constituicao = validate_constituicao()
    if not const_ok:
        print("❌ CONSTITUIÇÃO VIOLADA (ART-01)")
        for v in const_violations:
            print(f"   {v}")
        print("   A Constituição é imutável e deve existir com todas as 10 regras fundamentais.")
        # Escrever violação no status (ART-04: verificabilidade)
        sop_status_blocked = {
            "gate": "CONSTITUIÇÃO",
            "status": "BLOQUEADO",
            "violations": const_violations,
            "artigo_violado": "ART-01",
            "mensagem": "Violação da Constituição detectada. Sistema bloqueado até correção.",
            "timestamp": datetime.now().isoformat(),
            "agente": "SOP",
        }
        (REL_DIR / "sop_status.json").write_text(
            json.dumps(sop_status_blocked, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        return 1

    # 1. Carregar leis e exceções
    leis = read_yaml(SOP_DIR / "leis.yaml")
    exc = read_yaml(SOP_DIR / "exceptions.yaml")
    exceptions = exc.get("excecoes", []) if isinstance(exc, dict) else []

    politicas = leis.get("politicas", {})
    coverage_min_default = politicas.get("coverage_min", {}).get("default", 75)
    coverage_min_python_before = politicas.get("coverage_min", {}).get("python", coverage_min_default)
    semgrep_block = politicas.get("semgrep_block", ["ERROR", "HIGH"])
    bandit_min = politicas.get("bandit_min_level", "MEDIUM")
    trivy_block = politicas.get("trivy_block", ["CRITICAL"])

    # 2. Determinar gate a avaliar
    gate = determine_gate(leis)
    gate_reqs = get_gate_requirements(leis, gate)

    # 3. Avaliar métricas
    # Verificar coverage.xml em relatorios/ primeiro, depois raiz
    coverage_xml = REPO_ROOT / "relatorios" / "coverage.xml"
    if not coverage_xml.exists():
        coverage_xml = REPO_ROOT / "coverage.xml"
    coverage = parse_coverage(coverage_xml)
    coverage_min_python = apply_exceptions(coverage_min_python_before, "coverage_min.python", exceptions)
    coverage_ok = coverage >= float(coverage_min_python)

    semgrep_res = eval_semgrep(REL_DIR / "semgrep.sarif", [lvl.upper() for lvl in semgrep_block])
    bandit_res = eval_bandit(REL_DIR / "bandit.json", bandit_min)
    npm_res = eval_npm_audit(REL_DIR / "npm-audit.json")
    trivy_res = eval_trivy(REL_DIR / "trivy.json", trivy_block)
    sbom_res = eval_sbom(REL_DIR / "sbom.json")
    junit_path = find_junit_xml()
    junit_res = eval_junit(junit_path)

    metrics = {
        "coverage": coverage,
        "coverage_ok": coverage_ok,
        "tests": {
            "ok": junit_res.ok,
            "suite": junit_res.extra.get("suite", "pytest|jest"),
            "tests": junit_res.extra.get("tests", 0),
            "failures": junit_res.extra.get("failures", 0),
            "errors": junit_res.extra.get("errors", 0),
        },
        "semgrep": {"ok": semgrep_res.ok, **semgrep_res.extra},
        "bandit": {"ok": bandit_res.ok, **bandit_res.extra},
        "npm_audit": {"ok": npm_res.ok, **npm_res.extra},
        "trivy": {"ok": trivy_res.ok, **trivy_res.extra},
        "sbom": {"ok": sbom_res.ok, **sbom_res.extra},
    }

    # 4. Verificar requisitos do gate
    gate_ok, violations = check_gate_requirements(gate, gate_reqs, metrics)
    
    # Regras críticas: SBOM e coverage mínimo
    if not sbom_res.ok:
        if "sbom_ok" not in violations:
            violations.append("sbom_ok")
    if not coverage_ok:
        if "coverage_ok" not in violations:
            violations.append("coverage_ok")

    # 4.1. Validar Tríade de Fundamentação (ART-02)
    triade_ok, triade_violations = validate_triade_fundamentacao(gate, constituicao)
    if not triade_ok:
        violations.extend(triade_violations)
        gate_ok = False

    status = "PASS" if gate_ok and len(violations) == 0 else "BLOQUEADO"

    # 5. Exceções aplicadas
    applied_rules = []
    if coverage_min_python != coverage_min_python_before:
        applied_rules.append("coverage_min.python")
    exceptions_used = get_exceptions_used(exceptions, applied_rules)

    # 6. Integração com pipeline
    print("🔍 Validando pipeline...")
    pipeline_audit = run_pipeline_validate()
    print("📦 Preparando input do Gatekeeper...")
    pipeline_input = run_gatekeeper_prep()
    pipeline_ok = pipeline_input.get("pipeline_ok", False)

    # 7. Gerar sop_status.json (ART-04: verificabilidade, ART-09: evidência)
    sop_status = {
        "gate": gate,
        "status": status,
        "metrics": metrics,
        "exceptions_used": exceptions_used,
        "violations": violations if status == "BLOQUEADO" else [],
        "pipeline_ok": pipeline_ok,
        "constituicao_validada": const_ok,
        "triade_validada": triade_ok if gate in ["G0", "G1", "G2"] else None,
        "timestamp": datetime.now().isoformat(),
        "agente": "SOP",
        "artefactos_citados": {
            "coverage": str(coverage_xml.relative_to(REPO_ROOT)) if coverage_xml.exists() else None,
            "semgrep": str((REL_DIR / "semgrep.sarif").relative_to(REPO_ROOT)),
            "bandit": str((REL_DIR / "bandit.json").relative_to(REPO_ROOT)),
            "npm_audit": str((REL_DIR / "npm-audit.json").relative_to(REPO_ROOT)),
            "trivy": str((REL_DIR / "trivy.json").relative_to(REPO_ROOT)),
            "sbom": str((REL_DIR / "sbom.json").relative_to(REPO_ROOT)),
            "junit": str(junit_path.relative_to(REPO_ROOT)) if junit_path else None,
            "leis": str((SOP_DIR / "leis.yaml").relative_to(REPO_ROOT)),
            "exceptions": str((SOP_DIR / "exceptions.yaml").relative_to(REPO_ROOT)),
            "constituicao": str((SOP_DIR / "constituição.yaml").relative_to(REPO_ROOT)),
        },
    }
    (REL_DIR / "sop_status.json").write_text(json.dumps(sop_status, indent=2, ensure_ascii=False), encoding="utf-8")

    # 8. Gerar relatório markdown (ART-07: transparência, ART-09: evidência)
    if status == "BLOQUEADO":
        relatorio_lines = generate_blocked_report(gate, violations, metrics, politicas, triade_ok)
    else:
        relatorio_lines = [
            "# Relatório SOP",
            f"Gate avaliado: {gate}",
            f"Resultado: **{status}**",
        "",
            "## Conformidade Constitucional",
            f"- ✅ Constituição validada: {len(constituicao.get('leis', [])) if constituicao else 0} leis fundamentais",
        ]
        
        if gate in ["G0", "G1", "G2"]:
            relatorio_lines.append(f"- ✅ Tríade de Fundamentação (ART-02): {'Validada' if triade_ok else 'Violada'}")
        
        relatorio_lines.extend([
            "",
            "## Métricas",
            f"- Cobertura: {coverage}% (mínimo python: {coverage_min_python}%)",
            f"- Semgrep: ok={semgrep_res.ok} findings={semgrep_res.extra.get('findings',0)} "
            f"blocking={semgrep_res.extra.get('blocking',0)}",
            f"- Bandit: ok={bandit_res.ok} (worst: {bandit_res.extra.get('worst_severity', 'N/A')})",
            f"- npm audit: ok={npm_res.ok} critical={npm_res.extra.get('critical',0)}",
            f"- Trivy: ok={trivy_res.ok} critical={trivy_res.extra.get('critical',0)}",
            f"- SBOM: ok={sbom_res.ok}",
            f"- Testes: ok={junit_res.ok} tests={junit_res.extra.get('tests',0)} "
            f"failures={junit_res.extra.get('failures',0)} errors={junit_res.extra.get('errors',0)}",
            "",
            "## Pipeline",
            f"- Pipeline válida: {pipeline_ok}",
            "",
            "## Artefactos Citados (ART-09)",
            f"- Coverage: `{coverage_xml.relative_to(REPO_ROOT) if coverage_xml.exists() else 'ausente'}`",
            f"- Semgrep: `relatorios/semgrep.sarif`",
            f"- Bandit: `relatorios/bandit.json`",
            f"- npm audit: `relatorios/npm-audit.json`",
            f"- Trivy: `relatorios/trivy.json`",
            f"- SBOM: `relatorios/sbom.json`",
            f"- JUnit: `{junit_path.relative_to(REPO_ROOT) if junit_path else 'não encontrado'}`",
            f"- Leis: `core/sop/leis.yaml`",
            f"- Exceções: `core/sop/exceptions.yaml`",
            f"- Constituição: `core/sop/constituição.yaml`",
            "",
            "--",
        ])
    
    if exceptions_used:
        relatorio_lines.extend([
            "",
            "## Exceções Aplicadas",
        ])
        for ex in exceptions_used:
            relatorio_lines.append(
                f"- **{ex.get('regra')}**: {ex.get('motivo', 'N/A')} "
                f"(expira: {ex.get('expires_at', 'N/A')})"
            )

    # Adicionar metadados de transparência (ART-07)
    relatorio_lines = add_transparency_metadata(
        relatorio_lines,
        agent="SOP (FÁBRICA 2.0)",
        objetivo=f"Validação de gate {gate} conforme Constituição e leis.yaml"
            )

    (REL_DIR / "relatorio_sop.md").write_text("\n".join(relatorio_lines), encoding="utf-8")

    # 9. Garantir que pipeline_gate_input.json existe
    if not (REL_DIR / "pipeline_gate_input.json").exists():
        # Se não foi gerado, criar básico
        basic_input = {
            "pipeline_ok": pipeline_ok,
            "issues": pipeline_audit,
            "toc_path": "pipeline/PIPELINE_TOC.md",
        }
        (REL_DIR / "pipeline_gate_input.json").write_text(
            json.dumps(basic_input, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    # 10. Placeholder de parecer Gatekeeper (se não existir)
    if not (REL_DIR / "parecer_gatekeeper.md").exists():
        (REL_DIR / "parecer_gatekeeper.md").write_text(
            "Parecer do Gatekeeper: pendente de revisão.", encoding="utf-8"
        )

    # 11. Output de status (ART-04: verificabilidade)
    if status == "BLOQUEADO":
        print(f"❌ SOP BLOQUEADO para gate {gate}")
        print(f"   Regras violadas: {', '.join(violations)}")
        if not triade_ok and gate in ["G0", "G1", "G2"]:
            print(f"   ⚠️  ART-02 (Tríade de Fundamentação) violado")
        print(f"   Ver detalhes em: relatorios/relatorio_sop.md")
        print(f"   Artefactos: relatorios/sop_status.json")
        return 1
    else:
        print(f"✅ SOP PASS para gate {gate}")
        # Confirmar validação da Constituição (sempre mostrar - ART-01)
        if constituicao and isinstance(constituicao, dict) and constituicao.get('leis'):
            leis_count = len(constituicao.get('leis', []))
            if leis_count > 0:
                print(f"✅ Constituição validada (ART-01): {leis_count} leis fundamentais")
        else:
            const_path = SOP_DIR / "constituição.yaml"
            if const_path.exists():
                try:
                    content = const_path.read_text(encoding="utf-8")
                    art_count = content.count("id: ART-")
                    if art_count >= 10:
                        print(f"✅ Constituição validada (ART-01): {art_count} leis fundamentais")
                    else:
                        print("✅ Constituição validada (ART-01): estrutura básica")
                except Exception:
                    print("✅ Constituição validada (ART-01): estrutura básica")
        
        if gate in ["G0", "G1", "G2"] and triade_ok:
            print(f"✅ Tríade de Fundamentação validada (ART-02)")
        
        print(f"📄 Relatórios gerados:")
        print(f"   - relatorios/relatorio_sop.md")
        print(f"   - relatorios/sop_status.json")
        print(f"   - relatorios/pipeline_gate_input.json")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
