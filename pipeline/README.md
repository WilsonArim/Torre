**ÚNICO fluxo oficial:** `core/orquestrador/cli.py` + `Makefile`. Toda operação fora deste fluxo está proibida.

# FÁBRICA 2.0 — Manual Operacional Unificado

## Comandos principais

- `factory init <dest>`: cria novo projeto base
- `factory sync <proj_path>`: sincroniza leis, orquestrador, workflows
- `factory validate <proj_path>`: executa validações SOP oficiais
- `factory report <proj_path>`: agrega relatórios e sumários

## Pipeline — Fluxo e Estados

- TODO → EM_PROGRESSO → EM_REVISAO → AGUARDA_GATEKEEPER → DONE
- Transições exigem evidências registradas em relatorios/

## Áreas obrigatórias

- core/: orquestrador, SOP, leis, exceptions
- pipeline/: superpipeline, capítulos, módulos, templates
- relatorios/: outputs de CI e auditoria
- docs/: manuais oficiais
- tools/: configuração de compliance

Para detalhes sobre cada capítulo, estados da pipeline ou integração CLI/CI, consultar este README e docs/SOP_MANUAL.md.
