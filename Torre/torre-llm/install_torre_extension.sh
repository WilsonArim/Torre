#!/bin/bash

echo "🏰 Instalando Extensão da Torre Automaticamente..."
echo "=================================================="

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
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

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar se estamos no diretório correto
if [ ! -d "torre-extension" ]; then
    log_error "Diretório torre-extension não encontrado!"
    exit 1
fi

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
    local extension_name="torre-models-extension"
    local target_dir="$extensions_dir/$extension_name"
    
    log_info "Instalando extensão em: $target_dir"
    
    # Criar diretório da extensão
    mkdir -p "$target_dir"
    
    # Copiar arquivos da extensão
    cp torre-extension/package.json "$target_dir/"
    cp torre-extension/extension.js "$target_dir/"
    
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

# Verificar API da Torre
check_torre_api() {
    log_info "Verificando API da Torre..."
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        log_success "API da Torre está rodando"
        return 0
    else
        log_warning "API da Torre não está rodando"
        log_info "Execute: ./start_api.sh"
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
        
        # Verificar API da Torre
        check_torre_api
        
        echo ""
        echo "🎉 EXTENSÃO INSTALADA AUTOMATICAMENTE!"
        echo "====================================="
        echo ""
        echo "Próximos passos:"
        echo "1. Reiniciar o Cursor (se estiver rodando)"
        echo "2. Verificar se a extensão está ativa:"
        echo "   - Status bar deve mostrar: 🏰 Torre"
        echo "   - Notificação: 'Torre Models Extension ativada! 🏰'"
        echo ""
        echo "Como usar:"
        echo "1. Cmd+Shift+P → 'Torre: Enable Torre Auto'"
        echo "2. Cmd+Shift+T → Atalho para Torre Auto"
        echo "3. Status bar → Clique para mudar modelo"
        echo ""
        echo "Modelos disponíveis:"
        echo "🏰 Torre Auto - Seleção automática"
        echo "🏰 Torre Base - Correção de erros"
        echo "🏰 Torre Advice - Conselhos de código"
        echo "🏰 Torre Review - Revisão de código"
        echo "🏰 Torre Explain - Explicações"
        echo ""
        
    else
        log_warning "Diretório de extensões não encontrado automaticamente."
        echo ""
        echo "📋 Instalação Manual:"
        echo "===================="
        echo ""
        echo "1. Abrir Cursor"
        echo "2. Cmd+Shift+X (Extensões)"
        echo "3. Clicar em '...' (mais opções)"
        echo "4. Selecionar 'Install from VSIX...'"
        echo "5. Navegar para: $(pwd)/torre-extension/"
        echo "6. Selecionar package.json"
        echo ""
    fi
}

# Executar função principal
main "$@"
