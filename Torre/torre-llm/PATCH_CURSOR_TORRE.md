# 🚀 Patch "Torre (Qwen2.5-7B)" – Configuração no Cursor

Este patch permite usar a **Torre LLM** diretamente no Cursor via LM Studio ou Ollama.

---

## 📋 Opção 1: **LM Studio** (Recomendado)

### 1. **Configure o LM Studio**
- Abra **LM Studio** → **Developer → Local Server → Start**
- Anote o endereço: normalmente `http://localhost:1234/v1`
- [Documentação LM Studio](https://lmstudio.ai/docs/api/openai-api)

### 2. **Configure o Cursor**
No **Cursor → Settings → Models → API Keys**:

* **Override Base URL (OpenAI-compatible):**
  ```
  http://localhost:1234/v1
  ```

* **API Key:**
  ```
  local
  ```

* Clique **Verify/Save**

### 3. **Adicione o Modelo**
Ainda em **Models**, clique **Add model** e preencha:

* **Display name:**
  ```
  Torre
  ```

* **Model (ID):**
  ```
  qwen2.5-7b-instruct
  ```

* Salve

---

## 📋 Opção 2: **Ollama** (Alternativo)

### 1. **Configure o Ollama**
- Garanta o Ollama aberto
- Ele expõe API OpenAI-compatível em `http://localhost:11434/v1`
- [GitHub Ollama](https://github.com/cursor/cursor/issues/1380)

### 2. **Configure o Cursor**
No **Cursor → Settings → Models → API Keys**:

* **Override Base URL:**
  ```
  http://localhost:11434/v1
  ```

* **API Key:**
  ```
  local
  ```

* **Save/Verify**

### 3. **Adicione o Modelo**
**Models → Add model**:

* **Display name:**
  ```
  Torre
  ```

* **Model (ID):**
  ```
  qwen2.5:7b-instruct
  ```

* Salve

---

## 🧪 **Teste no Chat do Cursor**

```
[Modelo: Torre]
Diga "Olá! Sou a Torre (Qwen2.5-7B)".
```

---

## 💡 **Dicas Importantes**

* O **nome tem que bater** com o ID que o servidor mostra (é sensível a maiúsculas/minúsculas e espaços)
* Recursos especiais do Cursor (ex.: *tab completion*) podem continuar usando modelos internos; isso é normal
* Se o LM Studio mostrar um ID ligeiramente diferente, copie exatamente o que aparecer lá

---

## 🔗 **Links Úteis**

- [Documentação Cursor - API Keys](https://docs.cursor.com/settings/api-keys)
- [Cursor Community Forum - Local LLMs](https://forum.cursor.com/t/using-local-llms-with-cursor-is-it-possible/15494)
- [LM Studio - OpenAI Compatibility API](https://lmstudio.ai/docs/api/openai-api)
- [Ollama GitHub Issue](https://github.com/cursor/cursor/issues/1380)

---

## 🎯 **Resultado**

Após a configuração, você terá acesso à **Torre LLM** diretamente no Cursor, permitindo:

- ✅ Chat com a Torre
- ✅ Correção de código
- ✅ Sugestões inteligentes
- ✅ Integração completa com o ecossistema Torre

**A Torre está pronta para ser sua assistente de programação!** 🚀
