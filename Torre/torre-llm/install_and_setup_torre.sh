#!/usr/bin/env bash
set -e

echo "🚀 INSTALAÇÃO E CONFIGURAÇÃO COMPLETA DA TORRE"
echo "=============================================="

# Verificar se estamos no macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "✅ Detectado macOS"
    
    # Verificar se Ollama já está instalado
    if command -v ollama >/dev/null 2>&1; then
        echo "✅ Ollama já está instalado"
    else
        echo "📥 Instalando Ollama..."
        curl -fsSL https://ollama.com/install.sh | sh
        echo "✅ Ollama instalado com sucesso"
    fi
else
    echo "⚠️ Sistema não suportado automaticamente"
    echo "Instale o Ollama manualmente em: https://ollama.com/download"
    exit 1
fi

echo ""
echo "🔧 Configurando Torre LLM..."

# Executar o script de setup
cd "$(dirname "$0")"
./setup_ollama_torre.sh

echo ""
echo "🎉 CONFIGURAÇÃO COMPLETA!"
echo "========================="
echo ""
echo "📋 PRÓXIMOS PASSOS NO CURSOR:"
echo "1. Abra o Cursor"
echo "2. Vá em Settings → Models → API Keys"
echo "3. Configure:"
echo "   - Override Base URL: http://localhost:11434/v1"
echo "   - API Key: local"
echo "4. Add model:"
echo "   - Display Name: Torre"
echo "   - Model (ID): torre"
echo "5. Abra um chat e selecione 'Torre'"
echo ""
echo "🧪 TESTE:"
echo "Digite: 'Diga: Sou a Torre.'"
echo ""
echo "📁 Arquivos criados:"
echo "- setup_ollama_torre.sh (script de configuração)"
echo "- Modelfile (configuração do modelo)"
echo "- cursor_custom_model_example.json (exemplo para Cursor)"
echo "- PATCH_CURSOR_TORRE.md (documentação completa)"
echo "- CURSOR_CONFIG_QUICK.md (configuração rápida)"
