# Análise de Código Morto e Ficheiros Não Utilizados

**Data**: 2025-11-01  
**Agente**: SOP v3.0  
**Objetivo**: Identificar código morto, ficheiros órfãos e dependências não utilizadas

---

## 🔴 CRÍTICO - Ficheiros Mortos Confirmados

### 1. `Torre/core/orquestrador/cli.py`
- **Status**: ❌ **MORTO**
- **Tamanho**: ~300 bytes (apenas função de log)
- **Evidência**: 
  - Nenhuma referência encontrada em todo o código
  - Ficheiro contém apenas função `log_autoexec` não utilizada
  - Diretório `Torre/core/orquestrador/` não é referenciado em nenhum lugar
- **Ação**: **DELETAR** `Torre/core/orquestrador/cli.py` e diretório `Torre/core/orquestrador/` se estiver vazio

### 2. `core/scripts/plugins/licenses.py`
- **Status**: ❌ **MORTO**
- **Função**: `check_licenses()` - **NÃO UTILIZADA**
- **Evidência**:
  - Função `check_licenses` nunca chamada em `validator.py`
  - Plugin não é importado nem referenciado
  - Funcionalidade de verificação de licenças não implementada no fluxo principal
- **Ação**: **DELETAR** ou **IMPLEMENTAR** verificação de licenças no `validator.py`

---

## 🟠 Ficheiros Duplicados / Conflitantes

### 3. `Torre/orquestrador/cli.py` vs `core/orquestrador/cli.py`
- **Status**: ⚠️ **DUPLICADO** (mas ativo)
- **Evidência**:
  - Ambos existem e têm funcionalidades diferentes
  - `Torre/orquestrador/cli.py` - CLI específico da Torre
  - `core/orquestrador/cli.py` - CLI principal da FÁBRICA
- **Ação**: **MANTER** - São diferentes e ambos utilizados

---

## 🟡 Plugins Não Utilizados (Código Morto Parcial)

### Todos os plugins em `core/scripts/plugins/` têm funções não utilizadas:

1. **`plugins/bandit.py`**
   - Função `summarize_bandit()` não utilizada
   - `validator.py` implementa `eval_bandit()` diretamente

2. **`plugins/cov.py`**
   - Função `read_coverage_percent()` não utilizada
   - `validator.py` implementa `parse_coverage()` diretamente

3. **`plugins/junit.py`**
   - Função `read_junit_summary()` não utilizada
   - `validator.py` implementa `eval_junit()` diretamente

4. **`plugins/npm_audit.py`**
   - Função `summarize_npm_audit()` não utilizada
   - `validator.py` implementa `eval_npm_audit()` diretamente

5. **`plugins/sbom.py`**
   - Função `exists_sbom()` não utilizada
   - `validator.py` implementa `eval_sbom()` diretamente

6. **`plugins/semgrep.py`**
   - Função `summarize_semgrep()` não utilizada
   - `validator.py` implementa `eval_semgrep()` diretamente

7. **`plugins/trivy.py`**
   - Função `summarize_trivy()` não utilizada
   - `validator.py` implementa `eval_trivy()` diretamente

**Conclusão**: Os plugins foram criados mas **nunca integrados**. O `validator.py` reimplementa toda a lógica diretamente.

**Opções**:
- **A) DELETAR** todos os plugins (se lógica está completa em validator.py)
- **B) REFATORAR** validator.py para usar os plugins (melhor organização)
- **C) MANTER** como está (plugins podem ser usados no futuro)

---

## 📁 Ficheiros de Relatórios Antigos

### Relatórios em `relatorios/` que podem ser arquivados:

1. **Relatórios antigos** (mais de 7 dias):
   - `Auditoria Forense Estrutural.md`
   - `Auditoria_Docs_e_Scripts.md`
   - `autoexec_log.md`
   - `torre_auditoria_total.md`
   - `torre_setup.md`

**Ação**: Considerar mover para `arquivo/relatorios/` ou manter apenas últimos 30 dias

---

## ✅ Ficheiros Ativos Confirmados

### Ficheiros Core (todos utilizados):
- ✅ `core/orquestrador/cli.py` - **ATIVO** (usado no Makefile)
- ✅ `core/orquestrador/sop_cli.py` - **ATIVO** (usado no Makefile)
- ✅ `core/orquestrador/engineer_cli.py` - **ATIVO** (usado no Makefile)
- ✅ `core/orquestrador/mailbox_health.py` - **ATIVO** (usado no Makefile)
- ✅ `core/orquestrador/orders_gc.py` - **ATIVO** (usado no Makefile)
- ✅ `core/orquestrador/validate_constituicao.sh` - **ATIVO** (usado no Makefile)
- ✅ `core/orquestrador/config.yaml` - **ATIVO** (referenciado em cli.py)
- ✅ `core/scripts/validator.py` - **ATIVO** (usado pelo SOP)

---

## 📊 Resumo

| Categoria | Quantidade | Ação Recomendada |
|-----------|------------|------------------|
| Ficheiros mortos confirmados | 2 | **DELETAR** |
| Plugins não utilizados | 7 | **DELETAR** ou **REFATORAR** |
| Funções não utilizadas | 8+ | **LIMPAR** código |
| Relatórios antigos | 5+ | **ARQUIVAR** |

---

## 🎯 Recomendações Prioritárias

1. **DELETAR** `Torre/core/orquestrador/cli.py` (confirmado morto)
2. **DECIDIR** sobre plugins: deletar ou refatorar para usar
3. **ARQUIVAR** relatórios antigos (>30 dias)
4. **LIMPAR** funções não utilizadas dos plugins (se mantidos)

---

**Agente**: SOP (FÁBRICA 2.0)  
**Data/Hora**: 2025-11-01  
**Regras aplicadas**: ART-04 (Verificabilidade), ART-09 (Evidência)
