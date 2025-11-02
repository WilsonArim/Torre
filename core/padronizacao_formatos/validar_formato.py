#!/usr/bin/env python3
"""
Validador de Formato Obrigatório — FÁBRICA 2.0
Valida que todas as interações seguem o formato obrigatório.
Conforme doutrina: formato_interacoes.
"""
import re
import sys
from pathlib import Path
from typing import Tuple, List, Dict

REPO_ROOT = Path(__file__).resolve().parents[2]
DOUTRINA_PATH = REPO_ROOT / "core" / "sop" / "doutrina.yaml"


def validar_formato_interacao(conteudo: str) -> Tuple[bool, List[str]]:
    """
    Valida se uma interação segue o formato obrigatório.
    
    Args:
        conteudo: Conteúdo da interação a validar
    
    Returns:
        Tuple[bool, List[str]]: (valido, erros)
    """
    erros = []
    linhas = conteudo.split("\n")
    
    # Verificar início: PIPELINE/FORA_PIPELINE
    tem_inicio = False
    for i, linha in enumerate(linhas[:10]):  # Verificar primeiras 10 linhas
        if re.search(r"\*\*PIPELINE/FORA_PIPELINE\*\*.*(PIPELINE|FORA_PIPELINE)", linha, re.IGNORECASE):
            tem_inicio = True
            break
    
    if not tem_inicio:
        erros.append("Interação não contém identificação PIPELINE/FORA_PIPELINE no início")
    
    # Verificar OWNER (opcional mas recomendado)
    tem_owner = False
    for linha in linhas[:15]:
        if re.search(r"\*\*OWNER.*—.*Próxima ação\*\*", linha, re.IGNORECASE):
            tem_owner = True
            break
    
    # Verificar fim: COMANDO A EXECUTAR
    tem_fim = False
    for linha in reversed(linhas[-10:]):  # Verificar últimas 10 linhas
        if re.search(r"\*\*COMANDO A EXECUTAR\*\*", linha, re.IGNORECASE):
            tem_fim = True
            break
    
    if not tem_fim:
        erros.append("Interação não contém COMANDO A EXECUTAR no fim")
    
    valido = len(erros) == 0
    
    return valido, erros


def validar_ficheiro_markdown(caminho: Path) -> Tuple[bool, List[str]]:
    """
    Valida formato de um ficheiro markdown.
    
    Args:
        caminho: Caminho do ficheiro a validar
    
    Returns:
        Tuple[bool, List[str]]: (valido, erros)
    """
    if not caminho.exists():
        return False, [f"Ficheiro não existe: {caminho}"]
    
    if caminho.suffix != ".md":
        return False, [f"Ficheiro não é markdown: {caminho}"]
    
    try:
        conteudo = caminho.read_text(encoding="utf-8")
        return validar_formato_interacao(conteudo)
    except Exception as e:
        return False, [f"Erro ao ler ficheiro: {e}"]


def validar_todos_relatorios() -> Dict[str, Tuple[bool, List[str]]]:
    """
    Valida formato de todos os relatórios em relatorios/.
    
    Returns:
        Dict com resultados de validação por ficheiro
    """
    resultados = {}
    relatorios_dir = REPO_ROOT / "relatorios"
    
    if not relatorios_dir.exists():
        return resultados
    
    # Encontrar todos os ficheiros markdown
    for md_file in relatorios_dir.rglob("*.md"):
        valido, erros = validar_ficheiro_markdown(md_file)
        resultados[str(md_file.relative_to(REPO_ROOT))] = (valido, erros)
    
    return resultados


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: validar_formato.py <caminho> | validar_formato.py --todos")
        sys.exit(1)
    
    if sys.argv[1] == "--todos":
        resultados = validar_todos_relatorios()
        validos = sum(1 for v, _ in resultados.values() if v)
        invalidos = len(resultados) - validos
        
        print(f"Validação completa:")
        print(f"  ✅ Válidos: {validos}")
        print(f"  ❌ Inválidos: {invalidos}")
        
        for caminho, (valido, erros) in resultados.items():
            if not valido:
                print(f"\n❌ {caminho}:")
                for erro in erros:
                    print(f"    - {erro}")
        
        if invalidos > 0:
            sys.exit(1)
    else:
        caminho = Path(sys.argv[1])
        if not caminho.is_absolute():
            caminho = REPO_ROOT / caminho
        
        valido, erros = validar_ficheiro_markdown(caminho)
        
        if valido:
            print(f"✅ {caminho} está conforme o formato obrigatório")
        else:
            print(f"❌ {caminho} não está conforme:")
            for erro in erros:
                print(f"  - {erro}")
            sys.exit(1)
