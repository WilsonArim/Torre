# CURSOR_CONFIG_QUICK.md — Torre (Qwen2.5-7B)

## A) Se estiver com **Ollama**

- Base URL: `http://localhost:11434/v1`
- API Key: `local`
- Model (ID): `torre`
- Display name: `Torre`

**Teste rápido (Terminal):**

```bash
curl http://localhost:11434/v1/chat/completions       -H "Content-Type: application/json"       -d '{"model":"torre","messages":[{"role":"user","content":"Diga oi."}]}'
```

## B) Se estiver com **LM Studio**

- Start Server (Developer → Local Server)
- Base URL: `http://localhost:1234/v1`
- API Key: `local` (ou a que o app fornecer)
- Model (ID): `qwen2.5-7b-instruct` (ou o ID exato exibido no LM Studio)
- Display name: `Torre`

**Teste rápido (Terminal):**

```bash
curl http://localhost:1234/v1/chat/completions       -H "Content-Type: application/json"       -d '{"model":"qwen2.5-7b-instruct","messages":[{"role":"user","content":"Diga oi."}]}'
```

## Passos no Cursor

1. Settings → Models → **API Keys**
2. Ative **OpenAI-compatible** e **Override Base URL** (cole a Base URL acima)
3. API Key: `local`
4. **Add model** → Display Name: `Torre`, Model (ID): `torre` (Ollama) **ou** `qwen2.5-7b-instruct` (LM Studio)
5. Abra um chat e escolha **Torre**
