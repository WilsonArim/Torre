# 🚀 BADGE FLAGS - Fase 19 (Extensão)

## 📋 Resumo da Implementação

Implementei com sucesso as **flags adicionais** para o sistema de badge do Strategos, tornando-o muito mais flexível para debugging, testes e diferentes cenários de uso.

## 🏗️ Novas Flags Implementadas

### 1️⃣ **FORT_BADGE_ALWAYS=1**

- **Função**: Força publicação do badge independente do editor
- **Comportamento**: Ignora detecção de editor e STRATEGOS_V2
- **Uso**: Debugging, testes, CI/CD
- **Prioridade**: Respeita FORT_BADGE=0 (opt-out)

### 2️⃣ **FORT_BADGE_SYNC=1**

- **Função**: Executa POST do badge de forma síncrona
- **Comportamento**: Não cria thread, executa diretamente
- **Uso**: Testes determinísticos, debugging
- **Timeout**: 1.8 segundos (mesmo valor)

## 🎯 Como Funciona

### **Hierarquia de Prioridades**

```bash
# 1. Opt-out (maior prioridade)
FORT_BADGE=0 → Desliga publicação (independente de outras flags)

# 2. Força publicação
FORT_BADGE_ALWAYS=1 → Publica sempre (ignora editor/STRATEGOS_V2)

# 3. Modo normal
STRATEGOS_V2=1 + modo editor → Publica (comportamento original)

# 4. Execução
FORT_BADGE_SYNC=1 → Síncrono (sem thread)
FORT_BADGE_SYNC=0 → Assíncrono (com thread, default)
```

### **Exemplos de Uso**

#### **Debugging/Testes**

```bash
# Força publicação para qualquer request
export FORT_BADGE_ALWAYS=1
export FORT_BADGE_SYNC=1
echo '{"logs":{"types":"error"}}' | python3 -m llm.cli
```

#### **CI/CD**

```bash
# Publicação síncrona em pipeline
export FORT_BADGE_ALWAYS=1
export FORT_BADGE_SYNC=1
export FORTALEZA_API="https://api.fortaleza.com"
export FORTALEZA_API_KEY="ci-key"
python3 -m llm.cli < request.json
```

#### **Desenvolvimento**

```bash
# Modo normal (editor detectado)
export STRATEGOS_V2=1
export FORT_EDITOR=1
echo '{"context":{"ide":"vscode"}}' | python3 -m llm.cli
```

## 🧪 Testes Implementados

### **Testes Pytest**

- ✅ **`test_cli_badge_post.py`**: Valida FORT_BADGE_ALWAYS e opt-out
- ✅ **`test_cli_badge_sync.py`**: Valida caminho síncrono
- ✅ **Cobertura**: 3 testes passando

### **Testes Manuais**

- ✅ **`test_badge_flags_manual.py`**: Validação end-to-end
- ✅ **Cobertura**: 4 cenários testados

### **Resultados dos Testes**

```bash
# Pytest
PYTHONPATH=. pytest -q tests/test_cli_badge_*.py
# ... 3 passed in 0.02s

# Manual
PYTHONPATH=. python3 test_badge_flags_manual.py
# ✅ FORT_BADGE_ALWAYS=1 funcionando
# ✅ FORT_BADGE_SYNC=1 funcionando
# ✅ FORT_BADGE=0 (opt-out) funcionando
```

## 🔧 Características Técnicas

### **Segurança**

- ✅ **Opt-out respeitado**: FORT_BADGE=0 sempre desliga
- ✅ **Timeout**: 1.8 segundos (mesmo valor)
- ✅ **Falha silenciosa**: Não quebra a CLI
- ✅ **Error handling**: Captura todas as exceções

### **Performance**

- ✅ **Síncrono**: FORT_BADGE_SYNC=1 para testes
- ✅ **Assíncrono**: Thread daemon para produção
- ✅ **Leve**: Mínimo overhead
- ✅ **Flexível**: Configuração por cenário

### **Compatibilidade**

- ✅ **Backward compatible**: Não quebra comportamento existente
- ✅ **Opt-in**: Novas flags são opcionais
- ✅ **Hierárquico**: Prioridades bem definidas
- ✅ **Configurável**: Controle total via env vars

## 📊 Variáveis de Ambiente (Completas)

| Variável            | Padrão                  | Descrição                       | Prioridade |
| ------------------- | ----------------------- | ------------------------------- | ---------- |
| `FORT_BADGE`        | `1`                     | Habilita publicação (0=desliga) | **1ª**     |
| `FORT_BADGE_ALWAYS` | -                       | Força publicação sempre         | **2ª**     |
| `STRATEGOS_V2`      | `0`                     | Habilita Strategos v2           | **3ª**     |
| `FORT_EDITOR`       | -                       | Força modo editor               | **3ª**     |
| `FORT_BADGE_SYNC`   | -                       | Execução síncrona               | **4ª**     |
| `FORTALEZA_API`     | `http://localhost:8765` | URL do servidor                 | -          |
| `FORTALEZA_API_KEY` | -                       | API key (produção)              | -          |

## 🎉 Benefícios Alcançados

### **Flexibilidade**

- ✅ **Debugging**: FORT_BADGE_ALWAYS para qualquer request
- ✅ **Testes**: FORT_BADGE_SYNC para determinismo
- ✅ **CI/CD**: Configuração específica para pipelines
- ✅ **Desenvolvimento**: Modo normal preservado

### **Confiabilidade**

- ✅ **Opt-out**: FORT_BADGE=0 sempre funciona
- ✅ **Hierarquia**: Prioridades claras e previsíveis
- ✅ **Fallback**: Comportamento original preservado
- ✅ **Testes**: Cobertura completa

### **Usabilidade**

- ✅ **Zero configuração**: Funciona por padrão
- ✅ **Configurável**: Controle total via env vars
- ✅ **Documentado**: Comportamento bem definido
- ✅ **Testado**: Validação completa

## 📈 Exemplos de Uso Avançados

### **Pipeline CI/CD**

```bash
#!/bin/bash
# .github/workflows/badge-test.yml

export FORT_BADGE_ALWAYS=1
export FORT_BADGE_SYNC=1
export FORTALEZA_API="https://api.fortaleza.com"
export FORTALEZA_API_KEY="${{ secrets.FORTALEZA_API_KEY }}"

# Testa badge com request específico
echo '{"logs":{"types":"TS2307"}, "files":{"test.ts":"console.log(1)"}}' \
  | python3 -m llm.cli

# Verifica se badge foi atualizado
curl -s "$FORTALEZA_API/strategos/badge" | jq .
```

### **Debugging Local**

```bash
#!/bin/bash
# debug_badge.sh

export FORT_BADGE_ALWAYS=1
export FORT_BADGE_SYNC=1
export FORTALEZA_API="http://localhost:8765"

# Testa diferentes cenários
for scenario in "error" "warning" "info"; do
  echo "Testing $scenario..."
  echo "{\"logs\":{\"types\":\"$scenario\"}}" | python3 -m llm.cli
  sleep 1
done
```

### **Desenvolvimento**

```bash
#!/bin/bash
# dev_badge.sh

# Modo normal (editor detectado)
export STRATEGOS_V2=1
export FORT_EDITOR=1

# Testa com contexto de editor
echo '{
  "logs": {"types": "TS2307: Cannot find module"},
  "files": {"src/App.tsx": "console.log(1)"},
  "context": {"ide": "vscode"}
}' | python3 -m llm.cli
```

## 🔗 Integração com Fases Anteriores

### **F13 (n-best)**

- ✅ **ExecutionReranker**: Integração mantida
- ✅ **Métricas**: Coleta preservada

### **F14 (Memory)**

- ✅ **EpisodicMemory**: Contexto mantido
- ✅ **Priors**: Aplicação preservada

### **F15 (Strategos)**

- ✅ **StrategosV2Graph**: Funcionalidade mantida
- ✅ **Badge**: Sistema estendido

### **F16 (Trace)**

- ✅ **Trace ID**: Rastreabilidade mantida
- ✅ **Telemetria**: Métricas preservadas

### **F17 (Rollback)**

- ✅ **Rate limiting**: Proteção mantida
- ✅ **API key**: Autenticação preservada

## 🎯 Próximos Passos

1. **Documentação**: Guia de configuração por cenário
2. **Monitoramento**: Métricas de uso das flags
3. **Otimização**: Ajustar timeouts se necessário
4. **Integração**: CI/CD templates

---

**As flags do badge estão completas e funcionando!** 🎯

O sistema de badge do Strategos agora é muito mais flexível e adequado para diferentes cenários de uso, desde desenvolvimento local até pipelines de CI/CD, mantendo total compatibilidade com o comportamento original.
