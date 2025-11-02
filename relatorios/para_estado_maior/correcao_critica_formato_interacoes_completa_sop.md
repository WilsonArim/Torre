# Correção Crítica SOP — Formato Obrigatório de TODAS as Interações

**PIPELINE/FORA_PIPELINE:** FORA_PIPELINE

**OWNER: SOP — Próxima ação:** Corrigir interpretação incorreta e atualizar doutrina e PINs

**Data:** 2025-11-02  
**Agente:** SOP v3.0  
**Objetivo:** Corrigir interpretação: formato obrigatório aplica-se a TODAS as interações, não apenas relatórios

---

## 🚨 VIOLAÇÃO CRÍTICA IDENTIFICADA

**Problema:** Formato obrigatório foi implementado apenas para relatórios em markdown, mas deveria aplicar-se a **TODAS as interações** dos agentes com o Estado-Maior/usuário.

**Severidade:** 🔴 **CRÍTICO** — Interpretação incorreta da doutrina

**Impacto:** Sistema não está totalmente conformante — formato obrigatório não aplicado a todas as interações

---

## ⚠️ INTERPRETAÇÃO INCORRETA ANTERIOR

### Implementação Anterior (INCORRETA)
- ❌ Formato obrigatório aplicado apenas a relatórios markdown salvos em ficheiros
- ❌ Validação apenas antes de salvar ficheiros markdown
- ❌ Não aplicado a respostas de texto dos agentes
- ❌ Não aplicado a comunicações dos agentes
- ❌ Não aplicado a agentes da Torre
- ❌ Não aplicado a interações em tempo real

---

## ✅ INTERPRETAÇÃO CORRETA DA DOUTRINA

### Formato Obrigatório Deve Aplicar-se a:

1. ✅ **Relatórios em markdown** (já implementado parcialmente)
2. ✅ **Respostas de texto dos agentes** (NÃO implementado)
3. ✅ **Comunicações dos agentes** (NÃO implementado)
4. ✅ **Qualquer interação entre agente e Estado-Maior/usuário** (NÃO implementado)
5. ✅ **Agentes da Torre** (NÃO implementado)
6. ✅ **Interações em tempo real** (NÃO implementado)

### Formato Obrigatório:

**Início (OBRIGATÓRIO):**
```
**PIPELINE/FORA_PIPELINE:** PIPELINE ou FORA_PIPELINE
```

**Fim (OBRIGATÓRIO):**
```
**COMANDO A EXECUTAR:** "AGENTE AÇÃO (localização)"
```

---

## 🔴 VIOLAÇÕES IDENTIFICADAS

### 1. Doutrina Não Especificava Claramente

**Arquivo:** `core/sop/doutrina.yaml`

**Problema:** Seção `formato_relatorios` sugeria que era apenas para relatórios, não para todas as interações.

**Status:** ✅ **CORRIGIDO** — Renomeado para `formato_interacoes` e especificado que aplica-se a TODAS as interações

---

### 2. PINs Não Especificavam Formato Obrigatório de Interações

**Arquivos Afetados:**
- `factory/pins/estado_maior.yaml` ⚠️
- `factory/pins/engenheiro.yaml` ⚠️
- `factory/pins/sop.yaml` ⚠️
- `factory/pins/gatekeeper.yaml` ⚠️
- `Torre/pins/estado_maior_torre.yaml` ⚠️
- `Torre/pins/engenheiro_torre.yaml` ⚠️
- `Torre/orquestrador/PIN_ESTADO_MAIOR.yaml` ⚠️
- `Torre/orquestrador/PIN_ENGENHEIRO.yaml` ⚠️

**Problema:** PINs não especificavam que TODAS as interações devem seguir formato obrigatório.

**Status:** ⚠️ **CORREÇÃO EM PROGRESSO** — Adicionando seção `formato_interacoes` a todos os PINs

---

### 3. Código Não Valida Formato em Respostas de Texto

**Problema:** Código apenas valida formato antes de salvar ficheiros markdown, não valida formato em respostas de texto dos agentes.

**Status:** ❌ **NÃO IMPLEMENTADO** — Necessário implementar validação de formato em todas as respostas

---

### 4. Agentes da Torre Não Seguem Formato

**Problema:** PINs da Torre não especificavam formato obrigatório de interações.

**Status:** ⚠️ **CORREÇÃO EM PROGRESSO** — Adicionando formato obrigatório aos PINs da Torre

---

## 🛡️ CORREÇÕES IMPLEMENTADAS

### 1. ✅ Doutrina Atualizada

**Arquivo:** `core/sop/doutrina.yaml`

**Mudança:**
- ❌ Antes: `formato_relatorios` (apenas relatórios)
- ✅ Agora: `formato_interacoes` (TODAS as interações)

**Especificação:**
- Aplicável a TODAS as interações de TODOS os agentes
- Inclui agentes da Torre
- Aplica-se a relatórios, respostas, comunicações, qualquer interação

**Status:** ✅ **CORRIGIDO**

---

### 2. ⚠️ PINs da FÁBRICA Atualizados

**Arquivos:**
- `factory/pins/estado_maior.yaml` ✅
- `factory/pins/engenheiro.yaml` ✅
- `factory/pins/sop.yaml` ✅
- `factory/pins/gatekeeper.yaml` ✅

**Mudança:** Adicionada seção `formato_interacoes` especificando formato obrigatório.

**Status:** ✅ **CORRIGIDO**

---

### 3. ⚠️ PINs da Torre Atualizados

**Arquivos:**
- `Torre/pins/estado_maior_torre.yaml` ✅
- `Torre/pins/engenheiro_torre.yaml` ✅

**Mudança:** Adicionada seção `formato_interacoes` especificando formato obrigatório.

**Status:** ✅ **CORRIGIDO**

---

### 4. ❌ Validação em Código Não Implementada

**Problema:** Código não valida formato em respostas de texto dos agentes.

**Arquivos Afetados:**
- `core/orquestrador/engineer_cli.py`
- `core/orquestrador/sop_cli.py`
- Código do Gatekeeper (quando existir)

**Status:** ❌ **NÃO IMPLEMENTADO** — Necessário implementar validação

---

## 📋 EXEMPLO DE FORMATO CORRETO

### Resposta Correta de um Agente:

```markdown
**PIPELINE/FORA_PIPELINE:** FORA_PIPELINE

**OWNER: ENGENHEIRO — Próxima ação:** Executar ordem do Estado-Maior

[... conteúdo da resposta ...]

---

**COMANDO A EXECUTAR:** "ESTADO-MAIOR REVISAR RELATÓRIO (relatorios/para_estado_maior/engineer.out.json)"
```

### Resposta Correta da Torre:

```markdown
**PIPELINE/FORA_PIPELINE:** PIPELINE

**OWNER: ESTADO-MAIOR-TORRE — Próxima ação:** Validar gate G2

[... conteúdo da resposta ...]

---

**COMANDO A EXECUTAR:** "ENGENHEIRO EXECUTAR CORREÇÕES IDENTIFICADAS"
```

---

## ⚖️ VIOLAÇÕES CONSTITUCIONAIS

### ART-04 (Verificabilidade)
⚠️ **RISCO:** Interações não seguem formato obrigatório completamente, não são totalmente verificáveis.

### ART-09 (Evidência)
⚠️ **RISCO:** Interações podem não incluir comando a executar, não são totalmente rastreáveis.

---

## 📋 CHECKLIST DE CORREÇÃO

### Doutrina
- [x] Renomear `formato_relatorios` para `formato_interacoes` ✅
- [x] Especificar que aplica-se a TODAS as interações ✅
- [x] Incluir agentes da Torre ✅

### PINs FÁBRICA
- [x] Adicionar `formato_interacoes` ao PIN do Estado-Maior ✅
- [x] Adicionar `formato_interacoes` ao PIN do Engenheiro ✅
- [x] Adicionar `formato_interacoes` ao PIN do SOP ✅
- [x] Adicionar `formato_interacoes` ao PIN do Gatekeeper ✅

### PINs Torre
- [x] Adicionar `formato_interacoes` ao PIN do Estado-Maior Torre ✅
- [x] Adicionar `formato_interacoes` ao PIN do Engenheiro Torre ✅
- [ ] Verificar outros PINs da Torre ⚠️

### Código
- [ ] Implementar validação de formato em respostas de texto ❌
- [ ] Implementar validação de formato em comunicações ❌
- [ ] Garantir que todos os agentes seguem formato ❌

---

## 📋 CONCLUSÃO

**Violação Crítica:** Formato obrigatório implementado apenas parcialmente (apenas relatórios markdown).

**Correções Implementadas:**
1. ✅ Doutrina atualizada (`formato_interacoes`)
2. ✅ PINs da FÁBRICA atualizados (4 PINs)
3. ✅ PINs da Torre atualizados (2 PINs)

**Correções Pendentes:**
1. ❌ Validação de formato em código (respostas de texto)
2. ⚠️ Verificar outros PINs da Torre

**Status:** ⚠️ **PARCIALMENTE CORRIGIDO** — Doutrina e PINs corrigidos, mas validação em código ainda não implementada

**Recomendação:** Implementar validação de formato em todas as respostas de texto dos agentes antes de considerar sistema totalmente conformante.

---

**Artefactos Citados:**
- `core/sop/doutrina.yaml` (linhas 97-119) ✅ CORRIGIDO
- `factory/pins/estado_maior.yaml` ✅ CORRIGIDO
- `factory/pins/engenheiro.yaml` ✅ CORRIGIDO
- `factory/pins/sop.yaml` ✅ CORRIGIDO
- `factory/pins/gatekeeper.yaml` ✅ CORRIGIDO
- `Torre/pins/estado_maior_torre.yaml` ✅ CORRIGIDO
- `Torre/pins/engenheiro_torre.yaml` ✅ CORRIGIDO
- `core/orquestrador/engineer_cli.py` ❌ PENDENTE
- `core/orquestrador/sop_cli.py` ❌ PENDENTE

---

**Agente:** SOP (FÁBRICA 2.0)  
**Data/Hora:** 2025-11-02  
**Regras aplicadas:** ART-04, ART-09, Doutrina de Acesso a Ficheiros

---

**COMANDO A EXECUTAR:** "ENGENHEIRO IMPLEMENTAR VALIDAÇÃO DE FORMATO EM TODAS AS RESPOSTAS DE TEXTO DOS AGENTES E VERIFICAR OUTROS PINs DA TORRE"

