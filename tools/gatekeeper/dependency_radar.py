#!/usr/bin/env python3
"""
Dependency Radar — Gatekeeper
Sinaliza actions/pacotes desatualizados ou CVEs, abre Issue/PR draft.

Conforme doutrina: Gatekeeper pode ler e analisar, gerar relatórios.
Não modifica código-fonte, apenas sinaliza e abre Issues/PRs.
"""
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import yaml  # type: ignore
except Exception:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS_DIR = REPO_ROOT / ".github" / "workflows"
REPORTS_DIR = REPO_ROOT / "relatorios" / "para_estado_maior"
PACKAGE_JSON = REPO_ROOT / "package.json"
REQUIREMENTS_TXT = REPO_ROOT / "requirements.txt"


def load_yaml(path: Path) -> Any:
    """Carrega ficheiro YAML."""
    if not path.exists():
        return {}
    if yaml is None:
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def check_npm_dependencies() -> Tuple[List[Dict[str, Any]], List[str]]:
    """Verifica dependências npm desatualizadas ou com CVEs."""
    issues: List[Dict[str, Any]] = []
    warnings: List[str] = []

    if not PACKAGE_JSON.exists():
        warnings.append("package.json não encontrado — audit npm ignorado")
        return issues, warnings

    try:
        result = subprocess.run(
            ["npm", "audit", "--json"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode not in (0, 1):
            warnings.append(
                f"npm audit devolveu código {result.returncode}. Trecho: {(result.stderr or result.stdout)[:200]}"
            )

        output = result.stdout or ""
        if not output.strip():
            warnings.append("npm audit não retornou JSON — saída vazia")
            return issues, warnings

        try:
            audit_data = json.loads(output)
        except json.JSONDecodeError as exc:
            warnings.append(f"Falha ao analisar saída do npm audit: {exc}")
            return issues, warnings

        vulnerabilities = audit_data.get("vulnerabilities", {})
        if not vulnerabilities:
            warnings.append("npm audit não reportou vulnerabilidades (pode estar OK ou audit limitado)")

        for pkg_name, vuln_data in vulnerabilities.items():
            if not isinstance(vuln_data, dict):
                continue
            severity = vuln_data.get("severity", "unknown")
            if severity in ["high", "critical"]:
                issues.append(
                    {
                        "type": "npm_cve",
                        "package": pkg_name,
                        "severity": severity,
                        "description": vuln_data.get("title", "CVE detectado"),
                    }
                )
    except FileNotFoundError:
        warnings.append("npm não encontrado — instale npm para executar audit")
    except subprocess.TimeoutExpired:
        warnings.append("npm audit excedeu tempo limite (60s)")
    except Exception as exc:
        warnings.append(f"Erro inesperado ao executar npm audit: {exc}")

    return issues, warnings


def check_python_dependencies() -> Tuple[List[Dict[str, Any]], List[str]]:
    """Verifica dependências Python desatualizadas ou com CVEs."""
    issues: List[Dict[str, Any]] = []
    warnings: List[str] = []

    if not REQUIREMENTS_TXT.exists():
        warnings.append("requirements.txt não encontrado — pip-audit ignorado")
        return issues, warnings

    try:
        result = subprocess.run(
            ["pip-audit", "-r", str(REQUIREMENTS_TXT), "--format", "json"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode not in (0, 1):
            warnings.append(
                f"pip-audit devolveu código {result.returncode}. Trecho: {(result.stderr or result.stdout)[:200]}"
            )

        output = result.stdout or ""
        if not output.strip():
            warnings.append("pip-audit não retornou JSON — saída vazia")
            return issues, warnings

        try:
            audit_data = json.loads(output)
        except json.JSONDecodeError as exc:
            warnings.append(f"Falha ao analisar saída do pip-audit: {exc}")
            return issues, warnings

        vulns = audit_data.get("vulnerabilities", [])
        if not vulns:
            warnings.append("pip-audit não reportou vulnerabilidades (pode estar OK ou audit limitado)")

        for vuln in vulns:
            if not isinstance(vuln, dict):
                continue
            issues.append(
                {
                    "type": "pip_cve",
                    "package": vuln.get("name", "unknown"),
                    "severity": vuln.get("severity", "unknown"),
                    "description": vuln.get("description", "CVE detectado"),
                }
            )
    except FileNotFoundError:
        warnings.append("pip-audit não encontrado — instale pip-audit para executar análise")
    except subprocess.TimeoutExpired:
        warnings.append("pip-audit excedeu tempo limite (60s)")
    except Exception as exc:
        warnings.append(f"Erro inesperado ao executar pip-audit: {exc}")

    return issues, warnings


def check_github_actions() -> Tuple[List[Dict[str, Any]], List[str]]:
    """Verifica GitHub Actions desatualizadas."""
    issues: List[Dict[str, Any]] = []
    warnings: List[str] = []

    if not WORKFLOWS_DIR.exists():
        warnings.append("Diretório .github/workflows não encontrado — verificação de actions ignorada")
        return issues, warnings
    
    # Lista de actions conhecidas e suas versões mais recentes
    known_actions = {
        "actions/checkout": "v4",  # v4 é atual, v5 pode estar disponível
        "actions/setup-python": "v5",
        "actions/setup-node": "v4",
        "actions/upload-artifact": "v4",
        "gitleaks/gitleaks-action": "v2",
    }
    
    for workflow_file in WORKFLOWS_DIR.glob("*.yml"):
        try:
            workflow_content = workflow_file.read_text(encoding="utf-8")
            workflow_data = load_yaml(workflow_file)
            
            if not workflow_data:
                continue
            
            # Procurar uses: actions/...
            for line in workflow_content.split("\n"):
                if "uses:" in line and "actions/" in line:
                    for action_name, latest_version in known_actions.items():
                        if action_name in line:
                            # Verificar se está usando versão antiga
                            if f"{action_name}@v" in line:
                                # Extrair versão usada
                                parts = line.split("@")
                                if len(parts) > 1:
                                    version_used = parts[1].strip().split()[0] if parts[1].strip() else ""
                                    # Comparar versões (simplificado)
                                    if version_used and version_used < latest_version:
                                        issues.append({
                                            "type": "action_deprecated",
                                            "workflow": workflow_file.name,
                                            "action": action_name,
                                            "version_used": version_used,
                                            "latest_version": latest_version,
                                        })
        except Exception:
            pass
    
    return issues, warnings


def generate_issue_draft(issues: List[Dict[str, Any]]) -> str:
    """Gera rascunho de Issue para GitHub."""
    if not issues:
        return ""
    
    issue_content = f"""# Dependency Radar — Issues Detectados

**Data:** {datetime.now(timezone.utc).isoformat()}
**Agente:** Gatekeeper

## Resumo

{len(issues)} issue(s) detectado(s):

"""
    for i, issue in enumerate(issues, 1):
        issue_type = issue.get("type", "unknown")
        if issue_type == "npm_cve":
            issue_content += f"### {i}. CVE em npm: {issue.get('package')}\n"
            issue_content += f"- **Severidade:** {issue.get('severity')}\n"
            issue_content += f"- **Descrição:** {issue.get('description')}\n\n"
        elif issue_type == "pip_cve":
            issue_content += f"### {i}. CVE em Python: {issue.get('package')}\n"
            issue_content += f"- **Severidade:** {issue.get('severity')}\n"
            issue_content += f"- **Descrição:** {issue.get('description')}\n\n"
        elif issue_type == "action_deprecated":
            issue_content += f"### {i}. Action desatualizada: {issue.get('action')}\n"
            issue_content += f"- **Workflow:** {issue.get('workflow')}\n"
            issue_content += f"- **Versão usada:** {issue.get('version_used')}\n"
            issue_content += f"- **Versão mais recente:** {issue.get('latest_version')}\n\n"
    
    issue_content += """
## Ações Recomendadas

1. Atualizar dependências com CVEs críticos/altos
2. Atualizar GitHub Actions para versões mais recentes
3. Executar testes após atualizações

---
**Gerado por:** Gatekeeper Dependency Radar
"""
    
    return issue_content


def main() -> int:
    """Função principal."""
    print("=" * 50)
    print("🛡️ GATEKEEPER — Dependency Radar")
    print("=" * 50)
    
    all_issues: List[Dict[str, Any]] = []
    all_warnings: List[str] = []
    
    # Verificar npm
    print("\n📦 Verificando dependências npm...")
    npm_issues, npm_warnings = check_npm_dependencies()
    all_issues.extend(npm_issues)
    all_warnings.extend(npm_warnings)
    print(f"   {len(npm_issues)} issue(s) encontrado(s)")
    
    # Verificar Python
    print("🐍 Verificando dependências Python...")
    pip_issues, pip_warnings = check_python_dependencies()
    all_issues.extend(pip_issues)
    all_warnings.extend(pip_warnings)
    print(f"   {len(pip_issues)} issue(s) encontrado(s)")
    
    # Verificar GitHub Actions
    print("⚙️  Verificando GitHub Actions...")
    action_issues, action_warnings = check_github_actions()
    all_issues.extend(action_issues)
    all_warnings.extend(action_warnings)
    print(f"   {len(action_issues)} issue(s) encontrado(s)")
    
    # Gerar relatório
    report_content = f"""**PIPELINE/FORA_PIPELINE:** FORA_PIPELINE

**OWNER: GATEKEEPER — Próxima ação:** Gerar Issue/PR draft se issues detectados

---

## Dependency Radar — Análise de Dependências

**Data:** {datetime.now(timezone.utc).isoformat()}

### Resumo

- **Total de issues:** {len(all_issues)}
- **CVEs npm:** {len(npm_issues)}
- **CVEs Python:** {len(pip_issues)}
- **Actions desatualizadas:** {len(action_issues)}

### Issues Detectados

"""
    
    if all_issues:
        for issue in all_issues:
            issue_type = issue.get("type", "unknown")
            if issue_type in ["npm_cve", "pip_cve"]:
                report_content += f"- ❌ **CVE:** {issue.get('package')} ({issue.get('severity')})\n"
            elif issue_type == "action_deprecated":
                report_content += f"- ⚠️  **Action desatualizada:** {issue.get('action')} em {issue.get('workflow')}\n"
    else:
        report_content += "- ✅ Nenhum issue detectado\n"

    if all_warnings:
        report_content += "\n### Observações / Warnings\n"
        for warn in all_warnings:
            report_content += f"- ⚠️  {warn}\n"
    
    # Gerar rascunho de Issue
    if all_issues:
        issue_draft = generate_issue_draft(all_issues)
        issue_draft_path = REPORTS_DIR / f"dependency_radar_issue_{datetime.now(timezone.utc).strftime('%Y%m%d')}.md"
        issue_draft_path.parent.mkdir(parents=True, exist_ok=True)
        issue_draft_path.write_text(issue_draft, encoding="utf-8")
        report_content += f"\n**Issue draft gerado:** {issue_draft_path.relative_to(REPO_ROOT)}\n"
    
    report_content += "\n---\n\n**COMANDO A EXECUTAR:** \"ESTADO-MAIOR REVISAR ISSUES DETECTADOS E ABRIR ISSUE/PR SE NECESSÁRIO\""
    
    # Salvar relatório
    report_path = REPORTS_DIR / f"dependency_radar_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_content, encoding="utf-8")
    
    print(f"\n✅ Relatório salvo em: {report_path.relative_to(REPO_ROOT)}")
    if all_issues:
        print(f"📝 Issue draft gerado: {REPORTS_DIR / f'dependency_radar_issue_{datetime.now(timezone.utc).strftime('%Y%m%d')}.md'}")
    
    return 0 if not all_issues else 1


if __name__ == "__main__":
    sys.exit(main())

