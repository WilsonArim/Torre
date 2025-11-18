# Fortaleza LLM — Núcleo (engine/backends)

## O que é

Camada mínima para gerar **UM** `diff` unificado a partir de logs/files, com:

- perfis de decodificação (PATCH / PATCH_B) → A/B,
- prompts engineer-only,
- extração `<patch-info>` + `diff` e **validação**,
- backend **OpenAI-compat** (vLLM/Together/OpenRouter/…).

## Execução local (servidor opcional)

````bash
export OPENAI_BASE="https://api.openai.com/v1"
export OPENAI_API_KEY="sk-..."
export OPENAI_MODEL="qwen2.5-coder-7b-instruct"  # ou outro
python -m fortaleza-llm.llm.server
# POST http://localhost:8001/run  { "logs":{...},"files":{...} }

## Smoke (offline, sem rede)
Permite validar a CLI e o fluxo `{logs,files} -> {diff,metrics}` **sem** chamadas externas.

```bash
# 1) Ativar o modo smoke
export LLM_SMOKE=1

# 2) Usar a CLI com o exemplo fornecido
python -m fortaleza-llm.llm.cli < fortaleza-llm/examples/smoke_cli.json | jq .

# Saída esperada (exemplo):
# {
#   "diff": "--- a/fortaleza-llm/llm/README.md\\n+++ b/fortaleza-llm/llm/README.md\\n@@ -1,5 +1,8 @@\\n ...",
#   "metrics": { "decode_backend": "openai_compat", "decode_winner": "B", ... },
#   "patch_info": { "generator": "openai_compat", "mode": "smoke", "ts": 1710000000 }
# }

# 3) Desativar quando for usar backend real
unset LLM_SMOKE
````

## Integração

- **Gateway/Worker** (fora deste patch) deve apenas chamar `POST /run`
  e encaminhar `{diff, metrics}` para o resto da pipeline.

## Emit patch (Protocolo Vanguarda)

Quando precisares **exatamente** de `<patch-info> + ```diff```` (sem JSON):

```bash
# offline (sem rede)
export LLM_SMOKE=1
python -m fortaleza-llm.llm.emit < fortaleza-llm/examples/smoke_cli.json

# backend real (Qwen/7B, etc.)
unset LLM_SMOKE
export LLM_BASE="https://api.openrouter.ai/v1"    # exemplo OpenAI-compatible
export LLM_API_KEY="sk-..."
export LLM_MODEL="qwen2.5-coder-7b-instruct"
python -m fortaleza-llm.llm.emit < fortaleza-llm/examples/smoke_cli.json
```

## Ambiente

- `LLM_BACKEND=openai_compat` (default)
- `OPENAI_BASE`, `OPENAI_API_KEY`, `OPENAI_MODEL`
- `REPO_ROOT=.` (para ler configs e prompts)

## Notas

- Se `engineer.system.md` não existir, um **fallback seguro** é usado.
- Se `models.decode.yaml` não existir, perfis PATCH/PATCH_B **defaults** são usados.
