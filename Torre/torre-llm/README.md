# LLM-Engenheira — PoC

Loop: coletar erros → gerar **um** patch mínimo → `validate` → `dry_run` → `apply` → métricas.

## Requisitos
- Python 3.10+

## Executar
```bash
python -m torre-llm.orchestrator
```

Variáveis (opcional):
- `TORRE_API_BASE` (default: `http://localhost:8000`)
- `TORRE_WS` (default: `default`)
- `REPO_ROOT` (default: `.`)

## Estrutura
- `orchestrator.py` — ciclo principal
- `adapters/` — `run_lint`, `run_tests`, `run_build`
- `strategies/` — `playbook_simple.py` (patch mínimo)
- `utils/diff_utils.py` — helpers para diff unificado
- `client.py` — chamadas ao endpoint de ingest/estado

## Índice de Código (RAG-of-Code mínimo)
O orquestrador cria um índice leve de símbolos/exportações para orientar patches.

- JSON: `.torre/code_index.json`
- Resumo no patch: `torre-llm/INDEX_OVERVIEW.md`

Para gerar:
```bash
python -m torre-llm.run_offline
```
O índice é criado/atualizado automaticamente e um resumo é incluído no patch.

> Nota: A indexação ignora `node_modules/`, `.git/`, `dist/`, `build/`, `venv/`.
> Extensões: `.ts`, `.tsx`, `.js`, `.jsx`.

## Modo Offline (sem API)
Se não tiveres o servidor a correr, usa o runner offline. Ele **simula** `validate/dry_run/apply`, grava o diff em disco e imprime métricas JSON.

```bash
python -m torre-llm.run_offline
```

Saída (por defeito):
- Patches: `.torre/outbox/patch-<mode>-<YYYYMMDD-HHMMSS>.diff`
- Métricas: JSON no stdout

> Nota: O runner offline **não** aplica o patch no repo; guarda-o para revisão/aplicação manual.
