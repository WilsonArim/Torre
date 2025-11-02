#!/usr/bin/env python3
"""
torre/cli/validate_dataset.py - Validador de datasets conforme Constituição

Agente: Engenheiro da TORRE
Função: Valida datasets antes do treino (conformidade constitucional)
Regras: ART-04 (Verificabilidade), ART-09 (Evidência)
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Caminhos absolutos
TORRE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = TORRE_ROOT.parent
RELATORIOS_DIR = REPO_ROOT / "relatorios"
CONSTITUICAO_PATH = REPO_ROOT / "core" / "sop" / "constituição.yaml"


def validate_dataset_location(dataset_path: Path) -> bool:
    """Valida que dataset está dentro de torre/ (segurança)."""
    try:
        dataset_path.resolve().relative_to(TORRE_ROOT)
        return True
    except ValueError:
        print(f"❌ ERRO: Dataset fora do domínio torre/ (violação de segurança)")
        print(f"   Dataset: {dataset_path}")
        print(f"   Domínio permitido: {TORRE_ROOT}")
        return False


def validate_constitutional_compliance(dataset_path: Path) -> Dict[str, Any]:
    """Valida conformidade constitucional do dataset."""
    violations = []
    
    # Verificar que não referencia código fora do núcleo
    if dataset_path.is_file():
        try:
            content = dataset_path.read_text(encoding="utf-8")
            # Verificar referências a deprecated/ ou node_modules/
            if "deprecated/" in content or "node_modules/" in content:
                violations.append("Referências a diretórios proibidos (deprecated/, node_modules/)")
        except Exception:
            pass
    
    # Verificar que não altera Constituição
    if "constituição.yaml" in str(dataset_path) and "modif" in str(dataset_path).lower():
        violations.append("Tentativa de modificar Constituição (ART-01: Integridade)")
    
    return {
        "valid": len(violations) == 0,
        "violations": violations,
    }


def validate_dataset_structure(dataset_path: Path) -> Dict[str, Any]:
    """Valida estrutura básica do dataset."""
    issues = []
    
    if not dataset_path.exists():
        return {"valid": False, "issues": ["Dataset não encontrado"]}
    
    if dataset_path.is_file():
        # Dataset único
        if not dataset_path.suffix in [".json", ".yaml", ".yml", ".md", ".txt"]:
            issues.append(f"Formato não suportado: {dataset_path.suffix}")
    
    elif dataset_path.is_dir():
        # Dataset diretório
        files = list(dataset_path.rglob("*"))
        if len(files) == 0:
            issues.append("Diretório vazio")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
    }


def main(argv: list[str]) -> int:
    """Função principal do validador."""
    parser = argparse.ArgumentParser(
        prog="torre_validate_dataset",
        description="Valida dataset conforme Constituição"
    )
    
    parser.add_argument(
        "--dataset",
        type=Path,
        required=True,
        help="Caminho do dataset a validar"
    )
    
    args = parser.parse_args(argv)
    
    dataset_path = args.dataset
    
    # Resolver caminho relativo
    if not dataset_path.is_absolute():
        dataset_path = TORRE_ROOT / dataset_path
    
    print(f"🔍 Validando dataset: {dataset_path}")
    
    # Validação 1: Localização (segurança)
    if not validate_dataset_location(dataset_path):
        return 1
    
    # Validação 2: Estrutura
    structure_result = validate_dataset_structure(dataset_path)
    if not structure_result["valid"]:
        print(f"❌ Estrutura inválida:")
        for issue in structure_result["issues"]:
            print(f"   - {issue}")
        return 1
    
    # Validação 3: Conformidade constitucional
    compliance_result = validate_constitutional_compliance(dataset_path)
    if not compliance_result["valid"]:
        print(f"❌ Violações constitucionais detectadas:")
        for violation in compliance_result["violations"]:
            print(f"   - {violation}")
        return 1
    
    print(f"✅ Dataset válido e conforme à Constituição")
    print(f"   Localização: ✓")
    print(f"   Estrutura: ✓")
    print(f"   Conformidade: ✓")
    
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

