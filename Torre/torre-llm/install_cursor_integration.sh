#!/bin/bash

# Script de Instalação - Integração Cursor-Fortaleza
# Instala e configura a integração entre Cursor e API da Fortaleza

set -e

echo "🚀 INSTALAÇÃO DA INTEGRAÇÃO CURSOR-FORTALEZA"
echo "============================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Verificar dependências
check_dependencies() {
    log_info "Verificando dependências..."
    
    # Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 não encontrado. Instale Python 3.8+"
        exit 1
    fi
    log_success "Python3 encontrado"
    
    # Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js não encontrado. Instale Node.js 16+"
        exit 1
    fi
    log_success "Node.js encontrado"
    
    # npm
    if ! command -v npm &> /dev/null; then
        log_error "npm não encontrado"
        exit 1
    fi
    log_success "npm encontrado"
}

# Instalar dependências Python
install_python_deps() {
    log_info "Instalando dependências Python..."
    
    pip3 install --upgrade pip
    
    # Dependências principais
    pip3 install fastapi uvicorn requests pydantic
    
    # Dependências opcionais
    pip3 install python-multipart
    
    log_success "Dependências Python instaladas"
}

# Instalar dependências Node.js
install_node_deps() {
    log_info "Instalando dependências Node.js..."
    
    # Verificar se package.json existe
    if [ ! -f "package.json" ]; then
        log_warning "package.json não encontrado, criando..."
        npm init -y
    fi
    
    # Instalar dependências
    npm install --save-dev typescript @types/node
    
    log_success "Dependências Node.js instaladas"
}

# Configurar extensão do Cursor
setup_cursor_extension() {
    log_info "Configurando extensão do Cursor..."
    
    # Criar diretório para extensão
    mkdir -p cursor-extension
    
    # Verificar se extension.js já existe
    if [ ! -f "cursor-extension/extension.js" ]; then
        log_error "extension.js não encontrado em cursor-extension/"
        log_info "Certifique-se de que o arquivo foi criado corretamente"
        exit 1
    fi
    
    # Tornar executável
    chmod +x cursor-extension/extension.js
    
    log_success "Extensão do Cursor configurada"
}

# Configurar API da Fortaleza
setup_fortaleza_api() {
    log_info "Configurando API da Fortaleza..."
    
    # Verificar se api_server.py existe
    if [ ! -f "api_server.py" ]; then
        log_error "api_server.py não encontrado"
        log_info "Certifique-se de que o arquivo foi criado corretamente"
        exit 1
    fi
    
    # Tornar executável
    chmod +x api_server.py
    
    # Criar diretórios necessários
    mkdir -p .fortaleza/memory
    mkdir -p logs
    
    log_success "API da Fortaleza configurada"
}

# Criar scripts de controle
create_control_scripts() {
    log_info "Criando scripts de controle..."
    
    # Script para iniciar API
    cat > start_api.sh << 'EOF'
#!/bin/bash
echo "🚀 Iniciando API da Fortaleza..."
python3 api_server.py
EOF
    
    # Script para parar API
    cat > stop_api.sh << 'EOF'
#!/bin/bash
echo "🛑 Parando API da Fortaleza..."
pkill -f "api_server.py" || true
echo "✅ API parada"
EOF
    
    # Script para testar integração
    cat > test_integration.sh << 'EOF'
#!/bin/bash
echo "🧪 Testando integração Cursor-Fortaleza..."
python3 test_cursor_integration.py
EOF
    
    # Tornar executáveis
    chmod +x start_api.sh stop_api.sh test_integration.sh
    
    log_success "Scripts de controle criados"
}

# Criar arquivo de configuração
create_config() {
    log_info "Criando arquivo de configuração..."
    
    cat > fortaleza_config.json << 'EOF'
{
    "api": {
        "host": "0.0.0.0",
        "port": 8000,
        "cors_origins": ["*"]
    },
    "cursor": {
        "extension_enabled": true,
        "auto_fix": true,
        "show_notifications": true,
        "min_confidence": 0.8
    },
    "pipeline": {
        "pre_llm_timeout": 60,
        "llm_timeout": 120,
        "max_retries": 3
    }
}
EOF
    
    log_success "Arquivo de configuração criado"
}

# Criar documentação
create_docs() {
    log_info "Criando documentação..."
    
    cat > README_CURSOR_INTEGRATION.md << 'EOF'
# Integração Cursor-Fortaleza

## 🚀 Como usar

### 1. Iniciar API da Fortaleza
```bash
./start_api.sh
```

### 2. Carregar extensão no Cursor
- Abrir Cursor
- Ir para Extensões (Ctrl+Shift+X)
- Carregar extensão: `cursor-extension/extension.js`

### 3. Testar integração
```bash
./test_integration.sh
```

## 📋 Funcionalidades

- ✅ Correção automática de erros TypeScript
- ✅ Integração com pipeline da Fortaleza
- ✅ Métricas em tempo real
- ✅ Aprendizagem contínua

## 🔧 Configuração

Editar `fortaleza_config.json` para personalizar:
- Porta da API
- Configurações do Cursor
- Timeouts da pipeline

## 🛠️ Comandos úteis

- `./start_api.sh` - Inicia API
- `./stop_api.sh` - Para API
- `./test_integration.sh` - Testa integração

## 📊 Monitoramento

- API Health: http://localhost:8000/health
- Métricas: http://localhost:8000/metrics
- Documentação: http://localhost:8000/docs
EOF
    
    log_success "Documentação criada"
}

# Função principal
main() {
    echo "Iniciando instalação da integração Cursor-Fortaleza..."
    echo ""
    
    # Verificar se estamos no diretório correto
    if [ ! -f "api_server.py" ]; then
        log_error "Execute este script no diretório da Fortaleza LLM"
        exit 1
    fi
    
    # Executar etapas de instalação
    check_dependencies
    install_python_deps
    install_node_deps
    setup_cursor_extension
    setup_fortaleza_api
    create_control_scripts
    create_config
    create_docs
    
    echo ""
    echo "🎉 INSTALAÇÃO CONCLUÍDA!"
    echo "========================="
    echo ""
    echo "Próximos passos:"
    echo "1. Execute: ./start_api.sh"
    echo "2. Carregue a extensão no Cursor"
    echo "3. Teste com: ./test_integration.sh"
    echo ""
    echo "📖 Consulte README_CURSOR_INTEGRATION.md para mais detalhes"
    echo ""
}

# Executar função principal
main "$@"
