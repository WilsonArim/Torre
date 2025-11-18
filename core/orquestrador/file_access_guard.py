#!/usr/bin/env python3
"""
Guardas técnicas de acesso a ficheiros conforme doutrina.
Implementa validação obrigatória antes de qualquer escrita de ficheiro.

Conforme: core/sop/doutrina.yaml
"""
import fnmatch
from pathlib import Path, PurePosixPath
from typing import Tuple

try:
    import yaml  # type: ignore
except Exception:
    yaml = None


REPO_ROOT = Path(__file__).resolve().parents[2]
DOUTRINA_PATH = REPO_ROOT / "core" / "sop" / "doutrina.yaml"
VIOLACOES_LOG = REPO_ROOT / "relatorios" / "violacoes_acesso_ficheiros.log"


def load_doutrina() -> dict:
    """Carrega a doutrina de acesso a ficheiros."""
    if not DOUTRINA_PATH.exists():
        return {}
    
    if yaml is None:
        # Fallback básico se PyYAML não estiver disponível
        return {
            "acesso_ficheiros": {
                "engenheiro": {
                    "ler": ["*"],
                    "escrever": ["*"],
                    "requisito": "APENAS com ordem do Estado-Maior"
                },
                "estado_maior": {
                    "ler": ["*"],
                    "escrever": [
                        "relatorios/**/*.md",
                        "relatorios/**/*.yaml",
                        "relatorios/**/*.json",
                        "ordem/ordens/*.in.yaml"
                    ],
                    "proibido": [
                        "**/*.py",
                        "**/*.js",
                        "**/*.ts",
                        "core/**",
                        "pipeline/**"
                    ]
                },
                "sop": {
                    "ler": ["*"],
                    "escrever": [
                        "relatorios/**/*.md",
                        "relatorios/para_estado_maior/**"
                    ],
                    "proibido": [
                        "**/*.py",
                        "**/*.js",
                        "**/*.ts",
                        "core/**",
                        "pipeline/**"
                    ]
                },
                "gatekeeper": {
                    "ler": ["*"],
                    "escrever": [
                        "relatorios/parecer_gatekeeper.md",
                        "relatorios/**/*.md",
                        "relatorios/para_estado_maior/**"
                    ],
                    "proibido": [
                        "**/*.py",
                        "**/*.js",
                        "**/*.ts",
                        "core/**",
                        "pipeline/**"
                    ]
                }
            }
        }
    
    try:
        with open(DOUTRINA_PATH, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def matches_pattern(path_str: str, pattern: str) -> bool:
    """Verifica se um caminho corresponde a um padrão glob."""
    # Normalizar separadores
    path_norm = path_str.replace("\\", "/")
    pattern_norm = pattern.replace("\\", "/")

    # Primeiro tentar corresponder via semântica POSIX (suporta **)
    try:
        if PurePosixPath(path_norm).match(pattern_norm):
            return True
    except Exception:
        pass

    # Fallback para fnmatch (mantém compatibilidade com padrões antigos)
    return fnmatch.fnmatch(path_norm, pattern_norm)


def validar_permissao_escrita(agente: str, caminho: Path, tem_ordem_valida: bool = False) -> Tuple[bool, str]:
    """
    Valida se agente tem permissão para escrever no caminho.
    
    Args:
        agente: Nome do agente (ENGENHEIRO, ESTADO-MAIOR, SOP, GATEKEEPER)
        caminho: Caminho do ficheiro a escrever
        tem_ordem_valida: Se True, indica que Engenheiro tem ordem válida (usado apenas para ENGENHEIRO)
    
    Returns:
        Tuple[bool, str]: (permite, mensagem)
    """
    doutrina = load_doutrina()
    acesso = doutrina.get("acesso_ficheiros", {})
    
    # Normalizar agente
    agente_upper = agente.upper()
    caminho_str = str(caminho.relative_to(REPO_ROOT) if caminho.is_absolute() else caminho)
    caminho_str = caminho_str.replace("\\", "/")
    
    # ENGENHEIRO: pode escrever qualquer ficheiro, mas precisa de ordem
    if agente_upper == "ENGENHEIRO":
        eng_config = acesso.get("engenheiro", {})
        requisito = eng_config.get("requisito", "")
        
        if not tem_ordem_valida:
            log_violacao(agente, caminho_str, f"Engenheiro precisa de ordem válida: {requisito}")
            return False, f"ENGENHEIRO não pode escrever {caminho_str} sem ordem válida do Estado-Maior"
        
        return True, "OK"
    
    # ESTADO-MAIOR: só pode escrever relatórios
    elif agente_upper == "ESTADO-MAIOR":
        em_config = acesso.get("estado_maior", {})
        escrever_patterns = em_config.get("escrever", [])
        proibido_patterns = em_config.get("proibido", [])
        
        # Verificar se está proibido
        for pattern in proibido_patterns:
            if matches_pattern(caminho_str, pattern):
                # Exceção: relatórios podem estar em core/ ou pipeline/ se forem .md/.yaml/.json
                if caminho.suffix in [".md", ".yaml", ".json"]:
                    if "relatorios/" in caminho_str:
                        continue  # Permitir relatórios mesmo em core/ ou pipeline/
                log_violacao(agente, caminho_str, f"Padrão proibido: {pattern}")
                return False, f"ESTADO-MAIOR não pode escrever {caminho_str} (proibido: {pattern})"
        
        # Verificar se está permitido
        for pattern in escrever_patterns:
            if matches_pattern(caminho_str, pattern):
                return True, "OK"
        
        log_violacao(agente, caminho_str, "Caminho não está na lista de permissões")
        return False, f"ESTADO-MAIOR não pode escrever {caminho_str} (apenas relatórios .md/.yaml/.json e ordens)"
    
    # SOP e GATEKEEPER: só podem escrever markdown e relatorios/para_estado_maior/
    elif agente_upper in ["SOP", "GATEKEEPER"]:
        agente_config = acesso.get(agente_upper.lower(), {})
        escrever_patterns = agente_config.get("escrever", [])
        proibido_patterns = agente_config.get("proibido", [])
        
        # Verificar se está proibido
        for pattern in proibido_patterns:
            if matches_pattern(caminho_str, pattern):
                # Exceção: relatorios/para_estado_maior/ pode conter qualquer tipo de ficheiro
                if "relatorios/para_estado_maior/" in caminho_str:
                    continue
                log_violacao(agente, caminho_str, f"Padrão proibido: {pattern}")
                return False, f"{agente_upper} não pode escrever {caminho_str} (proibido: {pattern})"
        
        # Verificar se está permitido
        for pattern in escrever_patterns:
            if matches_pattern(caminho_str, pattern):
                return True, "OK"
        
        log_violacao(agente, caminho_str, "Caminho não está na lista de permissões")
        return False, f"{agente_upper} não pode escrever {caminho_str} (apenas markdown e relatorios/para_estado_maior/)"
    
    # Agente desconhecido
    log_violacao(agente, caminho_str, "Agente desconhecido")
    return False, f"Agente desconhecido: {agente}"


def log_violacao(agente: str, caminho: str, motivo: str) -> None:
    """Regista violação no log de violações."""
    from datetime import datetime
    
    VIOLACOES_LOG.parent.mkdir(parents=True, exist_ok=True)
    
    linha = f"[{datetime.now().isoformat()}] VIOLAÇÃO: {agente} tentou escrever {caminho} - {motivo}\n"
    
    try:
        with open(VIOLACOES_LOG, "a", encoding="utf-8") as f:
            f.write(linha)
    except Exception:
        pass  # Falha silenciosa se não conseguir escrever log


def validar_formato_relatorio(conteudo: str) -> Tuple[bool, str]:
    """
    Valida se um relatório segue o formato obrigatório.
    
    Returns:
        Tuple[bool, str]: (valido, mensagem)
    """
    linhas = conteudo.split("\n")
    
    # Verificar início: PIPELINE/FORA_PIPELINE
    tem_inicio = False
    for linha in linhas[:10]:  # Verificar primeiras 10 linhas
        if "PIPELINE/FORA_PIPELINE" in linha.upper() or "**PIPELINE/FORA_PIPELINE**" in linha.upper():
            tem_inicio = True
            break
    
    # Verificar fim: COMANDO A EXECUTAR
    tem_fim = False
    for linha in reversed(linhas[-10:]):  # Verificar últimas 10 linhas
        if "COMANDO A EXECUTAR" in linha.upper() or "**COMANDO A EXECUTAR**" in linha.upper():
            tem_fim = True
            break
    
    if not tem_inicio:
        return False, "Relatório não contém identificação PIPELINE/FORA_PIPELINE no início"
    
    if not tem_fim:
        return False, "Relatório não contém COMANDO A EXECUTAR no fim"
    
    return True, "OK"


def formatar_resposta_agente(
    agente: str,
    conteudo: str,
    pipeline_status: str = "FORA_PIPELINE",
    proxima_acao: str = "",
    comando_executar: str = ""
) -> str:
    """
    Formata resposta de agente conforme formato obrigatório de interações.
    
    Args:
        agente: Nome do agente (ENGENHEIRO, SOP, GATEKEEPER, ESTADO-MAIOR)
        conteudo: Conteúdo da resposta
        pipeline_status: "PIPELINE" ou "FORA_PIPELINE"
        proxima_acao: Próxima ação a executar (opcional, será gerado se vazio)
        comando_executar: Comando a executar (opcional, será gerado se vazio)
    
    Returns:
        str: Resposta formatada conforme doutrina
    """
    # Determinar próxima ação se não fornecida
    if not proxima_acao:
        if agente == "ENGENHEIRO":
            proxima_acao = "Aguardando novas ordens do Estado-Maior"
        elif agente == "SOP":
            proxima_acao = "Verificação concluída"
        elif agente == "GATEKEEPER":
            proxima_acao = "Parecer emitido"
        else:
            proxima_acao = "Operação concluída"
    
    # Determinar comando se não fornecido
    if not comando_executar:
        if agente == "ENGENHEIRO":
            comando_executar = "ESTADO-MAIOR ANALISAR RELATÓRIO E EMITIR NOVA ORDEM SE NECESSÁRIO"
        elif agente == "SOP":
            comando_executar = "ESTADO-MAIOR ANALISAR RELATÓRIO DO SOP"
        elif agente == "GATEKEEPER":
            comando_executar = "ESTADO-MAIOR ANALISAR PARECER DO GATEKEEPER"
        else:
            comando_executar = "AGENTE ANÁLISE CONCLUÍDA"
    
    # Montar resposta formatada
    resposta_formatada = f"""**PIPELINE/FORA_PIPELINE:** {pipeline_status}

**OWNER: {agente} — Próxima ação:** {proxima_acao}

{conteudo}

---

**COMANDO A EXECUTAR:** "{comando_executar}"
"""
    
    return resposta_formatada

