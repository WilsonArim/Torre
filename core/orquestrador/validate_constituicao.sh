#!/bin/bash
# Script de validação de imutabilidade da Constituição
# Valida que a Constituição não foi modificada

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CONSTITUICAO_PATH="${REPO_ROOT}/core/sop/constituição.yaml"

echo "🔒 Validando imutabilidade da Constituição..."

# Verificar se existe
if [ ! -f "$CONSTITUICAO_PATH" ]; then
    echo "❌ ERRO: Constituição ausente em $CONSTITUICAO_PATH"
    exit 1
fi

# Verificar se foi modificada no último commit (se houver histórico)
if git rev-parse HEAD~1 >/dev/null 2>&1; then
    if git diff --name-only HEAD~1 HEAD | grep -q "core/sop/constituição.yaml"; then
        echo "⚠️ ERRO CRÍTICO: Tentativa de modificação da Constituição detectada!"
        echo "A Constituição da FÁBRICA é imutável e não pode ser alterada."
        echo "Nenhum agente, humano ou LLM pode modificar core/sop/constituição.yaml"
        exit 1
    fi
fi

# Validar estrutura básica usando Python se disponível
if command -v python3 >/dev/null 2>&1; then
    python3 << EOF
import sys
from pathlib import Path

const_path = Path("${CONSTITUICAO_PATH}")
if not const_path.exists():
    print("❌ Constituição não encontrada")
    sys.exit(1)

try:
    content = const_path.read_text(encoding='utf-8')
    
    if not content.strip():
        print("❌ Constituição vazia")
        sys.exit(1)
    
    # Validação básica sem yaml
    if "imutavel: true" not in content.lower():
        print("❌ Constituição não marcada como imutável")
        sys.exit(1)
    
    # Contar leis pelo padrão "id: ART-"
    art_count = content.count("id: ART-")
    if art_count < 10:
        print(f"❌ Constituição incompleta: esperadas 10 leis, encontradas {art_count}")
        sys.exit(1)
    
    # Verificar IDs esperados
    ids_esperados = [f"ART-{i:02d}" for i in range(1, 11)]
    ids_encontrados = []
    for id_esperado in ids_esperados:
        if f"id: {id_esperado}" in content:
            ids_encontrados.append(id_esperado)
    
    faltantes = [id for id in ids_esperados if id not in ids_encontrados]
    if faltantes:
        print(f"❌ Leis ausentes: {', '.join(faltantes)}")
        sys.exit(1)
    
    # Tentar extrair versão
    versao = "N/A"
    for line in content.splitlines():
        if line.strip().startswith("versao:"):
            versao = line.split(":")[1].strip()
            break
    
    print("✅ Constituição válida e imutável")
    print(f"   Versão: {versao}")
    print(f"   Leis: {art_count}")
    sys.exit(0)
except Exception as e:
    print(f"❌ Erro ao validar Constituição: {e}")
    sys.exit(1)
EOF
else
    echo "⚠️ Python3 não disponível, validação básica apenas (ficheiro existe)"
fi

echo "✅ Validação da Constituição concluída"

