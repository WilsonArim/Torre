#!/usr/bin/env python3
"""
Formatador de Interações — FÁBRICA 2.0
Formata interações conforme formato obrigatório.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# Importar função de formatação do file_access_guard
try:
    sys.path.insert(0, str(REPO_ROOT / "core" / "orquestrador"))
    from file_access_guard import formatar_resposta_agente
except ImportError:
    # Fallback se não conseguir importar
    def formatar_resposta_agente(agente, conteudo, pipeline_status="FORA_PIPELINE", proxima_acao="", comando_executar=""):
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


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: formatar_interacao.py <agente> <conteudo> [pipeline_status] [proxima_acao] [comando_executar]")
        print("Exemplo: formatar_interacao.py ENGENHEIRO 'Relatório completo' PIPELINE 'Aguardar validação' 'ESTADO-MAIOR ANALISAR'")
        sys.exit(1)
    
    agente = sys.argv[1]
    conteudo = sys.argv[2]
    pipeline_status = sys.argv[3] if len(sys.argv) > 3 else "FORA_PIPELINE"
    proxima_acao = sys.argv[4] if len(sys.argv) > 4 else ""
    comando_executar = sys.argv[5] if len(sys.argv) > 5 else ""
    
    formato = formatar_resposta_agente(
        agente,
        conteudo,
        pipeline_status,
        proxima_acao,
        comando_executar
    )
    
    print(formato)
