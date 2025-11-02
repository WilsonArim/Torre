# 🏰 Torre Models Extension

## 📋 Instalação Manual

### **Método 1: Copiar arquivos manualmente**

1. **Abrir Cursor**
2. **Cmd+Shift+X** (Extensões)
3. **Clicar em "..."** (mais opções)
4. **Selecionar "Install from VSIX..."**
5. **Navegar para**: `/Users/wilsonarim/CURSOR/fortaleza 4.0/fortaleza-llm/torre-extension/`
6. **Selecionar**: `package.json`

### **Método 2: Instalar via terminal**

```bash
cd /Users/wilsonarim/CURSOR/fortaleza\ 4.0/fortaleza-llm/
code --install-extension torre-extension/
```

### **Método 3: Copiar para diretório de extensões**

```bash
# Encontrar diretório de extensões
find ~/Library -name "extensions" -type d | grep -i cursor

# Copiar arquivos
cp -r torre-extension/ ~/Library/Application\ Support/Cursor/User/extensions/torre-models-extension/
```

## 🔧 Verificação

Após instalação, verificar:

1. **Status bar** deve mostrar: `🏰 Torre`
2. **Cmd+Shift+P** → procurar por "Torre"
3. **Notificação**: "Torre Models Extension ativada! 🏰"

## 🚨 Solução de Problemas

Se não aparecer:

1. **Reiniciar Cursor**
2. **Verificar console**: Cmd+Option+I
3. **Procurar erros** relacionados a "torre"
4. **Verificar se API está rodando**: `curl http://localhost:8000/health`
