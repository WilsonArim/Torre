# 🔍 Como Verificar se Estás a Usar a Fortaleza

## 🎯 **Sinais de que a Fortaleza está ativa:**

### **1. ✅ API da Fortaleza rodando:**

```bash
curl http://localhost:8000/health
```

**Resultado esperado:**

```json
{
  "status": "healthy",
  "timestamp": "2025-08-26T14:00:00Z",
  "version": "1.0.0"
}
```

### **2. ✅ Extensão carregada no Cursor:**

- Abrir **Console do Cursor** (Cmd+Option+I)
- Procurar por: `"Fortaleza Cursor Extension carregada!"`

### **3. ✅ Correções automáticas:**

- Escrever código com erro
- Ver correção aplicada automaticamente
- Ver notificação: `"Correção aplicada com sucesso!"`

---

## 🚨 **Se NÃO estás a usar a Fortaleza:**

### **Problema 1: API não está rodando**

```bash
# Solução: Iniciar API
./start_api.sh
```

### **Problema 2: Extensão não carregada**

```bash
# Solução: Instalar extensão
./install_extension.sh
```

### **Problema 3: Erros não são corrigidos**

- Verificar se API está rodando
- Verificar se extensão está carregada
- Testar com: `./test_integration.sh`

---

## 🧪 **Teste Rápido:**

### **1. Criar arquivo com erro:**

```typescript
// test.ts
const name = undefinedVariable; // ❌ Erro TS2304
```

### **2. Verificar se Fortaleza corrige:**

- Se corrigir automaticamente: ✅ **Fortaleza ativa**
- Se não corrigir: ❌ **Fortaleza inativa**

---

## 📊 **Métricas de Uso:**

### **Ver métricas em tempo real:**

```bash
curl http://localhost:8000/metrics
```

### **Ver episódios salvos:**

```bash
cat .fortaleza/memory/episodes.jsonl
```

### **Ver logs da API:**

```bash
tail -f logs/api.log
```

---

## 🎯 **Indicadores Visuais:**

### **No Cursor:**

- **Status bar**: "Fortaleza: Ready"
- **Comando**: Cmd+Shift+F disponível
- **Notificações**: "Correção aplicada com sucesso!"

### **No Terminal:**

- **API rodando**: `python3 api_server.py`
- **Logs**: Mensagens de correção
- **Métricas**: Contadores aumentando

---

## 🔧 **Comandos de Verificação:**

### **Verificar tudo de uma vez:**

```bash
# 1. Verificar API
curl -s http://localhost:8000/health | grep -q "healthy" && echo "✅ API OK" || echo "❌ API não está rodando"

# 2. Verificar extensão
echo "Verificar no Console do Cursor: 'Fortaleza Cursor Extension carregada!'"

# 3. Testar correção
./test_integration.sh
```

---

## 🚀 **Como Ativar se Não Estiver Funcionando:**

### **Passo 1: Iniciar API**

```bash
./start_api.sh
```

### **Passo 2: Instalar Extensão**

```bash
./install_extension.sh
```

### **Passo 3: Reiniciar Cursor**

- Fechar Cursor
- Abrir Cursor novamente

### **Passo 4: Verificar**

```bash
./test_integration.sh
```

---

## 🎉 **Resultado Esperado:**

**Quando a Fortaleza está ativa, tu vês:**

- ✅ Correções automáticas
- ✅ Notificações de sucesso
- ✅ Logs de atividade
- ✅ Métricas aumentando
- ✅ Episódios sendo salvos

**Se não vês isso, a Fortaleza não está ativa!**

---

## 📞 **Solução de Problemas:**

### **API não inicia:**

```bash
# Verificar dependências
source venv/bin/activate
pip list | grep fastapi

# Verificar porta
lsof -i :8000
```

### **Extensão não carrega:**

```bash
# Verificar arquivos
ls -la cursor-extension/

# Instalar manualmente
./install_extension.sh
```

### **Erros não são corrigidos:**

```bash
# Testar integração
./test_integration.sh

# Verificar logs
tail -f logs/api.log
```

---

## 🎯 **Resumo:**

**Para saber se estás a usar a Fortaleza:**

1. **API rodando** em localhost:8000
2. **Extensão carregada** no Cursor
3. **Correções automáticas** acontecendo
4. **Notificações** aparecendo
5. **Métricas** aumentando

**Se algum destes falhar, a Fortaleza não está ativa!**
