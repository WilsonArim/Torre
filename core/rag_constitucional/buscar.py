#!/usr/bin/env python3
"""
Sistema de busca RAG Constitucional
Busca informação normativa, histórico e decisões
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]

def buscar(consulta: str, tipo: str = "todos") -> list:
    """
    Busca informação constitucional.
    
    Args:
        consulta: Termo ou frase a buscar
        tipo: Tipo de documento (constituicao, leis, doutrina, todos)
    
    Returns:
        Lista de documentos relevantes com citações
    """
    resultados = []
    
    documentos = {
        "constituicao": REPO_ROOT / "core/sop/constituição.yaml",
        "leis": REPO_ROOT / "core/sop/leis.yaml",
        "doutrina": REPO_ROOT / "core/sop/doutrina.yaml",
    }
    
    consulta_lower = consulta.lower()
    
    for doc_tipo, doc_path in documentos.items():
        if tipo != "todos" and tipo != doc_tipo:
            continue
        
        if not doc_path.exists():
            continue
        
        try:
            content = doc_path.read_text(encoding="utf-8")
            lines = content.splitlines()
            
            for i, line in enumerate(lines):
                if consulta_lower in line.lower():
                    contexto_inicio = max(0, i - 2)
                    contexto_fim = min(len(lines), i + 3)
                    contexto = "\n".join(lines[contexto_inicio:contexto_fim])
                    
                    resultados.append({
                        "tipo": doc_tipo,
                        "caminho": str(doc_path.relative_to(REPO_ROOT)),
                        "linha": i + 1,
                        "contexto": contexto,
                    })
        except Exception as e:
            print(f"Erro ao processar {doc_path}: {e}", file=sys.stderr)
    
    return resultados

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: buscar.py <consulta> [tipo]")
        sys.exit(1)
    
    consulta = sys.argv[1]
    tipo = sys.argv[2] if len(sys.argv) > 2 else "todos"
    
    resultados = buscar(consulta, tipo)
    
    import json
    print(json.dumps(resultados, indent=2, ensure_ascii=False))
