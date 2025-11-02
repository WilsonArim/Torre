# Auditoria Forense Estrutural — Estado-Maior da FÁBRICA 2.0

## Tabela de Limpeza

| Caminho/Ficheiro                    | Ação           | Motivo/Técnico                                               |
|-------------------------------------|----------------|--------------------------------------------------------------|
| ordem/codex_claude/                 | arquivar       | Sem uso operacional; histórico/tutoria                       |
| ordem/debug/                        | arquivar       | Não operacional; logs/eventos                                 |
| ordem/diario_de_bordo.md            | arquivar       | Histórico manual; não faz parte do núcleo                     |
| treino_torre/ (dir.)                | arquivar       | Conjunto de exemplos, datasets e treino                       |
| example.js                          | arquivar       | Ficheiro de teste, não referido por nenhum pipeline/CI        |
| core/scripts/__pycache__/           | remover        | Cache Python, não versionar                                   |
| docs/FACTORY_OPERATIONS.md          | fundido        | Integrado no README principal, para referência apenas moderna |

## Justificação Técnica
- **Risco**: Manter artefactos mortos eleva débito técnico e risco de uso inadvertido, violando ART-04, ART-09.
- **Impacto**: Elimina vetores de confusão; reforço de integridade, rastreabilidade e compliance.
- **Notas**: Markdowns e materiais históricos foram integrados se ainda possuíam valor didático.

## Registo das ações tomadas

- Arquivo de pastas legadas: tudo em `deprecated/`
- Eliminação de ficheiros/objetos: cache, duplicados e exemplos supérfluos
- Fusão de documentação: tudo operacional no README da pipeline
- Verificação final de referências: todos os diretórios não-núcleo estão limpos de menções a pipeline, superpipeline ou SOP (por grep recursivo)

**A FÁBRICA encontra-se limpa, ordenada e conforme à Constituição.**
