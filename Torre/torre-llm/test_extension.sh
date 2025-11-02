#!/bin/bash

echo "🧪 Testando Extensão da Torre..."
echo "================================"

# Verificar se arquivos existem
echo "1. Verificando arquivos da extensão..."
if [ -f "~/.cursor/extensions/torre-models-extension/package.json" ]; then
    echo "✅ package.json encontrado"
else
    echo "❌ package.json não encontrado"
fi

if [ -f "~/.cursor/extensions/torre-models-extension/extension.js" ]; then
    echo "✅ extension.js encontrado"
else
    echo "❌ extension.js não encontrado"
fi

# Verificar se Cursor está rodando
echo ""
echo "2. Verificando se Cursor está rodando..."
if pgrep -x "Cursor" > /dev/null; then
    echo "✅ Cursor está rodando"
    echo "   PID: $(pgrep -x "Cursor")"
else
    echo "❌ Cursor não está rodando"
fi

# Verificar API da Torre
echo ""
echo "3. Verificando API da Torre..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ API da Torre está rodando"
    curl -s http://localhost:8000/health | jq -r '.status'
else
    echo "❌ API da Torre não está rodando"
fi

# Instruções para o usuário
echo ""
echo "📋 INSTRUÇÕES PARA VERIFICAR:"
echo "=============================="
echo ""
echo "1. Se o Cursor está rodando, reinicie-o:"
echo "   - Cmd+Q para fechar"
echo "   - Abrir Cursor novamente"
echo ""
echo "2. Verificar se a extensão está ativa:"
echo "   - Status bar deve mostrar: 🏰 Torre"
echo "   - Notificação: '🏰 Torre Models Extension ativada!'"
echo ""
echo "3. Testar comandos:"
echo "   - Cmd+Shift+P → 'Torre: Enable Torre Auto'"
echo "   - Cmd+Shift+P → 'Torre: Enable Torre Base'"
echo "   - Cmd+Shift+P → 'Torre: Enable Torre Advice'"
echo ""
echo "4. Se não aparecer, verificar console:"
echo "   - Cmd+Option+I (ou tentar Cmd+Shift+I)"
echo "   - Procurar por: '🏰 Torre Extension: Ativando...'"
echo ""
echo "5. Se ainda não funcionar:"
echo "   - Verificar se há erros no console"
echo "   - Tentar instalação manual via Extensões"
