# Análise SOP — Falhas em Execução de Workflows CI/CD

**PIPELINE/FORA_PIPELINE:** PIPELINE

**OWNER: SOP — Próxima ação:** Corrigir caminhos e configurar Gitleaks para ignorar mocks de teste

**Data:** 2025-11-02  
**Agente:** SOP v3.0  
**Objetivo:** Analisar falhas identificadas na execução dos workflows corrigidos

---

## 🔍 RESUMO EXECUTIVO

**Status:** 🔴 **2 FALHAS CRÍTICAS IDENTIFICADAS**

**Workflows Afetados:** 2 (`fabrica-ci.yml`, `torre-battery.yml`)

**Severidade:** 🔴 **CRÍTICA** — Bloqueiam execução de testes de stress

**Correções Necessárias:** 2 (caminhos case-sensitive, configuração Gitleaks)

---

## 🔴 FALHA 1: SEGREDOS DETECTADOS PELO GITLEAKS (Falsos Positivos)

**Workflow:** `fabrica-ci.yml`  
**Job:** `security`  
**Status:** ❌ **FALHOU**

### Análise

**Detecções do Gitleaks:**
1. `Torre/torre-llm/PHASE19_SUMMARY.md` linha 97 — `curl-auth-header`
2. `Torre/torre-llm/evals/test_phase10.py` linha 17 — `generic-api-key`
3. `Torre/torre-llm/evals/test_phase14.py` linha 41 — `generic-api-key`
4. `Torre/torre-llm/evals/test_phase7.py` linha 256 — `generic-api-key`
5. `Torre/torre-llm/sanity_check_phase17.py` linha 62 — `generic-api-key`

### Validação dos "Segredos"

**Análise dos Arquivos:**

1. **`PHASE19_SUMMARY.md` linha 97:**
   ```bash
   curl -X POST http://localhost:8765/editor/patch \
     -H "x-api-key: your-api-key"
   ```
   ✅ **É um exemplo em documentação** — `your-api-key` é placeholder

2. **`test_phase10.py` linha 17:**
   ```python
   const api_key = "sk-123456789012345678901234567890";
   ```
   ✅ **É um mock de teste** — Padrão claramente falso (`sk-123456...`)

3. **`test_phase14.py` linha 41:**
   ```python
   "API key: sk-123456789012345678901234"
   ```
   ✅ **É um mock de teste** — Padrão claramente falso

4. **`test_phase7.py` linha 256:**
   ```python
   "API_KEY=sk-1234567890abcdef",
   "password=secret123"
   ```
   ✅ **São mocks de teste** — Strings de exemplo para testar detecção de segredos

5. **`sanity_check_phase17.py` linha 62:**
   ```python
   const api_key = "sk-123456789012345678901234567890";
   ```
   ✅ **É um mock de teste** — Padrão claramente falso

### Conclusão

**Todos os "segredos" detectados são:**
- ✅ Mocks/exemplos em arquivos de teste
- ✅ Placeholders em documentação
- ✅ Strings intencionais para testar detecção de segredos
- ❌ **NÃO são segredos reais**

**Impacto:**
- ❌ Workflow falha desnecessariamente
- ❌ Bloqueia execução de testes de stress
- ⚠️ Violação de ART-04 (Verificabilidade) — verificações incorretas bloqueiam pipeline

**Correção Necessária:**
- Configurar Gitleaks para ignorar esses arquivos/padrões
- Adicionar `.gitleaksignore` ou configurar exceções no workflow

---

## 🔴 FALHA 2: SCRIPTS NÃO ENCONTRADOS (Case Sensitivity)

**Workflow:** `torre-battery.yml`  
**Job:** `consolidate_reports`  
**Status:** ❌ **FALHOU**

### Análise

**Erro:**
```
python3: can't open file '/home/runner/work/Torre/Torre/torre/orquestrador/battery_consolidator.py': [Errno 2] No such file or directory
```

**Problema Identificado:**

**Workflow referencia:** `torre/orquestrador/battery_consolidator.py` (minúsculo)  
**Diretório real:** `Torre/orquestrador/battery_consolidator.py` (maiúsculo)

**Linhas Afetadas:**
- Linha 90: `python3 torre/orquestrador/battery_runner.py`
- Linha 140: `python3 torre/orquestrador/battery_consolidator.py`
- Linha 157: `python3 torre/orquestrador/battery_reporter.py`

### Validação

**Scripts Existentes:**
- ✅ `Torre/orquestrador/battery_runner.py` — Existe
- ✅ `Torre/orquestrador/battery_consolidator.py` — Existe
- ✅ `Torre/orquestrador/battery_reporter.py` — Existe

**Problema:**
- ❌ GitHub Actions executa em Linux (case-sensitive)
- ❌ `torre/` (minúsculo) ≠ `Torre/` (maiúsculo)
- ❌ Workflow usa caminho incorreto

**Impacto:**
- ❌ Workflow `torre-battery.yml` não executa
- ❌ Testes de stress não podem ser executados
- ❌ Consolidação de relatórios falha
- ⚠️ Violação de ART-04 (Verificabilidade) — scripts não executam

**Correção Necessária:**
- Corrigir caminhos no workflow para usar `Torre/orquestrador/` (maiúsculo)

---

## 📊 MATRIZ DE PROBLEMAS E CORREÇÕES

| # | Problema | Severidade | Workflow | Status |
|---|----------|------------|----------|--------|
| 1 | Falsos positivos Gitleaks | 🔴 CRÍTICA | `fabrica-ci.yml` | ⚠️ REQUER CORREÇÃO |
| 2 | Caminho case-sensitive | 🔴 CRÍTICA | `torre-battery.yml` | ⚠️ REQUER CORREÇÃO |

---

## ⚖️ CONFORMIDADE CONSTITUCIONAL

### ART-04 (Verificabilidade)
❌ **NÃO CONFORME:**
- Workflows falham por falsos positivos (Gitleaks)
- Scripts não executam devido a caminhos incorretos
- Verificações não são executadas corretamente

### ART-07 (Transparência)
⚠️ **PARCIALMENTE CONFORME:**
- Erros são reportados, mas incluem falsos positivos
- Mensagens de erro não distinguem falsos positivos de verdadeiros

### ART-09 (Evidência)
❌ **NÃO CONFORME:**
- Workflows falham sem executar verificações reais
- Evidências de execução são falsas (falsos positivos)

---

## 🚨 RECOMENDAÇÕES CRÍTICAS

### Prioridade CRÍTICA (Bloqueio Imediato)

#### 1. Corrigir Caminhos Case-Sensitive em `torre-battery.yml`

**Ação:** Corrigir caminhos de `torre/orquestrador/` para `Torre/orquestrador/`

**Linhas Afetadas:**
- Linha 90: `python3 Torre/orquestrador/battery_runner.py`
- Linha 140: `python3 Torre/orquestrador/battery_consolidator.py`
- Linha 157: `python3 Torre/orquestrador/battery_reporter.py`

**Prazo:** Imediato (bloqueia execução de testes de stress)

**Critérios de Sucesso:**
- ✅ Todos os caminhos corrigidos para `Torre/orquestrador/`
- ✅ Workflow executa sem erros de "file not found"
- ✅ Scripts executam corretamente

---

#### 2. Configurar Gitleaks para Ignorar Mocks de Teste

**Ação:** Criar `.gitleaksignore` ou configurar exceções no workflow

**Arquivos para Ignorar:**
- `Torre/torre-llm/PHASE19_SUMMARY.md` (documentação com exemplos)
- `Torre/torre-llm/evals/test_phase*.py` (arquivos de teste com mocks)
- `Torre/torre-llm/sanity_check_phase*.py` (arquivos de teste com mocks)

**Padrões para Ignorar:**
- `sk-1234567890*` (mocks de API keys)
- `your-api-key` (placeholders em documentação)
- `secret123` (strings de exemplo)

**Prazo:** Antes de executar testes de stress

**Critérios de Sucesso:**
- ✅ `.gitleaksignore` criado com padrões apropriados
- ✅ Workflow `fabrica-ci.yml` passa no job `security`
- ✅ Apenas segredos reais são detectados

---

### Prioridade ALTA (Requer Atenção)

#### 3. Adicionar Validação de Caminhos no Workflow

**Ação:** Adicionar step de verificação de existência antes de executar scripts

**Critérios de Sucesso:**
- ✅ Verificação de existência de scripts antes de executar
- ✅ Mensagens de erro claras se scripts não existirem
- ✅ Workflow falha explicitamente com mensagem útil

---

## ✅ CONCLUSÃO

**Status Geral:** 🔴 **2 FALHAS CRÍTICAS IDENTIFICADAS**

**Bloqueios para Testes de Stress:** ❌ **BLOQUEADO** — Requer correções antes de executar

**Recomendação:** 🔴 **CORRIGIR IMEDIATAMENTE** antes de executar testes de stress

**Problemas Identificados:**
1. ❌ Caminhos case-sensitive incorretos em `torre-battery.yml`
2. ❌ Falsos positivos do Gitleaks bloqueando `fabrica-ci.yml`

**Correções Necessárias:**
1. Corrigir caminhos para `Torre/orquestrador/` (maiúsculo)
2. Configurar Gitleaks para ignorar mocks de teste

---

**Artefactos Citados:**
- `.github/workflows/torre-battery.yml` (linhas 90, 140, 157)
- `.github/workflows/fabrica-ci.yml` (job security)
- `Torre/orquestrador/battery_runner.py` (existe)
- `Torre/orquestrador/battery_consolidator.py` (existe)
- `Torre/orquestrador/battery_reporter.py` (existe)
- `Torre/torre-llm/PHASE19_SUMMARY.md` (linha 97)
- `Torre/torre-llm/evals/test_phase10.py` (linha 17)
- `Torre/torre-llm/evals/test_phase14.py` (linha 41)
- `Torre/torre-llm/evals/test_phase7.py` (linha 256)
- `Torre/torre-llm/sanity_check_phase17.py` (linha 62)

---

**Agente:** SOP (FÁBRICA 2.0)  
**Data/Hora:** 2025-11-02  
**Regras aplicadas:** ART-04, ART-07, ART-09

---

**COMANDO A EXECUTAR:** "ENGENHEIRO CORRIGIR: Caminhos case-sensitive em `torre-battery.yml` (linhas 90, 140, 157) de `torre/orquestrador/` para `Torre/orquestrador/`. Criar `.gitleaksignore` para ignorar mocks de teste em `Torre/torre-llm/`. Ver detalhes em `relatorios/para_estado_maior/analise_falhas_workflows_execucao_sop.md`."

