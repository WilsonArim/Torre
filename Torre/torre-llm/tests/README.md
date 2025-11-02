# 🧪 Estratégia de Testes FastAPI

## 📋 Visão Geral

Implementamos **dois perfis de teste** para cobrir diferentes necessidades:

### 🔥 **Smoke (Rápido)**
- **Arquivo**: `test_fastapi_simple.py`
- **Objetivo**: Validação básica de infraestrutura
- **Tolerância**: Aceita 200/422/503/429
- **Uso**: Pre-push, CI rápido

### 📜 **Contrato (Estrito)**
- **Arquivo**: `test_fastapi_contract.py`
- **Objetivo**: Validação de contratos, auth, rate-limit
- **Tolerância**: 200 apenas (com validações específicas)
- **Uso**: PR gate, nightly

## 🚀 Como Usar

### Pipeline Sugerido

```bash
# Pre-push (rápido)
pytest -q tests/test_fastapi_simple.py

# PR gate (estrito)
TEST_PROFILE=strict pytest -q tests/test_fastapi_contract.py

# Nightly (completo)
TEST_PROFILE=strict pytest -q tests/test_fastapi_contract.py evals/test_phase*.py
```

### Demo Interativo

```bash
python3 demo_test_profiles.py
```

## 🔧 Configuração

### Variáveis de Ambiente

```bash
# Perfil de teste
TEST_PROFILE=strict  # ou omitir para smoke

# API Key para testes
FORTALEZA_API_KEY=test-key
```

### Helper Functions

```python
from tests._helpers import expect_ok, expect_auth_required, expect_rate_limited

# Asserções por perfil
expect_ok(200)  # 200 em strict, 200/422/503/429 em smoke
expect_auth_required(401)  # 401/403/422
expect_rate_limited(429)  # 429
```

## 📊 Cobertura

### Smoke Tests
- ✅ Health check
- ✅ Memory metrics
- ✅ Traces badge (tolerante)
- ✅ Rate limit básico

### Contract Tests
- ✅ Auth validation (401/403/422)
- ✅ Rate limiting (429)
- ✅ Schema validation
- ✅ WAF/security
- ✅ Endpoint contracts

## 🐛 Troubleshooting

### Erro 422 (Validation Error)
- **Causa**: Validação de parâmetros antes da verificação de auth
- **Solução**: Aceitar 422 como status válido em testes de auth

### Erro 503 (Service Unavailable)
- **Causa**: Módulos opcionais indisponíveis
- **Solução**: Testar condicionalmente se módulo está disponível

### Erro de Escopo (NameError)
- **Causa**: Variáveis globais mal definidas
- **Solução**: Usar `app.state` para estado global

## 🎯 Benefícios

### **Robustez**
- Não quebra se módulos opcionais estiverem indisponíveis
- Valida infraestrutura mesmo com dependências faltando

### **Diagnóstico**
- Identifica problemas específicos de cada endpoint
- Mostra quais módulos estão funcionando

### **Progresso**
- Permite avançar mesmo com módulos faltando
- Não bloqueia desenvolvimento

## 📈 Métricas

```bash
# Contar testes por perfil
grep -c "def test_" tests/test_fastapi_simple.py
grep -c "def test_" tests/test_fastapi_contract.py

# Executar com coverage
pytest --cov=llm tests/test_fastapi_contract.py
```
