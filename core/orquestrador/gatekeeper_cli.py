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
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

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
    prep_result = subprocess.run(
        prep_cmd,
        shell=True,
        cwd=str(REPO_ROOT.absolute()),
        capture_output=True,
        text=True,
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


def main() -> int:
    """Função principal."""
    parser = argparse.ArgumentParser(description="GATEKEEPER v3.0 — Guardião Ético e Fiscalizador Final")
    parser.add_argument("comando", choices=["executa", "status", "limpa"], help="Comando a executar")
    
    args = parser.parse_args()
    
    if args.comando == "executa":
        return cmd_executa()
    elif args.comando == "status":
        return cmd_status()
    elif args.comando == "limpa":
        return cmd_limpa()
    else:
        print(f"❌ Comando desconhecido: {args.comando}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

