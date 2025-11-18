#!/usr/bin/env python3
"""
Validador Pré-Commit FÁBRICA 2.0
Imita 100% os workflows GitHub localmente e bloqueia commit/push se falhar

Conforme ordem do Estado-Maior: eliminar ciclos de erro após push
"""
import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
MAKEFILE_DIR = REPO_ROOT / "core" / "orquestrador"
CONSTITUICAO_PATH = REPO_ROOT / "core" / "sop" / "constituição.yaml"
VALIDATOR_PATH = REPO_ROOT / "core" / "scripts" / "validator.py"
REL_DIR = REPO_ROOT / "relatorios"


class Colors:
    """Cores para output."""
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


def print_step(step_num: int, total: int, message: str) -> None:
    """Imprime passo da validação."""
    print(f"\n{Colors.OKBLUE}[{step_num}/{total}]{Colors.ENDC} {Colors.BOLD}{message}{Colors.ENDC}")


def print_success(message: str) -> None:
    """Imprime sucesso."""
    print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")


def print_error(message: str) -> None:
    """Imprime erro."""
    print(f"{Colors.FAIL}❌ {message}{Colors.ENDC}")


def print_warning(message: str) -> None:
    """Imprime aviso."""
    print(f"{Colors.WARNING}⚠️  {message}{Colors.ENDC}")


def run_command(cmd: List[str], cwd: Path = None, description: str = "") -> Tuple[bool, str]:
    """
    Executa comando e retorna (sucesso, output).
    
    Args:
        cmd: Comando a executar (lista)
        cwd: Diretório de trabalho
        description: Descrição do comando (para logs)
    
    Returns:
        Tuple[bool, str]: (sucesso, output)
    """
    try:
        result = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else str(REPO_ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        output = result.stdout + result.stderr
        return result.returncode == 0, output
    except Exception as e:
        return False, str(e)


def check_constitution_immutability(staged_files: List[str]) -> bool:
    """Valida imutabilidade da Constituição (step 1 do workflow)."""
    print_step(1, 8, "Validando imutabilidade da Constituição")
    
    if CONSTITUICAO_PATH.name in staged_files or str(CONSTITUICAO_PATH) in staged_files:
        print_error("Tentativa de modificação da Constituição detectada!")
        print_error("A Constituição da FÁBRICA é imutável e não pode ser alterada.")
        print_error("Nenhum agente, humano ou LLM pode modificar core/sop/constituição.yaml")
        return False
    
    print_success("Constituição intacta (imutável)")
    return True


def check_legacy_pipeline_scripts(staged_files: List[str]) -> bool:
    """Bloqueia scripts legados de pipeline (step 2 do workflow)."""
    print_step(2, 8, "Bloqueando scripts legados de pipeline")
    
    # Permitir arquivos de ordens legítimos
    allowed_patterns = [
        "ordem/ordens/",  # Arquivos de ordens (engineer.in.yaml, gatekeeper.in.yaml, etc.)
    ]
    
    # Bloquear apenas scripts legados
    blocked_patterns = [
        "deprecated/ordem/",  # Scripts legados em deprecated
    ]
    
    for file in staged_files:
        # Verificar se é permitido primeiro
        is_allowed = any(pattern in file for pattern in allowed_patterns)
        if is_allowed:
            continue
        
        # Verificar se é bloqueado
        for pattern in blocked_patterns:
            if pattern in file:
                print_error(f"Uso/modificação de scripts legados de pipeline é proibido: {file}")
                return False
    
    print_success("Nenhum script legado detectado")
    return True


def run_precommit() -> bool:
    """Executa pre-commit hooks (step 3 do workflow)."""
    print_step(3, 8, "Executando pre-commit hooks")
    
    # Verificar se pre-commit está instalado
    has_precommit, _ = run_command(["pre-commit", "--version"])
    if not has_precommit:
        print_warning("pre-commit não instalado, instalando...")
        success, output = run_command(["pip", "install", "pre-commit"])
        if not success:
            print_warning(f"Falha ao instalar pre-commit: {output}")
            # Continuar mesmo se não conseguir instalar
            return True
    
    # Executar pre-commit via Makefile
    success, output = run_command(
        ["make", "-C", str(MAKEFILE_DIR), "precommit"],
        cwd=REPO_ROOT
    )
    
    if success:
        print_success("Pre-commit hooks executados com sucesso")
    else:
        print_warning(f"Pre-commit retornou warnings (continuando...): {output[:200]}")
    
    return True  # Pre-commit não bloqueia se falhar (|| true no workflow)


def run_security_and_sbom() -> bool:
    """Gera security reports e SBOM (step 4 do workflow)."""
    print_step(4, 8, "Gerando security reports e SBOM")
    
    # Verificar dependências
    has_bandit, _ = run_command(["bandit", "--version"])
    has_coverage, _ = run_command(["coverage", "--version"])
    
    if not has_bandit or not has_coverage:
        print_warning("Instalando dependências de segurança...")
        run_command(["pip", "install", "bandit", "coverage"])
    
    # Executar security e SBOM via Makefile
    success_security, output_security = run_command(
        ["make", "-C", str(MAKEFILE_DIR), "security"],
        cwd=REPO_ROOT
    )
    
    if not success_security:
        print_warning(f"Alguns relatórios de segurança falharam (continuando...): {output_security[:200]}")
    
    success_sbom, output_sbom = run_command(
        ["make", "-C", str(MAKEFILE_DIR), "sbom"],
        cwd=REPO_ROOT
    )
    
    if not success_sbom:
        print_error(f"Falha ao gerar SBOM: {output_sbom[:200]}")
        return False
    
    # Verificar se SBOM foi gerado
    sbom_path = REL_DIR / "sbom.json"
    if not sbom_path.exists():
        print_error(f"SBOM não foi gerado em {sbom_path}")
        return False
    
    print_success(f"SBOM gerado: {sbom_path.relative_to(REPO_ROOT)}")
    return True


def run_sop_validation() -> bool:
    """Valida SOP (step 5 do workflow)."""
    print_step(5, 8, "Validando SOP")
    
    if not VALIDATOR_PATH.exists():
        print_error(f"core/scripts/validator.py não encontrado")
        return False
    
    success, output = run_command(
        ["python3", str(VALIDATOR_PATH)],
        cwd=REPO_ROOT
    )
    
    if not success:
        print_error("SOP validation falhou")
        print_error(output[:500])
        return False
    
    print_success("SOP validation passou")
    return True


def run_gatekeeper() -> bool:
    """Executa Gatekeeper (step 6 do workflow)."""
    print_step(6, 8, "Executando Gatekeeper")
    
    success, output = run_command(
        ["make", "-C", str(MAKEFILE_DIR), "gatekeeper_run"],
        cwd=REPO_ROOT
    )
    
    if not success:
        print_error("Gatekeeper falhou")
        print_error(output[:500])
        print_warning("Verifique logs em relatorios/parecer_gatekeeper.md")
        return False
    
    print_success("Gatekeeper passou")
    return True


def run_gatekeeper_prep() -> bool:
    """Executa Gatekeeper prep e valida pipeline (step 7 do workflow)."""
    print_step(7, 8, "Preparando Gatekeeper e validando pipeline")
    
    success_prep, output_prep = run_command(
        ["make", "-C", str(MAKEFILE_DIR), "gatekeeper_prep"],
        cwd=REPO_ROOT
    )
    
    if not success_prep:
        print_warning(f"Gatekeeper prep retornou warnings: {output_prep[:200]}")
    
    # Validar pipeline usando jq (se disponível)
    pipeline_input = REL_DIR / "pipeline_gate_input.json"
    if pipeline_input.exists():
        # Verificar se pipeline_ok é true usando Python (mais portável que jq)
        import json
        try:
            with open(pipeline_input, "r", encoding="utf-8") as f:
                data = json.load(f)
                pipeline_ok = data.get("pipeline_ok", False)
                if not pipeline_ok:
                    print_error("Pipeline inválido (pipeline_ok != true)")
                    return False
                print_success("Pipeline validado")
        except Exception as e:
            print_warning(f"Erro ao ler pipeline_gate_input.json: {e}")
            # Continuar se não conseguir ler
    
    return True


def get_staged_files() -> List[str]:
    """Obtém lista de arquivos staged no git."""
    success, output = run_command(["git", "diff", "--cached", "--name-only"])
    if success:
        return [f.strip() for f in output.split("\n") if f.strip()]
    return []


def main() -> int:
    """Função principal."""
    parser = argparse.ArgumentParser(
        description="Validador Pré-Commit FÁBRICA 2.0 - Imita workflows GitHub localmente"
    )
    parser.add_argument(
        "--skip-staged-check",
        action="store_true",
        help="Pular verificação de arquivos staged (útil para execução manual)"
    )
    args = parser.parse_args()
    
    print(f"\n{Colors.HEADER}{Colors.BOLD}🔒 Validador Pré-Commit FÁBRICA 2.0{Colors.ENDC}")
    print(f"{Colors.OKCYAN}Imitando workflows GitHub localmente...{Colors.ENDC}\n")
    
    # Obter arquivos staged (se não estiver em modo skip)
    staged_files = []
    if not args.skip_staged_check:
        staged_files = get_staged_files()
        if staged_files:
            print(f"{Colors.OKCYAN}Arquivos staged: {len(staged_files)}{Colors.ENDC}")
    
    # Executar validações na ordem dos workflows
    # Total de 7 passos principais
    TOTAL_STEPS = 7
    checks = [
        lambda: check_constitution_immutability(staged_files) if staged_files else True,
        lambda: check_legacy_pipeline_scripts(staged_files) if staged_files else True,
        run_precommit,
        run_security_and_sbom,
        run_sop_validation,
        run_gatekeeper,
        run_gatekeeper_prep,
    ]
    
    for i, check in enumerate(checks, 1):
        try:
            if not check():
                print_error(f"\n{Colors.FAIL}{Colors.BOLD}Validação falhou no passo {i}{Colors.ENDC}")
                print_error("Commit/Push bloqueado. Corrija os erros acima antes de tentar novamente.")
                return 1
        except Exception as e:
            print_error(f"Erro inesperado no passo {i}: {e}")
            return 1
    
    # Todos os checks passaram
    print_step(TOTAL_STEPS, TOTAL_STEPS, "Validação completa")
    print_success(f"\n{Colors.OKGREEN}{Colors.BOLD}✅ Todas as validações passaram!{Colors.ENDC}")
    print_success("Commit/Push autorizado.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

