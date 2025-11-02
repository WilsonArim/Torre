**PIPELINE/FORA_PIPELINE:** FORA_PIPELINE

**OWNER: SOP — Próxima ação:** Identificar e corrigir critérios dúbios que permitem comportamentos incorretos

# Auditoria SOP — Critérios Dúbios em FÁBRICA e Torre

**Data:** 2025-11-02  
**Agente:** SOP v3.0  
**Objetivo:** Auditoria completa de PINs e políticas para identificar áreas de interpretação ambígua

---

## 🚨 RESUMO EXECUTIVO

**Critérios Dúbios Identificados:** 12 problemas graves

**Violações Constitucionais Potenciais:** ART-03, ART-04, ART-09

**Status:** ⚠️ **AÇÃO URGENTE NECESSÁRIA**

---

## 📋 PROBLEMAS IDENTIFICADOS

### 🔴 CRÍTICO — Encerramento Prematuro (RESOLVIDO)

**Status:** ✅ **CORRIGIDO** (já resolvido anteriormente)

**Problema:** Estado-Maior marcava capítulos como finalizados sem verificação prévia.

**Correção Aplicada:**
- ✅ `factory/pins/estado_maior.yaml` — salvaguardas adicionadas
- ✅ `Torre/pins/estado_maior_torre.yaml` — salvaguardas adicionadas

---

### 🔴 CRÍTICO — Engenheiro Torre: Progresso Sem Salvaguardas

**Arquivo:** `Torre/pins/engenheiro_torre.yaml`

**Linhas 29-36:** Seção `progresso` sem salvaguardas

```yaml
progresso:
  - evento: conclusao_capitulo_pipeline
    acao:
      - emitir no relatório/mailbox: "PIPELINE - Capítulo concluído (N/M)"
  - evento: conclusao_superpipeline
    acao:
      - emitir no relatório/mailbox: "PIPELINE - Capítulo concluído (M/M) — SUPERPIPELINE FINALIZADA."
      - anexar artefatos/logs finais e marcar status em engineer.out.json
```

**Problema:** Engenheiro Torre pode marcar progresso sem verificar se:
- Execução foi realmente concluída
- Artefatos foram entregues
- Validação foi realizada

**Risco:** Mesmo problema que ocorreu com Estado-Maior, mas no Engenheiro.

**Violação Constitucional:** ART-04 (Verificabilidade), ART-09 (Evidência)

**Recomendação:**
```yaml
progresso:
  - evento: conclusao_capitulo_pipeline
    acao:
      - emitir no relatório/mailbox: "PIPELINE - Capítulo concluído (N/M)"
    pre_requisitos:
      - execucao_completa: true
      - artefatos_entregues: true
      - ordem_status_done: true
      - relatorio_gerado: true
```

---

### 🔴 CRÍTICO — Engenheiro Torre v3: Progresso Sem Salvaguardas

**Arquivo:** `Torre/orquestrador/PIN_ENGENHEIRO.yaml`

**Linhas 44:** Política `during_pipeline` ambígua

```yaml
during_pipeline:
  - Sempre reportar progresso "N/M" ao concluir capítulo/entrega.
```

**Problema:** Não especifica **quando** concluir (após verificação ou antes?).

**Violação Constitucional:** ART-04 (Verificabilidade)

**Recomendação:**
```yaml
during_pipeline:
  - Sempre reportar progresso "N/M" ao concluir capítulo/entrega, APENAS após verificar execução completa, entrega de artefatos e geração de relatório válido.
```

---

### 🔴 CRÍTICO — Engenheiro FÁBRICA: Progresso Sem Salvaguardas

**Arquivo:** `factory/pins/engenheiro.yaml`

**Linhas 44-45:** Política `during_pipeline` ambígua

```yaml
during_pipeline:
  - Sempre reportar progresso "N/M" ao concluir capítulo/entrega.
```

**Problema:** Mesma ambiguidade — não especifica pré-requisitos de verificação.

**Violação Constitucional:** ART-04 (Verificabilidade)

**Recomendação:**
```yaml
during_pipeline:
  - Sempre reportar progresso "N/M" ao concluir capítulo/entrega, APENAS após verificar execução completa, entrega de artefatos e geração de relatório válido.
salvaguarda_progresso:
  obrigatorio:
    - Nunca marcar progresso_capitulo: N/M até verificar execução completa da ordem, entrega de artefatos e geração de relatório válido.
    - Bloquear marcação de progresso se ordem não estiver em status DONE ou se relatório não foi gerado.
```

---

### 🟡 ALTO — Gatekeeper: Parecer Sem Validação Prévia Explícita

**Arquivo:** `factory/pins/gatekeeper.yaml`

**Linhas 45-46:** Política `during_pipeline` ambígua

```yaml
during_pipeline:
  - Após validação, sempre marcar progresso "N/M" em pareceres.
```

**Problema:** Não especifica:
- O que constitui "validação" válida
- Se deve aguardar relatório SOP antes de parecer
- Quais verificações são obrigatórias

**Violação Constitucional:** ART-03 (Consciência Técnica), ART-09 (Evidência)

**Recomendação:**
```yaml
during_pipeline:
  - Após validação completa (relatório SOP com status PASS, verificação de artefatos, análise de conformidade), sempre marcar progresso "N/M" em pareceres.
salvaguarda_parecer:
  obrigatorio:
    - Nunca emitir parecer APROVADO sem relatório SOP válido com status PASS.
    - Nunca emitir parecer sem verificar artefatos citados no relatório SOP.
    - Sempre citar artefactos específicos que fundamentam o parecer (ART-09).
```

---

### 🟡 ALTO — SOP: Progresso Sem Validação Explícita

**Arquivo:** `factory/pins/sop.yaml`

**Linhas 42-43:** Política `during_pipeline` ambígua

```yaml
during_pipeline:
  - Após varredura, sempre marcar progresso "N/M" no relatório.
```

**Problema:** Não especifica:
- O que constitui "varredura" completa
- Se deve verificar artefatos antes de marcar progresso
- Quais verificações são obrigatórias

**Violação Constitucional:** ART-09 (Evidência)

**Recomendação:**
```yaml
during_pipeline:
  - Após varredura completa (todos os artefatos verificados, todas as leis aplicadas, relatório gerado), sempre marcar progresso "N/M" no relatório.
salvaguarda_progresso:
  obrigatorio:
    - Nunca marcar progresso_capitulo: N/M até completar varredura de todos os artefatos relevantes.
    - Sempre citar artefactos verificados no relatório (ART-09).
```

---

### 🟡 ALTO — Estado-Maior FÁBRICA: Sequência Não Enforçada

**Arquivo:** `factory/pins/estado_maior.yaml`

**Linhas 53-54:** Política `during_pipeline` menciona sequência mas não é enforçada

```yaml
during_pipeline:
  - Após relatório do ENGENHEIRO, o ESTADO-MAIOR solicita parecer (GATEKEEPER+SOP) e só então decide avançar gate.
```

**Problema:** Instrução descritiva, mas não há guarda técnica que impeça avançar sem seguir sequência.

**Violação Constitucional:** ART-03 (Consciência Técnica)

**Recomendação:**
```yaml
during_pipeline:
  - Após relatório do ENGENHEIRO, o ESTADO-MAIOR solicita parecer (GATEKEEPER+SOP) e só então decide avançar gate.
salvaguarda_sequencia:
  obrigatorio:
    - Sequência obrigatória: ENGENHEIRO executa → SOP valida → Gatekeeper julga → EM decide.
    - Bloquear decisão de avanço se faltar parecer SOP ou Gatekeeper.
    - Verificar que pareceres existem e têm status válido antes de decidir.
```

---

### 🟡 ALTO — Engenheiro Torre: Responsabilidades Ambigas

**Arquivo:** `Torre/pins/engenheiro_torre.yaml`

**Linhas 6-10:** Responsabilidades incluem "Validar pipeline" e "auditar código"

```yaml
responsibilities:
  - Executar ordens vindas do Estado-Maior (arquivo: engineer.in.yaml)
  - Gerar entregáveis, logs, métricas e relatórios técnicos (engineer.out.json)
  - Validar pipeline, rodar testes, refatorar e auditar código conforme etapas recebidas
  - Nunca executar ou modificar áreas restritas/externas à TORRE
```

**Problema:** "Validar pipeline" e "auditar código" podem ser interpretados como funções de SOP/Gatekeeper.

**Violação Constitucional:** ART-03 (Consciência Técnica)

**Recomendação:**
```yaml
responsibilities:
  - Executar ordens vindas do Estado-Maior (arquivo: engineer.in.yaml)
  - Gerar entregáveis, logs, métricas e relatórios técnicos (engineer.out.json)
  - Executar testes técnicos, refatorar código conforme etapas recebidas
  - Rodar ferramentas de validação técnica (make pipeline_validate, make sop) sem interpretar resultados
  - Nunca executar ou modificar áreas restritas/externas à TORRE
  - NUNCA emitir pareceres de conformidade ou aprovação (isso é SOP/Gatekeeper)
```

---

### 🟡 ALTO — Torre: Papéis Compostos Sem Clarificação

**Arquivo:** `Torre/pins/estado_maior_torre.yaml`

**Linha 6:** `composed_roles: ["EM", "GATEKEEPER", "SOP"]`

**Problema:** Embora tenha salvaguardas de sequência, não há explicação explícita de que "composed_roles" não significa "auto-aprovação simultânea".

**Risco:** Pode ser interpretado como "posso aprovar tudo sozinho".

**Violação Constitucional:** ART-03 (Consciência Técnica)

**Recomendação:**
```yaml
composed_roles: ["EM", "GATEKEEPER", "SOP"]
role_boundary_policy:
  explicacao: >
    "composed_roles" significa que Estado-Maior ATUA como Gatekeeper/SOP,
    mas ainda deve seguir sequência obrigatória e não pode auto-aprovar
    sem verificação independente de execução real e artefatos.
    Sequência obrigatória: ENGENHEIRO → SOP (valida) → Gatekeeper (julga) → EM (decide).
  auto_aprovacao_proibida: true
  sequencia_obrigatoria: true
```

---

### 🟠 MÉDIO — Engenheiro: Progresso Sem Verificação de Ordem

**Arquivo:** `factory/pins/engenheiro.yaml` e `Torre/orquestrador/PIN_ENGENHEIRO.yaml`

**Problema:** Políticas de progresso não verificam se:
- Ordem está em status DONE
- Relatório foi gerado corretamente
- Todos os steps foram executados

**Violação Constitucional:** ART-04 (Verificabilidade)

**Recomendação:**
```yaml
salvaguarda_progresso:
  obrigatorio:
    - Verificar que ordem está em status DONE antes de marcar progresso.
    - Verificar que relatório foi gerado e tem estrutura válida.
    - Verificar que todos os steps da ordem foram executados com sucesso.
```

---

### 🟠 MÉDIO — Gatekeeper: Parecer Sem Citação Obrigatória

**Arquivo:** `factory/pins/gatekeeper.yaml`

**Linhas 31-38:** `allowed_actions` não menciona obrigatoriedade de citação de artefactos

**Problema:** Gatekeeper pode emitir parecer sem citar artefactos específicos.

**Violação Constitucional:** ART-09 (Evidência)

**Recomendação:**
```yaml
allowed_actions:
  - emitir_parecer (com citação obrigatória de artefactos - ART-09)
  - auditar_gate
  - bloquear_pipeline
  - liberar PASS/WARN/BLOCKED (com justificativa baseada em artefactos)
  - comentar_risco
  - reportar findings/compliance (com artefactos citados)
  - registrar progresso N/M
salvaguarda_parecer:
  obrigatorio:
    - Todo parecer deve citar artefactos específicos que fundamentam a decisão (ART-09).
    - Parecer sem citação de artefactos é inválido e deve ser rejeitado.
```

---

### 🟠 MÉDIO — SOP: Validação Sem Checklist Explícito

**Arquivo:** `factory/pins/sop.yaml`

**Problema:** Não há checklist explícito de verificações obrigatórias antes de gerar relatório.

**Violação Constitucional:** ART-04 (Verificabilidade), ART-09 (Evidência)

**Recomendação:**
```yaml
salvaguarda_validacao:
  checklist_obrigatorio:
    - Constituição validada (ART-01, ART-02)
    - Tríade verificada (se gate G0-G2)
    - Artefatos verificados (coverage, sbom, semgrep, etc.)
    - Exceções aplicadas (se houver)
    - Relatório gerado com metadados (ART-07)
    - Artefactos citados no relatório (ART-09)
```

---

### 🟠 MÉDIO — Diferenças Entre PINs da Torre e FÁBRICA

**Problema:** PINs da Torre têm estruturas diferentes dos PINs da FÁBRICA, criando ambiguidade sobre qual seguir.

**Exemplos:**
- Torre: `engenheiro_torre.yaml` (v1) vs `PIN_ENGENHEIRO.yaml` (v3)
- Torre: `estado_maior_torre.yaml` tem `composed_roles`, FÁBRICA não tem
- Torre: estrutura de `progresso` diferente da FÁBRICA

**Violação Constitucional:** ART-04 (Verificabilidade), ART-06 (Coerência)

**Recomendação:**
```yaml
# Padronizar estrutura de PINs entre Torre e FÁBRICA
# Torre deve seguir mesma estrutura que FÁBRICA, com adaptações mínimas
# Deprecar PINs antigos e manter apenas versões congruentes
```

---

## 📊 MATRIZ DE PROBLEMAS

| Problema | Severidade | FÁBRICA | Torre | Status |
|----------|------------|---------|-------|--------|
| Encerramento prematuro EM | 🔴 CRÍTICO | ✅ Corrigido | ✅ Corrigido | ✅ |
| Progresso Engenheiro sem salvaguardas | 🔴 CRÍTICO | ⚠️ Presente | ⚠️ Presente | ⚠️ |
| Sequência não enforçada | 🟡 ALTO | ⚠️ Presente | ⚠️ Presente | ⚠️ |
| Parecer sem validação prévia | 🟡 ALTO | ⚠️ Presente | N/A | ⚠️ |
| Progresso SOP sem checklist | 🟡 ALTO | ⚠️ Presente | N/A | ⚠️ |
| Papéis compostos ambíguos | 🟡 ALTO | N/A | ⚠️ Presente | ⚠️ |
| Responsabilidades ambíguas | 🟡 ALTO | N/A | ⚠️ Presente | ⚠️ |
| Progresso sem verificação ordem | 🟠 MÉDIO | ⚠️ Presente | ⚠️ Presente | ⚠️ |
| Parecer sem citação obrigatória | 🟠 MÉDIO | ⚠️ Presente | N/A | ⚠️ |
| Validação sem checklist | 🟠 MÉDIO | ⚠️ Presente | N/A | ⚠️ |
| Diferenças estruturais PINs | 🟠 MÉDIO | N/A | ⚠️ Presente | ⚠️ |

---

## ⚖️ VIOLAÇÕES CONSTITUCIONAIS IDENTIFICADAS

### ART-03 (Consciência Técnica)
**Problemas:**
- Engenheiro Torre pode interpretar "validar pipeline" como função de SOP
- Papéis compostos podem ser interpretados como auto-aprovação
- Sequência não é tecnicamente enforçada

**Recomendação:** Adicionar guardas técnicas e clarificações explícitas.

---

### ART-04 (Verificabilidade)
**Problemas:**
- Progresso marcado sem verificação de ordem DONE
- Progresso marcado sem verificação de relatório gerado
- Sequência não é verificável retroativamente

**Recomendação:** Adicionar salvaguardas com pré-requisitos verificáveis.

---

### ART-09 (Evidência)
**Problemas:**
- Gatekeeper pode emitir parecer sem citar artefactos
- Progresso marcado sem citação de artefactos verificados
- SOP pode validar sem checklist explícito de artefactos

**Recomendação:** Tornar citação de artefactos obrigatória em todas as ações.

---

## 🛡️ RECOMENDAÇÕES PRIORITÁRIAS

### Prioridade CRÍTICA

#### 1. Adicionar Salvaguardas de Progresso ao Engenheiro

**Arquivos Afetados:**
- `factory/pins/engenheiro.yaml`
- `Torre/pins/engenheiro_torre.yaml`
- `Torre/orquestrador/PIN_ENGENHEIRO.yaml`

**Ação:**
```yaml
salvaguarda_progresso:
  obrigatorio:
    - Nunca marcar progresso_capitulo: N/M até verificar execução completa da ordem, entrega de artefatos e geração de relatório válido.
    - Verificar que ordem está em status DONE.
    - Verificar que relatório foi gerado e tem estrutura válida.
    - Verificar que todos os steps foram executados com sucesso.
```

---

#### 2. Enforçar Sequência Obrigatória Tecnicamente

**Arquivos Afetados:**
- `factory/pins/estado_maior.yaml`
- `Torre/pins/estado_maior_torre.yaml`

**Ação:**
```yaml
salvaguarda_sequencia:
  obrigatorio:
    - Sequência obrigatória: ENGENHEIRO executa → SOP valida → Gatekeeper julga → EM decide.
    - Bloquear decisão de avanço se faltar parecer SOP ou Gatekeeper.
    - Verificar que pareceres existem e têm status válido antes de decidir.
  guarda_tecnica:
    script: "core/orquestrador/validar_sequencia.py"
    bloqueia_se: ["sop_nao_pass", "gatekeeper_nao_aprovado", "sequencia_nao_respeitada"]
```

---

### Prioridade ALTA

#### 3. Clarificar Papéis Compostos na Torre

**Arquivo:** `Torre/pins/estado_maior_torre.yaml`

**Ação:**
```yaml
composed_roles: ["EM", "GATEKEEPER", "SOP"]
role_boundary_policy:
  explicacao: >
    "composed_roles" significa que Estado-Maior ATUA como Gatekeeper/SOP,
    mas ainda deve seguir sequência obrigatória e não pode auto-aprovar
    sem verificação independente de execução real e artefatos.
  auto_aprovacao_proibida: true
  sequencia_obrigatoria: true
```

---

#### 4. Tornar Citação de Artefactos Obrigatória

**Arquivos Afetados:**
- `factory/pins/gatekeeper.yaml`
- `factory/pins/sop.yaml`

**Ação:**
```yaml
salvaguarda_artefactos:
  obrigatorio:
    - Todo parecer/relatório deve citar artefactos específicos que fundamentam a decisão (ART-09).
    - Parecer/relatório sem citação de artefactos é inválido e deve ser rejeitado.
```

---

#### 5. Adicionar Checklist Explícito ao SOP

**Arquivo:** `factory/pins/sop.yaml`

**Ação:**
```yaml
salvaguarda_validacao:
  checklist_obrigatorio:
    - Constituição validada (ART-01, ART-02)
    - Tríade verificada (se gate G0-G2)
    - Artefatos verificados (coverage, sbom, semgrep, etc.)
    - Exceções aplicadas (se houver)
    - Relatório gerado com metadados (ART-07)
    - Artefactos citados no relatório (ART-09)
```

---

### Prioridade MÉDIA

#### 6. Padronizar Estrutura de PINs

**Ação:** Criar template padrão e garantir que Torre e FÁBRICA sigam mesma estrutura.

---

#### 7. Clarificar Responsabilidades do Engenheiro Torre

**Arquivo:** `Torre/pins/engenheiro_torre.yaml`

**Ação:** Remover ambiguidade sobre "validar pipeline" e "auditar código".

---

## 📋 CHECKLIST DE IMPLEMENTAÇÃO

### Engenheiro
- [ ] Adicionar `salvaguarda_progresso` ao PIN FÁBRICA
- [ ] Adicionar `salvaguarda_progresso` ao PIN Torre v1
- [ ] Adicionar `salvaguarda_progresso` ao PIN Torre v3
- [ ] Atualizar políticas `during_pipeline` com pré-requisitos explícitos

### Estado-Maior
- [ ] Adicionar `salvaguarda_sequencia` com guarda técnica
- [ ] Clarificar papéis compostos na Torre
- [ ] Implementar script de validação de sequência

### Gatekeeper
- [ ] Adicionar `salvaguarda_parecer` com checklist obrigatório
- [ ] Tornar citação de artefactos obrigatória
- [ ] Atualizar políticas com pré-requisitos explícitos

### SOP
- [ ] Adicionar `salvaguarda_validacao` com checklist obrigatório
- [ ] Atualizar políticas com pré-requisitos explícitos

### Padronização
- [ ] Criar template padrão de PIN
- [ ] Alinhar estrutura entre Torre e FÁBRICA
- [ ] Deprecar PINs antigos conflitantes

---

## ⚖️ CONFORMIDADE CONSTITUCIONAL FINAL

### ART-03 (Consciência Técnica)
⚠️ **RISCO ALTO:** Papéis podem ser interpretados incorretamente

### ART-04 (Verificabilidade)
⚠️ **RISCO ALTO:** Decisões podem não ser verificáveis retroativamente

### ART-09 (Evidência)
⚠️ **RISCO MÉDIO:** Decisões podem não citar artefactos obrigatoriamente

---

## 📋 CONCLUSÃO

**Critérios Dúbios Identificados:** 12 problemas graves

**Problemas Críticos:** 3 (progresso sem salvaguardas, sequência não enforçada)

**Problemas de Alta Severidade:** 5 (pareceres, validações, papéis compostos)

**Problemas de Média Severidade:** 4 (citações, checklists, padronização)

**Status:** ⚠️ **AÇÃO URGENTE NECESSÁRIA**

**Recomendação:** Implementar todas as salvaguardas recomendadas para blindar sistema constitucionalmente.

---

**Artefactos Citados:**
- `factory/pins/estado_maior.yaml` (linhas 50-54)
- `factory/pins/engenheiro.yaml` (linhas 44-45)
- `factory/pins/gatekeeper.yaml` (linhas 45-46)
- `factory/pins/sop.yaml` (linhas 42-43)
- `Torre/pins/estado_maior_torre.yaml` (linhas 6, 31-35)
- `Torre/pins/engenheiro_torre.yaml` (linhas 6-10, 29-36)
- `Torre/orquestrador/PIN_ENGENHEIRO.yaml` (linhas 44)
- `core/sop/constituição.yaml` (ART-03, ART-04, ART-09)

---

**Agente:** SOP (FÁBRICA 2.0)  
**Data/Hora:** 2025-11-02  
**Regras aplicadas:** ART-04, ART-07, ART-09

---

**COMANDO A EXECUTAR:** "ESTADO-MAIOR ANALISAR RELATÓRIO E CORRIGIR CRITÉRIOS DÚBIOS IDENTIFICADOS"

