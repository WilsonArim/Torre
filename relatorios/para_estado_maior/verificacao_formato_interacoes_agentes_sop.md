# Verificação SOP — Formato Obrigatório em Respostas dos Agentes

**PIPELINE/FORA_PIPELINE:** FORA_PIPELINE

**OWNER: SOP — Próxima ação:** Verificar implementação do formato obrigatório em todas as respostas principais dos agentes

**Data:** 2025-11-02  
**Agente:** SOP v3.0  
**Objetivo:** Verificar se formato obrigatório está corretamente implementado em todas as respostas principais dos agentes

---

## 🔍 VERIFICAÇÃO REALIZADA

### Funções Principais de Resposta Identificadas

#### 1. **ENGENHEIRO** (`core/orquestrador/engineer_cli.py`)

**Função:** `cmd_executa()` (linhas 402-570)

**Status:** ✅ **IMPLEMENTADO CORRETAMENTE**

**Evidência:**
- Linha 560: Chama `formatar_resposta_agente()` com todos os parâmetros necessários
- Linha 536: Determina `pipeline_status` corretamente
- Linha 568: Imprime resposta formatada usando `print(resposta_formatada)`

**Formato aplicado:**
```python
resposta_formatada = formatar_resposta_agente(
    "ENGENHEIRO",
    conteudo_resposta,
    pipeline_status=pipeline_status,
    proxima_acao=proxima_acao,
    comando_executar=comando_executar
)
```

**Outras funções verificadas:**
- `cmd_status()` (linhas 573-607): ❌ **NÃO IMPLEMENTA FORMATO** — Apenas prints simples
- `cmd_limpa()` (linhas 610-628): ❌ **NÃO IMPLEMENTA FORMATO** — Apenas prints simples

---

#### 2. **SOP** (`core/orquestrador/sop_cli.py`)

**Função:** `cmd_executa()` (linhas 642-758)

**Status:** ✅ **IMPLEMENTADO CORRETAMENTE**

**Evidência:**
- Linha 748: Chama `formatar_resposta_agente()` com todos os parâmetros necessários
- Linha 729: Determina `pipeline_status` corretamente
- Linha 756: Imprime resposta formatada usando `print(resposta_formatada)`

**Formato aplicado:**
```python
resposta_formatada = formatar_resposta_agente(
    "SOP",
    conteudo_resposta,
    pipeline_status=pipeline_status,
    proxima_acao=proxima_acao,
    comando_executar=comando_executar
)
```

**Função:** `cmd_varredura_incongruencias()` (linhas 858-1000)

**Status:** ✅ **IMPLEMENTADO CORRETAMENTE**

**Evidência:**
- Linha 968: Chama `formatar_resposta_agente()` com todos os parâmetros necessários
- Linha 956: Determina `pipeline_status` corretamente
- Linha 976: Imprime resposta formatada usando `print(resposta_formatada)`

**Outras funções verificadas:**
- `cmd_status()` (linhas 761-813): ❌ **NÃO IMPLEMENTA FORMATO** — Apenas prints simples
- `cmd_limpa()` (linhas 814-855): ❌ **NÃO IMPLEMENTA FORMATO** — Apenas prints simples

---

#### 3. **Função de Formatação** (`core/orquestrador/file_access_guard.py`)

**Função:** `formatar_resposta_agente()` (linhas 231-287)

**Status:** ✅ **IMPLEMENTADA CORRETAMENTE**

**Evidência:**
- Linha 241: Adiciona `**PIPELINE/FORA_PIPELINE:**` no início
- Linha 242: Adiciona `**OWNER: {agente} — Próxima ação:**` 
- Linha 268: Adiciona `**COMANDO A EXECUTAR:**` no fim
- Implementa formato completo conforme doutrina

**Código:**
```python
def formatar_resposta_agente(agente: str, conteudo: str, pipeline_status: str = "FORA_PIPELINE", proxima_acao: str = "", comando_executar: str = ""):
    """
    Formata resposta do agente conforme doutrina de formato obrigatório.
    
    Formato obrigatório:
    - Início: **PIPELINE/FORA_PIPELINE:** PIPELINE ou FORA_PIPELINE
    - Fim: **COMANDO A EXECUTAR:** "AGENTE AÇÃO (localização)"
    """
    # ... implementação completa ...
```

---

## 🔴 PROBLEMAS IDENTIFICADOS

### 1. **ENGENHEIRO — `cmd_status()` e `cmd_limpa()` Não Implementam Formato**

**Arquivo:** `core/orquestrador/engineer_cli.py`

**Funções Afetadas:**
- `cmd_status()` (linhas 573-607)
- `cmd_limpa()` (linhas 610-628)

**Problema:** Estas funções usam apenas `print()` simples, não seguem formato obrigatório.

**Severidade:** 🟠 **MÉDIA** — Funções secundárias, mas ainda são respostas do agente

---

### 2. **SOP — `cmd_status()` e `cmd_limpa()` Não Implementam Formato**

**Arquivo:** `core/orquestrador/sop_cli.py`

**Funções Afetadas:**
- `cmd_status()` (linhas 761-813)
- `cmd_limpa()` (linhas 814-855)

**Problema:** Estas funções usam apenas `print()` simples, não seguem formato obrigatório.

**Severidade:** 🟠 **MÉDIA** — Funções secundárias, mas ainda são respostas do agente

---

### 3. **Fallback em Caso de Importação Falhada**

**Arquivo:** `core/orquestrador/engineer_cli.py` (linhas 48-49)  
**Arquivo:** `core/orquestrador/sop_cli.py` (linhas 50-51)

**Problema:** Se `file_access_guard` não puder ser importado, fallback retorna conteúdo sem formatação.

**Código:**
```python
def formatar_resposta_agente(agente: str, conteudo: str, pipeline_status: str = "FORA_PIPELINE", proxima_acao: str = "", comando_executar: str = ""):
    return conteudo  # Fallback: retornar conteúdo sem formatação
```

**Severidade:** 🟡 **BAIXA** — Apenas em caso de erro de importação, mas deve garantir formato sempre

---

## ✅ PONTOS POSITIVOS

### 1. Função Principal de Formatação Implementada Corretamente

- `formatar_resposta_agente()` em `file_access_guard.py` implementa formato completo
- Inclui início (`PIPELINE/FORA_PIPELINE`)
- Inclui fim (`COMANDO A EXECUTAR`)
- Inclui `OWNER: AGENTE — Próxima ação:`

### 2. Funções Principais Usam Formatação

- `engineer_cli.py` → `cmd_executa()` ✅
- `sop_cli.py` → `cmd_executa()` ✅
- `sop_cli.py` → `cmd_varredura_incongruencias()` ✅

### 3. Relatórios Markdown Seguem Formato

- `generate_incongruencias_report()` em `sop_cli.py` inclui formato obrigatório (linhas 544, 633)

---

## 📋 RESUMO DA VERIFICAÇÃO

### Funções Principais (Execução de Ordens)

| Agente | Função | Status |
|--------|--------|--------|
| ENGENHEIRO | `cmd_executa()` | ✅ **CORRETO** |
| SOP | `cmd_executa()` | ✅ **CORRETO** |
| SOP | `cmd_varredura_incongruencias()` | ✅ **CORRETO** |

### Funções Secundárias (Status/Limpeza)

| Agente | Função | Status |
|--------|--------|--------|
| ENGENHEIRO | `cmd_status()` | ❌ **NÃO IMPLEMENTA** |
| ENGENHEIRO | `cmd_limpa()` | ❌ **NÃO IMPLEMENTA** |
| SOP | `cmd_status()` | ❌ **NÃO IMPLEMENTA** |
| SOP | `cmd_limpa()` | ❌ **NÃO IMPLEMENTA** |

---

## ⚖️ CONFORMIDADE CONSTITUCIONAL

### ART-04 (Verificabilidade)
⚠️ **RISCO PARCIAL:** Funções secundárias não seguem formato obrigatório, reduzindo verificabilidade

### ART-09 (Evidência)
⚠️ **RISCO PARCIAL:** Funções secundárias não incluem comando a executar, reduzindo rastreabilidade

---

## 🛡️ RECOMENDAÇÕES

### Prioridade ALTA

1. **Atualizar `cmd_status()` e `cmd_limpa()` do ENGENHEIRO**
   - Implementar `formatar_resposta_agente()` nestas funções
   - Garantir formato obrigatório em todas as respostas

2. **Atualizar `cmd_status()` e `cmd_limpa()` do SOP**
   - Implementar `formatar_resposta_agente()` nestas funções
   - Garantir formato obrigatório em todas as respostas

### Prioridade MÉDIA

3. **Melhorar Fallback**
   - Garantir que fallback também implemente formato obrigatório mesmo em caso de erro de importação

---

## 📋 CONCLUSÃO

**Status Geral:** ⚠️ **PARCIALMENTE CONFORMANTE**

**Funções Principais:** ✅ **CORRETAS** — Todas as funções principais que executam ordens implementam formato obrigatório corretamente

**Funções Secundárias:** ❌ **NÃO CONFORMANTES** — Funções de status e limpeza não implementam formato obrigatório

**Recomendação:** Implementar formato obrigatório em todas as funções que geram respostas ao usuário/Estado-Maior, incluindo funções secundárias.

---

**Artefactos Citados:**
- `core/orquestrador/engineer_cli.py` (linhas 402-628) ⚠️
- `core/orquestrador/sop_cli.py` (linhas 642-1000) ⚠️
- `core/orquestrador/file_access_guard.py` (linhas 231-287) ✅
- `core/sop/doutrina.yaml` (formato_interacoes) ✅

---

**Agente:** SOP (FÁBRICA 2.0)  
**Data/Hora:** 2025-11-02  
**Regras aplicadas:** ART-04, ART-09, Doutrina de Acesso a Ficheiros (formato_interacoes)

---

**COMANDO A EXECUTAR:** "ENGENHEIRO IMPLEMENTAR FORMATO OBRIGATÓRIO EM TODAS AS FUNÇÕES QUE GERAM RESPOSTAS: Atualizar cmd_status() e cmd_limpa() do ENGENHEIRO e SOP para usar formatar_resposta_agente(), e melhorar fallback para garantir formato mesmo em caso de erro de importação"

