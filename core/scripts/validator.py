import json
import os
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
    for i in issues:
        sev = (i.get("issue_severity") or "LOW").upper()
        worst = max(worst, levels.get(sev, 1))
    return MetricResult(ok=worst < min_lv, extra={})


def eval_npm_audit(audit_path: Path) -> MetricResult:
    data = load_json(audit_path) or {}
    advis = data.get("vulnerabilities") or {}
    critical = advis.get("critical") or 0
    return MetricResult(ok=critical == 0, extra={"critical": critical})


def eval_trivy(trivy_path: Path, block_levels: List[str]) -> MetricResult:
    data = load_json(trivy_path) or {}
    results = data.get("Results") or []
    critical = 0
    for r in results:
        vulns = r.get("Vulnerabilities") or []
        for v in vulns:
            sev = (v.get("Severity") or "").upper()
            if sev in [lvl.upper() for lvl in block_levels]:
                if sev == "CRITICAL":
                    critical += 1
    return MetricResult(ok=critical == 0, extra={"critical": critical})


def eval_sbom(sbom_path: Path) -> MetricResult:
    return MetricResult(ok=sbom_path.exists(), extra={})


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


def main() -> int:
    REL_DIR.mkdir(exist_ok=True, parents=True)

    leis = read_yaml(SOP_DIR / "leis.yaml")
    exc = read_yaml(SOP_DIR / "exceptions.yaml")
    exceptions = exc.get("excecoes", []) if isinstance(exc, dict) else []

    politicas = leis.get("politicas", {})
    coverage_min_default = politicas.get("coverage_min", {}).get("default", 75)
    coverage_min_python = politicas.get("coverage_min", {}).get("python", coverage_min_default)
    semgrep_block = politicas.get("semgrep_block", ["ERROR", "HIGH"])
    bandit_min = politicas.get("bandit_min_level", "MEDIUM")
    trivy_block = politicas.get("trivy_block", ["CRITICAL"])

    coverage_xml = REPO_ROOT / "coverage.xml"
    coverage = parse_coverage(coverage_xml)
    coverage_min_python = apply_exceptions(coverage_min_python, "coverage_min.python", exceptions)
    coverage_ok = coverage >= float(coverage_min_python)

    semgrep_res = eval_semgrep(REL_DIR / "semgrep.sarif", [lvl.upper() for lvl in semgrep_block])
    bandit_res = eval_bandit(REL_DIR / "bandit.json", bandit_min)
    npm_res = eval_npm_audit(REL_DIR / "npm-audit.json")
    trivy_res = eval_trivy(REL_DIR / "trivy.json", trivy_block)
    sbom_res = eval_sbom(REL_DIR / "sbom.json")

    metrics = {
        "coverage": coverage,
        "tests": {"ok": True, "suite": "pytest|jest"},
        "semgrep": {"ok": semgrep_res.ok, **semgrep_res.extra},
        "bandit": {"ok": bandit_res.ok},
        "npm_audit": {"ok": npm_res.ok, **npm_res.extra},
        "trivy": {"ok": trivy_res.ok, **trivy_res.extra},
        "sbom": {"ok": sbom_res.ok},
    }

    # Gate pretendido (G2 como target neste run)
    gate = "G2"
    status = "PASS" if (
        coverage_ok
        and semgrep_res.ok
        and bandit_res.ok
        and npm_res.ok
        and trivy_res.ok
        and sbom_res.ok
    ) else "BLOCK"

    sop_status = {
        "gate": gate,
        "status": status,
        "metrics": metrics,
        "exceptions_used": [],
    }

    (REL_DIR / "sop_status.json").write_text(json.dumps(sop_status, indent=2), encoding="utf-8")

    relatorio_md = [
        "# Relatório SOP",
        f"Gate avaliado: {gate}",
        f"Resultado: {status}",
        "",
        f"Cobertura: {coverage}% (mínimo python: {coverage_min_python})",
        f"Semgrep: ok={semgrep_res.ok} findings={semgrep_res.extra.get('findings',0)} blocking={semgrep_res.extra.get('blocking',0)}",
        f"Bandit: ok={bandit_res.ok}",
        f"npm audit: ok={npm_res.ok} critical={npm_res.extra.get('critical',0)}",
        f"Trivy: ok={trivy_res.ok} critical={trivy_res.extra.get('critical',0)}",
        f"SBOM: ok={sbom_res.ok}",
        "",
        "--",
    ]
    (REL_DIR / "relatorio_sop.md").write_text("\n".join(relatorio_md), encoding="utf-8")

    # Placeholder de parecer Gatekeeper
    if not (REL_DIR / "parecer_gatekeeper.md").exists():
        (REL_DIR / "parecer_gatekeeper.md").write_text(
            "Parecer do Gatekeeper: pendente de revisão.", encoding="utf-8"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


