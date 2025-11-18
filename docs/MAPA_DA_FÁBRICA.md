# MAPA DA FÁBRICA — Estrutura após Auditoria Forense

## Núcleo Operacional (ESSENCIAL)

```
core/
  orquestrador/    # CLI, Makefile, config, validação Constituição
  scripts/         # Validadores oficiais SOP
  sop/             # Constituição (imutável), leis, exceções
pipeline/
  superpipeline.yaml           # Plano-mestre
  capitulos/                   # Estrutura por capítulos
  modulos/                     # Módulos e tarefas
  _templates/                  # Templates OFICIAIS (CHAPTER, STAGE, TASK)
  PIPELINE_TOC.md, README.md
relatorios/
  parecer_gatekeeper.md        # ART-04, ART-09
  pipeline_audit.json
  pipeline_gate_input.json
  relatorio_sop.md
  sop_status.json
  semgrep.sarif
  sbom.json
  npm-audit.json
  ...
docs/
  SOP_MANUAL.md, GATEKEEPER_MANUAL.md # Documentação-chave
  MAPA_DA_FÁBRICA.md                  # (Este documento)
tools/
  CODEOWNERS, pre-commit-config.yaml, commitlint.config.cjs
.github/
  workflows/ci.yml, release.yml
package.json, package-lock.json, requirements.txt
```

## Governança

- `core/sop/constituição.yaml` ⇒ **IMUTÁVEL**
- `core/sop/leis.yaml, exceptions.yaml` ⇒ Governo técnico/operacional
- `docs/` e `tools/` ⇒ Documentação e política de compliance
- `.github/workflows/` ⇒ Fluxos e proteções de CI

## Auxiliares e Opcionais

- `core/templates/project_skeleton/` # Skeleton para inicialização rápida
- `node_modules/` (auto-gerado, não versionar)
- `deprecated/` (só para histórico e arqueologia técnica)

## Gerados automaticamente

- `core/scripts/__pycache__/` # Limpo sempre no build
- `relatorios/` # Arquivos de saída/validação

**Legenda**:

- ESSENCIAL: obrigatório pelo fluxo e política
- IMUTÁVEL: só pode ser alterado sob regime de exceção
- Gerado: automatizado ou resultado de CI
- Opcional: utilidade, mas não parte do núcleo

**Estado final:**

> Todos os caminhos de pipeline, SOP e Governação apontam apenas para diretórios do núcleo. Nenhum ficheiro externo ao núcleo faz referência a pipelines, garantindo respeito total à Constituição.
