#!/bin/bash
# Verifica Luz Verde - Validação de condições para avançar
# Este script verifica se todas as condições estão OK para prosseguir

set -e

echo "🟢 Verificando Luz Verde..."
echo ""

# Verificações básicas
CHECKS_PASSED=0
CHECKS_TOTAL=3

# 1. Verificar Constituição
if [ -f "core/sop/constituição.yaml" ]; then
    echo "✅ Constituição presente"
    ((CHECKS_PASSED++))
else
    echo "❌ Constituição ausente"
fi

# 2. Verificar estrutura básica
if [ -d "core" ] && [ -d "pipeline" ]; then
    echo "✅ Estrutura básica OK"
    ((CHECKS_PASSED++))
else
    echo "❌ Estrutura básica incompleta"
fi

# 3. Verificar scripts de validação
if [ -f "core/scripts/validator.py" ]; then
    echo "✅ Scripts de validação presentes"
    ((CHECKS_PASSED++))
else
    echo "⚠️  Scripts de validação não encontrados"
fi

echo ""
if [ $CHECKS_PASSED -eq $CHECKS_TOTAL ]; then
    echo "🟢 Luz Verde: TODOS OS CHECKS PASSARAM"
    exit 0
else
    echo "🟡 Luz Verde: ALGUNS CHECKS FALHARAM ($CHECKS_PASSED/$CHECKS_TOTAL)"
    exit 1
fi

