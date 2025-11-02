# Auditoria Técnica de Documentação e Scripts — FÁBRICA 2.0

## 1. Resumo Executivo

- **Documentação (.md) analisada**: 25
- **Scripts SHELL (.sh) analisados**: 11
- **Elimináveis/Obsoletos**: .md (0, todos já em deprecated se obsoletos), .sh (6)

## 2. Tabela de Documentação

| Caminho | Categoria | Ação | Motivo/Resumo |
|---|---|---|---|
| relatorios/Auditoria Forense Estrutural.md | obrigatório | manter | Auditoria estrutural |
| relatorios/relatorio_sop.md | obrigatório | manter | Output do validador oficial |
| relatorios/parecer_gatekeeper.md | obrigatório | manter | Output do Gatekeeper |
| pipeline/README.md | obrigatório | manter | Manual operacional |
| docs/SOP_MANUAL.md | obrigatório | manter | Manual SOP |
| docs/GATEKEEPER_MANUAL.md | obrigatório | manter | Manual Gatekeeper |
| docs/MAPA_DA_FÁBRICA.md | obrigatório | manter | Mapa pós-auditoria |
| pipeline/PIPELINE_TOC.md | obrigatório | manter | Sumário pipeline |
| pipeline/_templates/*.md | obrigatório | manter | Templates pipeline |
| pipeline/modulos/**/*.md | obrigatório | manter | Capítulos/etapas/tarefas pipeline |
| relatorios/Auditoria_Docs_e_Scripts.md | obrigatório | manter | Este relatório |
| core/templates/project_skeleton/README.md | complementar | manter | Skeleton para projetos |
| deprecated/ordem/*.md | obsoleto | manter onde está | Histórico já arquivado |
| deprecated/treino_torre/*.md | obsoleto | manter onde está | Treino/dataset |

## 3. Tabela de Scripts

| Caminho | Estado | Ação | Motivo/Resumo |
|---|---|---|---|
| core/orquestrador/validate_constituicao.sh | ativo | manter | Usado no Makefile para proteger a Constituição |
| ordem/gatekeeper.sh | obsoleto | eliminar | Substituído por CLI Python, risco de bypass |
| ordem/setup_branch_protection.sh | redundante | avaliar | Só setup inicial, confirmar uso |
| ordem/verifica_luz_verde.sh | obsoleto | eliminar | Não é chamado nos fluxos oficiais |
| ordem/make_aula.sh | obsoleto | eliminar | Só uso dataset antigo |
| ordem/validate_sop.sh | obsoleto | eliminar | Substituído por pipeline CI |
| ordem/hooks/pre-commit.sh | obsoleto | eliminar | Pre-commit gerido via tools/ agora |
| deprecated/ordem/*.sh | obsoleto | manter onde está | Arquivados e bloqueados |

## 4. Conclusão

- **Recomendações**:  
  - Eliminar todos os `.sh` ativos em `ordem/` que não são referenciados no núcleo.
  - Garantir que documentação antiga fora do núcleo permaneça apenas em `deprecated/` para historial.
  - Atualizar README e docs principais sempre que a política mudar.
  - Consolidar instruções de governança apenas nos manuais oficiais.

- **Ficheiros a eliminar**:  
  - ordem/gatekeeper.sh  
  - ordem/verifica_luz_verde.sh  
  - ordem/make_aula.sh  
  - ordem/validate_sop.sh  
  - ordem/hooks/pre-commit.sh

- **Observações**:  
  - Não há redundância operacional relevante entre SHELL e Python/Make no núcleo.
  - Automação está agora centralizada via Python e CI, conforme exigência constitucional.

---

**Auditoria técnica concluída. Relatório criado em relatorios/Auditoria_Docs_e_Scripts.md.**
