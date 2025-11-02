#!/usr/bin/env python3
"""
PIN — ENGENHEIRO v3.0
Sistema de execução de ordens do Estado-Maior
Respeita ART-04 (Verificabilidade) e ART-09 (Evidência)

PROIBIÇÕES ABSOLUTAS (ART-03: Consciência Técnica):
- ❌ NÃO pode atuar como Estado-Maior (aprovador de gates, criador de políticas)
- ❌ NÃO pode atuar como Gatekeeper (veta gates, avalia ética)
- ❌ NÃO pode atuar como SOP (valida conformidade, bloqueia gates)

FLUXO OBRIGATÓRIO:
1. Estado-Maior cria ordem em mailbox (engineer.in.yaml)
2. Estado-Maior marca ordem com ACK=ACCEPTED
3. ENGENHEIRO executa apenas steps técnicos (sem assumir papéis de outros agentes)
4. ENGENHEIRO gera relatório e entrega para Estado-Maior avaliar

GUARDAS:
- Sem ACK=ACCEPTED → execução bloqueada
- Mailbox inválido → execução bloqueada
- Tentativa de atuar como EM/GK/SOP → execução abortada
- Outros PINs ativos além do v3 → execução abortada
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml  # type: ignore
except Exception:
    yaml = None

# Importar guardas de acesso a ficheiros
try:
    from file_access_guard import validar_permissao_escrita, formatar_resposta_agente
except ImportError:
    # Fallback se não conseguir importar
    def validar_permissao_escrita(agente: str, caminho: Path, tem_ordem_valida: bool = False):
        # Em modo fallback, sempre permitir se houver ordem válida
        if agente == "ENGENHEIRO" and tem_ordem_valida:
            return True, "OK"
        return True, "OK (fallback)"  # Modo permissivo em fallback
    
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
ARCHIVE_DIR = REPO_ROOT / "arquivo" / "ordens"
ENGINEER_IN = ORDERS_DIR / "engineer.in.yaml"
ENGINEER_OUT = REPORTS_DIR / "engineer.out.json"
ORQUESTRADOR_DIR = REPO_ROOT / "core" / "orquestrador"


def load_yaml(path: Path) -> List[Dict[str, Any]]:
    """Carrega ficheiro YAML com lista de ordens."""
    if not path.exists():
        return []
    if yaml is None:
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            # Remover comentários de linha (mas não comentários inline)
            # Não removemos todos os comentários para manter compatibilidade
            data = yaml.safe_load(content) or []
            # Garantir que é uma lista
            if not isinstance(data, list):
                # Se é um dict único, colocar em lista
                if isinstance(data, dict):
                    return [data]
                return []
            # Filtrar None e garantir que são dicts
            result = [item for item in data if isinstance(item, dict)]
            return result
    except Exception as e:
        # Se falhar, retornar lista vazia
        return []


def save_yaml(path: Path, data: List[Dict[str, Any]], tem_ordem_valida: bool = False) -> None:
    """Guarda lista de ordens em YAML."""
    # Validar permissão de escrita conforme doutrina
    permite, mensagem = validar_permissao_escrita("ENGENHEIRO", path, tem_ordem_valida)
    if not permite:
        raise PermissionError(f"❌ BLOQUEADO: {mensagem}")
    
    path.parent.mkdir(parents=True, exist_ok=True)
    if yaml is None:
        return
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)


def load_json(path: Path) -> List[Dict[str, Any]]:
    """Carrega ficheiro JSON com lista de relatórios."""
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else [data]
    except Exception:
        return []


def save_json(path: Path, data: List[Dict[str, Any]], tem_ordem_valida: bool = False) -> None:
    """Guarda lista de relatórios em JSON."""
    # Validar permissão de escrita conforme doutrina
    permite, mensagem = validar_permissao_escrita("ENGENHEIRO", path, tem_ordem_valida)
    if not permite:
        raise PermissionError(f"❌ BLOQUEADO: {mensagem}")
    
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_open_orders() -> List[Dict[str, Any]]:
    """Retorna ordens com status OPEN."""
    orders = load_yaml(ENGINEER_IN)
    # Filtrar ordens OPEN e normalizar campo id/order_id
    open_orders = []
    for o in orders:
        if o.get("status") == "OPEN":
            # Normalizar: usar 'id' se existir, senão 'order_id'
            if "id" not in o and "order_id" in o:
                o["id"] = o["order_id"]
            open_orders.append(o)
    return open_orders


def get_latest_open_order() -> Optional[Dict[str, Any]]:
    """Retorna a última ordem aberta (mais recente por created_at ou última na lista)."""
    open_orders = get_open_orders()
    if not open_orders:
        return None
    
    # Priorizar ordens com urgency="critical" ou ordem mais recente
    critical_orders = [o for o in open_orders if o.get("urgency") == "critical"]
    if critical_orders:
        # Ordenar críticas por created_at
        try:
            critical_orders.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            return critical_orders[0]
        except Exception:
            return critical_orders[0]
    
    # Ordenar por created_at se disponível
    try:
        open_orders.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    except Exception:
        pass
    
    return open_orders[0]


def execute_step(step: Dict[str, Any]) -> Dict[str, Any]:
    """Executa um step de uma ordem. Retorna resultado."""
    # GUARDA: Proibir atuação como EM/GK/SOP
    step_type = step.get("type", "command")
    step_command = step.get("command", "")
    step_target = step.get("target", "")
    step_validation = step.get("validation", "")
    
    # GUARDA: Proibir apenas ações que assumem papéis de aprovação/criação de políticas
    # Permitir comandos técnicos como "make sop" ou "make gatekeeper_prep" (são ferramentas, não papéis)
    forbidden_actions = [
        "emitir_parecer", "aprovar_gate", "criar_politica", "veta_gate",
        "gatekeeper_run", "sop_executa"  # Apenas comandos que executam funções de aprovação
    ]
    
    step_text = f"{step_command} {step_target} {step_validation}".lower()
    # Verificar apenas ações explícitas de aprovação, não ferramentas técnicas
    for forbidden_action in forbidden_actions:
        if forbidden_action in step_text:
            return {
                "step_id": step.get("id", "unknown"),
                "status": "BLOCKED",
                "error": f"PROIBIDO: Step tenta executar ação de aprovação ({forbidden_action}). ENGENHEIRO não pode assumir papéis de EM/GK/SOP (ART-03).",
                "policy": "ART-03: Consciência Técnica - ENGENHEIRO executa apenas, não aprova gates ou cria políticas"
            }
    
    step_id = step.get("id", "unknown")
    result = {
        "step_id": step_id,
        "type": step_type,
        "status": "FAILED",
        "output": "",
        "error": None,
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    try:
        if step_type == "command":
            cmd = step.get("command", "")
            if not cmd:
                result["error"] = "Comando vazio"
                return result
            
            # CORREÇÃO: Usar shell=True mas garantir que cwd é Path absoluto (suporta espaços)
            # O cwd já é REPO_ROOT que é Path absoluto, então está correto
            proc = subprocess.run(
                cmd,
                shell=True,
                cwd=str(REPO_ROOT.absolute()),  # Garantir caminho absoluto
                capture_output=True,
                text=True,
                timeout=step.get("timeout", 300),
            )
            
            result["status"] = "SUCCESS" if proc.returncode == 0 else "FAILED"
            result["output"] = proc.stdout
            result["returncode"] = proc.returncode
            if proc.stderr:
                result["error"] = proc.stderr
        
        elif step_type == "make":
            target = step.get("target", "")
            if not target:
                result["error"] = "Target Make vazio"
                return result
            
            # Suportar wildcards: se target contém % e há args, substituir
            args = step.get("args", "")
            if "%" in target and args:
                target = target.replace("%", args)
            
            # CORREÇÃO: Usar caminho absoluto entre aspas para suportar espaços
            makefile_dir = ORQUESTRADOR_DIR.absolute()
            cmd = f'make -C "{makefile_dir}" {target}'
            proc = subprocess.run(
                cmd,
                shell=True,
                cwd=str(REPO_ROOT.absolute()),  # Garantir caminho absoluto
                capture_output=True,
                text=True,
                timeout=step.get("timeout", 300),
            )
            
            result["status"] = "SUCCESS" if proc.returncode == 0 else "FAILED"
            result["output"] = proc.stdout
            result["returncode"] = proc.returncode
            if proc.stderr:
                result["error"] = proc.stderr
        
        elif step_type == "validation":
            validation_type = step.get("validation", "sop")
            if validation_type == "sop":
                # CORREÇÃO: Usar make sop que já está configurado, ou executar validator diretamente
                # Preferir make sop pois já tem todas as dependências
                makefile_dir = ORQUESTRADOR_DIR.absolute()
                cmd = f'make -C "{makefile_dir}" sop'
            elif validation_type == "pipeline":
                makefile_dir = ORQUESTRADOR_DIR.absolute()
                cmd = f'make -C "{makefile_dir}" pipeline_validate'
            elif validation_type == "gatekeeper":
                makefile_dir = ORQUESTRADOR_DIR.absolute()
                cmd = f'make -C "{makefile_dir}" gatekeeper_run'
            else:
                result["error"] = f"Tipo de validação desconhecido: {validation_type}"
                return result
            
            proc = subprocess.run(
                cmd,
                shell=True,
                cwd=str(REPO_ROOT.absolute()),  # Garantir caminho absoluto
                capture_output=True,
                text=True,
                timeout=step.get("timeout", 600),  # Validações podem demorar mais
            )
            
            result["status"] = "SUCCESS" if proc.returncode == 0 else "FAILED"
            result["output"] = proc.stdout
            result["returncode"] = proc.returncode
            if proc.stderr:
                result["error"] = proc.stderr
        
        else:
            result["error"] = f"Tipo de step desconhecido: {step_type}"
    
    except subprocess.TimeoutExpired:
        result["error"] = "Timeout excedido"
        result["status"] = "TIMEOUT"
    except Exception as e:
        result["error"] = str(e)
        result["status"] = "ERROR"
    
    return result


def generate_report(order: Dict[str, Any], step_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Gera relatório padronizado para o Estado-Maior."""
    # Contar resultados
    success_count = sum(1 for r in step_results if r.get("status") == "SUCCESS")
    failed_count = sum(1 for r in step_results if r.get("status") in ("FAILED", "ERROR", "TIMEOUT"))
    
    # Extrair métricas dos outputs
    metrics = {
        "steps_total": len(step_results),
        "steps_success": success_count,
        "steps_failed": failed_count,
        "success_rate": round(success_count / len(step_results) * 100, 2) if step_results else 0,
    }
    
    # Artefactos gerados (identificar por padrões nos outputs)
    artefacts = []
    for result in step_results:
        if result.get("status") == "SUCCESS":
            output = result.get("output", "")
            # Detectar artefactos comuns
            if "relatorios/" in output:
                artefacts.append("Relatórios gerados")
            if "coverage.xml" in output or "coverage" in output.lower():
                artefacts.append("Coverage report")
            if "sbom.json" in output:
                artefacts.append("SBOM")
    
    # Falhas graves identificadas (POLÍTICA ZERO RISCO: não existem riscos, apenas falhas)
    failures = []
    for result in step_results:
        if result.get("status") != "SUCCESS":
            failures.append({
                "step": result.get("step_id", "unknown"),
                "severity": "CRITICAL",  # Qualquer falha é crítica e bloqueia
                "description": result.get("error", "Step falhou"),
                "policy": "ZERO RISCO: Falhas são bloqueios imediatos",
            })
    
    # Recomendações
    recommendations = []
    if failed_count > 0:
        recommendations.append("POLÍTICA ZERO RISCO: Corrigir todas as falhas antes de prosseguir")
    if success_count == len(step_results) and len(failures) == 0:
        recommendations.append("Ordem executada com sucesso. Sistema livre de falhas graves.")
    
    report = {
        "order_id": order.get("id", "unknown"),
        "order_title": order.get("title", "Sem título"),
        "status": "DONE",
        "executed_at": datetime.utcnow().isoformat(),
        "executed_by": "ENGENHEIRO-v3.0",
        "order_created_at": order.get("created_at", ""),
        "ack_accepted_at": order.get("ack_at", ""),
        "metrics": metrics,
        "artefacts": list(set(artefacts)),  # Remover duplicados
        "failures": failures,  # POLÍTICA ZERO RISCO: falhas são bloqueios imediatos
        "recommendations": recommendations,
        "step_results": step_results,
        "logs": {
            "order_path": str(ENGINEER_IN.relative_to(REPO_ROOT)),
            "report_path": str(ENGINEER_OUT.relative_to(REPO_ROOT)),
        },
    }
    
    return report


def is_mailbox_valid(orders):
    if not orders or not isinstance(orders, list):
        return False
    if len(orders) == 0:
        return False
    for o in orders:
        if not isinstance(o, dict):
            return False
        # Aceitar tanto 'id' quanto 'order_id' como identificador válido
        if 'id' not in o and 'order_id' not in o:
            return False
    return True

def validate_order_format_inline(order: Dict[str, Any]) -> tuple[bool, List[str]]:
    """Validação inline do formato da ordem. Retorna (válido, erros)."""
    errors = []
    
    # Verificar steps são comandos executáveis
    steps = order.get("steps", [])
    for i, step in enumerate(steps, 1):
        if isinstance(step, str):
            # Step como string: deve conter comando executável após ":"
            if ":" in step:
                parts = step.split(":", 1)
                command = parts[1].strip() if len(parts) > 1 else ""
                if not command or len(command) < 5:
                    errors.append(f"Step {i} parece descrição, não comando: '{step[:50]}...'")
            else:
                # String sem ":" provavelmente é descrição
                errors.append(f"Step {i} parece descrição sem comando: '{step[:50]}...'")
        elif isinstance(step, dict):
            step_type = step.get("type", "")
            if step_type not in ["command", "make", "validation"]:
                errors.append(f"Step {i} tipo inválido: '{step_type}'")
            if step_type == "command" and not step.get("command"):
                errors.append(f"Step {i} tipo 'command' sem campo 'command'")
    
    return len(errors) == 0, errors


def cmd_executa() -> int:
    """Executa a última ordem aberta, com checagem robusta de mailbox."""
    # GUARDA: Verificar se há outros PINs ativos além do v3
    other_pins = [
        REPO_ROOT / "Torre/orquestrador/engineer_executor.py",
        REPO_ROOT / "Torre/orquestrador/PIN.md",
    ]
    active_other_pins = [p for p in other_pins if p.exists()]
    if active_other_pins:
        print("❌ EXECUÇÃO ABORTADA: Outros PINs ativos encontrados além do v3.0")
        for pin_path in active_other_pins:
            print(f"   ⚠️ {pin_path.relative_to(REPO_ROOT)}")
        print("   Apenas PIN v3.0 (core/orquestrador/engineer_cli.py) deve estar ativo.")
        print("   Mova PINs antigos para factory/pins/_deprecated/ antes de executar.")
        return 3
    
    print("🔍 Validando mailbox engineer.in.yaml...")
    raw = None
    try:
        raw = open(ENGINEER_IN,"r",encoding="utf-8").read()
    except Exception:
        print("❌ Não foi possível ler mailbox engineer.in.yaml")
        return 2
    try:
        orders = load_yaml(ENGINEER_IN)
        print(f"🔍 DEBUG: Ordens carregadas: {len(orders)}")
        if orders:
            print(f"🔍 DEBUG: Primeira ordem keys: {list(orders[0].keys())}")
    except Exception as e:
        print(f"❌ Erro de parsing YAML: {e}\n{raw[:1000]}")
        return 2
    if not is_mailbox_valid(orders):
        print("❌ Mailbox de ordens inválido ou vazio. Nenhuma execução será feita.")
        print(f"🔍 DEBUG: Tipo de orders: {type(orders)}, Tamanho: {len(orders) if isinstance(orders, list) else 'N/A'}")
        if orders and len(orders) > 0:
            print(f"🔍 DEBUG: Primeira ordem: {orders[0]}")
        print("   Corrija o engineer.in.yaml. Formato: lista de dicionários válidos (ordens OPEN). Exemplo:")
        print("- order_id: ...\n  ...campos obrigatórios...")
        return 2
    print("✅ Mailbox yaml válido. Seguindo para busca de ordem aberta...")
    
    order = get_latest_open_order()
    if not order:
        print("❌ Nenhuma ordem aberta encontrada em engineer.in.yaml")
        return 1
    
    order_id = order.get("id", "unknown")
    order_title = order.get("title", "Sem título")
    print(f"📋 Ordem encontrada: {order_id} — {order_title}")
    
    # GUARDA: Validar formato da ordem (steps executáveis)
    format_valid, format_errors = validate_order_format_inline(order)
    if not format_valid:
        print("❌ EXECUÇÃO BLOQUEADA: Ordem não segue formato padrão")
        print("   Erros de formato:")
        for error in format_errors:
            print(f"      - {error}")
        print("   Consulte: relatorios/modelo_ordem_engenheiro.md")
        print("   Regra: Steps devem ser comandos executáveis, não descrições")
        return 2
    
    # GUARDA: ACK obrigatório - não executa sem ACK explícito
    ack = order.get("ack", {})
    if isinstance(ack, dict):
        ack_status = ack.get("status", "PENDING")
    else:
        ack_status = ack if ack else "PENDING"
    
    if ack_status != "ACCEPTED":
        print(f"❌ EXECUÇÃO BLOQUEADA: Ordem não tem ACK=ACCEPTED")
        print(f"   ACK atual: {ack_status}")
        print(f"   ACK completo: {ack}")
        print(f"   Ordens devem ser explicitamente aceites antes da execução.")
        print(f"   Fluxo obrigatório: Estado-Maior → ordem → ACK → execução")
        return 1
    
    # Executar steps
    steps = order.get("steps", [])
    if not steps:
        print("⚠️ Ordem sem steps definidos")
        steps = []
    
    print(f"🚀 Executando {len(steps)} step(s)...")
    step_results = []
    
    for step in steps:
        # Normalizar step: se for string, converter para dict
        if isinstance(step, str):
            # Extrair comando se houver ":" (formato "descrição: comando")
            if ":" in step:
                parts = step.split(":", 1)
                description = parts[0].strip()
                command = parts[1].strip()
            else:
                description = step
                command = step
            
            step = {
                "id": f"step-{len(step_results)+1}",
                "type": "command",
                "command": command,
                "description": description
            }
        step_id = step.get("id", f"step-{len(step_results)+1}")
        print(f"  → Step: {step_id}")
        result = execute_step(step)
        step_results.append(result)
        
        if result.get("status") == "SUCCESS":
            print(f"    ✅ Sucesso")
        else:
            print(f"    ❌ Falhou: {result.get('error', 'Erro desconhecido')}")
    
    # Gerar relatório
    print("📊 Gerando relatório...")
    report = generate_report(order, step_results)
    
    # Guardar relatório (com validação de ordem válida)
    reports = load_json(ENGINEER_OUT)
    reports.append(report)
    save_json(ENGINEER_OUT, reports, tem_ordem_valida=True)
    
    # Atualizar ordem para DONE (com validação de ordem válida)
    order["status"] = "DONE"
    order["completed_at"] = datetime.utcnow().isoformat()
    orders = load_yaml(ENGINEER_IN)
    for i, o in enumerate(orders):
        if o.get("id") == order_id:
            orders[i] = order
            break
    save_yaml(ENGINEER_IN, orders, tem_ordem_valida=True)
    
    # Determinar status da pipeline
    gate = order.get("gate", "G0")
    pipeline_status = "PIPELINE" if gate and gate != "G0" else "FORA_PIPELINE"
    
    # Gerar resposta formatada conforme doutrina
    conteudo_resposta = f"""✅ Ordem {order_id} executada e marcada como DONE
📄 Relatório salvo em: {ENGINEER_OUT.relative_to(REPO_ROOT)}

📊 Resumo:
   Steps executados: {report['metrics']['steps_total']}
   Sucessos: {report['metrics']['steps_success']}
   Falhas: {report['metrics']['steps_failed']}"""
    
    if report.get("failures"):
        conteudo_resposta += f"\n\n❌ Falhas graves identificadas: {len(report['failures'])}\n   POLÍTICA ZERO RISCO: Todas as falhas são bloqueios imediatos"
        for failure in report["failures"]:
            conteudo_resposta += f"\n   - {failure['step']}: {failure['description']}"
    
    # Determinar próxima ação e comando
    if report["metrics"]["steps_failed"] > 0:
        proxima_acao = "Corrigir falhas antes de prosseguir"
        comando_executar = "ESTADO-MAIOR ANALISAR FALHAS E CORRIGIR ANTES DE PROSSEGUIR"
    else:
        proxima_acao = "Aguardando novas ordens do Estado-Maior"
        comando_executar = "ESTADO-MAIOR ANALISAR RELATÓRIO E EMITIR NOVA ORDEM SE NECESSÁRIO"
    
    resposta_formatada = formatar_resposta_agente(
        "ENGENHEIRO",
        conteudo_resposta,
        pipeline_status=pipeline_status,
        proxima_acao=proxima_acao,
        comando_executar=comando_executar
    )
    
    print(resposta_formatada)
    
    return 0 if report["metrics"]["steps_failed"] == 0 else 1


def cmd_status() -> int:
    """Mostra status atual das ordens."""
    orders = load_yaml(ENGINEER_IN)
    reports = load_json(ENGINEER_OUT)
    
    open_orders = [o for o in orders if o.get("status") == "OPEN"]
    done_orders = [o for o in orders if o.get("status") == "DONE"]
    
    # Construir conteúdo da resposta
    conteudo_resposta = f"""📊 Status do ENGENHEIRO
{'=' * 50}
📋 Ordens abertas: {len(open_orders)}"""
    
    for order in open_orders:
        order_id = order.get("id", "unknown")
        title = order.get("title", "Sem título")
        created = order.get("created_at", "N/A")
        ack = order.get("ack", "PENDING")
        conteudo_resposta += f"\n   - {order_id}: {title}\n     Criada: {created}\n     ACK: {ack}"
    
    conteudo_resposta += f"\n\n✅ Ordens concluídas: {len(done_orders)}"
    if done_orders:
        for order in done_orders[-5:]:  # Últimas 5
            order_id = order.get("id", "unknown")
            title = order.get("title", "Sem título")
            completed = order.get("completed_at", "N/A")
            conteudo_resposta += f"\n   - {order_id}: {title} (concluída: {completed})"
    
    conteudo_resposta += f"\n\n📄 Relatórios gerados: {len(reports)}"
    if reports:
        latest = reports[-1]
        conteudo_resposta += f"\n   Último: {latest.get('order_id', 'unknown')} — {latest.get('status', 'unknown')}\n   Executado em: {latest.get('executed_at', 'N/A')}"
    
    # Formatar resposta conforme doutrina
    resposta_formatada = formatar_resposta_agente(
        "ENGENHEIRO",
        conteudo_resposta,
        pipeline_status="FORA_PIPELINE",
        proxima_acao="Status consultado - Sistema operacional",
        comando_executar="ESTADO-MAIOR VERIFICAR STATUS E EMITIR ORDEM SE NECESSÁRIO"
    )
    
    print(resposta_formatada)
    
    return 0


def cmd_limpa() -> int:
    """Rotaciona relatórios antigos."""
    conteudo_resposta = "🧹 Rotacionando relatórios antigos...\n"
    
    # Usar o script existente se disponível
    rotate_script = REPO_ROOT / "core" / "orquestrador" / "orders_gc.py"
    if rotate_script.exists():
        try:
            subprocess.run([sys.executable, str(rotate_script)], cwd=str(REPO_ROOT), check=True)
            conteudo_resposta += "✅ Rotação concluída"
            resultado = 0
        except subprocess.CalledProcessError:
            conteudo_resposta += "⚠️ Erro ao executar script de rotação"
            resultado = 1
    else:
        conteudo_resposta += "⚠️ Script de rotação não encontrado (orders_gc.py)"
        resultado = 1
    
    # Formatar resposta conforme doutrina
    resposta_formatada = formatar_resposta_agente(
        "ENGENHEIRO",
        conteudo_resposta,
        pipeline_status="FORA_PIPELINE",
        proxima_acao="Limpeza concluída" if resultado == 0 else "Corrigir erro de rotação",
        comando_executar="ESTADO-MAIOR VERIFICAR LIMPEZA E CONTINUAR OPERAÇÃO"
    )
    
    print(resposta_formatada)
    
    return resultado


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(prog="engineer", description="PIN — ENGENHEIRO v3.0")
    sub = parser.add_subparsers(dest="cmd", required=True)
    
    sub.add_parser("executa", help="Executa a última ordem aberta")
    sub.add_parser("status", help="Mostra status atual")
    sub.add_parser("limpa", help="Rotaciona relatórios antigos")
    
    args = parser.parse_args(argv)
    
    if args.cmd == "executa":
        return cmd_executa()
    elif args.cmd == "status":
        return cmd_status()
    elif args.cmd == "limpa":
        return cmd_limpa()
    
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

