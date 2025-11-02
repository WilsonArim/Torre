# 🏰 Guia Final - Modelos da Torre

## ✅ **Status Atual:**
- **API da Torre**: ✅ Rodando em localhost:8000
- **Extensão instalada**: ✅ Em ~/.cursor/extensions/torre-models-extension/
- **Arquivos prontos**: ✅ package.json e extension.js

---

## 🚀 **Como usar os modelos da Torre:**

### **1. Abrir o Cursor**
- A extensão será carregada automaticamente

### **2. Verificar se está ativa:**
- **Status bar** (canto inferior direito): `🏰 Torre`
- **Notificação**: `"🏰 Torre Models Extension ativada!"`

### **3. Usar os modelos:**
- **Cmd+Shift+P** → `"Torre: Enable Torre Auto"`
- **Cmd+Shift+P** → `"Torre: Enable Torre Base"`
- **Cmd+Shift+P** → `"Torre: Enable Torre Advice"`
- **Cmd+Shift+P** → `"Torre: Enable Torre Review"`
- **Cmd+Shift+P** → `"Torre: Enable Torre Explain"`

### **4. Status bar interativa:**
- **Clique no ícone** 🏰 na status bar
- **Muda o modelo** ativo
- **Mostra notificações** de status

---

## 🎯 **Modelos Disponíveis:**

### **🏰 Torre Auto**
- **Função**: Seleção automática do melhor modelo
- **Uso**: Para tarefas gerais
- **Comando**: `Torre: Enable Torre Auto`

### **🏰 Torre Base**
- **Função**: Correção de erros de código
- **Uso**: Quando há erros TypeScript/JavaScript
- **Comando**: `Torre: Enable Torre Base`

### **🏰 Torre Advice**
- **Função**: Conselhos e melhorias de código
- **Uso**: Para otimizar e melhorar código
- **Comando**: `Torre: Enable Torre Advice`

### **🏰 Torre Review**
- **Função**: Revisão e análise de código
- **Uso**: Para analisar arquivos completos
- **Comando**: `Torre: Enable Torre Review`

### **🏰 Torre Explain**
- **Função**: Explicações de conceitos
- **Uso**: Para entender código ou conceitos
- **Comando**: `Torre: Enable Torre Explain`

---

## 🔧 **Se não aparecer:**

### **Opção 1: Reiniciar Cursor**
1. **Cmd+Q** para fechar Cursor
2. **Abrir Cursor** novamente
3. **Verificar status bar**

### **Opção 2: Verificar console**
1. **Cmd+Option+I** (ou Cmd+Shift+I)
2. **Procurar por**: `"🏰 Torre Extension: Ativando..."`
3. **Verificar se há erros**

### **Opção 3: Instalação manual**
1. **Cmd+Shift+X** (Extensões)
2. **Clicar em "..."** (mais opções)
3. **"Install from VSIX..."**
4. **Navegar para**: `/Users/wilsonarim/CURSOR/fortaleza 4.0/fortaleza-llm/torre-extension/`
5. **Selecionar**: `package.json`

---

## 🎉 **Resultado Esperado:**

**Quando funcionar, vais ver:**
- ✅ **Status bar**: `🏰 Torre` (ou modelo ativo)
- ✅ **Notificações**: Confirmação de ativação
- ✅ **Comandos**: Disponíveis no Command Palette
- ✅ **Funcionalidade**: Modelos da Torre integrados

**Os modelos da Torre estarão disponíveis como qualquer outro modelo no Cursor!** 🏰✨

---

## 📞 **Suporte:**

Se ainda não funcionar:
1. **Verificar se API está rodando**: `curl http://localhost:8000/health`
2. **Verificar arquivos**: `ls -la ~/.cursor/extensions/torre-models-extension/`
3. **Reiniciar Cursor** completamente
4. **Verificar console** para erros

**A extensão está instalada e pronta! Só precisas abrir o Cursor!** 🚀
