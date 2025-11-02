#!/bin/bash

echo "🔄 Recarregando Extensão da Torre..."
echo "===================================="

# Verificar se Cursor está rodando
if pgrep -x "Cursor" > /dev/null; then
    echo "⚠️ Cursor está rodando. Reinicie o Cursor para aplicar as correções."
    echo ""
    echo "📋 Passos:"
    echo "1. Cmd+Q para fechar Cursor"
    echo "2. Abrir Cursor novamente"
    echo "3. Verificar se o erro desapareceu"
    echo ""
    echo "✅ Extensão corrigida e pronta!"
else
    echo "✅ Cursor não está rodando"
    echo "A extensão será carregada quando abrir o Cursor"
fi

# Verificar arquivos
echo ""
echo "📁 Verificando arquivos da extensão:"
ls -la ~/.cursor/extensions/torre-models-extension/

# Verificar API
echo ""
echo "🔍 Verificando API da Torre:"
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ API da Torre está rodando"
else
    echo "❌ API da Torre não está rodando"
    echo "Execute: ./start_api.sh"
fi

echo ""
echo "🎯 Correções aplicadas:"
echo "- Tratamento de erros melhorado"
echo "- Função activateModel centralizada"
echo "- Logs mais detalhados"
echo "- Try/catch em todas as operações"
echo ""
echo "🚀 Pronto! Abre o Cursor e testa novamente!"

