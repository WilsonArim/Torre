# PATCH_CURSOR_TORRE.md — Integrar "Torre" no Cursor

Este patch prepara a LLM **Torre** (alias para **Qwen2.5-7B Instruct**) para uso no Cursor.
Você pode seguir **Ollama** (recomendado) ou **LM Studio**.

---
## 1) OLLAMA — com alias `torre`

1. Instale o Ollama (Windows/Mac/Linux).
2. Abra o Terminal na pasta deste patch e rode:
   ```bash
   ./setup_ollama_torre.sh
   ```
   (No Windows PowerShell, rode: `./setup_ollama_torre.ps1`)
3. No Cursor:
   - Settings → Models → API Keys → **OpenAI-compatible**
   - **Override Base URL**: `http://localhost:11434/v1`
   - **API Key**: `local`
   - **Add model** → Display Name: `Torre`, Model (ID): `torre`
4. Abra um chat e selecione **Torre**.

### Modelfile incluído
O arquivo `Modelfile` define a Torre como um alias do `qwen2.5:7b-instruct` com parâmetros padrão.

---
## 2) LM STUDIO — sem alias (usa o ID real)

1. Baixe **Qwen2.5 7B Instruct** e vá em Developer → **Local Server → Start**.
2. No Cursor:
   - **Override Base URL**: `http://localhost:1234/v1`
   - **API Key**: `local` (ou a do app)
   - **Add model** → Display Name: `Torre`, Model (ID): `qwen2.5-7b-instruct` (ou o ID exibido)
3. Teste com o prompt de validação abaixo.

---
## Teste de validação (cURL)

**Ollama**
```bash
curl http://localhost:11434/v1/chat/completions       -H "Content-Type: application/json"       -d '{"model":"torre","messages":[{"role":"user","content":"Explique em 1 frase quem é você."}]}'
```

**LM Studio**
```bash
curl http://localhost:1234/v1/chat/completions       -H "Content-Type: application/json"       -d '{"model":"qwen2.5-7b-instruct","messages":[{"role":"user","content":"Explique em 1 frase quem é você."}]}'
```

---
## Observações
- O modelo pode ser pesado em FP16; se precisar, use uma quantização (`q4_K_M` no Ollama).
- Alguns recursos do Cursor (ex.: tab completion) podem continuar usando modelos internos.
- Deixe este diretório `torre-llm/` guardado para reinstalação rápida.
