# 🚀 Torre LLM - Configuração no Cursor

Este guia permite configurar a **Torre LLM** (Qwen2.5-7B) diretamente no Cursor.

## 📦 **Arquivos Incluídos**

- `install_and_setup_torre.sh` - Instalação automática (macOS)
- `setup_ollama_torre.sh` - Configuração do Ollama
- `Modelfile` - Configuração do modelo Torre
- `cursor_custom_model_example.json` - Exemplo de configuração
- `PATCH_CURSOR_TORRE.md` - Documentação completa
- `CURSOR_CONFIG_QUICK.md` - Configuração rápida

## 🚀 **Instalação Automática (macOS)**

```bash
cd torre-llm
./install_and_setup_torre.sh
```

Este script irá:
1. ✅ Instalar o Ollama automaticamente
2. ✅ Baixar o modelo Qwen2.5-7B
3. ✅ Criar o alias "torre"
4. ✅ Testar a API
5. ✅ Fornecer instruções para o Cursor

## 🔧 **Configuração Manual**

### **Opção 1: Ollama (Recomendado)**

1. **Instale o Ollama:**
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```

2. **Configure a Torre:**
   ```bash
   cd torre-llm
   ./setup_ollama_torre.sh
   ```

3. **No Cursor:**
   - Settings → Models → API Keys
   - Override Base URL: `http://localhost:11434/v1`
   - API Key: `local`
   - Add model → Display Name: `Torre`, Model (ID): `torre`

### **Opção 2: LM Studio**

1. **Instale o LM Studio** em https://lmstudio.ai
2. **Start Server** (Developer → Local Server)
3. **No Cursor:**
   - Settings → Models → API Keys
   - Override Base URL: `http://localhost:1234/v1`
   - API Key: `local`
   - Add model → Display Name: `Torre`, Model (ID): `qwen2.5-7b-instruct`

## 🧪 **Teste**

Após a configuração, abra um chat no Cursor e digite:

```
[Modelo: Torre]
Diga "Olá! Sou a Torre (Qwen2.5-7B)".
```

## 📋 **Configuração Rápida**

Para configuração em 30 segundos, veja: `CURSOR_CONFIG_QUICK.md`

## 📖 **Documentação Completa**

Para instruções detalhadas, veja: `PATCH_CURSOR_TORRE.md`

## 🎯 **Resultado**

Após a configuração, você terá:
- ✅ Chat com a Torre LLM
- ✅ Correção de código
- ✅ Sugestões inteligentes
- ✅ Integração completa com o ecossistema Torre

**A Torre está pronta para ser sua assistente de programação!** 🚀
