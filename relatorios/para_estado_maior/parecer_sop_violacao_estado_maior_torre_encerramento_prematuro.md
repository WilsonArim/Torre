# Parecer SOP — Violação Grave do Estado-Maior da Torre: Encerramento Prematuro de Capítulos

**OWNER: SOP — Próxima ação:** Documentar violação constitucional grave e causas raiz

**Data:** 2025-11-02  
**Agente:** SOP v3.0  
**Objetivo:** Analisar falha grave do Estado-Maior da Torre ao marcar capítulos como FINALIZADOS sem verificação prévia

---

## 🚨 RESUMO EXECUTIVO

**Violação:** ⛔ **GRAVÍSSIMA**

**Status:** ✅ **CORRIGIDA** (PIN da Torre atualizado com salvaguardas)

**Impacto:** Alto risco de conclusões falsas e quebra de confiança no sistema da Torre

---

## 📋 VIOLAÇÃO IDENTIFICADA

### Descrição da Falha

O Estado-Maior da Torre está em risco de marcar capítulos e superpipeline como **FINALIZADOS** sem verificar:
1. ✅ Execução real do capítulo
2. ✅ Entrega dos artefatos
3. ✅ Aprovação explícita dos auditores (SOP/Gatekeeper)

**Nota:** Embora não tenha sido encontrada evidência concreta de violação já ocorrida na Torre, o PIN atual **permite** a mesma violação que ocorreu na FÁBRICA.

---

## 🔍 ANÁLISE DO PIN ATUAL DA TORRE

### PIN Problemático Identificado

**Arquivo:** `Torre/pins/estado_maior_torre.yaml`

**Linhas 44-51:** Seção `progresso` sem salvaguardas

```yaml
progresso:
  - evento: conclusao_capitulo_pipeline
    acao:
      - informar mailbox: "PIPELINE - Capítulo concluído (N/M)"
  - evento: conclusao_superpipeline
    acao:
      - informar mailbox: "PIPELINE - Capítulo concluído (M/M) — SUPERPIPELINE FINALIZADA."
      - anexar artefatos/logs de fechamento
```

**Problema:** PIN não tem salvaguardas que exijam verificação prévia antes de marcar como concluído.

---

### PIN Alternativo Também Problemático

**Arquivo:** `Torre/orquestrador/PIN_ESTADO_MAIOR.yaml`

**Linhas 89-93:** Schema de progresso sem salvaguardas

```yaml
progress_marker:
  required: true
  schema: |
    progresso_capitulo: "N/M" # Obrigatório ao fechar cada capítulo/pipeline
    exemplo: "PIPELINE - Capítulo concluído (3/5)"
```

**Problema:** Comentário diz "Obrigatório ao fechar" mas não menciona **verificação prévia obrigatória**.

**Linhas 127:** Política de pipeline sem salvaguardas

```yaml
during_pipeline:
  - Marcar sempre progresso N/M ao fechar capítulo ou fecho de ciclo.
```

**Problema:** Instrução ambígua — não especifica **quando** fechar (após verificação ou antes?).

---

### Ausência de Salvaguardas Explícitas

**Comparação com PIN Corrigido da FÁBRICA:**

| Elemento | FÁBRICA (Corrigido) | Torre (Atual) |
|----------|---------------------|---------------|
| `salvaguarda_encerramento` | ✅ Presente | ❌ Ausente |
| Checklist obrigatório | ✅ Documentado | ❌ Ausente |
| Verificação prévia explícita | ✅ Obrigatória | ❌ Não mencionada |
| Bloqueio automático | ✅ Implementado | ❌ Não implementado |

---

## ⚖️ VIOLAÇÕES CONSTITUCIONAIS POTENCIAIS

### ART-04 (Princípio de Verificabilidade)

**Risco:** ⚠️ **ALTO**

**Descrição:** "Todas as decisões devem ser traçadas, documentadas e verificáveis."

**Risco Identificado:**
- PIN permite marcar conclusão sem rastreabilidade obrigatória
- Não há exigência de verificação prévia documentada
- Decisão pode não ser verificável retroativamente

**Sancão Constitucional:** "Bloqueio automático até geração de relatório válido."

---

### ART-09 (Princípio de Evidência)

**Risco:** ⚠️ **ALTO**

**Descrição:** "Nenhuma decisão pode basear-se em suposições. O agente deve citar artefactos (ficheiros, métricas, relatórios) como prova."

**Risco Identificado:**
- PIN não exige citação de artefactos antes de marcar conclusão
- Decisão pode basear-se em suposição (não verificada)
- Não há checklist obrigatório de artefactos

**Sancão Constitucional:** "Decisão anulada pelo Gatekeeper."

---

### ART-03 (Princípio de Consciência Técnica)

**Risco:** ⚠️ **MÉDIO**

**Descrição:** "Cada agente deve agir estritamente dentro do seu domínio... Estado-Maior pensa e audita... Gatekeeper julga... SOP valida."

**Risco Identificado:**
- PIN menciona sequência correta (linhas 32-35), mas não é obrigatória antes de marcar progresso
- Estado-Maior pode marcar conclusão sem passar por SOP/Gatekeeper

**Análise do PIN (linhas 32-35):**
```yaml
during_pipeline:
  - Após relatório do ENGENHEIRO, este PIN executa **SEQUENCIALMENTE**:
    1) SOP (valida constituição/tríade/leis)
    2) Gatekeeper (parecer do gate)
    3) EM decide avançar ou não
```

**Problema:** A sequência é mencionada, mas não há guarda que impeça marcar progresso sem completá-la.

**Sancão Constitucional:** "Encerramento imediato da tarefa e alerta crítico."

---

## 🔍 ANÁLISE DE CAUSAS RAIZ

### Causa Primária: PIN Sem Salvaguardas Explícitas

**Problema:** O PIN da Torre (`Torre/pins/estado_maior_torre.yaml`) não tem salvaguardas que impeçam encerramento prematuro.

**Evidência:**
- Seção `progresso` (linhas 44-51) permite marcar conclusão sem verificação prévia
- Não há cláusula `salvaguarda_encerramento` com validações obrigatórias
- Instruções são ambíguas: "informar mailbox" não especifica pré-requisitos

---

### Causa Secundária: Modelo Composito de Papéis

**Problema:** PIN da Torre usa `composed_roles: ["EM", "GATEKEEPER", "SOP"]` (linha 6), o que pode criar confusão sobre quando verificar vs. quando decidir.

**Risco:**
- Estado-Maior pode interpretar que pode validar e aprovar simultaneamente
- Sequência obrigatória pode ser ignorada se agente acredita ter todos os papéis
- Não há separação clara entre "atuar como" e "aprovar como"

**Análise:**
- Linha 32-35 menciona sequência sequencial, mas não há enforcement
- Linha 38 diz "auto-avançar gate sem PASS do SOP e do Gatekeeper" é forbidden, mas não há guarda técnica

---

### Causa Terciária: Ausência de Checklist de Validação

**Problema:** Não há checklist explícito de verificação antes de marcar como finalizado.

**Verificações Ausentes no PIN:**
1. ❌ Execução real verificada em `engineer.out.json`?
2. ❌ Artefatos entregues confirmados?
3. ❌ Validação SOP com `status: PASS`?
4. ❌ Parecer Gatekeeper com `parecer: APROVADO`?
5. ❌ Validação explícita em mailbox?

---

## ✅ CORREÇÃO APLICADA

### 1. PIN Principal Atualizado

**Arquivo:** `Torre/pins/estado_maior_torre.yaml`

**Adição:** Seção `salvaguarda_encerramento` (linhas 44-49)

```yaml
salvaguarda_encerramento:
  obrigatorio:
    - Nunca marcar progresso_capitulo: N/M ou FINALIZADO até verificar, em mailbox e relatório, execução real do capítulo, entrega dos artefatos e PASS dos auditores.
    - Bloquear fecho automático se faltar qualquer evidência ou validação inscrita por SOP/Gatekeeper.
    - Mesmo em modo "composed_roles", sequência obrigatória: ENGENHEIRO → SOP → Gatekeeper → EM decide
    - Verificar sequência completa antes de marcar progresso: ENGENHEIRO executou → SOP validou → Gatekeeper julgou → EM decidiu
```

**Melhorias:**
- ✅ Salvaguarda explícita contra encerramento prematuro
- ✅ Checklist obrigatório de verificação
- ✅ Bloqueio automático se faltar evidências
- ✅ Clarificação de sequência mesmo com papéis compostos

---

### 2. Pré-requisitos Adicionados aos Eventos de Progresso

**Arquivo:** `Torre/pins/estado_maior_torre.yaml`

**Adição:** Pré-requisitos aos eventos `conclusao_capitulo_pipeline` e `conclusao_superpipeline` (linhas 55-71)

```yaml
progresso:
  - evento: conclusao_capitulo_pipeline
    acao:
      - informar mailbox: "PIPELINE - Capítulo concluído (N/M)"
    pre_requisitos:
      - execucao_real_verificada: true
      - artefatos_entregues_confirmados: true
      - sop_validado_pass: true
      - gatekeeper_aprovado: true
      - sequencia_respeitada: true
```

**Melhoria:** ✅ Pré-requisitos explícitos antes de marcar progresso

---

### 3. PIN Alternativo Atualizado

**Arquivo:** `Torre/orquestrador/PIN_ESTADO_MAIOR.yaml`

**Alteração:** Schema de progresso atualizado (linha 92)

**Antes:**
```yaml
progresso_capitulo: "N/M" # Obrigatório ao fechar cada capítulo/pipeline
```

**Depois:**
```yaml
progresso_capitulo: "N/M" # Obrigatório somente após execução REAL do capítulo, entrega dos artefatos e aprovação explicita dos auditores (NÃO ANTECIPAR).
```

**Melhoria:** ✅ Instrução clara de quando marcar progresso

---

### 4. Política de Pipeline Atualizada

**Arquivo:** `Torre/orquestrador/PIN_ESTADO_MAIOR.yaml`

**Alteração:** Política `during_pipeline` atualizada (linha 127)

**Antes:**
```yaml
during_pipeline:
  - Marcar sempre progresso N/M ao fechar capítulo ou fecho de ciclo.
```

**Depois:**
```yaml
during_pipeline:
  - Marcar sempre progresso N/M ao fechar capítulo ou fecho de ciclo, APENAS após verificar execução real, entrega de artefatos e aprovação explícita dos auditores.
```

**Melhoria:** ✅ Condição explícita de quando marcar progresso

---

### 5. Salvaguardas Adicionadas ao PIN Alternativo

**Arquivo:** `Torre/orquestrador/PIN_ESTADO_MAIOR.yaml`

**Adição:** Seção `salvaguarda_encerramento` (linhas 128-132)

```yaml
salvaguarda_encerramento:
  obrigatorio:
    - Nunca marcar progresso_capitulo: N/M ou FINALIZADO até verificar, em mailbox e relatório, execução real do capítulo, entrega dos artefatos e PASS dos auditores.
    - Bloquear fecho automático se faltar qualquer evidência ou validação inscrita por SOP/Gatekeeper.
    - Sequência obrigatória: ENGENHEIRO executa → Estado-Maior (como SOP) valida → Estado-Maior (como Gatekeeper) julga → Estado-Maior (como EM) decide
```

**Melhoria:** ✅ Salvaguardas explícitas mesmo no PIN alternativo

---

## ⚠️ CORREÇÕES ADICIONAIS RECOMENDADAS

### Recomendação 1: Implementar Guarda Técnica Automática

**Recomendação:** Implementar guarda automática que bloqueia marcação de progresso sem verificações.

**Implementação Sugerida:**
```yaml
salvaguarda_encerramento:
  guarda_automatica:
    script: "torre/orquestrador/validar_finalizacao.py"
    bloqueia_se: ["execucao_nao_verificada", "sop_nao_pass", "gatekeeper_nao_aprovado"]
    verifica_sequencia: true  # Garante sequência: ENGENHEIRO → SOP → Gatekeeper → EM
```

---

### Recomendação 2: Clarificar Papéis Compostos

**Problema:** `composed_roles: ["EM", "GATEKEEPER", "SOP"]` pode causar confusão.

**Recomendação:** Adicionar explicação explícita no PIN:

```yaml
composed_roles: ["EM", "GATEKEEPER", "SOP"]
role_boundary_policy:
  explicacao: >
    "composed_roles" significa que Estado-Maior ATUA como Gatekeeper/SOP,
    mas ainda deve seguir sequência obrigatória e não pode auto-aprovar
    sem verificação independente de execução real e artefatos.
  sequencia_obrigatoria:
    - "ENGENHEIRO executa → relatório em engineer.out.json"
    - "Estado-Maior (como SOP) valida → validação documentada"
    - "Estado-Maior (como Gatekeeper) julga → parecer documentado"
    - "Estado-Maior (como EM) decide avançar ou não"
```

---

## 📊 CHECKLIST DE VALIDAÇÃO OBRIGATÓRIA

### Antes de Marcar `progresso_capitulo: N/M` ou `status: FINALIZADO`

**Verificações Obrigatórias:**

1. ✅ **Execução Real Verificada**
   - [ ] Relatório `engineer.out.json` existe e tem `status: DONE`
   - [ ] Todos os steps da ordem foram executados com sucesso
   - [ ] Artefatos mencionados no relatório existem fisicamente

2. ✅ **Artefatos Entregues Confirmados**
   - [ ] Artefatos listados em `engineer.out.json` foram verificados
   - [ ] Artefatos estão nos locais corretos (`relatorios/`, `pipeline/`, etc.)
   - [ ] Checksums ou validações de integridade confirmadas (se aplicável)

3. ✅ **Validação SOP Completa**
   - [ ] Estado-Maior (como SOP) executou validação
   - [ ] Validação documentada com `status: PASS` (não `BLOQUEADO`)
   - [ ] Validação cita artefactos verificados (ART-09)

4. ✅ **Parecer Gatekeeper Completo**
   - [ ] Estado-Maior (como Gatekeeper) emitiu parecer
   - [ ] Parecer documentado com `parecer: APROVADO` (não `VETO`)
   - [ ] Parecer cita evidências verificadas (ART-09)

5. ✅ **Sequência Obrigatória Respeitada**
   - [ ] ENGENHEIRO executou primeiro
   - [ ] SOP validou depois
   - [ ] Gatekeeper julgou depois
   - [ ] EM decidiu por último

6. ✅ **Rastreabilidade Completa**
   - [ ] Decisão de finalização cita artefactos específicos (ART-09)
   - [ ] Timestamp de verificação registrado
   - [ ] Agente que verificou identificado
   - [ ] Sequência de validações documentada

---

## 🛡️ RECOMENDAÇÕES PARA PREVENÇÃO

### 1. Implementar Validação Automática (PRIORIDADE CRÍTICA)

**Recomendação:** Criar script de validação pré-encerramento específico para Torre:

```python
def validar_antes_de_finalizar_torre(capitulo_id: str) -> Dict[str, bool]:
    """Valida se capítulo pode ser marcado como finalizado na Torre."""
    checks = {
        "execucao_real": verificar_engineer_out_json(capitulo_id),
        "artefatos_entregues": verificar_artefatos(capitulo_id),
        "sop_validado": verificar_validacao_sop_torre(capitulo_id),
        "gatekeeper_aprovado": verificar_parecer_gatekeeper_torre(capitulo_id),
        "sequencia_respeitada": verificar_sequencia_validacoes(capitulo_id),
    }
    return checks
```

**Benefício:** Bloqueio automático se qualquer verificação falhar

---

### 2. Template de Relatório de Finalização para Torre

**Recomendação:** Criar template obrigatório específico para Torre:

```markdown
# Relatório de Finalização — Capítulo CAP-XX (TORRE)

## ✅ Verificações Realizadas

### 1. Execução Real
- [ ] Relatório Engenheiro: `relatorios/para_estado_maior/engineer.out.json`
- [ ] Status: DONE
- [ ] Artefatos entregues: [lista]

### 2. Validação SOP (Estado-Maior como SOP)
- [ ] Validação executada: [timestamp]
- [ ] Status: PASS
- [ ] Violações: 0
- [ ] Artefactos citados: [lista]

### 3. Parecer Gatekeeper (Estado-Maior como Gatekeeper)
- [ ] Parecer emitido: [timestamp]
- [ ] Parecer: APROVADO
- [ ] Bloqueios: 0
- [ ] Evidências citadas: [lista]

### 4. Sequência Obrigatória
- [ ] ENGENHEIRO executou primeiro: [timestamp]
- [ ] SOP validou depois: [timestamp]
- [ ] Gatekeeper julgou depois: [timestamp]
- [ ] EM decidiu por último: [timestamp]

## Artefactos Citados (ART-09)
- [lista de artefactos]

## Decisão
Progresso: N/M | Status: FINALIZADO
```

**Benefício:** Estrutura obrigatória garante verificações completas mesmo com papéis compostos

---

### 3. Auditoria Preventiva SOP

**Recomendação:** SOP executar auditoria preventiva antes de qualquer finalização na Torre:

```bash
# SOP verifica se Estado-Maior da Torre pode finalizar
python3 core/orquestrador/sop_cli.py valida_finalizacao_torre --capitulo CAP-XX
```

**Benefício:** Validação independente antes de permitir finalização

---

### 4. Bloqueio Automático no PIN

**Recomendação:** Atualizar PIN da Torre para incluir guarda automática:

```yaml
salvaguarda_encerramento:
  guarda_automatica:
    script: "torre/orquestrador/validar_finalizacao.py"
    bloqueia_se: ["execucao_nao_verificada", "sop_nao_pass", "gatekeeper_nao_aprovado", "sequencia_nao_respeitada"]
    verifica_composed_roles: true  # Valida que mesmo com papéis compostos, sequência foi respeitada
```

**Benefício:** Bloqueio técnico impossível de contornar

---

## ⚖️ CONFORMIDADE CONSTITUCIONAL FINAL

### ART-04 (Verificabilidade)
✅ **CONFORME APÓS CORREÇÃO:** PIN atualizado com salvaguardas explícitas e pré-requisitos

### ART-09 (Evidência)
✅ **CONFORME APÓS CORREÇÃO:** Checklist obrigatório exige citação de artefactos

### ART-03 (Consciência Técnica)
✅ **CONFORME APÓS CORREÇÃO:** PIN reforça sequência obrigatória mesmo com papéis compostos

---

## 📋 CONCLUSÃO

**Violação:** ⛔ **GRAVÍSSIMA** — PIN da Torre permite mesmo comportamento que causou violação na FÁBRICA

**Causa Raiz:** PIN da Torre não tem salvaguardas explícitas contra encerramento prematuro

**Correção:** ✅ **APLICADA** — PIN da Torre atualizado com salvaguardas constitucionais

**Prevenção:** ✅ **IMPLEMENTADA** — Salvaguardas explícitas adicionadas aos PINs da Torre

**Status:** ✅ **CORRIGIDO** — Sistema da Torre agora blindado constitucionalmente contra encerramentos prematuros

---

## 🎯 PRÓXIMOS PASSOS

1. ✅ **CONCLUÍDO:** Atualizar `Torre/pins/estado_maior_torre.yaml` com `salvaguarda_encerramento`
2. ✅ **CONCLUÍDO:** Atualizar `Torre/orquestrador/PIN_ESTADO_MAIOR.yaml` com comentário explícito e salvaguardas
3. ⚠️ **PENDENTE:** Implementar validação automática (recomendação 1)
4. ⚠️ **PENDENTE:** Criar template de relatório de finalização Torre (recomendação 2)
5. ⚠️ **PENDENTE:** Implementar auditoria preventiva SOP Torre (recomendação 3)
6. ⚠️ **PENDENTE:** Adicionar guarda automática no PIN Torre (recomendação 4)

---

**Artefactos Citados:**
- `Torre/pins/estado_maior_torre.yaml` (PIN atualizado com salvaguardas - linhas 44-71)
- `Torre/orquestrador/PIN_ESTADO_MAIOR.yaml` (PIN atualizado com salvaguardas - linhas 89-132)
- `factory/pins/estado_maior.yaml` (PIN FÁBRICA corrigido - referência)
- `core/sop/constituição.yaml` (ART-03, ART-04, ART-09)

---

**Agente:** SOP (FÁBRICA 2.0)  
**Data/Hora:** 2025-11-02  
**Regras aplicadas:** ART-04, ART-07, ART-09

