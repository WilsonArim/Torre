#!/usr/bin/env python3
"""
torre/orquestrador/cli.py - CLI do Orquestrador da TORRE

PIN — Engenheiro da TORRE
Executa ordens do Estado-Maior e operações de treino
Regras: ART-04 (Verificabilidade), ART-07 (Transparência), ART-09 (Evidência)
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


# Caminhos absolutos
TORRE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = TORRE_ROOT.parent
ORDERS_DIR = REPO_ROOT / "ordem" / "ordens"
REPORTS_DIR = REPO_ROOT / "relatorios" / "para_estado_maior"
ENGINEER_IN = ORDERS_DIR / "engineer.in.yaml"
ENGINEER_OUT = REPORTS_DIR / "engineer.out.json"
CORE_ORQUESTRADOR = REPO_ROOT / "core" / "orquestrador"
TORRE_CLI = TORRE_ROOT / "cli"


def log_message(message: str, level: str = "INFO") -> None:
    """Regista mensagem no log."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    log_file = TORRE_ROOT / "logs" / f"orquestrador_{datetime.now().strftime('%Y%m%d')}.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    log_line = f"[{timestamp}] [{level}] {message}\n"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_line)
    
    print(f"[{level}] {message}")


def load_yaml(path: Path) -> List[Dict[str, Any]]:
    """Carrega ficheiro YAML."""
    if not path.exists():
        return []
    if yaml is None:
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or []
            return data if isinstance(data, list) else [data]
    except Exception:
        return []


def save_json(path: Path, data: List[Dict[str, Any]]) -> None:
    """Guarda JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_open_orders() -> List[Dict[str, Any]]:
    """Retorna ordens abertas do Estado-Maior."""
    orders = load_yaml(ENGINEER_IN)
    return [o for o in orders if o.get("status") == "OPEN"]


def cmd_treino(phase: str) -> int:
    """Executa treino de uma fase específica."""
    valid_phases = ["fase0", "fase1", "fase2", "fase3", "fase4", "fase5"]
    
    if phase not in valid_phases:
        print(f"❌ Fase inválida: {phase}")
        print(f"   Fases válidas: {', '.join(valid_phases)}")
        return 1
    
    # Mapear fase para número
    phase_num = int(phase.replace("fase", ""))
    
    log_message(f"Iniciando treino da {phase}", "INFO")
    
    # Executar treino via CLI da TORRE
    train_script = TORRE_CLI / "train.py"
    if not train_script.exists():
        log_message(f"ERRO: Script de treino não encontrado: {train_script}", "ERROR")
        return 1
    
    try:
        result = subprocess.run(
            [sys.executable, str(train_script), "--phase", str(phase_num)],
            cwd=str(TORRE_ROOT),
            capture_output=True,
            text=True,
            timeout=3600,  # 1 hora máximo
        )
        
        if result.returncode == 0:
            log_message(f"Treino da {phase} concluído com sucesso", "INFO")
            print(result.stdout)
            return 0
        else:
            log_message(f"ERRO no treino da {phase}: {result.stderr}", "ERROR")
            print(result.stderr)
            return 1
            
    except subprocess.TimeoutExpired:
        log_message(f"Timeout no treino da {phase}", "ERROR")
        return 1
    except Exception as e:
        log_message(f"ERRO ao executar treino: {e}", "ERROR")
        return 1


def cmd_pipeline_validate() -> int:
    """Valida pipeline conforme SOP."""
    log_message("Validando pipeline", "INFO")
    
    try:
        result = subprocess.run(
            [sys.executable, str(CORE_ORQUESTRADOR / "cli.py"), "validate_pipeline"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=300,
        )
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        
        if result.returncode == 0:
            log_message("Pipeline validada com sucesso", "INFO")
        else:
            log_message(f"Pipeline inválida (returncode: {result.returncode})", "WARNING")
        
        return result.returncode
        
    except Exception as e:
        log_message(f"ERRO ao validar pipeline: {e}", "ERROR")
        return 1


def cmd_sop() -> int:
    """Executa validação SOP."""
    log_message("Executando validação SOP", "INFO")
    
    validator_script = REPO_ROOT / "core" / "scripts" / "validator.py"
    if not validator_script.exists():
        log_message(f"ERRO: Script de validação SOP não encontrado", "ERROR")
        return 1
    
    try:
        result = subprocess.run(
            [sys.executable, str(validator_script)],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=300,
        )
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        
        if result.returncode == 0:
            log_message("SOP validado com sucesso", "INFO")
        else:
            log_message(f"SOP bloqueado (returncode: {result.returncode})", "WARNING")
        
        return result.returncode
        
    except Exception as e:
        log_message(f"ERRO ao executar SOP: {e}", "ERROR")
        return 1


def cmd_gatekeeper_run() -> int:
    """Executa Gatekeeper."""
    log_message("Executando Gatekeeper", "INFO")
    
    try:
        # Primeiro preparar inputs
        prep_result = subprocess.run(
            [sys.executable, str(CORE_ORQUESTRADOR / "cli.py"), "gatekeeper_prep"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=300,
        )
        
        if prep_result.returncode != 0:
            log_message(f"ERRO ao preparar Gatekeeper: {prep_result.stderr}", "ERROR")
            return 1
        
        # Executar Gatekeeper
        result = subprocess.run(
            [sys.executable, str(CORE_ORQUESTRADOR / "cli.py"), "gatekeeper_run"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=300,
        )
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        
        if result.returncode == 0:
            log_message("Gatekeeper executado com sucesso", "INFO")
        else:
            log_message(f"Gatekeeper emitiu VETO (returncode: {result.returncode})", "WARNING")
        
        return result.returncode
        
    except Exception as e:
        log_message(f"ERRO ao executar Gatekeeper: {e}", "ERROR")
        return 1


def cmd_executa_ordem() -> int:
    """Executa ordem do Estado-Maior (ciclo completo v1.0)."""
    log_message("Procurando ordem aberta do Estado-Maior", "INFO")
    
    # Usar o executor v1.0 específico da TORRE
    executor = TORRE_ROOT / "orquestrador" / "engineer_executor.py"
    if executor.exists():
        try:
            result = subprocess.run(
                [sys.executable, str(executor), "executa"],
                cwd=str(REPO_ROOT),
                capture_output=False,
                timeout=3600,
            )
            return result.returncode
        except Exception as e:
            log_message(f"ERRO ao executar ordem via executor: {e}", "ERROR")
            return 1
    else:
        # Fallback para engineer_cli.py do core
        engineer_cli = CORE_ORQUESTRADOR / "engineer_cli.py"
        if engineer_cli.exists():
            try:
                result = subprocess.run(
                    [sys.executable, str(engineer_cli), "executa"],
                    cwd=str(REPO_ROOT),
                    capture_output=False,
                    timeout=3600,
                )
                return result.returncode
            except Exception as e:
                log_message(f"ERRO ao executar ordem via engineer_cli: {e}", "ERROR")
                return 1
        else:
            log_message("Nenhum executor encontrado", "ERROR")
            return 1


def cmd_status() -> int:
    """Mostra status das ordens e operações."""
    open_orders = get_open_orders()
    
    print("📊 Status da TORRE")
    print("=" * 50)
    print(f"📋 Ordens abertas: {len(open_orders)}")
    
    for order in open_orders:
        order_id = order.get("order_id", "unknown")
        objective = order.get("objective", "Sem objetivo")
        created_at = order.get("created_at", "N/A")
        print(f"   - {order_id}")
        print(f"     {objective}")
        print(f"     Criada: {created_at}")
    
    # Verificar relatórios
    reports = []
    if ENGINEER_OUT.exists():
        try:
            reports = json.loads(ENGINEER_OUT.read_text(encoding="utf-8"))
        except Exception:
            pass
    
    print(f"\n📄 Relatórios gerados: {len(reports)}")
    if reports:
        latest = reports[-1]
        print(f"   Último: {latest.get('order_id', 'unknown')}")
        print(f"   Status: {latest.get('status', 'unknown')}")
        print(f"   Executado: {latest.get('executed_at', 'N/A')}")
    
    return 0


def generate_report_entry(order_id: str, command: str, result: int, output: str = "") -> Dict[str, Any]:
    """Gera entrada de relatório para o Estado-Maior."""
    return {
        "order_id": order_id,
        "command": command,
        "status": "SUCCESS" if result == 0 else "FAILED",
        "executed_at": datetime.utcnow().isoformat(),
        "executed_by": "ENGENHEIRO-TORRE",
        "output": output[:1000] if output else "",  # Limitar tamanho
        "returncode": result,
    }


# --- WHO ACTS ----------------------------------------------------
import re

OWNERSHIP_MATRIX = [
  (r"(constitui|lei|sop|superpipeline|cap[ií]tulo|gate(s)?|aprova|bloqueia)", "ESTADO-MAIOR"),
  (r"(cria ordem|order|ordem|assinatura|gpg|checksum)", "ESTADO-MAIOR"),
  (r"(c[oó]digo|refator|test(e|es)|pytest|lint|make|script|cli\.py|yaml|json|sbom)", "ENGENHEIRO"),
  (r"(instala|setup|depend[eê]ncia|pre-commit|semgrep|bandit|trivy|cyclonedx)", "ENGENHEIRO"),
]

def who_acts(task:str, gate:str|None=None):
    if gate in ("G0","G2","G4"): return "ESTADO-MAIOR"
    if gate in ("G1","G3"): return "ENGENHEIRO"
    t = task.lower()
    for pat, owner in OWNERSHIP_MATRIX:
        if re.search(pat, t): return owner
    # fallback bootstrap: estratégia->EM, execução->Engenheiro
    return "ESTADO-MAIOR" if len(t) < 12 else "ENGENHEIRO"

# --- CLI Argumento: who_acts -----
if __name__ == "__main__":
    if len(sys.argv)>=2 and sys.argv[1]=="who_acts":
        gate = None
        task = " ".join(sys.argv[2:]) if len(sys.argv)>2 else ""
        # aceitar --gate Gx opcional
        for i,a in enumerate(sys.argv):
            if a=="--gate" and i+1<len(sys.argv): gate=sys.argv[i+1]
        owner = who_acts(task, gate)
        msg = f"OWNER: {owner} — Próxima ação: {'decidir/emitir ordem' if owner=='ESTADO-MAIOR' else 'executar/gerar relatório'}"
        print(json.dumps({"owner":owner,"message":msg}, ensure_ascii=False))
        sys.exit(0)


def main(argv: List[str]) -> int:
    """Função principal."""
    parser = argparse.ArgumentParser(
        prog="torre_orquestrador",
        description="CLI do Orquestrador da TORRE — PIN Engenheiro"
    )
    
    sub = parser.add_subparsers(dest="cmd", required=True)
    
    # Comando treino
    p_treino = sub.add_parser("treino", help="Executa treino de uma fase")
    p_treino.add_argument("phase", choices=["fase0", "fase1", "fase2", "fase3", "fase4", "fase5"],
                         help="Fase de treino a executar")
    
    # Comandos de validação
    sub.add_parser("pipeline_validate", help="Valida pipeline")
    sub.add_parser("sop", help="Executa validação SOP")
    sub.add_parser("gatekeeper_run", help="Executa Gatekeeper")
    
    # Comandos de ordens
    sub.add_parser("executa", help="Executa ordem do Estado-Maior")
    sub.add_parser("status", help="Mostra status das ordens")
    
    args = parser.parse_args(argv)
    
    if args.cmd == "treino":
        return cmd_treino(args.phase)
    elif args.cmd == "pipeline_validate":
        return cmd_pipeline_validate()
    elif args.cmd == "sop":
        return cmd_sop()
    elif args.cmd == "gatekeeper_run":
        return cmd_gatekeeper_run()
    elif args.cmd == "executa":
        return cmd_executa_ordem()
    elif args.cmd == "status":
        return cmd_status()
    
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

