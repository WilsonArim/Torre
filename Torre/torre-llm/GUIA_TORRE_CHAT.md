# 🏰 Guia - Torre Chat (Tua LLM)

## 🎯 **O que é o Torre Chat:**

### **Interface para usar a TUA LLM da Torre:**
- **Como ChatGPT/Claude** - interface de chat
- **Seleção de modelos** - diferentes especializações
- **Histórico de conversas** - salva automaticamente
- **Configuração persistente** - lembra modelo escolhido

---

## 🚀 **Como usar:**

### **1. Iniciar o Chat:**
```bash
./start_chat.sh
```

### **2. Selecionar Modelo:**
```
🏰 MODELOS DA TORRE DISPONÍVEIS:
==================================================

torre-base:
  Nome: Torre Base
  Descrição: Modelo base da Torre para correção de erros
  Tipo: correction

torre-advice:
  Nome: Torre Advice
  Descrição: Modelo especializado em dar conselhos de código
  Tipo: advice

torre-review:
  Nome: Torre Review
  Descrição: Modelo para revisão e análise de código
  Tipo: review

torre-explain:
  Nome: Torre Explain
  Descrição: Modelo para explicar conceitos e código
  Tipo: explain
```

### **3. Fazer Perguntas:**
```
🤔 Tu: Como corrigir erro TS2304?
🏰 Torre Base: A variável undefinedVariable não está definida...
```

---

## 🎯 **Modelos Disponíveis:**

### **1. Torre Base** (`torre-base`)
- **Função**: Correção de erros
- **Uso**: "Como corrigir este erro?"
- **Exemplo**: "Corrige o erro TS2304 neste código"

### **2. Torre Advice** (`torre-advice`)
- **Função**: Conselhos de código
- **Uso**: "Dá-me conselhos sobre..."
- **Exemplo**: "Como melhorar este código?"

### **3. Torre Review** (`torre-review`)
- **Função**: Revisão de código
- **Uso**: "Revisa este código"
- **Exemplo**: "Analisa este arquivo e encontra problemas"

### **4. Torre Explain** (`torre-explain`)
- **Função**: Explicações
- **Uso**: "Explica este conceito"
- **Exemplo**: "O que é TypeScript?"

---

## 🛠️ **Comandos Disponíveis:**

### **Comandos Principais:**
- `models` - Mostrar modelos disponíveis
- `select` - Selecionar modelo
- `chat` - Iniciar chat com modelo
- `history` - Mostrar histórico
- `config` - Mostrar configuração
- `help` - Mostrar ajuda
- `quit` - Sair

### **Comandos do Chat:**
- `quit` - Sair do chat
- `clear` - Limpar histórico

---

## 💬 **Exemplos de Uso:**

### **Exemplo 1: Correção de Erro**
```
🎯 Modelo atual: Torre Base
Digite comando (help para ajuda): chat

💬 CHAT COM FORTALEZA BASE
==================================================
Modelo: Torre Base
Tipo: correction
Descrição: Modelo base da Torre para correção de erros

🤔 Tu: Como corrigir erro TS2304?
🤖 Torre Base: O erro TS2304 significa que uma variável não está definida...
```

### **Exemplo 2: Conselhos de Código**
```
🎯 Modelo atual: Torre Advice
Digite comando (help para ajuda): chat

💬 CHAT COM FORTALEZA ADVICE
==================================================
Modelo: Torre Advice
Tipo: advice
Descrição: Modelo especializado em dar conselhos de código

🤔 Tu: Como melhorar este código React?
🤖 Torre Advice: Aqui estão algumas sugestões para melhorar...
```

### **Exemplo 3: Revisão de Código**
```
🎯 Modelo atual: Torre Review
Digite comando (help para ajuda): chat

💬 CHAT COM FORTALEZA REVIEW
==================================================
Modelo: Torre Review
Tipo: review
Descrição: Modelo para revisão e análise de código

🤔 Tu: Revisa este arquivo TypeScript
🤖 Torre Review: Analisando o código, encontrei...
```

---

## 📊 **Funcionalidades:**

### **✅ Histórico Automático:**
- Salva todas as conversas
- Acesso via comando `history`
- Contexto para próximas perguntas

### **✅ Configuração Persistente:**
- Lembra modelo escolhido
- Salva em `.fortaleza/chat_config.json`
- Carrega automaticamente

### **✅ Múltiplos Modelos:**
- 4 modelos especializados
- Troca fácil entre modelos
- Cada modelo tem função específica

### **✅ Interface Intuitiva:**
- Comandos simples
- Ajuda integrada
- Feedback claro

---

## 🔧 **Configuração:**

### **Arquivo de Configuração:**
```json
{
  "current_model": "fortaleza-base",
  "last_used": "2025-08-26T14:00:00Z"
}
```

### **Localização:**
- `.fortaleza/chat_config.json`

---

## 🎯 **Vantagens vs ChatGPT/Claude:**

| **ChatGPT/Claude** | **Torre Chat** |
|-------------------|-------------------|
| Modelo genérico | Modelos especializados |
| Sem contexto | Histórico persistente |
| Sem configuração | Configuração salva |
| Interface web | Interface local |
| Dependência externa | Tua LLM local |

---

## 🚀 **Como começar:**

### **1. Primeira vez:**
```bash
./start_chat.sh
# Selecionar modelo
# Iniciar chat
```

### **2. Uso normal:**
```bash
./start_chat.sh
# Comando: chat
# Fazer perguntas
```

### **3. Trocar modelo:**
```bash
# Comando: select
# Escolher novo modelo
# Comando: chat
```

---

## 🎉 **Resultado:**

**Tu agora tens:**
- ✅ **Interface de chat** para tua LLM
- ✅ **Seleção de modelos** especializados
- ✅ **Histórico persistente** de conversas
- ✅ **Configuração salva** automaticamente
- ✅ **Como ChatGPT/Claude** mas com tua LLM

**É simples: `./start_chat.sh` e começar a conversar!** 🚀
