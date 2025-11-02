#!/bin/bash

echo "🔧 Instalando Extensão Fortaleza no Cursor..."
echo "=============================================="

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Funções de log
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Encontrar diretório de extensões do Cursor
find_cursor_extensions() {
    # Possíveis localizações no Mac
    possible_paths=(
        "$HOME/Library/Application Support/Cursor/User/extensions"
        "$HOME/.cursor/extensions"
        "$HOME/Library/Application Support/Cursor/extensions"
    )
    
    for path in "${possible_paths[@]}"; do
        if [ -d "$path" ]; then
            echo "$path"
            return 0
        fi
    done
    
    return 1
}

# Instalar extensão
install_extension() {
    local extensions_dir="$1"
    local extension_name="fortaleza-cursor-extension"
    local target_dir="$extensions_dir/$extension_name"
    
    log_info "Instalando extensão em: $target_dir"
    
    # Criar diretório da extensão
    mkdir -p "$target_dir"
    
    # Copiar arquivos da extensão
    cp cursor-extension/extension.js "$target_dir/"
    cp cursor-extension/package.json "$target_dir/"
    
    log_success "Extensão instalada em: $target_dir"
}

# Verificar se Cursor está rodando
check_cursor_running() {
    if pgrep -x "Cursor" > /dev/null; then
        log_warning "Cursor está rodando. Reinicie o Cursor para carregar a extensão."
        return 0
    else
        log_info "Cursor não está rodando. A extensão será carregada quando abrir o Cursor."
        return 1
    fi
}

# Função principal
main() {
    log_info "Procurando diretório de extensões do Cursor..."
    
    # Encontrar diretório de extensões
    extensions_dir=$(find_cursor_extensions)
    
    if [ $? -eq 0 ]; then
        log_success "Diretório de extensões encontrado: $extensions_dir"
        
        # Instalar extensão
        install_extension "$extensions_dir"
        
        # Verificar se Cursor está rodando
        check_cursor_running
        
        echo ""
        echo "🎉 EXTENSÃO INSTALADA!"
        echo "======================"
        echo ""
        echo "Próximos passos:"
        echo "1. Reiniciar o Cursor (se estiver rodando)"
        echo "2. Verificar se a extensão está ativa:"
        echo "   - Abrir Console (Cmd+Option+I)"
        echo "   - Procurar por: 'Fortaleza Cursor Extension carregada!'"
        echo "3. Testar com: ./test_integration.sh"
        echo ""
        echo "Comando manual: Cmd+Shift+F"
        echo ""
        
    else
        log_warning "Diretório de extensões não encontrado automaticamente."
        echo ""
        echo "📋 Instalação Manual:"
        echo "====================="
        echo ""
        echo "1. Abrir Cursor"
        echo "2. Ir para Extensões (Cmd+Shift+X)"
        echo "3. Clicar em '...' (mais opções)"
        echo "4. Selecionar 'Install from VSIX...'"
        echo "5. Navegar para: $(pwd)/cursor-extension/"
        echo "6. Selecionar package.json"
        echo ""
        echo "Ou carregar manualmente via console:"
        echo "1. Abrir Console (Cmd+Option+I)"
        echo "2. Copiar conteúdo de cursor-extension/extension.js"
        echo "3. Colar no console e pressionar Enter"
        echo ""
    fi
}

# Executar função principal
main "$@"
