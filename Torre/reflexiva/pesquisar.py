#!/usr/bin/env python3
"""
Torre Reflexiva — Módulo de Pesquisa Externa
Opera apenas como medidor estatístico. NÃO tem autonomia para criar.
Pode criar apenas ficheiros YAML e Markdown na sua pasta.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any

REPO_ROOT = Path(__file__).resolve().parents[2]
REFLEXIVA_DIR = REPO_ROOT / "Torre" / "reflexiva"
PESQUISAS_DIR = REFLEXIVA_DIR / "pesquisas"
SINTESES_DIR = REFLEXIVA_DIR / "sinteses"


def pesquisar_tema(tema: str, fontes_externas: List[str] = None) -> Dict[str, Any]:
    """
    Pesquisa tema externo (simulado — requer integração real futura).
    
    Args:
        tema: Tema a pesquisar
        fontes_externas: Lista de fontes externas (opcional)
    
    Returns:
        Dict com resultados da pesquisa
    """
    # NOTA: Esta é uma implementação base. Integração real requer:
    # - Web scraping controlado
    # - APIs de pesquisa
    # - Filtros de segurança
    
    resultado = {
        "tema": tema,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agente": "TORRE_REFLEXIVA",
        "tipo": "pesquisa_externa",
        "fontes": fontes_externas or [],
        "resultados": [],
        "metadados": {
            "objetivo": f"Pesquisar informações sobre: {tema}",
            "regras_aplicadas": [
                "ART-05: Não-Autonomia Absoluta",
                "ART-07: Transparência (metadados obrigatórios)",
                "Apenas YAML/MD na pasta Torre/reflexiva/",
            ],
        },
    }
    
    # Simulação de resultados (será substituído por pesquisa real)
    resultado["resultados"] = [
        {
            "fonte": "simulada",
            "resumo": f"Informações sobre {tema}",
            "relevancia": "media",
        }
    ]
    
    return resultado


def gerar_sintese(pesquisa_id: str, tema: str, resultados: List[Dict]) -> Dict[str, Any]:
    """
    Gera síntese da pesquisa (apenas estatísticas e análise).
    
    Args:
        pesquisa_id: ID da pesquisa
        tema: Tema pesquisado
        resultados: Resultados da pesquisa
    
    Returns:
        Dict com síntese
    """
    sintese = {
        "pesquisa_id": pesquisa_id,
        "tema": tema,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agente": "TORRE_REFLEXIVA",
        "tipo": "sintese",
        "estatisticas": {
            "total_resultados": len(resultados),
            "relevancia_alta": sum(1 for r in resultados if r.get("relevancia") == "alta"),
            "relevancia_media": sum(1 for r in resultados if r.get("relevancia") == "media"),
            "relevancia_baixa": sum(1 for r in resultados if r.get("relevancia") == "baixa"),
        },
        "analise": {
            "coerencia_interna": "verificar",
            "alinhamento_constitucional": "verificar",
        },
        "metadados": {
            "objetivo": f"Sintetizar pesquisa sobre: {tema}",
            "regras_aplicadas": [
                "ART-05: Não-Autonomia Absoluta",
                "ART-07: Transparência (metadados obrigatórios)",
                "Apenas medidor estatístico — não cria código",
            ],
        },
    }
    
    return sintese


def salvar_pesquisa(pesquisa: Dict[str, Any]) -> Path:
    """Salva pesquisa em YAML na pasta permitida."""
    pesquisa_id = f"pesquisa_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    pesquisa_file = PESQUISAS_DIR / f"{pesquisa_id}.yaml"
    
    # Converter para YAML (formato simples)
    yaml_content = "# Pesquisa Torre Reflexiva\n\n"
    yaml_content += f"tema: {pesquisa['tema']}\n"
    yaml_content += f"timestamp: {pesquisa['timestamp']}\n"
    yaml_content += f"agente: {pesquisa['agente']}\n"
    yaml_content += f"tipo: {pesquisa['tipo']}\n\n"
    yaml_content += "fontes:\n"
    
    for fonte in pesquisa.get('fontes', []):
        yaml_content += f"  - {fonte}\n"
    
    yaml_content += "\nresultados:\n"
    for resultado in pesquisa.get('resultados', []):
        yaml_content += f"  - fonte: {resultado.get('fonte', 'desconhecida')}\n"
        yaml_content += f"    resumo: {resultado.get('resumo', 'N/A')}\n"
        yaml_content += f"    relevancia: {resultado.get('relevancia', 'media')}\n"
    
    yaml_content += "\nmetadados:\n"
    yaml_content += f"  objetivo: \"{pesquisa['metadados']['objetivo']}\"\n"
    yaml_content += "  regras_aplicadas:\n"
    for regra in pesquisa['metadados']['regras_aplicadas']:
        yaml_content += f"    - {regra}\n"
    
    pesquisa_file.write_text(yaml_content, encoding="utf-8")
    
    return pesquisa_file


def salvar_sintese(sintese: Dict[str, Any]) -> Path:
    """Salva síntese em Markdown na pasta permitida."""
    sintese_id = f"sintese_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    sintese_file = SINTESES_DIR / f"{sintese_id}.md"
    
    md_content = "# Síntese Torre Reflexiva\n\n"
    md_content += f"**Tema:** {sintese['tema']}\n"
    md_content += f"**Pesquisa ID:** {sintese['pesquisa_id']}\n"
    md_content += f"**Timestamp:** {sintese['timestamp']}\n"
    md_content += f"**Agente:** {sintese['agente']}\n\n"
    md_content += "## Estatísticas\n\n"
    md_content += f"- Total de resultados: {sintese['estatisticas']['total_resultados']}\n"
    md_content += f"- Relevância alta: {sintese['estatisticas']['relevancia_alta']}\n"
    md_content += f"- Relevância média: {sintese['estatisticas']['relevancia_media']}\n"
    md_content += f"- Relevância baixa: {sintese['estatisticas']['relevancia_baixa']}\n\n"
    md_content += "## Análise\n\n"
    md_content += f"- Coerência interna: {sintese['analise']['coerencia_interna']}\n"
    md_content += f"- Alinhamento constitucional: {sintese['analise']['alinhamento_constitucional']}\n\n"
    md_content += "## Metadados\n\n"
    md_content += f"**Objetivo:** {sintese['metadados']['objetivo']}\n\n"
    md_content += "**Regras Aplicadas:**\n"
    for regra in sintese['metadados']['regras_aplicadas']:
        md_content += f"- {regra}\n"
    
    sintese_file.write_text(md_content, encoding="utf-8")
    
    return sintese_file


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: pesquisar.py <tema> [fonte1] [fonte2] ...")
        sys.exit(1)
    
    tema = sys.argv[1]
    fontes = sys.argv[2:] if len(sys.argv) > 2 else []
    
    # Pesquisar
    pesquisa = pesquisar_tema(tema, fontes)
    pesquisa_file = salvar_pesquisa(pesquisa)
    print(f"✅ Pesquisa salva em: {pesquisa_file.relative_to(REPO_ROOT)}")
    
    # Gerar síntese
    sintese = gerar_sintese(
        pesquisa_file.stem,
        tema,
        pesquisa.get('resultados', [])
    )
    sintese_file = salvar_sintese(sintese)
    print(f"✅ Síntese salva em: {sintese_file.relative_to(REPO_ROOT)}")
    
    import json
    print(json.dumps({
        "pesquisa": str(pesquisa_file.relative_to(REPO_ROOT)),
        "sintese": str(sintese_file.relative_to(REPO_ROOT)),
    }, indent=2))
