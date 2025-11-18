# Decisão do Estado-Maior — Funções Adicionais do Gatekeeper

**Data:** 2025-11-02T22:30:00Z  
**Autor:** Estado-Maior da FÁBRICA  
**Referência:** Parecer SOP em `relatorios/para_estado_maior/parecer_gatekeeper_funcoes_adicionais_sop.md`

---

## Resumo Executivo

**Status:** Decisão final emitida — 5 funções aprovadas, 1 função rejeitada (alternativa aprovada)

**Conformidade constitucional:** Conforme (após ajustes na doutrina)

**Recomendação:** Implementar 5 funções aprovadas + alternativa para Auto-Fix

---

## Decisões do Estado-Maior

### Funções Aprovadas (5/6)

#### 1. ✅ Preflight Local (Pre-Commit) — APROVADO

- **Função:** Valida workflows YAML, actions deprecadas, permissões GITHUB_TOKEN, scripts chamados, permissões de execução
- **Justificativa:** Compatível com papel atual do Gatekeeper, apenas leitura, validação técnica
- **Conformidade:** ART-04, ART-07, ART-09, Doutrina
- **Status:** APROVADO PARA IMPLEMENTAÇÃO

#### 2. ✅ Guard no PR/CI (GitHub) — APROVADO

- **Função:** Bloqueia merge se houver policies violadas, mais exigente que GitHub
- **Justificativa:** Compatível com papel atual, validação e bloqueio já são responsabilidades do Gatekeeper
- **Conformidade:** ART-04, ART-07, ART-09, Doutrina
- **Status:** APROVADO PARA IMPLEMENTAÇÃO

#### 3. ✅ Vercel Guard (Pré-Deploy) — APROVADO COM AJUSTE

- **Função:** Smoke local: `vercel pull` + `vercel build` (dry-run) + validação de `vercel.json`
- **Justificativa:** Compatível, dry-run não modifica código, validação técnica alinhada
- **Conformidade:** ART-04, ART-07, ART-09: Conforme | Doutrina: Requer clarificação
- **Ajuste necessário:** Clarificar na doutrina que Gatekeeper pode executar comandos externos para validação (dry-run, sem modificar código)
- **Status:** APROVADO PARA IMPLEMENTAÇÃO (após ajuste na doutrina)

#### 4. ✅ Dependency Radar (Agendado) — APROVADO

- **Função:** Sinaliza actions/pacotes desatualizados ou CVEs, abre Issue/PR draft
- **Justificativa:** Compatível com papel atual, leitura e análise, Issues/PRs são relatórios estruturados
- **Conformidade:** ART-04, ART-07, ART-09, Doutrina
- **Status:** APROVADO PARA IMPLEMENTAÇÃO

#### 5. ✅ Post-Mortem (Falha) — APROVADO

- **Função:** Quando workflow falhar, gera causa-raiz e patch sugerido
- **Justificativa:** Compatível com papel atual, análise e parecer já são responsabilidades, gera relatório (permitido)
- **Conformidade:** ART-04, ART-07, ART-09, Doutrina
- **Status:** APROVADO PARA IMPLEMENTAÇÃO

---

### Função Rejeitada (1/6) — Alternativa Aprovada

#### 6. ❌ Auto-Fix com PIN — REJEITADO (Alternativa Aprovada)

**Motivo da Rejeição:**

- **Violação da Doutrina:** Gatekeeper não pode modificar código-fonte (`.py`, `.js`, `.yaml`, etc.)
- **ART-03 (Consciência Técnica):** Separação de responsabilidades — Gatekeeper valida/audita, Engenheiro executa
- **Doutrina imutável:** `core/sop/doutrina.yaml` proíbe explicitamente modificação de código pelo Gatekeeper

**Alternativa Aprovada:**

- **Gatekeeper gera patch/ordem, Engenheiro aplica:**
  1. Gatekeeper detecta problema e gera patch em formato diff (Markdown/relatório)
  2. Gatekeeper cria ordem em `ordem/ordens/engineer.in.yaml` com:
     - `objective`: "Aplicar correção sugerida pelo Gatekeeper"
     - `steps`: Patch detalhado em formato aplicável
     - `context_refs`: Relatório do Gatekeeper com análise
  3. Engenheiro recebe ordem, aplica correção, reporta resultado
  4. Gatekeeper valida correção aplicada

**Vantagens da Alternativa:**

- ✅ Mantém doutrina intacta
- ✅ Preserva separação de responsabilidades (ART-03)
- ✅ Mantém rastreabilidade completa (ART-04, ART-09)
- ✅ Engenheiro mantém controle sobre modificações de código
- ✅ Gatekeeper mantém papel de validador/auditor

**Status:** REJEITADO (Auto-Fix direto) | APROVADO (Alternativa: Gatekeeper → Ordem → Engenheiro)

---

## Ajustes Necessários na Doutrina

### 1. Clarificar Execução de Comandos Externos para Validação

**Localização:** `core/sop/doutrina.yaml` (secção `gatekeeper`)

**Ajuste:**

```yaml
gatekeeper:
  ler: ["*"]
  escrever:
    - "relatorios/**/*.md"
    - "relatorios/para_estado_maior/**"
  executar_comandos_externos:
    permitido: true
    condicoes:
      - "Apenas para validação (dry-run, smoke tests)"
      - "NUNCA modificar código-fonte ou configurações"
      - "Exemplos permitidos: vercel build (dry-run), npm audit (read-only), git diff (read-only)"
      - "Exemplos proibidos: git commit, npm install, make build (modifica artefactos)"
    explicacao: >
      O Gatekeeper pode executar comandos externos APENAS para validação e análise.
      Qualquer comando que modifique código-fonte, configurações ou artefactos é proibido.
      Comandos de validação (dry-run, read-only) são permitidos.
```

**Justificativa:** Vercel Guard requer execução de comandos externos para validação (dry-run), mas não modifica código. Esta clarificação permite validações técnicas sem violar a doutrina.

---

## Ordem de Implementação

### Fase 1: Ajustar Doutrina

- **Agente:** SOP
- **Tarefa:** Clarificar execução de comandos externos para validação na doutrina
- **Artefacto:** `core/sop/doutrina.yaml` atualizado

### Fase 2: Implementar Funções Aprovadas

- **Agente:** Engenheiro
- **Tarefa:** Implementar as 5 funções aprovadas:
  1. Preflight Local (Pre-Commit)
  2. Guard no PR/CI (GitHub)
  3. Vercel Guard (Pré-Deploy)
  4. Dependency Radar (Agendado)
  5. Post-Mortem (Falha)
- **Artefactos:** Scripts/tools em `tools/gatekeeper/` ou `core/orquestrador/gatekeeper_*.py`

### Fase 3: Implementar Alternativa para Auto-Fix

- **Agente:** Engenheiro
- **Tarefa:** Implementar fluxo Gatekeeper → Ordem → Engenheiro para correções automáticas
- **Artefactos:**
  - Função em `core/orquestrador/gatekeeper_cli.py` para gerar ordem com patch
  - Template de ordem para correções sugeridas

---

## Conformidade Constitucional

**ART-01 (Integridade):** ✅ Conforme

- Gatekeeper mantém papel de guardião ético
- Funções adicionais não comprometem integridade

**ART-02 (Tríade de Fundamentação):** ✅ Conforme

- Funções não afetam Tríade
- Apenas validações e guardas

**ART-03 (Consciência Técnica):** ✅ Conforme

- Separação de responsabilidades mantida
- Gatekeeper valida, Engenheiro executa (alternativa Auto-Fix)

**ART-04 (Verificabilidade):** ✅ Conforme

- Todas as funções são rastreáveis
- Pareceres e relatórios gerados

**ART-07 (Transparência):** ✅ Conforme

- Processos transparentes
- Relatórios gerados

**ART-09 (Evidência):** ✅ Conforme

- Baseado em artefactos
- Evidências citadas

**ART-10 (Continuidade):** ✅ Conforme

- Funções garantem continuidade e resiliência
- Post-Mortem e Dependency Radar previnem falhas futuras

---

## Conclusão

**Status Final:** 5 funções aprovadas para implementação imediata, 1 função rejeitada com alternativa aprovada

**Próximos Passos:**

1. SOP ajustar doutrina (execução de comandos externos para validação)
2. Engenheiro implementar 5 funções aprovadas
3. Engenheiro implementar alternativa para Auto-Fix (Gatekeeper → Ordem → Engenheiro)

**Rastreabilidade:**

- Parecer SOP: `relatorios/para_estado_maior/parecer_gatekeeper_funcoes_adicionais_sop.md`
- Decisão EM: `relatorios/para_estado_maior/decisao_estado_maior_funcoes_gatekeeper.md`
- Ordem SOP: `ordem/ordens/sop.in.yaml` (ajustar doutrina)
- Ordem Engenheiro: `ordem/ordens/engineer.in.yaml` (implementar funções)

---

**Assinatura:** Estado-Maior da FÁBRICA  
**Data:** 2025-11-02T22:30:00Z
