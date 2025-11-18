# A/B + Score (v1)

## Objetivo

Quando existem várias formas válidas de corrigir, escolhemos **1 patch vencedor** de modo **determinístico** e **idempotente**.

## Fonte de variações

- `autofix_base_shim` (inserção de shim no topo do .tsx)
- `ts_codemods` (no-unused/imports/path)

## Score v1 (offline)

- Critério: **menor nº de linhas no diff** (`diff_size`).
- Desempate: nome do gerador (ordem alfabética) para ser determinístico.

> Nota: Em modo online futuro, o score passa a combinar `apply_clean`, `lint_clean`, `tests_pass`, tempo e `diff_size`.

## Invariantes

- UM único diff final.
- Idempotente: mesmos candidatos ⇒ mesmo vencedor.
- Guardrails ativos (paths sensíveis proibidos).

## Como validar

```bash
python -m fortaleza-llm.run_offline
# stdout inclui: ab_candidates, ab_winner
```
