# TORRE — Especificação de Integração

## 1) Identidade & arranque

- **Nome do modelo (exibição):** `torre`
- **Repositório/pasta local:** `../Torre` (caminho relativo ao projeto Fortaleza)
- **Forma de arranque preferida:** Ollama (serviço local)
- **Porta exposta pela Torre:** `11434` (API OpenAI-compatível do Ollama)
- **Healthcheck disponível?** `GET /api/tags` → 200 + lista de modelos

### Comandos de arranque (local)

```bash
# Instalar Ollama (macOS)
brew install ollama

# Iniciar serviço
brew services start ollama

# Configurar modelo Torre
ollama create torre -f Modelfile
ollama run torre  # primeira execução para download

# Verificar status
ollama list | grep torre
```

---

## 2) API — Contrato dos endpoints

### 2.1 Endpoint principal de geração

- **Método + Rota:** `POST /v1/chat/completions`
- **Autenticação:** Nenhuma (local)
- **Request JSON (esperado pela Torre):**

```json
{
  "model": "torre",
  "messages": [
    { "role": "system", "content": "..." },
    { "role": "user", "content": "..." }
  ],
  "stream": false,
  "temperature": 0.7,
  "max_tokens": 512,
  "top_p": 0.9,
  "top_k": 40,
  "presence_penalty": 0.0,
  "frequency_penalty": 0.0,
  "stop": ["\n", "Human:", "Assistant:"]
}
```

- **Response JSON (quando `stream=false`):**

```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1756275757,
  "model": "torre",
  "system_fingerprint": "fp_ollama",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "texto gerado"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 31,
    "completion_tokens": 48,
    "total_tokens": 79
  }
}
```

### 2.2 Streaming (suportado)

- **Tipo:** `text/event-stream`
- **Evento/dado por chunk:** `data: {"id":"...","choices":[{"delta":{"content":"..."}}]}`
- **Sinal de fim:** `data: [DONE]`

### 2.3 Outros endpoints úteis

- **`GET /v1/models`** → lista de modelos disponíveis
- **`GET /api/tags`** → detalhes dos modelos (Ollama nativo)
- **`POST /v1/embeddings`** → embeddings (se suportado)

---

## 3) Parametrização suportada

- `temperature` (0.0-2.0, default: 0.7)
- `top_p` (0.0-1.0, default: 0.9)
- `top_k` (1-100, default: 40)
- `max_tokens` (limite: 4096)
- `presence_penalty` (-2.0-2.0, default: 0.0)
- `frequency_penalty` (-2.0-2.0, default: 0.0)
- `stop` (strings): suportado
- `system` prompt: Sim
- `tools` / function calling: Não
- **Context window:** 32K tokens (Qwen2.5-7B)

---

## 4) Segurança & limites

- **Autenticação:** Nenhuma (serviço local)
- **CORS:** Não aplicável (local)
- **Rate limit:** Não aplicável (local)
- **Tamanho máximo do request:** 32K tokens
- **Dados sensíveis / PII:** Processamento local, sem envio externo

---

## 5) Qualidade/observabilidade

- **Logs:** Ollama logs via `brew services log ollama`
- **Métricas:** Não disponível
- **Tracing:** Não disponível
- **Erro típico:**

```json
{
  "error": {
    "message": "model not found: torre",
    "type": "invalid_request_error",
    "code": "model_not_found"
  }
}
```

---

## 6) Performance

- **RPS alvo** (1x instância): 2-5 RPS
- **Latência P50/P95** (prompt padrão): 2-5s / 5-10s
- **Context window** (tokens): 32K
- **Limite de concorrência recomendado:** 2-3 requests simultâneos

---

## 7) Mapeamento para OpenAI (adapter)

- **`messages[]`** → formato OpenAI padrão (role + content)
- **Resposta** → `choices[0].message.content`
- **Streaming** → `choices[0].delta.content` por chunk
- **Erros** → formato OpenAI padrão `{ error: { message, type, code } }`

---

## 8) Exemplo real (end-to-end)

### Request (cURL)

```bash
curl -sS -X POST "http://localhost:11434/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "torre",
    "messages": [{"role":"user","content":"Olá, Torre!"}],
    "stream": false,
    "temperature": 0.7
  }'
```

### Response (JSON)

```json
{
  "id": "chatcmpl-146",
  "object": "chat.completion",
  "created": 1756275757,
  "model": "torre",
  "system_fingerprint": "fp_ollama",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Olá! Parece que você enviou apenas \"Teste\". Como posso ajudar você com isso?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 31,
    "completion_tokens": 48,
    "total_tokens": 79
  }
}
```

---

## 9) Variáveis de ambiente recomendadas

- `TORRE_BASE=http://localhost:11434`
- `TORRE_MODEL=torre`
- `TORRE_TIMEOUT_MS=300000`
- `TORRE_ENABLE_STREAM=true`
- `TORRE_TEMPERATURE=0.7`
- `TORRE_MAX_TOKENS=2048`

---

## 10) Check rápido (pre-flight)

- [x] Consigo `curl http://localhost:11434/api/tags` com 200
- [x] `POST /v1/chat/completions` responde com JSON válido
- [x] Streaming emite chunks + fim
- [x] Campos obrigatórios documentados
- [x] Limites (tokens/bytes) claros

---

## 11) Configuração Cursor

Para usar a Torre no Cursor IDE:

1. **Settings → Models → API Keys**
   - **OpenAI-compatible → Override Base URL:** `http://localhost:11434/v1`
   - **API Key:** `local`

2. **Models → Add model**
   - **Display name:** `Torre`
   - **Model (ID):** `torre`

3. **Teste no chat:**
   - Selecione modelo "Torre"
   - Envie: "Explique em 1 frase o que é a Torre (Qwen2.5-7B)."

---

## 12) Troubleshooting

- **"model not found: torre"** → `ollama create torre -f Modelfile`
- **"connection refused"** → `brew services start ollama`
- **"lento/memória"** → use quantização Q4_K_M (já configurada)
- **"401/Key inválida"** → mantenha API Key = `local`
