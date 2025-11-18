#!/usr/bin/env python3
"""
CLI do Orquestrador da FÁBRICA 2.0
Implementação mínima para compatibilidade com workflows GitHub Actions
"""
import argparse
import subprocess
import sys
from pathlib import Path

# Caminhos
ORQUESTRADOR_DIR = Path(__file__).parent
REPO_ROOT = ORQUESTRADOR_DIR.parent.parent


def cmd_gatekeeper_prep() -> int:
    """Prepara inputs do Gatekeeper."""
    try:
        result = subprocess.run(
            ["make", "-C", str(ORQUESTRADOR_DIR), "gatekeeper_prep"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return result.returncode
    except Exception as e:
        print(f"ERRO ao preparar Gatekeeper: {e}", file=sys.stderr)
        return 1


def cmd_gatekeeper_run() -> int:
    """Executa Gatekeeper."""
    try:
        # Primeiro preparar inputs
        prep_result = subprocess.run(
            ["make", "-C", str(ORQUESTRADOR_DIR), "gatekeeper_prep"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
        )
        
        if prep_result.returncode != 0:
            print(f"AVISO: gatekeeper_prep falhou, continuando...", file=sys.stderr)
        
        # Executar Gatekeeper via Makefile
        result = subprocess.run(
            ["make", "-C", str(ORQUESTRADOR_DIR), "gatekeeper_run"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
        )
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        
        return result.returncode
        
    except Exception as e:
        print(f"ERRO ao executar Gatekeeper: {e}", file=sys.stderr)
        return 1


def main() -> int:
    """Função principal."""
    parser = argparse.ArgumentParser(
        prog="fabric_orquestrador",
        description="CLI do Orquestrador da FÁBRICA 2.0"
    )
    
    sub = parser.add_subparsers(dest="cmd", required=True)
    
    # Comandos
    sub.add_parser("gatekeeper_prep", help="Prepara inputs do Gatekeeper")
    sub.add_parser("gatekeeper_run", help="Executa Gatekeeper")
    
    args = parser.parse_args()
    
    if args.cmd == "gatekeeper_prep":
        return cmd_gatekeeper_prep()
    elif args.cmd == "gatekeeper_run":
        return cmd_gatekeeper_run()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

