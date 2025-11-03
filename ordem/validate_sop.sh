#!/bin/bash
# Validar SOP - Script de validação do Sistema Operacional da Política
# Este script valida conformidade com a Constituição da FÁBRICA

set -e

echo "🔒 Validando SOP (Sistema Operacional da Política)..."
echo ""

# Verificar se o validador Python existe
if [ -f "core/scripts/validator.py" ]; then
    echo "✅ Validador encontrado: core/scripts/validator.py"
    python3 core/scripts/validator.py
    EXIT_CODE=$?
    
    if [ $EXIT_CODE -eq 0 ]; then
        echo ""
        echo "✅ Validação SOP concluída com sucesso"
        exit 0
    else
        echo ""
        echo "⚠️  Validação SOP encontrou problemas (exit code: $EXIT_CODE)"
        exit $EXIT_CODE
    fi
else
    echo "⚠️  Validador não encontrado em core/scripts/validator.py"
    echo "   Usando validação básica..."
    
    # Validação básica de fallback
    if [ -f "core/sop/constituição.yaml" ]; then
        echo "✅ Constituição encontrada"
        exit 0
    else
        echo "❌ Constituição não encontrada"
        exit 1
    fi
fi

