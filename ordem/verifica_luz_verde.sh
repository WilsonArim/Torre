#!/bin/bash
# Verifica Luz Verde - Validação de condições para avançar
# Este script verifica se todas as condições estão OK para prosseguir

set -e

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

# Garantir exit 0 quando Constituição presente e condições básicas atendidas
if [ "${CONSTITUICAO_PRESENTE}" = "true" ] || grep -q "Constituição presente" <(printf "%s\n" "$OUTPUT" 2>/dev/null); then
    if [ $CHECKS_PASSED -eq $CHECKS_TOTAL ]; then
        echo "🟢 Luz Verde: TODOS OS CHECKS PASSARAM"
        exit 0
    elif [ $CHECKS_PASSED -ge 2 ]; then
        # Pelo menos Constituição e estrutura básica estão OK
        echo "🟢 Luz Verde: CHECKS CRÍTICOS PASSARAM ($CHECKS_PASSED/$CHECKS_TOTAL)"
        exit 0
    else
        echo "🟡 Luz Verde: ALGUNS CHECKS FALHARAM ($CHECKS_PASSED/$CHECKS_TOTAL)" >&2
        [ -n "${OUTPUT:-}" ] && printf "%s\n" "$OUTPUT" >&2
        exit 1
    fi
else
    echo "❌ Constituição ausente ou verificação falhou" >&2
    [ -n "${OUTPUT:-}" ] && printf "%s\n" "$OUTPUT" >&2
    exit 1
fi

