# Correção Crítica SOP — Formato Obrigatório de Interações

**PIPELINE/FORA_PIPELINE:** FORA_PIPELINE

**OWNER: SOP — Próxima ação:** Corrigir interpretação incorreta do formato obrigatório

**Data:** 2025-11-02  
**Agente:** SOP v3.0  
**Objetivo:** Corrigir interpretação incorreta: formato obrigatório aplica-se a TODAS as interações, não apenas relatórios

---

## 🚨 VIOLAÇÃO CRÍTICA IDENTIFICADA

**Problema:** Formato obrigatório foi implementado apenas para relatórios em markdown, mas deveria aplicar-se a **TODAS as interações** dos agentes.

**Severidade:** 🔴 **CRÍTICO** — Interpretação incorreta da doutrina

---

## ⚠️ INTERPRETAÇÃO INCORRETA ANTERIOR

### Implementação Anterior (INCORRETA)
- ❌ Formato obrigatório aplicado apenas a relatórios markdown salvos em ficheiros
- ❌ Validação apenas antes de salvar ficheiros markdown
- ❌ Não aplicado a respostas de texto dos agentes
- ❌ Não aplicado a comunicações dos agentes
- ❌ Não aplicado a agentes da Torre

---

## ✅ INTERPRETAÇÃO CORRETA DA DOUTRINA

### Formato Obrigatório Deve Aplicar-se a:

1. ✅ **Relatórios em markdown** (já implementado)
2. ✅ **Respostas de texto dos agentes** (NÃO implementado)
3. ✅ **Comunicações dos agentes** (NÃO implementado)
4. ✅ **Qualquer interação entre agente e Estado-Maior/usuário** (NÃO implementado)
5. ✅ **Agentes da Torre** (NÃO implementado)

### Formato Obrigatório:

**Início:**
```
**PIPELINE/FORA_PIPELINE:** PIPELINE ou FORA_PIPELINE
```

**Fim:**
```
**COMANDO A EXECUTAR:** "AGENTE AÇÃO (localização)"
```

---

## 🔴 VIOLAÇÕES IDENTIFICADAS

### 1. Doutrina Não Especifica Claramente

**Arquivo:** `core/sop/doutrina.yaml`

**Problema:** Seção `formato_relatorios` sugere que é apenas para relatórios, não para todas as interações.

**Correção:** Renomear para `formato_interacoes` e especificar que aplica-se a TODAS as interações.

---

### 2. PINs Não Especificam Formato Obrigatório de Interações

**Arquivos Afetados:**
- `factory/pins/estado_maior.yaml`
- `factory/pins/engenheiro.yaml`
- `factory/pins/sop.yaml`
- `factory/pins/gatekeeper.yaml`
- `Torre/pins/estado_maior_torre.yaml`
- `Torre/pins/engenheiro_torre.yaml`

**Problema:** PINs não especificam que TODAS as interações devem seguir formato obrigatório.

**Correção:** Adicionar seção `formato_interacoes` em todos os PINs.

---

### 3. Código Não Valida Formato em Respostas de Texto

**Problema:** Código apenas valida formato antes de salvar ficheiros markdown, não valida formato em respostas de texto dos agentes.

**Correção:** Implementar validação de formato em todas as respostas dos agentes.

---

### 4. Agentes da Torre Não Seguem Formato

**Problema:** PINs da Torre não especificam formato obrigatório de interações.

**Correção:** Adicionar formato obrigatório aos PINs da Torre.

---

## 🛡️ CORREÇÕES NECESSÁRIAS

### Prioridade CRÍTICA

#### 1. Atualizar Doutrina

**Arquivo:** `core/sop/doutrina.yaml`

**Ação:** Renomear `formato_relatorios` para `formato_interacoes` e especificar que aplica-se a TODAS as interações.

---

#### 2. Atualizar Todos os PINs

**Arquivos:**
- `factory/pins/estado_maior.yaml`
- `factory/pins/engenheiro.yaml`
- `factory/pins/sop.yaml`
- `factory/pins/gatekeeper.yaml`
- `Torre/pins/estado_maior_torre.yaml`
- `Torre/pins/engenheiro_torre.yaml`
- `Torre/orquestrador/PIN_ESTADO_MAIOR.yaml`
- `Torre/orquestrador/PIN_ENGENHEIRO.yaml`

**Ação:** Adicionar seção `formato_interacoes` especificando formato obrigatório para TODAS as interações.

---

#### 3. Implementar Validação em Código

**Arquivos:**
- `core/orquestrador/engineer_cli.py`
- `core/orquestrador/sop_cli.py`
- Código do Gatekeeper (quando existir)

**Ação:** Implementar validação de formato em todas as respostas de texto dos agentes.

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

---

## ⚖️ VIOLAÇÕES CONSTITUCIONAIS

### ART-04 (Verificabilidade)
❌ **VIOLAÇÃO:** Interações não seguem formato obrigatório, não são totalmente verificáveis.

### ART-09 (Evidência)
❌ **VIOLAÇÃO:** Interações não incluem comando a executar, não são totalmente rastreáveis.

---

## 📋 CONCLUSÃO

**Violação Crítica:** Formato obrigatório implementado apenas parcialmente (apenas relatórios markdown).

**Correção Necessária:** Implementar formato obrigatório para TODAS as interações de TODOS os agentes.

**Status:** 🔴 **BLOQUEADO** — Interpretação incorreta precisa ser corrigida antes de considerar sistema conformante.

---

**Artefactos Citados:**
- `core/sop/doutrina.yaml` (linhas 97-109) ⚠️
- `factory/pins/estado_maior.yaml` ⚠️
- `factory/pins/engenheiro.yaml` ⚠️
- `factory/pins/sop.yaml` ⚠️
- `factory/pins/gatekeeper.yaml` ⚠️
- `Torre/pins/estado_maior_torre.yaml` ⚠️
- `Torre/pins/engenheiro_torre.yaml` ⚠️

---

**Agente:** SOP (FÁBRICA 2.0)  
**Data/Hora:** 2025-11-02  
**Regras aplicadas:** ART-04, ART-09, Doutrina de Acesso a Ficheiros

---

**COMANDO A EXECUTAR:** "ENGENHEIRO CORRIGIR INTERPRETAÇÃO: Atualizar doutrina.yaml (renomear formato_relatorios para formato_interacoes), adicionar formato_interacoes a TODOS os PINs (FÁBRICA e Torre), e implementar validação de formato em TODAS as respostas de texto dos agentes"

