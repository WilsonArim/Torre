# Parecer SOP — Gatekeeper: Acumulação de Funções Adicionais

**PIPELINE/FORA_PIPELINE:** FORA_PIPELINE

**OWNER: SOP — Próxima ação:** Parecer emitido — análise de conformidade concluída

**Data:** 2025-11-02  
**Agente:** SOP v3.0  
**Objetivo:** Analisar se o Gatekeeper pode acumular funções adicionais propostas pelo Estado-Maior

---

## 🔍 RESUMO EXECUTIVO

**Status:** ⚠️ **ANÁLISE COMPLETA** — Algumas funções compatíveis, outras requerem ajustes

**Conformidade Constitucional:** ⚠️ **PARCIALMENTE CONFORME** — Requer ajustes na doutrina de acesso

**Recomendação:** ✅ **APROVAR COM AJUSTES** — Implementar funções compatíveis, ajustar doutrina para outras

---

## 📊 ANÁLISE DAS FUNÇÕES PROPOSTAS

### 1. ✅ Preflight Local (Pre-Commit) — COMPATÍVEL

**Função Proposta:**

- Valida workflows YAML
- Verifica actions deprecadas
- Valida permissões do GITHUB_TOKEN
- Verifica existência de scripts chamados
- Verifica permissões de execução (+x) em .sh

**Análise:**

- ✅ **Compatível com papel atual do Gatekeeper**
- ✅ **Leitura apenas** — não viola doutrina de acesso
- ✅ **Validação técnica** — alinhado com responsabilidades
- ✅ **Pode executar antes de commit** — não requer modificação de código

**Conformidade:**

- ✅ ART-04: Verificável — validações rastreáveis
- ✅ ART-07: Transparente — validações reportadas
- ✅ ART-09: Baseado em evidências — valida arquivos existentes
- ✅ Doutrina de acesso: Conforme — apenas leitura

**Status:** ✅ **APROVADO**

---

### 2. ✅ Guard no PR/CI (GitHub) — COMPATÍVEL

**Função Proposta:**

- Bloqueia merge se houver policies violadas
- Mais exigente que o GitHub

**Análise:**

- ✅ **Compatível com papel atual do Gatekeeper**
- ✅ **Validação e bloqueio** — já é responsabilidade do Gatekeeper
- ✅ **Não modifica código** — apenas valida e bloqueia
- ✅ **Integração com CI** — já existe (`gatekeeper_run`)

**Conformidade:**

- ✅ ART-04: Verificável — bloqueios rastreáveis
- ✅ ART-07: Transparente — pareceres gerados
- ✅ ART-09: Baseado em evidências — valida artefactos
- ✅ Doutrina de acesso: Conforme — apenas leitura e relatórios

**Status:** ✅ **APROVADO**

---

### 3. ⚠️ Vercel Guard (Pré-Deploy) — REQUER AJUSTE

**Função Proposta:**

- Smoke local: `vercel pull` + `vercel build` (dry-run) + validação de `vercel.json`

**Análise:**

- ⚠️ **Compatível com papel, mas requer execução de comandos externos**
- ⚠️ **Executa `vercel pull` e `vercel build`** — comandos externos
- ✅ **Dry-run** — não modifica código
- ✅ **Validação técnica** — alinhado com responsabilidades

**Conformidade:**

- ✅ ART-04: Verificável — validações rastreáveis
- ✅ ART-07: Transparente — resultados reportados
- ✅ ART-09: Baseado em evidências — valida configurações
- ⚠️ **Doutrina de acesso:** Requer ajuste — execução de comandos externos não está explicitamente permitida/proibida

**Recomendação:**

- ✅ **APROVAR** — Execução de comandos externos para validação (dry-run) é aceitável
- ⚠️ **AJUSTE:** Clarificar na doutrina que Gatekeeper pode executar comandos externos para validação (sem modificar código)

**Status:** ⚠️ **APROVADO COM AJUSTE NA DOUTRINA**

---

### 4. ✅ Dependency Radar (Agendado) — COMPATÍVEL

**Função Proposta:**

- Sinaliza actions/pacotes desatualizados ou CVEs
- Abre Issue/PR draft

**Análise:**

- ✅ **Compatível com papel atual do Gatekeeper**
- ✅ **Leitura e análise** — não modifica código diretamente
- ⚠️ **Abre Issue/PR draft** — criação de arquivos (Issue/PR são arquivos no GitHub)
- ✅ **Sinalização** — alinhado com responsabilidades de guardião

**Conformidade:**

- ✅ ART-04: Verificável — sinalizações rastreáveis
- ✅ ART-07: Transparente — issues/PRs documentados
- ✅ ART-09: Baseado em evidências — analisa dependências
- ⚠️ **Doutrina de acesso:** Requer verificação — criação de Issues/PRs pode ser considerado "escrita" de relatórios (já permitido)

**Recomendação:**

- ✅ **APROVAR** — Issues/PRs são relatórios estruturados, já permitidos pela doutrina
- ✅ **CONFIRMAR:** Issues/PRs são considerados "relatórios" conforme doutrina

**Status:** ✅ **APROVADO**

---

### 5. ✅ Post-Mortem (Falha) — COMPATÍVEL

**Função Proposta:**

- Quando algum workflow falhar, gera causa-raiz e patch sugerido

**Análise:**

- ✅ **Compatível com papel atual do Gatekeeper**
- ✅ **Análise e parecer** — já é responsabilidade do Gatekeeper
- ✅ **Gera relatório** — já permitido pela doutrina
- ✅ **Sugere patch** — pode ser em formato de relatório (Markdown)

**Conformidade:**

- ✅ ART-04: Verificável — análises rastreáveis
- ✅ ART-07: Transparente — relatórios gerados
- ✅ ART-09: Baseado em evidências — analisa logs/artefactos
- ✅ Doutrina de acesso: Conforme — gera relatórios Markdown (permitido)

**Status:** ✅ **APROVADO**

---

### 6. ⚠️ Auto-Fix com PIN (Opcional) — REQUER AJUSTE CRÍTICO

**Função Proposta:**

- Só aplica correções quando comentas no PR: `/gatekeeper apply <PIN>`

**Análise:**

- ⚠️ **CRÍTICO:** Requer modificação de código-fonte
- ⚠️ **Violação potencial da doutrina de acesso:**
  - Gatekeeper pode apenas escrever relatórios Markdown
  - Modificar código-fonte (.py, .js, .yaml, etc.) está **PROIBIDO**
- ⚠️ **Auto-fix aplica mudanças** — modifica arquivos
- ✅ **Requer aprovação explícita** (`/gatekeeper apply <PIN>`) — bom controle

**Conformidade:**

- ✅ ART-04: Verificável — correções rastreáveis (com PIN)
- ✅ ART-07: Transparente — correções documentadas
- ✅ ART-09: Baseado em evidências — correções baseadas em análise
- ❌ **Doutrina de acesso:** **NÃO CONFORME** — Gatekeeper não pode modificar código-fonte

**Recomendação CRÍTICA:**

- ❌ **NÃO APROVAR** — Violaria doutrina de acesso a ficheiros
- ✅ **ALTERNATIVA 1:** Gatekeeper gera patch em formato diff (Markdown/relatório), Engenheiro aplica
- ✅ **ALTERNATIVA 2:** Ajustar doutrina para permitir auto-fix com PIN explícito (requer aprovação do Estado-Maior)
- ✅ **ALTERNATIVA 3:** Gatekeeper cria ordem para Engenheiro aplicar correção

**Status:** ❌ **NÃO APROVADO** (requer ajuste na doutrina ou alternativa)

---

## ⚖️ ANÁLISE DE CONFORMIDADE CONSTITUCIONAL

### ART-01 (Integridade)

✅ **CONFORME**

- Gatekeeper mantém papel de guardião ético
- Funções adicionais não comprometem integridade

### ART-02 (Tríade de Fundamentação)

✅ **CONFORME**

- Funções não afetam Tríade
- Apenas validações e guardas

### ART-04 (Verificabilidade)

✅ **CONFORME**

- Todas as funções são rastreáveis
- Pareceres e relatórios gerados

### ART-07 (Transparência)

✅ **CONFORME**

- Processos transparentes
- Relatórios gerados

### ART-09 (Evidência)

✅ **CONFORME**

- Baseado em artefactos
- Evidências citadas

---

## 📋 ANÁLISE DA DOUTRINA DE ACESSO

### Doutrina Atual para Gatekeeper

**Permitido:**

- ✅ Ler qualquer ficheiro
- ✅ Escrever relatórios Markdown
- ✅ Escrever em `relatorios/para_estado_maior/`

**Proibido:**

- ❌ Modificar código-fonte (.py, .js, .ts, .yaml, etc.)
- ❌ Modificar configurações em `core/` ou `pipeline/`

### Impacto das Funções Propostas

| Função           | Acesso Necessário           | Conforme Doutrina?               |
| ---------------- | --------------------------- | -------------------------------- |
| Preflight Local  | Leitura apenas              | ✅ SIM                           |
| Guard no PR/CI   | Leitura + Relatórios        | ✅ SIM                           |
| Vercel Guard     | Leitura + Comandos externos | ⚠️ Requer clarificação           |
| Dependency Radar | Leitura + Issues/PRs        | ✅ SIM (Issues/PRs = relatórios) |
| Post-Mortem      | Leitura + Relatórios        | ✅ SIM                           |
| Auto-Fix         | **Modificação de código**   | ❌ **NÃO**                       |

---

## ✅ RECOMENDAÇÕES

### Funções Aprovadas (5/6)

1. ✅ **Preflight Local (Pre-Commit)** — APROVADO
2. ✅ **Guard no PR/CI (GitHub)** — APROVADO
3. ⚠️ **Vercel Guard (Pré-Deploy)** — APROVADO COM AJUSTE (clarificar execução de comandos externos)
4. ✅ **Dependency Radar (Agendado)** — APROVADO
5. ✅ **Post-Mortem (Falha)** — APROVADO

### Função Não Aprovada (1/6)

6. ❌ **Auto-Fix com PIN (Opcional)** — **NÃO APROVADO**

**Motivo:** Violaria doutrina de acesso a ficheiros (Gatekeeper não pode modificar código-fonte)

**Alternativas Propostas:**

- **Alternativa 1:** Gatekeeper gera patch em formato diff (Markdown), Engenheiro aplica
- **Alternativa 2:** Ajustar doutrina para permitir auto-fix com PIN explícito (requer aprovação do Estado-Maior)
- **Alternativa 3:** Gatekeeper cria ordem para Engenheiro aplicar correção

---

## 🔧 AJUSTES NECESSÁRIOS

### 1. Clarificar Doutrina de Acesso

**Ajuste Necessário:**

- Clarificar que Gatekeeper pode executar comandos externos para validação (dry-run)
- Confirmar que Issues/PRs são considerados "relatórios" conforme doutrina

**Localização:** `core/sop/doutrina.yaml`

### 2. Auto-Fix: Decisão do Estado-Maior

**Opções:**

1. **Manter proibição** — Gatekeeper não pode modificar código (recomendado)
2. **Ajustar doutrina** — Permitir auto-fix com PIN explícito (requer aprovação)
3. **Usar alternativa** — Gatekeeper gera patch, Engenheiro aplica

---

## ✅ CONCLUSÃO

**Status Geral:** ⚠️ **5/6 FUNÇÕES APROVADAS** — 1 função requer ajuste na doutrina ou alternativa

**Funções Aprovadas:**

- ✅ Preflight Local (Pre-Commit)
- ✅ Guard no PR/CI (GitHub)
- ⚠️ Vercel Guard (Pré-Deploy) — requer clarificação na doutrina
- ✅ Dependency Radar (Agendado)
- ✅ Post-Mortem (Falha)

**Função Não Aprovada:**

- ❌ Auto-Fix com PIN — viola doutrina de acesso (requer ajuste ou alternativa)

**Conformidade Constitucional:** ✅ **CONFORME** (após ajustes)

**Recomendação Final:**

- ✅ **APROVAR** 5 funções compatíveis
- ⚠️ **DECIDIR** sobre Auto-Fix (ajustar doutrina ou usar alternativa)
- ⚠️ **CLARIFICAR** doutrina para execução de comandos externos (Vercel Guard)

---

**Artefactos Citados:**

- `factory/pins/gatekeeper.yaml` (PIN atual do Gatekeeper)
- `core/sop/doutrina.yaml` (doutrina de acesso a ficheiros)
- `core/orquestrador/gatekeeper_cli.py` (implementação atual)

---

**Agente:** SOP (FÁBRICA 2.0)  
**Data/Hora:** 2025-11-02  
**Regras aplicadas:** ART-01, ART-02, ART-04, ART-07, ART-09, Doutrina de Acesso

---

**COMANDO A EXECUTAR:** "ESTADO-MAIOR DECIDIR SOBRE AUTO-FIX (AJUSTAR DOUTRINA OU USAR ALTERNATIVA). ENGENHEIRO IMPLEMENTAR 5 FUNÇÕES APROVADAS. SOP VALIDAR AJUSTES NA DOUTRINA APÓS DECISÃO DO ESTADO-MAIOR."
