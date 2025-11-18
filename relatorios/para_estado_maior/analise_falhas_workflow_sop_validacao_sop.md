# Análise SOP — Falhas de Validação em Workflows GitHub Actions

**PIPELINE/FORA_PIPELINE:** PIPELINE

**OWNER: SOP — Próxima ação:** Análise de falhas concluída — problemas identificados e soluções recomendadas

**Data:** 2025-11-02  
**Agente:** SOP v3.0  
**Objetivo:** Analisar falhas de validação do SOP nos workflows GitHub Actions e identificar causas raiz

---

## 🔍 RESUMO EXECUTIVO

**Status:** ⚠️ **PROBLEMAS IDENTIFICADOS** — Workflows falhando na validação SOP

**Falhas Detectadas:** 4 workflows falharam no passo "Validate SOP"

**Causas Identificadas:**

1. ⚠️ **SBOM ausente** (`sbom_ok` violado)
2. ⚠️ **White Paper ausente** (`ART-02: White Paper (Estratégia) ausente`)
3. ⚠️ **Bandit ausente** (`bandit_ok` violado em alguns casos)

**Impacto:** Workflows bloqueados no gate G2

---

## 📊 ANÁLISE DAS FALHAS

### Workflows Afetados

1. ✅ **`security` job** — **PASSOU** (Gitleaks funcionou corretamente)
2. ❌ **`validate (20.x, 3.9)`** — **FALHOU**
3. ❌ **`ordem-checks`** — **FALHOU**
4. ❌ **`build`** — **FALHOU**
5. ❌ **`validate (20.x, 3.11)`** — **FALHOU**

### Padrão de Falhas Identificado

**Todos os workflows falharam no mesmo passo:**

```
X SOP BLOQUEADO para gate G2
Regras violadas: sbom_ok, [bandit_ok], ART-02: White Paper (Estratégia) ausente
▲ ART-02 (Tríade de Fundamentação) violado
```

---

## 🔍 ANÁLISE DETALHADA

### 1. ⚠️ SBOM Ausente (`sbom_ok` violado)

**Problema:**

- O SOP requer `relatorios/sbom.json` para validação do gate G2
- O arquivo não está sendo gerado ou não existe no momento da validação

**Evidência:**

- Todos os workflows reportam `sbom_ok` como regra violada
- O SOP bloqueia no gate G2 quando SBOM está ausente

**Causa Provável:**

1. SBOM não está sendo gerado no workflow antes da validação SOP
2. O caminho do SBOM não corresponde ao esperado pelo validator
3. A geração do SBOM falhou silenciosamente

**Recomendação:**

- Verificar se existe step de geração de SBOM no workflow
- Garantir que SBOM é gerado ANTES do passo "Validate SOP"
- Adicionar step de geração de SBOM se não existir

---

### 2. ⚠️ White Paper Ausente (`ART-02` violado)

**Problema:**

- ART-02 (Tríade de Fundamentação) requer White Paper (Estratégia)
- O SOP não encontra o White Paper e bloqueia o gate G2

**Evidência:**

- Todos os workflows reportam `ART-02: White Paper (Estratégia) ausente`
- O SOP bloqueia quando a Tríade de Fundamentação está incompleta

**Causa Provável:**

1. White Paper não existe no repositório
2. O caminho do White Paper não corresponde ao esperado pelo validator
3. O White Paper existe mas não está no formato esperado

**Recomendação:**

- Verificar se White Paper existe conforme ART-02
- Garantir que White Paper está no caminho esperado
- Se for Torre (não FÁBRICA), verificar se aplicam regras diferentes

---

### 3. ⚠️ Bandit Ausente (`bandit_ok` violado em alguns casos)

**Problema:**

- Alguns workflows também reportam `bandit_ok` como violado
- O SOP requer relatório do Bandit para gate G2

**Evidência:**

- Workflows `build` e `ordem-checks` reportam `bandit_ok` violado
- Workflows `validate` apenas reportam `sbom_ok`

**Causa Provável:**

- Bandit não está sendo executado ou relatório não está sendo gerado
- Diferença na configuração entre workflows

---

## 🔍 ANÁLISE DO CONTEXTO

### Diferença entre FÁBRICA e Torre

**Observação Crítica:**

- As imagens mostram workflows do repositório **"WilsonArim/Torre"**
- O SOP está validando conforme regras da **FÁBRICA**
- A Torre pode ter requisitos diferentes ou dispensar certos artefactos

**Questão Crítica:**

- O SOP deve aplicar regras diferentes para Torre vs FÁBRICA?
- Ou a Torre também deve seguir ART-02 e ter SBOM?

---

## ⚖️ CONFORMIDADE CONSTITUCIONAL

### ART-02 (Tríade de Fundamentação)

⚠️ **VIOLADO**

- White Paper (Estratégia) ausente
- Gate G2 bloqueado conforme regra constitucional

### ART-04 (Verificabilidade)

⚠️ **NÃO CONFORME**

- Workflows falham sem executar verificações completas
- Falta de artefactos impede verificação adequada

### ART-07 (Transparência)

✅ **CONFORME**

- Erros são reportados claramente
- Artefactos são citados para diagnóstico

### ART-09 (Evidência)

⚠️ **NÃO CONFORME**

- Falta de SBOM impede evidências completas
- Workflows não podem avançar sem artefactos obrigatórios

---

## 🔧 RECOMENDAÇÕES CRÍTICAS

### Prioridade ALTA

#### 1. Gerar SBOM Antes da Validação SOP

**Ação Imediata:**

- Adicionar step de geração de SBOM em todos os workflows ANTES de "Validate SOP"
- Garantir que `relatorios/sbom.json` existe antes da validação

**Exemplo de Step:**

```yaml
- name: Generate SBOM
  run: |
    # Comando para gerar SBOM (ex: cyclonedx-bom, syft, etc.)
    # Garantir que gera em relatorios/sbom.json
```

#### 2. Verificar White Paper Conforme ART-02

**Ação Imediata:**

- Verificar se Torre precisa de White Paper conforme ART-02
- Se sim, criar/verificar White Paper
- Se não, ajustar validação SOP para Torre

#### 3. Garantir Bandit Executado (se aplicável)

**Ação Imediata:**

- Adicionar step de execução do Bandit
- Garantir que relatório é gerado antes da validação SOP

---

## ✅ CONCLUSÃO

**Status Geral:** ⚠️ **PROBLEMAS IDENTIFICADOS** — Workflows falhando na validação SOP

**Causas Raiz Identificadas:**

1. ⚠️ SBOM ausente — requer geração antes da validação
2. ⚠️ White Paper ausente — requer verificação ART-02
3. ⚠️ Bandit ausente (alguns casos) — requer execução antes da validação

**Impacto:**

- Workflows bloqueados no gate G2
- CI/CD não pode avançar
- Conformidade constitucional violada

**Recomendações Críticas:**

1. ⏭️ Engenheiro adicionar geração de SBOM nos workflows ANTES de "Validate SOP"
2. ⏭️ Estado-Maior decidir se Torre precisa de White Paper conforme ART-02
3. ⏭️ Engenheiro garantir execução do Bandit onde necessário

**Próximos Passos:**

1. ⏭️ Aplicar correções nos workflows
2. ⏭️ Validar que SBOM é gerado corretamente
3. ⏭️ Resolver questão do White Paper (Torre vs FÁBRICA)
4. ⏭️ Re-executar workflows para confirmação

---

**Artefactos Citados:**

- Workflows GitHub Actions (falhando)
- `relatorios/sop_status.json` (status atual)
- `relatorios/relatorio_sop.md` (detalhes de validação)
- `core/scripts/validator.py` (validador SOP)

---

**Agente:** SOP (FÁBRICA 2.0)  
**Data/Hora:** 2025-11-02  
**Regras aplicadas:** ART-02, ART-04, ART-07, ART-09

---

**COMANDO A EXECUTAR:** "ENGENHEIRO ADICIONAR GERAÇÃO DE SBOM NOS WORKFLOWS ANTES DE 'VALIDATE SOP'. ESTADO-MAIOR DECIDIR SE TORRE PRECISA DE WHITE PAPER CONFORME ART-02. ENGENHEIRO GARANTIR EXECUÇÃO DO BANDIT ONDE NECESSÁRIO. SOP VALIDAR CORREÇÕES APLICADAS."
