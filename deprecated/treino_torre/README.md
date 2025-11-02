# Treino da Torre (Qwen) — Aulas

Cada ORDEM concluída (DONE) vira **uma aula** para a Torre. As aulas explicam:

- Contexto, problema, causa, solução e provas (testes + gatekeeper).
- Permitem a Torre **diagnosticar e propor correções** no futuro (RAG) e, depois, servir de dataset de treino.

## Como criar uma aula

1. Após o Gatekeeper dar 7/7 PASSOU e o Estado-Maior marcar DONE:

./ordem/make_aula.sh 2025-09-30-001 "M01" "E01" "T001" "micro-gama-jwt" "jwt,rbac,fastapi"

2. O script gera `/treino_torre/2025-09-30-001-micro-gama-jwt.md` a partir do template.
3. O Engenheiro (Claude) preenche as secções com PATCH, TESTES, RCA e PLAYBOOK.
4. Atualiza o `/treino_torre/TOC.md` com o link da nova aula.

## Regras

- Nome do ficheiro: `YYYY-MM-DD-XXX-slug.md`.
- Frontmatter deve conter: `id, capitulo, etapa, tarefa, tags, estado_final`.
- O Diário de Bordo deve incluir o link para a aula quando marcar DONE.
