# Bake-off — Nossa LLM vs Claude (Sonnet) — Guia rápido

Este diretório contém o **harness de avaliação** para comparar, de forma reprodutível, a nossa **LLM-Engenheira** com um modelo de referência (ex.: **Claude 3.5 Sonnet**).

## O que mede

- **SLI1**: % de episódios com _diff_ **válido** (e, se disponível, **validação Fortaleza**).
- **Latência p95**.
- **Tamanho do patch** (linhas +/-).
- (Opcional) **Validação pelo backend Fortaleza** (`/reports/ingest?mode=validate`).

> Critérios de vitória recomendados: ver "Definição de melhor" no projeto (SLI1, diff_size, p95, custo).

## Como correr (mínimo)

```bash
# 1) (Opcional) Validar via Fortaleza API:
# export FORTALEZA_API_BASE="http://localhost:8765"
# export FORTALEZA_WS="default"

# 2) (Opcional) Claude via API oficial:
# export ANTHROPIC_API_KEY="sk-ant-..."
# export CLAUDE_MODEL="claude-3-5-sonnet-20240620"

# 3) Our LLM via CLI já funciona out-of-the-box
python3 fortaleza-llm/evals/run_bakeoff.py
```

Saída:

- `.fortaleza/evals/bakeoff-YYYYMMDD-HHMMSS.json` — métricas máquina.
- `.fortaleza/evals/bakeoff-YYYYMMDD-HHMMSS.md` — relatório humano (resumo).

## Dataset

Por omissão usa `evals/datasets/bakeoff.sample.jsonl` (12 episódios curtos).  
Para corrida "séria", aponte para um JSONL maior:

```bash
python3 fortaleza-llm/evals/run_bakeoff.py --dataset fortaleza-llm/training/datasets/code/examples.jsonl
```

## Providers

Config embutida por `ENV`:

- **Nossa LLM (CLI)**: `python3 -m fortaleza-llm.llm.cli` (já configurado).
- **Claude Sonnet (API)**: `ANTHROPIC_API_KEY` (+ `CLAUDE_MODEL`, opcional).
- **(Opcional) OpenAI-compat**: `OPENAI_API_KEY`, `OPENAI_BASE`, `OPENAI_MODEL`.

## Notas

- Sem dependências externas (só **stdlib**). HTTP feito com `urllib`.
- Se `FORTALEZA_API_BASE` estiver setado, valida os diffs no backend (melhor SLI1).
- O harness **não aplica** patches em disco; delega validação à Fortaleza quando possível.
