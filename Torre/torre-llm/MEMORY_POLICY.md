# MEMORY_POLICY — Fortaleza LLM (F14+)

## Escopo

- **Armazenar**: sinais agregados de episódios (erros, toolchain, caminhos **relativos**), decisões (patch/ADVISORY), métricas (verde/falha, latência).
- **Não armazenar**: PII, trechos de código completos, prompts, segredos, paths absolutos, URLs privadas.
- **Sanitização**: emails→`[redacted-email]`, chaves→`[redacted-secret]`, limite defensivo (2.000 chars/campo).
- **Retenção**: episódios em `.fortaleza/memory/episodes.jsonl` com rotação (5MB/arquivo; máx. 7 arquivos).
- **Promoção de regras**: somente após **N≥3 sucessos** e **0 regressões**; despromoção imediata ao 1º sinal de regressão.
- **Ótica de workspace**: memória é local a cada repo (pasta `.fortaleza/`), versionamento opcional, auditável.

## Direitos do usuário

- **Opt-out**: defina `FORT_MEM=0` para desativar gravação/aplicação.
- **Purge**: apagar `.fortaleza/memory/*` remove todo o histórico local.

## Auditoria

- Cada execução recebe `trace_id` (v4). Métricas são exportáveis em JSON/CSV via endpoints/CLIs existentes.
