#!/bin/bash

# Build script para extensão Fortaleza LLM Bridge

set -e

echo "🔨 Building Fortaleza LLM Bridge Extension..."

# Diretório da extensão
EXT_DIR="extensions/vscode"
BUILD_DIR="build/extension"

# Limpar build anterior
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

# Copiar arquivos da extensão
echo "📦 Copiando arquivos..."
cp -r "$EXT_DIR"/* "$BUILD_DIR/"

# Instalar dependências
echo "📥 Instalando dependências..."
cd "$BUILD_DIR"
npm install

# Compilar TypeScript
echo "🔧 Compilando TypeScript..."
npm run compile

# Criar ZIP
echo "📦 Criando ZIP..."
cd ../..
zip -r "fortaleza-bridge-v0.1.0.zip" "$BUILD_DIR" -x "*.git*" "node_modules/*" "*.map"

echo "✅ Build completo: fortaleza-bridge-v0.1.0.zip"
echo ""
echo "📋 Para usar:"
echo "1. Unzip: unzip fortaleza-bridge-v0.1.0.zip"
echo "2. Abra a pasta no VS Code"
echo "3. Pressione F5 para testar"
echo ""
echo "🔧 Para publicar:"
echo "1. cd build/extension"
echo "2. npm install -g vsce"
echo "3. vsce package"
