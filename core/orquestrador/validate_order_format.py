#!/usr/bin/env python3
"""
Validador de Formato de Ordens - ENGENHEIRO v3.0
Garante que todas as ordens seguem o padrão documentado em modelo_ordem_engenheiro.md
Respeita ART-04 (Verificabilidade) e ART-09 (Evidência)
"""
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

try:
    import yaml  # type: ignore
except Exception:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parents[2]
ORDERS_DIR = REPO_ROOT / "ordem" / "ordens"
ENGINEER_IN = ORDERS_DIR / "engineer.in.yaml"
MODELO_DOC = REPO_ROOT / "relatorios" / "modelo_ordem_engenheiro.md"


def validate_order_format(order: Dict[str, Any]) -> tuple[bool, List[str]]:
    """Valida se ordem segue formato padrão. Retorna (válido, lista_erros)."""
    errors = []
    
    # Campos obrigatórios
    required_fields = [
        "order_id", "version", "from_role", "to_role", 
        "project", "objective", "ack", "status"
    ]
    
    for field in required_fields:
        if field not in order:
            errors.append(f"Campo obrigatório ausente: {field}")
    
    # ACK obrigatório e ACCEPTED para execução
    ack = order.get("ack", {})
    if isinstance(ack, dict):
        ack_status = ack.get("status", "PENDING")
        if ack_status == "PENDING" and order.get("status") == "OPEN":
            errors.append("⚠️ ACK ainda PENDING - ordem não será executada até ACK=ACCEPTED")
    elif not ack:
        errors.append("Campo 'ack' ausente - ACK obrigatório")
    
    # Steps devem ser comandos executáveis, não descrições
    steps = order.get("steps", [])
    if not steps:
        errors.append("⚠️ Ordem sem steps definidos")
    else:
        for i, step in enumerate(steps, 1):
            if isinstance(step, str):
                # Step como string: verificar se parece comando executável
                if not any(char in step for char in [":", " ", "(", "="]):
                    # Provavelmente só descrição, não comando
                    errors.append(f"Step {i} parece descrição, não comando executável: '{step[:50]}...'")
            elif isinstance(step, dict):
                step_type = step.get("type", "")
                if step_type not in ["command", "make", "validation"]:
                    errors.append(f"Step {i} tipo inválido: '{step_type}' (aceites: command, make, validation)")
                
                if step_type == "command" and not step.get("command"):
                    errors.append(f"Step {i} tipo 'command' sem campo 'command'")
                if step_type == "make" and not step.get("target"):
                    errors.append(f"Step {i} tipo 'make' sem campo 'target'")
                if step_type == "validation" and not step.get("validation"):
                    errors.append(f"Step {i} tipo 'validation' sem campo 'validation'")
    
    return len(errors) == 0, errors


def validate_all_orders() -> int:
    """Valida todas as ordens no mailbox."""
    if not ENGINEER_IN.exists():
        print(f"❌ Mailbox não encontrado: {ENGINEER_IN}")
        return 1
    
    if yaml is None:
        print("⚠️ PyYAML não disponível, validação limitada")
        return 1
    
    try:
        with open(ENGINEER_IN, "r", encoding="utf-8") as f:
            orders = yaml.safe_load(f) or []
        
        if not isinstance(orders, list):
            print("❌ Mailbox deve conter lista de ordens")
            return 1
        
        print(f"🔍 Validando {len(orders)} ordem(ns)...")
        print("=" * 60)
        
        all_valid = True
        for i, order in enumerate(orders, 1):
            if not isinstance(order, dict):
                continue
            
            order_id = order.get("order_id", f"ordem-{i}")
            status = order.get("status", "UNKNOWN")
            
            print(f"\n📋 Ordem {i}: {order_id} (status: {status})")
            
            is_valid, errors = validate_order_format(order)
            
            if is_valid:
                print("   ✅ Formato válido")
            else:
                all_valid = False
                print("   ❌ Erros encontrados:")
                for error in errors:
                    print(f"      - {error}")
        
        print("\n" + "=" * 60)
        if all_valid:
            print("✅ Todas as ordens seguem o padrão documentado")
            print(f"📄 Modelo de referência: {MODELO_DOC.relative_to(REPO_ROOT)}")
            return 0
        else:
            print("❌ Algumas ordens não seguem o padrão")
            print(f"📄 Consulte o modelo: {MODELO_DOC.relative_to(REPO_ROOT)}")
            return 1
            
    except Exception as e:
        print(f"❌ Erro ao validar ordens: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(validate_all_orders())

