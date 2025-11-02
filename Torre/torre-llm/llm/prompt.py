from __future__ import annotations
from pathlib import Path
from typing import Dict, Any
import time, json

PROTO_HEADER = """# ORDEM DE MISSÃO: PROTOCOLO DE OUTPUT (VANGUARDA)
1) Responder APENAS com:
   - <patch-info>{"generator":"LLM","ts":%d}</patch-info>
   - Um ÚNICO bloco ```diff``` (unificado, aplicável com git apply)
2) Não escrever nada fora desses blocos.
""" % int(time.time())

def load_system_prompt(repo_root: Path) -> str:
    p = repo_root / "fortaleza-llm" / "configs" / "engineer.system.md"
    if p.exists():
        return p.read_text(encoding="utf-8")
    # fallback mínimo (engineer-only)
    return (
        "# FORTALEZA — ENGINEER-ONLY\n"
        "Função: gerar **um único patch diff** unificado + metadados <patch-info>.\n"
        "Fora de escopo: qualquer tema não-técnico.\n"
        "Regras: 1 diff, compatível com `git apply`, sem tocar em segredos.\n"
    )

def build_user_prompt(logs: Dict[str, str] | None, files: Dict[str, str] | None) -> str:
    logs = logs or {}
    files = files or {}
    log_txt = "\\n".join((v or "")[:2000] for _, v in list(logs.items())[:6])
    file_list = "\\n".join(f"- {k}" for k in list(files.keys())[:20])
    return (
        PROTO_HEADER
        + "\n## CONTEXTO\n"
        + ("### LOGS (amostra)\n" + (log_txt or "(sem logs)")) + "\n\n"
        + ("### FICHEIROS (nomes)\n" + (file_list or "(sem files)")) + "\n\n"
        + "## TAREFA\n"
        + "Gera **um único** diff unificado que:\n"
        + "- é mínimo e reversível;\n"
        + "- corrige os erros sinalizados nos logs;\n"
        + "- mantém-se dentro de src/**/* quando possível;\n"
        + "- NÃO inclui nada fora do bloco ```diff``` e do <patch-info>.\n"
    )
