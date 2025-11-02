#!/usr/bin/env python3
"""
Replicação Instantânea — FÁBRICA 2.0
Script para copiar pipelines/projetos, herdando Tríade e Leis.
Conforme ART-02 (Tríade de Fundamentação) e ART-06 (Coerência entre Projetos).
"""
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]


def validar_triade_fundamentacao() -> Tuple[bool, List[str]]:
    """
    Valida se a Tríade de Fundamentação existe na FÁBRICA.
    
    Returns:
        Tuple[bool, List[str]]: (valido, faltantes)
    """
    faltantes = []
    
    # White Paper
    white_paper_paths = [
        REPO_ROOT / "docs" / "white_paper.md",
        REPO_ROOT / "docs" / "WHITE_PAPER.md",
        REPO_ROOT / "WHITE_PAPER.md",
    ]
    tem_white_paper = any(p.exists() for p in white_paper_paths)
    if not tem_white_paper:
        faltantes.append("White Paper")
    
    # Arquitetura
    arquitetura_paths = [
        REPO_ROOT / "docs" / "arquitetura.md",
        REPO_ROOT / "docs" / "ARQUITETURA.md",
        REPO_ROOT / "ARQUITETURA.md",
        REPO_ROOT / "docs" / "architecture.md",
    ]
    tem_arquitetura = any(p.exists() for p in arquitetura_paths)
    if not tem_arquitetura:
        faltantes.append("Arquitetura")
    
    # Base Operacional
    base_operacional_paths = [
        REPO_ROOT / "docs" / "base_operacional.md",
        REPO_ROOT / "docs" / "BASE_OPERACIONAL.md",
        REPO_ROOT / "BASE_OPERACIONAL.md",
        REPO_ROOT / "pipeline" / "README.md",
    ]
    tem_base_operacional = any(p.exists() for p in base_operacional_paths)
    if not tem_base_operacional:
        faltantes.append("Base Operacional")
    
    return len(faltantes) == 0, faltantes


def copiar_estrutura_core(destino: Path) -> List[str]:
    """
    Copia estrutura core (Constituição, Leis, SOPs) para projeto replicado.
    
    Args:
        destino: Diretório de destino do projeto replicado
    
    Returns:
        Lista de ficheiros copiados
    """
    copiados = []
    
    # Criar estrutura core no destino
    core_dest = destino / "core"
    core_dest.mkdir(parents=True, exist_ok=True)
    
    # Copiar Constituição e Leis
    estruturas_obrigatorias = [
        ("core/sop/constituição.yaml", "core/sop/constituição.yaml"),
        ("core/sop/leis.yaml", "core/sop/leis.yaml"),
        ("core/sop/exceptions.yaml", "core/sop/exceptions.yaml"),
        ("core/sop/doutrina.yaml", "core/sop/doutrina.yaml"),
    ]
    
    for origem_rel, destino_rel in estruturas_obrigatorias:
        origem_abs = REPO_ROOT / origem_rel
        destino_abs = destino / destino_rel
        
        if origem_abs.exists():
            destino_abs.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(origem_abs, destino_abs)
            copiados.append(destino_rel)
    
    return copiados


def copiar_triade(destino: Path) -> List[str]:
    """
    Copia Tríade de Fundamentação para projeto replicado.
    
    Args:
        destino: Diretório de destino do projeto replicado
    
    Returns:
        Lista de ficheiros copiados
    """
    copiados = []
    
    docs_dest = destino / "docs"
    docs_dest.mkdir(parents=True, exist_ok=True)
    
    # White Paper
    white_paper_paths = [
        REPO_ROOT / "docs" / "white_paper.md",
        REPO_ROOT / "docs" / "WHITE_PAPER.md",
        REPO_ROOT / "WHITE_PAPER.md",
    ]
    for wp_path in white_paper_paths:
        if wp_path.exists():
            dest_wp = docs_dest / "WHITE_PAPER.md"
            shutil.copy2(wp_path, dest_wp)
            copiados.append("docs/WHITE_PAPER.md")
            break
    
    # Arquitetura
    arquitetura_paths = [
        REPO_ROOT / "docs" / "arquitetura.md",
        REPO_ROOT / "docs" / "ARQUITETURA.md",
        REPO_ROOT / "ARQUITETURA.md",
        REPO_ROOT / "docs" / "architecture.md",
    ]
    for arq_path in arquitetura_paths:
        if arq_path.exists():
            dest_arq = docs_dest / "ARQUITETURA.md"
            shutil.copy2(arq_path, dest_arq)
            copiados.append("docs/ARQUITETURA.md")
            break
    
    # Base Operacional
    base_operacional_paths = [
        REPO_ROOT / "docs" / "base_operacional.md",
        REPO_ROOT / "docs" / "BASE_OPERACIONAL.md",
        REPO_ROOT / "BASE_OPERACIONAL.md",
        REPO_ROOT / "pipeline" / "README.md",
    ]
    for bo_path in base_operacional_paths:
        if bo_path.exists():
            dest_bo = docs_dest / "BASE_OPERACIONAL.md"
            shutil.copy2(bo_path, dest_bo)
            copiados.append("docs/BASE_OPERACIONAL.md")
            break
    
    return copiados


def gerar_metadados_replicacao(
    projeto_nome: str,
    origem: Path,
    destino: Path,
    triade_copiada: List[str],
    leis_copiadas: List[str]
) -> Dict[str, Any]:
    """
    Gera metadados de replicação conforme ART-07.
    
    Args:
        projeto_nome: Nome do projeto replicado
        origem: Caminho do projeto origem
        destino: Caminho do projeto destino
        triade_copiada: Lista de ficheiros da Tríade copiados
        leis_copiadas: Lista de ficheiros de leis copiados
    
    Returns:
        Dict com metadados de replicação
    """
    return {
        "projeto_nome": projeto_nome,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agente": "ENGENHEIRO",
        "tipo": "replicacao_instantanea",
        "origem": str(origem.relative_to(REPO_ROOT)),
        "destino": str(destino.relative_to(REPO_ROOT)),
        "triade_copiada": triade_copiada,
        "leis_copiadas": leis_copiadas,
        "metadados": {
            "objetivo": f"Replicar projeto {projeto_nome} herdando Tríade e Leis da FÁBRICA",
            "regras_aplicadas": [
                "ART-02: Tríade de Fundamentação",
                "ART-06: Coerência entre Projetos",
                "ART-07: Transparência (metadados obrigatórios)",
            ],
        },
    }


def replicar_projeto(projeto_nome: str, destino_path: str) -> Dict[str, Any]:
    """
    Replica projeto da FÁBRICA para novo destino.
    
    Args:
        projeto_nome: Nome do projeto replicado
        destino_path: Caminho de destino (relativo ou absoluto)
    
    Returns:
        Dict com resultado da replicação
    """
    # Validar Tríade antes de replicar
    triade_ok, faltantes = validar_triade_fundamentacao()
    if not triade_ok:
        return {
            "status": "BLOQUEADO",
            "motivo": f"Tríade incompleta: {', '.join(faltantes)}",
            "artefactos": [],
        }
    
    # Resolver caminho de destino
    if Path(destino_path).is_absolute():
        destino = Path(destino_path)
    else:
        destino = REPO_ROOT.parent / destino_path
    
    # Criar diretório de destino
    destino.mkdir(parents=True, exist_ok=True)
    
    # Copiar Tríade
    print(f"📚 Copiando Tríade de Fundamentação...")
    triade_copiada = copiar_triade(destino)
    print(f"  ✅ {len(triade_copiada)} ficheiros da Tríade copiados")
    
    # Copiar estrutura core (Constituição e Leis)
    print(f"⚖️  Copiando Constituição e Leis...")
    leis_copiadas = copiar_estrutura_core(destino)
    print(f"  ✅ {len(leis_copiadas)} ficheiros de leis copiados")
    
    # Gerar metadados de replicação
    metadados = gerar_metadados_replicacao(
        projeto_nome,
        REPO_ROOT,
        destino,
        triade_copiada,
        leis_copiadas
    )
    
    # Salvar metadados no projeto replicado
    metadados_file = destino / "replicacao_metadados.json"
    with open(metadados_file, "w", encoding="utf-8") as f:
        json.dump(metadados, f, indent=2, ensure_ascii=False)
    
    return {
        "status": "SUCCESS",
        "projeto_nome": projeto_nome,
        "destino": str(destino.relative_to(REPO_ROOT)),
        "triade_copiada": triade_copiada,
        "leis_copiadas": leis_copiadas,
        "metadados": str(metadados_file.relative_to(REPO_ROOT)),
    }


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: replicar.py <nome_projeto> <destino>")
        print("Exemplo: replicar.py meu_projeto ../meu_projeto")
        sys.exit(1)
    
    projeto_nome = sys.argv[1]
    destino_path = sys.argv[2]
    
    resultado = replicar_projeto(projeto_nome, destino_path)
    
    if resultado["status"] == "SUCCESS":
        print(f"\n✅ Projeto '{projeto_nome}' replicado com sucesso!")
        print(f"Destino: {resultado['destino']}")
        print(f"Tríade: {len(resultado['triade_copiada'])} ficheiros")
        print(f"Leis: {len(resultado['leis_copiadas'])} ficheiros")
        print(f"Metadados: {resultado['metadados']}")
        import json
        print(json.dumps(resultado, indent=2, ensure_ascii=False))
    else:
        print(f"\n❌ Replicação bloqueada: {resultado.get('motivo', 'Erro desconhecido')}")
        sys.exit(1)
