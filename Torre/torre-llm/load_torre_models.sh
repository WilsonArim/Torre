#!/bin/bash

echo "🏰 Carregando Modelos da Torre no Cursor..."
echo "============================================"

# Verificar se estamos no diretório correto
if [ ! -f "cursor-torre-integration.js" ]; then
    echo "❌ Arquivo cursor-torre-integration.js não encontrado!"
    echo "Execute este script no diretório da Fortaleza LLM"
    exit 1
fi

echo "✅ Arquivo de integração encontrado"

# Instruções para o usuário
echo ""
echo "📋 COMO CARREGAR OS MODELOS DA TORRE NO CURSOR:"
echo "================================================"
echo ""
echo "1. Abrir Cursor"
echo "2. Abrir Console do Developer (Cmd+Option+I)"
echo "3. Copiar e colar o seguinte código:"
echo ""
echo "----------------------------------------"
cat cursor-torre-integration.js
echo "----------------------------------------"
echo ""
echo "4. Pressionar Enter"
echo "5. Verificar se aparece: '🏰 Torre Integration carregada!'"
echo ""
echo "6. Ir para Configurações > Modelos"
echo "7. Os modelos da Torre devem aparecer na lista!"
echo ""

# Verificar se API está rodando
echo "🔍 Verificando se API da Torre está rodando..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ API da Torre está rodando"
else
    echo "⚠️ API da Torre não está rodando"
    echo "Execute: ./start_api.sh"
fi

echo ""
echo "🎯 MODELOS DA TORRE QUE SERÃO ADICIONADOS:"
echo "=========================================="
echo "🏰 Torre Auto - Seleção automática"
echo "🏰 Torre Base - Correção de erros"
echo "🏰 Torre Advice - Conselhos de código"
echo "🏰 Torre Review - Revisão de código"
echo "🏰 Torre Explain - Explicações"
echo ""

echo "🚀 Pronto! Siga as instruções acima para carregar os modelos."
