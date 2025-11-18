# 🚀 FASE 18: Golden Set + Red-Team + PR Gate + Impact Analysis + Memory Policy

## 📋 Resumo da Implementação

A **Fase 18** foi implementada com sucesso, fornecendo um sistema completo de **qualidade e segurança** para o Torre LLM, com todos os componentes **opt-in** e **não invasivos**.

## 🏗️ Componentes Implementados

### 1️⃣ **Golden Set** (`evals/golden/`)

- **Runner**: `run_golden.py` - executa casos de teste com métricas
- **Casos**: 3 casos de teste (TS2304, TS2307, FastAPI import)
- **Gate**: Configurável via `GOLDEN_MIN_SR` (default: ≥95%)
- **Output**: `.fortaleza/golden/golden-YYYYMMDD-HHMMSS.json`

### 2️⃣ **Red-Team** (`evals/redteam/`)

- **Runner**: `run_redteam.py` - testa seeds de segurança
- **Seeds**: 3 seeds (dotenv leak, path traversal, symlink)
- **Gate**: Todos os seeds devem ser **negados** (0 diffs aplicáveis)
- **Validação**: Secret scan, path validation, security violations

### 3️⃣ **Impact Analysis** (`tools/impact/`)

- **Seletor**: `select_tests.py` - mapeia arquivos alterados → testes
- **Heurística**: Prefixos por diretório (src/, llm/, evals/)
- **Fallback**: Smoke test se nenhum mapeamento encontrado
- **Output**: JSON array de testes selecionados

### 4️⃣ **PR Gate** (`.github/workflows/`)

- **Workflow**: `pr-gate.yml` - CI/CD automatizado
- **Timeout**: 25 minutos
- **Steps**:
  1. Checkout + Setup Python
  2. Install dependencies
  3. Impact Analysis (seleção inteligente)
  4. Smoke & Contract tests (strict mode)
  5. Golden Set (amostra) + Red-Team

### 5️⃣ **Memory Policy** (`MEMORY_POLICY.md`)

- **Escopo**: Episódios, decisões, métricas (sem PII)
- **Sanitização**: Emails, chaves, paths absolutos
- **Retenção**: `.fortaleza/memory/` com rotação automática
- **Opt-out**: `FORT_MEM=0` para desativar

## 🎯 Resultados dos Testes

### ✅ **Golden Set**

```
Success Rate: 100.0% (2/2 casos)
Gate: ✅ PASSOU (≥95%)
```

### ✅ **Red-Team**

```
Seeds Negados: 3/3 (100%)
Gate: ✅ PASSOU (todos negados)
```

### ✅ **Impact Analysis**

```
Input: ["llm/server.py", "evals/test_phase18_smoke.py"]
Output: ["evals/test_phase*.py", "tests/test_fastapi_contract.py"]
```

## 🚀 Como Usar

### **Local (Desenvolvimento)**

```bash
# Golden Set (amostra)
python3 evals/golden/run_golden.py 3

# Red-Team
python3 evals/redteam/run_redteam.py

# Impact Analysis
echo '["llm/server.py"]' | python3 tools/impact/select_tests.py

# Demo completo
python3 demo_phase18.py
```

### **CI/CD (Automatizado)**

- **Trigger**: Pull Request para `main`/`master`
- **Execução**: GitHub Actions workflow
- **Gates**: Golden Set ≥95% + Red-Team 100% negado
- **Timeout**: 25 minutos

## 🔧 Configuração

### **Variáveis de Ambiente**

```bash
# Golden Set
GOLDEN_MIN_SR=95          # Gate de sucesso (%)

# Red-Team
LLM_RERANK=1              # Habilitar rerank
STRATEGOS_V2=1            # Habilitar strategos

# Memory
FORT_MEM=1                # Habilitar memória (default)
FORT_MEM=0                # Desabilitar memória

# Tests
TEST_PROFILE=strict       # Modo estrito
FORTALEZA_API_KEY=test    # API key para testes
```

## 📊 Métricas e Monitoramento

### **Golden Set Metrics**

- Success rate por execução
- Duração por caso
- Trace ID para rastreabilidade
- Métricas de rerank e strategos

### **Red-Team Metrics**

- Seeds negados vs. total
- Violações de segurança detectadas
- Diffs aplicáveis vs. esperado

### **Impact Analysis Metrics**

- Testes selecionados por PR
- Cobertura de mudanças
- Tempo de execução otimizado

## 🎉 Benefícios Alcançados

### **Qualidade**

- ✅ **Golden Set** garante regressões não passem
- ✅ **Impact Analysis** otimiza tempo de CI
- ✅ **Gates configuráveis** para diferentes níveis

### **Segurança**

- ✅ **Red-Team** previne vazamentos de segredos
- ✅ **Path validation** bloqueia traversal attacks
- ✅ **Secret scanning** integrado

### **Produtividade**

- ✅ **Opt-in** não quebra fluxo existente
- ✅ **Fast feedback** com impact analysis
- ✅ **Configurável** para diferentes projetos

### **Auditoria**

- ✅ **Memory Policy** formalizada
- ✅ **Trace IDs** para rastreabilidade
- ✅ **Métricas exportáveis** em JSON/CSV

## 🔮 Próximos Passos

1. **Expansão do Golden Set**: Mais casos de teste
2. **Red-Team Seeds**: Cenários mais complexos
3. **Memory Analytics**: Dashboards de métricas
4. **Custom Gates**: Configuração por projeto
5. **Integration Tests**: Testes end-to-end

---

**A Fase 18 está completa e pronta para produção!** 🎯
