# Fortaleza LLM — Treino/Afinação (70/20/10)

Objetivo: preparar **dados verificáveis** para a LLM engenheira, com foco em:
1) **Programação**, 2) **Resolução de problemas**, 3) **Auditoria forense**,
sempre referenciando as *lentes* dos mestres (Aristóteles, Dijkstra, Hoare, Knuth, Saltzer, etc.).

## Proporções
- **70% Código real**: episódios `logs → patch (diff unificado) → tests a verde`.
- **20% Anti-padrões + correções**: cheiros comuns + patch mínimo idempotente.
- **10% Cartas dos Mestres (RAG)**: princípios operacionais (não filosóficos).

## Estrutura
```
training/
├── schemas/
│   ├── episode.schema.json
│   ├── anti_pattern.schema.json
│   └── card.schema.yaml
├── datasets/
│   ├── code/
│   │   └── examples.jsonl
│   └── anti_patterns/
│       └── examples.jsonl
└── templates/
    ├── episode.jsonl
    └── anti_pattern.jsonl
```

## Campos (resumo)
### `episode` (70%)
- `domain`: `"programming" | "problem_solving" | "forensic_audit"`
- `logs`: `{ lint?, tests?, build?, runtime? }`
- `files_before`: `{ "path": "conteúdo" }` (amostra pequena)
- `patch_unified`: string (***UM*** diff unificado)
- `tests_added`: `{ "path": "conteúdo" }` ou lista
- `outcome`: `{ lint_clean: bool, tests_pass: bool, apply_clean: bool }`
- `lenses_applied`: ex.: `["ARISTÓTELES","DIJKSTRA","HOARE"]`
- `notes`: livre (curto)

### `anti_pattern` (20%)
- `name`, `smell`, `detectors` (regex/hints), `fix_strategy`, `minimal_patch_example`

### `card` (10% — RAG)
- `name`, `domain_tags`, `principles[]`, `rules[]`, `anti_patterns[]`, `examples[]`

## Regras de curadoria
- **Provas > Opiniões**: cada episódio contém *logs reais* e *diff* aplicável.
- **Patch único**: formato unificado, compatível com `git apply`.
- **Idempotência**: se aplicado duas vezes, não deve piorar (quando aplicável).
- **Sem segredos/PII**: *hard-deny* (seguindo Saltzer/Schneier).
- **Referenciar lentes**: `lenses_applied` com 2–5 lentes relevantes.

## Como usar (alto nível)
- *Afinação supervisionada*: usar `datasets/code/*.jsonl` como pares entrada→saída.
- *RAG*: carregar `llm/rag/CANON.md` e/ou `card.schema.yaml` → contexto no prompt.
- *Avaliação*: medir % de patches que passam lint/tests e score por lente aplicada.

> Este diretório contém **dados** e **esquemas**. Não altera o runtime.
