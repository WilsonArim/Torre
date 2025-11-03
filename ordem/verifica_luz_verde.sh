#!/bin/bash
# Verifica Luz Verde - Validação de condições para avançar

set -o pipefail
# manter set -e só se todos os comandos críticos forem tratados; aqui não usamos set -e para permitir tratamento controlado
# set -e

echo "🟢 Verificando Luz Verde..."
echo ""

# Verificações básicas
CHECKS_PASSED=0
CHECKS_TOTAL=3
CONSTITUICAO_PRESENTE="false"
OUTPUT=""

# 1. Verificar Constituição
if [ -f "core/sop/constituição.yaml" ]; then
    echo "✅ Constituição presente"
    CONSTITUICAO_PRESENTE="true"
    ((CHECKS_PASSED++))
    OUTPUT="${OUTPUT}✅ Constituição presente\n"
else
    echo "❌ Constituição ausente"
    OUTPUT="${OUTPUT}❌ Constituição ausente\n"
fi

# 2. Verificar estrutura básica
if [ -d "core" ] && [ -d "pipeline" ]; then
    echo "✅ Estrutura básica OK"
    ((CHECKS_PASSED++))
    OUTPUT="${OUTPUT}✅ Estrutura básica OK\n"
else
    echo "❌ Estrutura básica incompleta"
    OUTPUT="${OUTPUT}❌ Estrutura básica incompleta\n"
fi

# 3. Verificar scripts de validação
if [ -f "core/scripts/validator.py" ]; then
    echo "✅ Scripts de validação presentes"
    ((CHECKS_PASSED++))
    OUTPUT="${OUTPUT}✅ Scripts de validação presentes\n"
else
    echo "⚠️  Scripts de validação não encontrados"
    OUTPUT="${OUTPUT}⚠️  Scripts de validação não encontrados\n"
fi

echo ""

# Lógica decisória: só exit 1 se falharem checks críticos
# Considera críticos: Constituição e Estrutura básica
if [ "${CONSTITUICAO_PRESENTE}" = "true" ] && [ -d "core" ] && [ -d "pipeline" ]; then
    if [ $CHECKS_PASSED -eq $CHECKS_TOTAL ]; then
        echo "🟢 Luz Verde: TODOS OS CHECKS PASSARAM"
        printf "%b\n" "$OUTPUT"
        exit 0
    else
        echo "🟢 Luz Verde: CHECKS CRÍTICOS PASSARAM ($CHECKS_PASSED/$CHECKS_TOTAL)"
        printf "%b\n" "$OUTPUT"
        exit 0
    fi
else
    echo "❌ Luz Verde: CHECKS CRÍTICOS FALHARAM ($CHECKS_PASSED/$CHECKS_TOTAL)" >&2
    [ -n "${OUTPUT:-}" ] && printf "%b\n" "$OUTPUT" >&2
    exit 1
fi

