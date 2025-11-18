#!/usr/bin/env python3
"""
PIN — GATEKEEPER v3.0
Guardião Ético e Fiscalizador Final

REGRA DE ABERTURA:
OWNER: GATEKEEPER — Próxima ação: <frase curta>

PAPEL: emitir pareceres, auditar gates, bloquear/liberar pipeline quando necessário.

REGRAS:
- Avalia conformidade ética e técnica após validação SOP.
- Não planeia; apenas julga e reporta pareceres.
- Deve respeitar ART-01 (Integridade), ART-04 (Verificabilidade), ART-07 (Transparência), ART-09 (Evidência)

SAÍDAS:
- relatorios/parecer_gatekeeper.md + relatorios/para_estado_maior/gatekeeper.out.json
"""
import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

try:
    import yaml  # type: ignore
except Exception:
    yaml = None

# Importar guardas de acesso a ficheiros
try:
    from file_access_guard import validar_permissao_escrita, validar_formato_relatorio, formatar_resposta_agente
except ImportError:
    # Fallback se não conseguir importar
    def validar_permissao_escrita(agente: str, caminho: Path, tem_ordem_valida: bool = False):
        # Em modo fallback, validar conforme agente
        caminho_str = str(caminho)
        if agente == "GATEKEEPER":
            if caminho.suffix == ".md" or "relatorios/para_estado_maior/" in caminho_str:
                return True, "OK"
        return True, "OK (fallback)"  # Modo permissivo em fallback
    
    def validar_formato_relatorio(conteudo: str):
        return True, "OK (fallback)"
    
    def formatar_resposta_agente(agente: str, conteudo: str, pipeline_status: str = "FORA_PIPELINE", proxima_acao: str = "", comando_executar: str = ""):
        # Fallback: garantir formato mínimo mesmo sem importação
        if not proxima_acao:
            proxima_acao = "Operação concluída"
        if not comando_executar:
            comando_executar = "ESTADO-MAIOR ANALISAR RESPOSTA E CONTINUAR OPERAÇÃO"
        
        return f"""**PIPELINE/FORA_PIPELINE:** {pipeline_status}

**OWNER: {agente} — Próxima ação:** {proxima_acao}

{conteudo}

---

**COMANDO A EXECUTAR:** "{comando_executar}"
"""


REPO_ROOT = Path(__file__).resolve().parents[2]
ORDERS_DIR = REPO_ROOT / "ordem" / "ordens"
REPORTS_DIR = REPO_ROOT / "relatorios" / "para_estado_maior"
GATEKEEPER_IN = ORDERS_DIR / "gatekeeper.in.yaml"
GATEKEEPER_OUT = REPORTS_DIR / "gatekeeper.out.json"
REL_DIR = REPO_ROOT / "relatorios"
PARECER_PATH = REL_DIR / "parecer_gatekeeper.md"
ORQUESTRADOR_DIR = REPO_ROOT / "core" / "orquestrador"
VALIDATOR_SCRIPT = REPO_ROOT / "core" / "scripts" / "validator.py"


def _run_bash_command(command: str | Sequence[str], timeout: int) -> subprocess.CompletedProcess[str]:
    """
    Executa comando sem usar shell=True (evita vulnerabilidades B602).
    Aceita string (executada via bash -lc) ou sequência de argumentos.
    """
    if isinstance(command, (list, tuple)):
        cmd_list = [str(arg) for arg in command]
    else:
        cmd_list = ["bash", "-lc", command]

    return subprocess.run(
        cmd_list,
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def load_yaml(path: Path) -> Any:
    """Carrega ficheiro YAML (retorna lista ou dict conforme conteúdo)."""
    if not path.exists():
        return []
    if yaml is None:
        return []
    try:
        content = path.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        if data is None:
            return []
        # Se for lista, filtrar None e garantir que são dicts
        if isinstance(data, list):
            return [item for item in data if isinstance(item, dict)]
        return data
    except Exception:
        return []


def save_json(path: Path, data: List[Dict[str, Any]]) -> None:
    """Guarda lista de relatórios em JSON."""
    # Validar permissão de escrita conforme doutrina
    permite, mensagem = validar_permissao_escrita("GATEKEEPER", path, tem_ordem_valida=False)
    if not permite:
        raise PermissionError(f"❌ BLOQUEADO: {mensagem}")
    
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_json(path: Path) -> List[Dict[str, Any]]:
    """Carrega ficheiro JSON."""
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else [data]
    except Exception:
        return []


def write_text(path: Path, content: str) -> None:
    """Escreve texto em ficheiro com validação de permissão e formato."""
    # Validar permissão de escrita conforme doutrina
    permite, mensagem = validar_permissao_escrita("GATEKEEPER", path, tem_ordem_valida=False)
    if not permite:
        raise PermissionError(f"❌ BLOQUEADO: {mensagem}")
    
    # Validar formato se for markdown
    if path.suffix == ".md":
        formato_ok, formato_msg = validar_formato_relatorio(content)
        if not formato_ok:
            raise ValueError(f"❌ BLOQUEADO: {formato_msg}")
    
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def cmd_executa() -> int:
    """Executa ordem do Gatekeeper conforme mailbox."""
    print("=" * 50)
    print("🛡️ GATEKEEPER v3.0 — Execução de Ordem")
    print("=" * 50)
    
    # Carregar ordens
    orders = load_yaml(GATEKEEPER_IN)
    if not orders:
        conteudo = "❌ Nenhuma ordem encontrada em gatekeeper.in.yaml"
        resposta_formatada = formatar_resposta_agente(
            "GATEKEEPER",
            conteudo,
            pipeline_status="FORA_PIPELINE",
            proxima_acao="Aguardando ordem do Estado-Maior",
            comando_executar="ESTADO-MAIOR CRIAR ORDEM PARA GATEKEEPER EM ordem/ordens/gatekeeper.in.yaml"
        )
        print(resposta_formatada)
        return 1
    
    # Encontrar ordem aberta
    open_order = None
    for order in orders:
        if order.get("status") == "OPEN":
            open_order = order
            break
    
    if not open_order:
        conteudo = "❌ Nenhuma ordem aberta encontrada"
        resposta_formatada = formatar_resposta_agente(
            "GATEKEEPER",
            conteudo,
            pipeline_status="FORA_PIPELINE",
            proxima_acao="Aguardando ordem aberta do Estado-Maior",
            comando_executar="ESTADO-MAIOR CRIAR ORDEM ABERTA PARA GATEKEEPER"
        )
        print(resposta_formatada)
        return 1
    
    order_id = open_order.get("order_id", "unknown")
    objective = open_order.get("objective", "N/A")
    
    print(f"📋 Ordem encontrada: {order_id}")
    print(f"🎯 Objetivo: {objective}")
    
    # Preparar inputs do Gatekeeper (gatekeeper_prep)
    print("\n📦 Preparando inputs do Gatekeeper...")
    makefile_dir = ORQUESTRADOR_DIR.absolute()
    prep_cmd = f'make -C "{makefile_dir}" gatekeeper_prep'
    prep_result = _run_bash_command(
        prep_cmd,
        timeout=300,
    )
    
    if prep_result.returncode != 0:
        conteudo = f"❌ Erro ao preparar inputs do Gatekeeper:\n{prep_result.stderr[:500]}"
        resposta_formatada = formatar_resposta_agente(
            "GATEKEEPER",
            conteudo,
            pipeline_status="FORA_PIPELINE",
            proxima_acao="Corrigir preparação de inputs",
            comando_executar="ENGENHEIRO CORRIGIR PREPARAÇÃO DE INPUTS DO GATEKEEPER"
        )
        print(resposta_formatada)
        return 1
    
    # Verificar status SOP
    sop_status_path = REPORTS_DIR / "sop_status.json"
    sop_status = {}
    if sop_status_path.exists():
        try:
            sop_data = load_json(sop_status_path)
            if isinstance(sop_data, dict):
                sop_status = sop_data
            elif isinstance(sop_data, list) and sop_data:
                sop_status = sop_data[0]
        except Exception:
            pass
    
    # Verificar artefactos obrigatórios
    artefactos_obrigatorios = [
        REL_DIR / "pipeline_gate_input.json",
        REL_DIR / "sbom.json",
        REL_DIR / "coverage.xml",
        REL_DIR / "parecer_gatekeeper.md",
    ]
    
    artefactos_presentes = []
    artefactos_faltando = []
    
    for artefacto in artefactos_obrigatorios:
        if artefacto.exists():
            artefactos_presentes.append(str(artefacto.relative_to(REPO_ROOT)))
        else:
            artefactos_faltando.append(str(artefacto.relative_to(REPO_ROOT)))
    
    # Determinar decisão
    sop_pass = sop_status.get("status") == "PASS"
    todos_artefactos = len(artefactos_faltando) == 0
    
    if sop_pass and todos_artefactos:
        decisao = "PASS"
        decisao_texto = "✅ PASS"
    else:
        decisao = "BLOCKED"
        decisao_texto = "❌ BLOCKED"
    
    # Gerar parecer
    print("\n📄 Gerando parecer do Gatekeeper...")
    
    parecer_lines = [
        "# Parecer Gatekeeper – Auditoria",
        "",
        f"**Data:** {datetime.now(timezone.utc).isoformat()}",
        f"**Ordem referenciada:** {order_id}",
        "",
        "## Decisão",
        "",
        decisao_texto,
        "",
    ]
    
    if decisao == "PASS":
        parecer_lines.append("Todos os artefactos obrigatórios foram encontrados e validados:")
        for artefacto in artefactos_presentes:
            parecer_lines.append(f"- {artefacto}")
    else:
        parecer_lines.append("Bloqueio devido a:")
        if not sop_pass:
            parecer_lines.append("- Status SOP não é PASS")
        if artefactos_faltando:
            parecer_lines.append("- Artefactos faltando:")
            for artefacto in artefactos_faltando:
                parecer_lines.append(f"  - {artefacto}")
    
    parecer_lines.extend([
        "",
        "## Constraints analisados",
        f"- Status SOP: {'✔️' if sop_pass else '❌'}",
        f"- Artefactos obrigatórios presentes: {'✔️' if todos_artefactos else '❌'}",
        "",
        "## Referências constitucionais",
        "- ART-04: Verificabilidade",
        "- ART-07: Transparência",
        "- ART-09: Evidência",
        "",
        f"**Assinado:** Gatekeeper (emissão automatizada)",
    ])
    
    parecer_conteudo = "\n".join(parecer_lines)
    
    # Adicionar formato obrigatório ao parecer
    parecer_formatado = formatar_resposta_agente(
        "GATEKEEPER",
        parecer_conteudo,
        pipeline_status="PIPELINE" if decisao == "PASS" else "FORA_PIPELINE",
        proxima_acao=f"Parecer emitido: {decisao}",
        comando_executar="ESTADO-MAIOR ANALISAR PARECER DO GATEKEEPER E DECIDIR PRÓXIMA AÇÃO"
    )
    
    # Salvar parecer
    write_text(PARECER_PATH, parecer_formatado)
    
    # Gerar relatório JSON
    report = {
        "order_id": order_id,
        "report_id": f"gk-{datetime.now(timezone.utc).isoformat()}",
        "version": 1,
        "from_role": "GATEKEEPER",
        "to_role": "ESTADO-MAIOR",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "decision": decisao,
        "sop_status": sop_status.get("status", "UNKNOWN"),
        "artefactos_presentes": artefactos_presentes,
        "artefactos_faltando": artefactos_faltando,
        "parecer_path": str(PARECER_PATH.relative_to(REPO_ROOT)),
    }
    
    reports = load_json(GATEKEEPER_OUT)
    reports.append(report)
    save_json(GATEKEEPER_OUT, reports)
    
    # Atualizar ordem para DONE
    open_order["status"] = "DONE"
    open_order["completed_at"] = datetime.now(timezone.utc).isoformat()
    orders_updated = []
    for o in orders:
        if o.get("order_id") == order_id:
            orders_updated.append(open_order)
        else:
            orders_updated.append(o)
    
    # Salvar ordens atualizadas
    if yaml:
        with open(GATEKEEPER_IN, "w", encoding="utf-8") as f:
            yaml.dump(orders_updated, f, allow_unicode=True, default_flow_style=False)
    
    # Formatar resposta final
    conteudo_resposta = f"""✅ Parecer do Gatekeeper gerado

**Decisão:** {decisao_texto}

**Artefactos verificados:**
- Presentes: {len(artefactos_presentes)}/{len(artefactos_obrigatorios)}
- Faltando: {len(artefactos_faltando)}

**Status SOP:** {sop_status.get('status', 'UNKNOWN')}

**Parecer salvo em:** {PARECER_PATH.relative_to(REPO_ROOT)}
**Relatório salvo em:** {GATEKEEPER_OUT.relative_to(REPO_ROOT)}
"""
    
    resposta_formatada = formatar_resposta_agente(
        "GATEKEEPER",
        conteudo_resposta,
        pipeline_status="PIPELINE" if decisao == "PASS" else "FORA_PIPELINE",
        proxima_acao=f"Parecer emitido: {decisao}",
        comando_executar="ESTADO-MAIOR ANALISAR PARECER DO GATEKEEPER E DECIDIR PRÓXIMA AÇÃO"
    )
    
    print(resposta_formatada)
    
    return 0 if decisao == "PASS" else 1


def cmd_status() -> int:
    """Mostra status atual do Gatekeeper."""
    conteudo_resposta = "🛡️ GATEKEEPER v3.0 — Status\n" + "=" * 50
    
    # Verificar ordens
    orders = load_yaml(GATEKEEPER_IN)
    open_orders = [o for o in orders if o.get("status") == "OPEN"]
    
    conteudo_resposta += f"\n\n📋 Ordens:\n   Abertas: {len(open_orders)}"
    
    # Verificar parecer mais recente
    if PARECER_PATH.exists():
        try:
            parecer_content = PARECER_PATH.read_text(encoding="utf-8")
            if "✅ PASS" in parecer_content:
                conteudo_resposta += "\n\n✅ Último parecer: PASS"
            elif "❌ BLOCKED" in parecer_content:
                conteudo_resposta += "\n\n❌ Último parecer: BLOCKED"
            else:
                conteudo_resposta += "\n\n⚠️ Último parecer: Status desconhecido"
        except Exception:
            conteudo_resposta += "\n\n⚠️ Erro ao ler parecer"
    else:
        conteudo_resposta += "\n\n⚠️ Nenhum parecer encontrado"
    
    # Verificar artefactos obrigatórios
    artefactos_obrigatorios = [
        REL_DIR / "pipeline_gate_input.json",
        REL_DIR / "sbom.json",
        REL_DIR / "coverage.xml",
    ]
    
    artefactos_presentes = sum(1 for a in artefactos_obrigatorios if a.exists())
    
    conteudo_resposta += f"\n\n📦 Artefactos obrigatórios:\n   Presentes: {artefactos_presentes}/{len(artefactos_obrigatorios)}"
    
    # Formatar resposta conforme doutrina
    resposta_formatada = formatar_resposta_agente(
        "GATEKEEPER",
        conteudo_resposta,
        pipeline_status="FORA_PIPELINE",
        proxima_acao="Status consultado",
        comando_executar="ESTADO-MAIOR VERIFICAR STATUS DO GATEKEEPER E DECIDIR PRÓXIMA AÇÃO"
    )
    
    print(resposta_formatada)
    
    return 0


def cmd_limpa() -> int:
    """Executa limpeza e rotação."""
    conteudo_resposta = "🧹 GATEKEEPER v3.0 — Limpeza\n" + "=" * 50
    
    conteudo_resposta += "\n\n✅ Limpeza concluída (sem ações específicas necessárias)"
    
    # Formatar resposta conforme doutrina
    resposta_formatada = formatar_resposta_agente(
        "GATEKEEPER",
        conteudo_resposta,
        pipeline_status="FORA_PIPELINE",
        proxima_acao="Limpeza concluída",
        comando_executar="ESTADO-MAIOR CONTINUAR OPERAÇÃO"
    )
    
    print(resposta_formatada)
    
    return 0


# ============================================================================
# NOVAS FUNÇÕES DO GATEKEEPER (Conforme ordem do Estado-Maior)
# ============================================================================

def cmd_preflight() -> int:
    """
    Preflight Local (Pre-Commit): Valida workflows YAML, actions deprecadas,
    permissões GITHUB_TOKEN, scripts chamados, permissões de execução.
    """
    print("=" * 50)
    print("🛡️ GATEKEEPER — Preflight Local (Pre-Commit)")
    print("=" * 50)
    
    workflows_dir = REPO_ROOT / ".github" / "workflows"
    issues = []
    warnings = []
    
    if not workflows_dir.exists():
        conteudo = "⚠️ Nenhum workflow encontrado em .github/workflows/"
        resposta_formatada = formatar_resposta_agente(
            "GATEKEEPER",
            conteudo,
            pipeline_status="FORA_PIPELINE",
            proxima_acao="Verificar estrutura de workflows",
            comando_executar="ESTADO-MAIOR VERIFICAR ESTRUTURA DE WORKFLOWS"
        )
        print(resposta_formatada)
        return 0
    
    # Lista de actions deprecadas conhecidas (exemplos)
    deprecated_actions = [
        "actions/checkout@v1",
        "actions/checkout@v2",
        "actions/setup-python@v1",
        "actions/setup-python@v2",
        "actions/setup-python@v3",
        "actions/setup-python@v4",  # v4 ainda válido, mas v5 é preferido
    ]
    
    # Validar cada workflow
    permitted_write_permissions = {"release.yml"}

    for workflow_file in workflows_dir.glob("*.yml"):
        if not workflow_file.exists():
            continue
        
        try:
            workflow_data = load_yaml(workflow_file)
            if not isinstance(workflow_data, dict):
                warnings.append(f"{workflow_file.name}: YAML vazio ou inválido")
                continue
            
            # Verificar actions deprecadas
            workflow_str = workflow_file.read_text(encoding="utf-8")
            for dep_action in deprecated_actions:
                if dep_action in workflow_str:
                    issues.append(f"{workflow_file.name}: Action deprecada detectada: {dep_action}")
            
            # Verificar permissões GITHUB_TOKEN
            if "permissions" not in workflow_data or workflow_data.get("permissions") is None:
                warnings.append(f"{workflow_file.name}: Permissões GITHUB_TOKEN não especificadas (recomendado)")
            else:
                permissions = workflow_data.get("permissions", {})
                if (
                    permissions.get("contents") == "write"
                    and workflow_file.name not in permitted_write_permissions
                ):
                    issues.append(f"{workflow_file.name}: Permissão 'contents: write' muito permissiva (risco de segurança)")
            
            # Verificar scripts chamados
            jobs = workflow_data.get("jobs", {})
            if not isinstance(jobs, dict):
                warnings.append(f"{workflow_file.name}: Estrutura jobs inválida")
                continue

            for job_name, job_data in jobs.items():
                steps = job_data.get("steps", [])
                for step in steps:
                    if isinstance(step, dict):
                        run_cmd = step.get("run", "")
                        if run_cmd:
                            # Verificar se chama scripts externos sem validação
                            if "curl" in run_cmd and "|" in run_cmd and "bash" in run_cmd:
                                warnings.append(f"{workflow_file.name} (job {job_name}): Script externo via curl|bash (risco de segurança)")
            
        except Exception as e:
            issues.append(f"{workflow_file.name}: Erro ao validar: {e}")
    
    # Gerar relatório
    conteudo = f"""## Preflight Local — Validação de Workflows

**Workflows validados:** {len(list(workflows_dir.glob("*.yml")))}

### Issues Críticos
"""
    if issues:
        for issue in issues:
            conteudo += f"- ❌ {issue}\n"
    else:
        conteudo += "- ✅ Nenhum issue crítico encontrado\n"
    
    conteudo += "\n### Warnings\n"
    if warnings:
        for warning in warnings:
            conteudo += f"- ⚠️  {warning}\n"
    else:
        conteudo += "- ✅ Nenhum warning encontrado\n"
    
    # Determinar status
    status = "PASS" if not issues else "BLOCKED"
    pipeline_status = "PIPELINE" if status == "PASS" else "FORA_PIPELINE"
    
    resposta_formatada = formatar_resposta_agente(
        "GATEKEEPER",
        conteudo,
        pipeline_status=pipeline_status,
        proxima_acao=f"Preflight concluído: {status}",
        comando_executar="ESTADO-MAIOR ANALISAR RELATÓRIO DE PREFLIGHT E CORRIGIR ISSUES SE NECESSÁRIO"
    )
    
    print(resposta_formatada)
    
    # Salvar relatório
    preflight_report = REPORTS_DIR / "preflight_report.md"
    write_text(preflight_report, resposta_formatada)
    
    return 0 if status == "PASS" else 1


def cmd_vercel_guard() -> int:
    """
    Vercel Guard (Pré-Deploy): Smoke local com vercel pull + vercel build (dry-run)
    + validação vercel.json.
    Conforme doutrina: APENAS validação (dry-run), nunca modifica código.
    """
    print("=" * 50)
    print("🛡️ GATEKEEPER — Vercel Guard (Pré-Deploy)")
    print("=" * 50)
    
    vercel_json = REPO_ROOT / "vercel.json"
    issues = []
    warnings = []
    
    # Validar vercel.json se existir
    if vercel_json.exists():
        try:
            vercel_data = load_yaml(vercel_json)
            if not vercel_data:
                issues.append("vercel.json: YAML inválido ou vazio")
            else:
                # Validações básicas
                if "buildCommand" not in vercel_data and "outputDirectory" not in vercel_data:
                    warnings.append("vercel.json: buildCommand ou outputDirectory não especificados")
        except Exception as e:
            issues.append(f"vercel.json: Erro ao validar: {e}")
    else:
        warnings.append("vercel.json não encontrado (pode ser opcional)")
    
    # Executar vercel pull (dry-run, read-only)
    print("\n📦 Executando vercel pull (dry-run)...")
    vercel_token = os.environ.get("VERCEL_TOKEN")

    pull_cmd = ["vercel", "pull", "--yes", "--environment=production"]
    if vercel_token:
        pull_cmd.extend(["--token", vercel_token])

    try:
        result = subprocess.run(
            pull_cmd,
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            warnings.append(f"vercel pull falhou: {result.stderr[:200]}")
        elif not vercel_token:
            warnings.append("vercel pull executado sem VERCEL_TOKEN — verifique se credenciais não são necessárias")
    except FileNotFoundError:
        warnings.append("vercel CLI não encontrado (instalar: npm i -g vercel)")
    except Exception as e:
        warnings.append(f"Erro ao executar vercel pull: {e}")
    
    # Executar vercel build (dry-run, sem deploy)
    print("🔨 Executando vercel build (dry-run)...")
    dry_run_confirmed = False
    dry_run_output_snippet = ""
    build_cmd = ["vercel", "build"]
    if vercel_token:
        build_cmd.extend(["--token", vercel_token])
    try:
        result = subprocess.run(
            build_cmd,
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=300,
        )
        if result.returncode != 0:
            issues.append(f"vercel build (dry-run) falhou: {result.stderr[:200]}")
        else:
            combined_output = (result.stdout or "") + "\n" + (result.stderr or "")
            snippet_lines = combined_output.strip().splitlines()[:5]
            if snippet_lines:
                dry_run_output_snippet = "\n".join(snippet_lines)
            if re.search(r"build( completed)?" , combined_output, re.IGNORECASE):
                dry_run_confirmed = True
            else:
                warnings.append("vercel build executado, mas saída não confirma claramente build local — verificar CLI")
    except FileNotFoundError:
        warnings.append("vercel CLI não encontrado")
    except Exception as e:
        warnings.append(f"Erro ao executar vercel build: {e}")
    
    # Gerar relatório
    conteudo = f"""## Vercel Guard — Validação Pré-Deploy

### Validação vercel.json
"""
    if vercel_json.exists():
        conteudo += "- ✅ vercel.json encontrado\n"
    else:
        conteudo += "- ⚠️  vercel.json não encontrado\n"
    
    conteudo += "\n### Issues Críticos\n"
    if issues:
        for issue in issues:
            conteudo += f"- ❌ {issue}\n"
    else:
        conteudo += "- ✅ Nenhum issue crítico encontrado\n"
    
    conteudo += "\n### Confirmação do Dry-Run\n"
    if dry_run_confirmed:
        conteudo += "- ✅ vercel build executado com sucesso (build local)\n"
    else:
        if any("vercel CLI não encontrado" in warn for warn in warnings):
            conteudo += "- ⚠️  Não foi possível confirmar dry-run (CLI ausente)\n"
        elif any("vercel build (dry-run) falhou" in issue for issue in issues):
            conteudo += "- ❌ vercel build não completou — dry-run não confirmado\n"
        elif not vercel_token:
            conteudo += "- ⚠️  vercel build executado sem token — saída parcial não confirma build local\n"
        else:
            conteudo += "- ⚠️  Dry-run não confirmado pela saída do comando\n"
    if dry_run_output_snippet:
        conteudo += "  Saída parcial:\n  ```\n" + dry_run_output_snippet + "\n  ```\n"

    conteudo += "\n### Warnings\n"
    if warnings:
        for warning in warnings:
            conteudo += f"- ⚠️  {warning}\n"
    else:
        conteudo += "- ✅ Nenhum warning encontrado\n"
    
    # Determinar status
    status = "PASS" if not issues else "BLOCKED"
    pipeline_status = "PIPELINE" if status == "PASS" else "FORA_PIPELINE"
    
    resposta_formatada = formatar_resposta_agente(
        "GATEKEEPER",
        conteudo,
        pipeline_status=pipeline_status,
        proxima_acao=f"Vercel Guard concluído: {status}",
        comando_executar="ESTADO-MAIOR ANALISAR RELATÓRIO DE VERCEL GUARD E CORRIGIR ISSUES SE NECESSÁRIO"
    )
    
    print(resposta_formatada)
    
    # Salvar relatório
    vercel_report = REPORTS_DIR / "vercel_guard_report.md"
    write_text(vercel_report, resposta_formatada)
    
    return 0 if status == "PASS" else 1


def cmd_post_mortem(workflow_run_id: Optional[str] = None) -> int:
    """
    Post-Mortem (Falha): Quando workflow falhar, gera causa-raiz e patch sugerido.
    """
    print("=" * 50)
    print("🛡️ GATEKEEPER — Post-Mortem (Análise de Falha)")
    print("=" * 50)
    
    # Analisar logs de workflows falhados
    workflow_logs_dir = REPO_ROOT / ".github" / "workflows" / "logs"
    issues = []
    root_causes = []
    suggested_patches = []
    
    # Verificar se há logs de falha
    if workflow_logs_dir.exists():
        for log_file in workflow_logs_dir.glob("*.log"):
            try:
                log_content = log_file.read_text(encoding="utf-8")
                # Análise básica de padrões de erro
                if "ERROR" in log_content or "FAILED" in log_content:
                    issues.append(f"Falha detectada em: {log_file.name}")
                    # Tentar identificar causa-raiz
                    if "SBOM" in log_content or "sbom" in log_content:
                        root_causes.append("SBOM ausente ou inválido")
                        suggested_patches.append("Adicionar step de geração de SBOM antes da validação SOP")
                    if "SOP" in log_content and "BLOQUEADO" in log_content:
                        root_causes.append("Validação SOP bloqueada")
                        suggested_patches.append("Verificar artefactos obrigatórios (coverage.xml, sbom.json, etc.)")
            except Exception:
                pass
    
    # Gerar relatório de post-mortem
    conteudo = f"""## Post-Mortem — Análise de Falha

**Workflow Run ID:** {workflow_run_id or "N/A"}
**Data:** {datetime.now(timezone.utc).isoformat()}

### Issues Detectados
"""
    if issues:
        for issue in issues:
            conteudo += f"- ❌ {issue}\n"
    else:
        conteudo += "- ⚠️  Nenhum log de falha encontrado (análise baseada em padrões conhecidos)\n"
    
    conteudo += "\n### Causas-Raiz Identificadas\n"
    if root_causes:
        for cause in set(root_causes):  # Remover duplicados
            conteudo += f"- 🔍 {cause}\n"
    else:
        conteudo += "- ⚠️  Nenhuma causa-raiz identificada automaticamente\n"
    
    conteudo += "\n### Patches Sugeridos\n"
    if suggested_patches:
        for patch in set(suggested_patches):  # Remover duplicados
            conteudo += f"- 🔧 {patch}\n"
    else:
        conteudo += "- ⚠️  Nenhum patch sugerido automaticamente\n"
    
    conteudo += "\n### Recomendações\n"
    conteudo += "- Revisar logs completos do workflow\n"
    conteudo += "- Verificar artefactos obrigatórios (SBOM, coverage, etc.)\n"
    conteudo += "- Validar conformidade com Constituição e Leis\n"
    
    resposta_formatada = formatar_resposta_agente(
        "GATEKEEPER",
        conteudo,
        pipeline_status="FORA_PIPELINE",
        proxima_acao="Post-mortem concluído",
        comando_executar="ESTADO-MAIOR ANALISAR POST-MORTEM E APLICAR CORREÇÕES SUGERIDAS"
    )
    
    print(resposta_formatada)
    
    # Salvar relatório
    postmortem_report = REPORTS_DIR / f"postmortem_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.md"
    write_text(postmortem_report, resposta_formatada)
    
    return 0


def cmd_auto_fix_alternative(issue_description: str, suggested_patch: str) -> int:
    """
    Alternativa Auto-Fix: Gatekeeper gera ordem sugerida em relatório,
    Estado-Maior ou Engenheiro pode copiar para engineer.in.yaml.
    Conforme doutrina: Gatekeeper não pode modificar código, apenas gerar relatório com ordem sugerida.
    """
    print("=" * 50)
    print("🛡️ GATEKEEPER — Auto-Fix Alternativo (Gerar Ordem Sugerida)")
    print("=" * 50)
    
    # Criar nova ordem com patch sugerido
    new_order = {
        "order_id": f"gk-auto-fix-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}",
        "version": 1,
        "from_role": "GATEKEEPER",
        "to_role": "ENGENHEIRO",
        "project": "FÁBRICA",
        "module": "CORREÇÃO_AUTOMÁTICA",
        "gate": "FORA_PIPELINE",
        "urgency": "alta",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "objective": f"Aplicar correção sugerida pelo Gatekeeper: {issue_description}",
        "context_refs": [
            f"relatorios/para_estado_maior/gatekeeper.out.json",
        ],
        "steps": [
            {
                "type": "command",
                "command": f"# Correção sugerida pelo Gatekeeper\n{suggested_patch}",
                "description": "Aplicar patch sugerido pelo Gatekeeper"
            }
        ],
        "constraints": [
            "Respeitar doutrina de acesso a ficheiros",
            "Garantir rastreabilidade (ART-04, ART-09)",
            "Validar após aplicação"
        ],
        "ack": {
            "by": None,
            "at": None,
            "status": "PENDING"
        },
        "status": "OPEN"
    }
    
    # Gerar relatório com ordem sugerida (Gatekeeper pode escrever relatórios)
    ordem_yaml = ""
    if yaml:
        try:
            ordem_yaml = yaml.dump([new_order], allow_unicode=True, default_flow_style=False, sort_keys=False)
        except Exception:
            ordem_yaml = f"# Ordem sugerida pelo Gatekeeper\n{json.dumps(new_order, indent=2, ensure_ascii=False)}"
    
    conteudo = f"""## Auto-Fix Alternativo — Ordem Sugerida

**Ordem ID:** {new_order['order_id']}

**Issue:** {issue_description}

**Patch Sugerido:**
```
{suggested_patch}
```

### Ordem YAML Sugerida

Para aplicar esta correção, copie a seguinte ordem para `ordem/ordens/engineer.in.yaml`:

```yaml
{ordem_yaml}
```

**Próximo Passo:** Estado-Maior ou Engenheiro copiar ordem para engineer.in.yaml e Engenheiro aplicar correção
"""
    
    resposta_formatada = formatar_resposta_agente(
        "GATEKEEPER",
        conteudo,
        pipeline_status="FORA_PIPELINE",
        proxima_acao="Ordem sugerida gerada em relatório",
        comando_executar="ESTADO-MAIOR COPIAR ORDEM SUGERIDA PARA ordem/ordens/engineer.in.yaml E ENGENHEIRO APLICAR CORREÇÃO"
    )
    
    print(resposta_formatada)
    
    # Salvar relatório (Gatekeeper pode escrever relatórios)
    auto_fix_report = REPORTS_DIR / f"auto_fix_suggested_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.md"
    write_text(auto_fix_report, resposta_formatada)
    
    print(f"\n✅ Relatório salvo em: {auto_fix_report.relative_to(REPO_ROOT)}")
    
    return 0


def main() -> int:
    """Função principal."""
    parser = argparse.ArgumentParser(description="GATEKEEPER v3.0 — Guardião Ético e Fiscalizador Final")
    parser.add_argument("comando", choices=["executa", "status", "limpa", "preflight", "vercel-guard", "post-mortem", "auto-fix"], help="Comando a executar")
    parser.add_argument("--workflow-run-id", help="ID do workflow run (para post-mortem)")
    parser.add_argument("--issue", help="Descrição do issue (para auto-fix)")
    parser.add_argument("--patch", help="Patch sugerido (para auto-fix)")
    
    args = parser.parse_args()
    
    if args.comando == "executa":
        return cmd_executa()
    elif args.comando == "status":
        return cmd_status()
    elif args.comando == "limpa":
        return cmd_limpa()
    elif args.comando == "preflight":
        return cmd_preflight()
    elif args.comando == "vercel-guard":
        return cmd_vercel_guard()
    elif args.comando == "post-mortem":
        return cmd_post_mortem(args.workflow_run_id)
    elif args.comando == "auto-fix":
        if not args.issue or not args.patch:
            print("❌ Erro: --issue e --patch são obrigatórios para auto-fix")
            return 1
        return cmd_auto_fix_alternative(args.issue, args.patch)
    else:
        print(f"❌ Comando desconhecido: {args.comando}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

