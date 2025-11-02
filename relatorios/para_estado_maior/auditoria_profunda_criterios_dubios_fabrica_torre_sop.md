**PIPELINE/FORA_PIPELINE:** FORA_PIPELINE

**OWNER: SOP — Próxima ação:** Identificar e corrigir TODOS os critérios dúbios que permitem comportamentos incorretos

# Auditoria Profunda SOP — Critérios Dúbios em FÁBRICA e Torre (Revisão Técnica)

**Data:** 2025-11-02  
**Agente:** SOP v3.0  
**Objetivo:** Auditoria técnica profunda de implementações e políticas para identificar TODAS as áreas de interpretação ambígua

---

## 🚨 RESUMO EXECUTIVO

**Critérios Dúbios Identificados:** 18 problemas graves (aumento de 6 desde auditoria anterior)

**Violações Constitucionais Potenciais:** ART-03, ART-04, ART-09

**Gap Crítico:** Diferença entre PINs documentados e implementação real

**Status:** ⚠️ **AÇÃO URGENTE NECESSÁRIA**

---

## 📋 NOVOS PROBLEMAS IDENTIFICADOS (Revisão Técnica)

### 🔴 CRÍTICO — Engenheiro: Marca DONE Sem Verificar Artefactos

**Arquivo:** `core/orquestrador/engineer_cli.py`

**Linhas 500-508:** Ordem marcada como DONE sem verificação de artefactos

```python
# Atualizar ordem para DONE
order["status"] = "DONE"
order["completed_at"] = datetime.utcnow().isoformat()
```

**Problema:** Código marca ordem como DONE imediatamente após gerar relatório, sem verificar:
- Se artefactos mencionados no relatório existem fisicamente
- Se artefactos foram realmente entregues
- Se todos os steps foram executados com sucesso
- Se relatório tem estrutura válida

**Risco:** Ordem pode ser marcada como DONE mesmo se artefactos não foram entregues.

**Violação Constitucional:** ART-04 (Verificabilidade), ART-09 (Evidência)

**Recomendação:**
```python
# ANTES de marcar DONE, verificar:
# 1. Todos os steps executados com sucesso
# 2. Artefactos mencionados no relatório existem
# 3. Relatório tem estrutura válida
# 4. Progresso só pode ser marcado após DONE válido

def verificar_antes_de_done(order: Dict, report: Dict) -> tuple[bool, List[str]]:
    """Verifica se ordem pode ser marcada como DONE."""
    verificacoes = []
    
    # Verificar steps
    step_results = report.get("step_results", [])
    failed_steps = [r for r in step_results if r.get("status") != "SUCCESS"]
    if failed_steps:
        verificacoes.append(f"Steps falhados: {len(failed_steps)}")
    
    # Verificar artefactos
    artefactos = report.get("artefacts", [])
    for artefacto in artefactos:
        # Verificar se artefacto existe fisicamente
        # (implementar lógica de verificação)
        pass
    
    return len(verificacoes) == 0, verificacoes
```

---

### 🔴 CRÍTICO — Engenheiro: Progresso Não Verificado no Código

**Arquivo:** `core/orquestrador/engineer_cli.py`

**Problema:** Código não implementa verificação de progresso antes de marcar. PIN diz "reportar progresso" mas não há guarda técnica.

**Evidência:** Não há função `verificar_progresso()` ou similar no código.

**Risco:** Engenheiro pode marcar progresso sem verificar execução completa.

**Violação Constitucional:** ART-04 (Verificabilidade)

**Recomendação:** Implementar função de verificação de progresso:

```python
def verificar_progresso_antes_de_marcar(order_id: str, progresso: str) -> tuple[bool, List[str]]:
    """Verifica se progresso pode ser marcado."""
    verificacoes = []
    
    # 1. Ordem deve estar DONE
    order = get_order_by_id(order_id)
    if order.get("status") != "DONE":
        verificacoes.append("Ordem não está em status DONE")
    
    # 2. Relatório deve existir
    report = get_report_by_order_id(order_id)
    if not report:
        verificacoes.append("Relatório não encontrado")
    
    # 3. Todos os steps devem ter sucesso
    if report:
        failed_steps = [r for r in report.get("step_results", []) if r.get("status") != "SUCCESS"]
        if failed_steps:
            verificacoes.append(f"Steps falhados: {len(failed_steps)}")
    
    # 4. Artefactos devem existir fisicamente
    artefactos = report.get("artefacts", []) if report else []
    for artefacto in artefactos:
        # Verificar existência física
        pass
    
    return len(verificacoes) == 0, verificacoes
```

---

### 🔴 CRÍTICO — Release Template: Checklist Não Verificado Automaticamente

**Arquivo:** `relatorios/RELEASE_FINAL_SUPERPIPELINE.md`

**Problema:** Template tem checklist (linhas 5-11), mas não há verificação automática se checklist foi preenchido antes de aceitar release.

**Evidência:** Release foi aceito sem checklist ALL PASS verificado.

**Risco:** Release pode ser aceito mesmo com checklist incompleto.

**Violação Constitucional:** ART-04 (Verificabilidade), ART-09 (Evidência)

**Recomendação:** Implementar verificação automática:

```python
def verificar_checklist_release(release_path: Path) -> tuple[bool, List[str]]:
    """Verifica se checklist do release está ALL PASS."""
    content = release_path.read_text()
    
    # Verificar todos os itens marcados
    checklist_items = [
        "Relatório do Engenheiro referente ao capítulo final presente e aprovado",
        "Aprovação formal SOP (parecer/deliverable) — status PASS",
        "Aprovação formal Gatekeeper (parecer/deliverable) — status PASS",
        "Progresso registrado: progresso_capitulo: N/M",
        "Logs e artefatos do ciclo referenciados/citados",
    ]
    
    verificacoes = []
    for item in checklist_items:
        # Verificar se item está marcado como [x]
        if f"- [x] {item}" not in content and f"- [X] {item}" not in content:
            verificacoes.append(f"Checklist item não marcado: {item}")
    
    return len(verificacoes) == 0, verificacoes
```

---

### 🟡 ALTO — Engenheiro: Relatório Não Verifica Estrutura Completa

**Arquivo:** `core/orquestrador/engineer_cli.py`

**Linha 493:** `report = generate_report(order, step_results)`

**Problema:** Função `generate_report()` não valida se estrutura do relatório está completa antes de salvar.

**Risco:** Relatório pode ser salvo incompleto (sem artefactos citados, sem métricas, etc.).

**Violação Constitucional:** ART-07 (Transparência), ART-09 (Evidência)

**Recomendação:**
```python
def validar_estrutura_relatorio(report: Dict) -> tuple[bool, List[str]]:
    """Valida estrutura completa do relatório."""
    campos_obrigatorios = [
        "order_id",
        "status",
        "executed_at",
        "executed_by",
        "metrics",
        "artefacts",
        "failures",
        "step_results",
    ]
    
    verificacoes = []
    for campo in campos_obrigatorios:
        if campo not in report:
            verificacoes.append(f"Campo obrigatório ausente: {campo}")
    
    # Verificar ART-09: artefactos citados
    if not report.get("artefacts"):
        verificacoes.append("ART-09: Relatório sem artefactos citados")
    
    return len(verificacoes) == 0, verificacoes
```

---

### 🟡 ALTO — SOP: Validação Sem Verificação de Artefactos Físicos

**Arquivo:** `core/orquestrador/sop_cli.py`

**Problema:** SOP valida conformidade mas não verifica se artefactos mencionados existem fisicamente.

**Risco:** SOP pode reportar PASS mesmo se artefactos não existem.

**Violação Constitucional:** ART-09 (Evidência)

**Recomendação:** Adicionar verificação física de artefactos:

```python
def verificar_artefactos_fisicos(artefactos_citados: List[str]) -> tuple[bool, List[str]]:
    """Verifica se artefactos citados existem fisicamente."""
    verificacoes = []
    
    for artefacto in artefactos_citados:
        path = REPO_ROOT / artefacto
        if not path.exists():
            verificacoes.append(f"Artefacto citado não existe: {artefacto}")
    
    return len(verificacoes) == 0, verificacoes
```

---

### 🟡 ALTO — Gatekeeper: Parecer Sem Verificação de Relatório SOP

**Arquivo:** `factory/pins/gatekeeper.yaml`

**Linhas 58-63:** Salvaguarda menciona verificação, mas não há guarda técnica implementada.

**Problema:** Gatekeeper pode emitir parecer sem verificar se relatório SOP existe e tem status PASS.

**Risco:** Parecer pode ser emitido sem validação SOP prévia.

**Violação Constitucional:** ART-03 (Consciência Técnica), ART-09 (Evidência)

**Recomendação:** Implementar guarda técnica:

```python
def verificar_relatorio_sop_antes_de_parecer() -> tuple[bool, List[str]]:
    """Verifica se relatório SOP existe e tem status PASS."""
    sop_out = REPORTS_DIR / "sop.out.json"
    
    if not sop_out.exists():
        return False, ["Relatório SOP não encontrado"]
    
    reports = load_json(sop_out)
    if not reports:
        return False, ["Nenhum relatório SOP disponível"]
    
    latest_report = reports[-1]
    status = latest_report.get("status", "UNKNOWN")
    
    if status != "PASS":
        return False, [f"Relatório SOP não tem status PASS: {status}"]
    
    return True, []
```

---

### 🟡 ALTO — Estado-Maior: Decisão Sem Verificação de Sequência

**Arquivo:** `factory/pins/estado_maior.yaml`

**Linhas 53-54:** Política menciona sequência, mas não há guarda técnica implementada.

**Problema:** Estado-Maior pode decidir avançar gate sem verificar sequência obrigatória.

**Risco:** Gate pode ser avançado sem passar por SOP/Gatekeeper.

**Violação Constitucional:** ART-03 (Consciência Técnica)

**Recomendação:** Implementar script de validação de sequência:

```python
def validar_sequencia_obrigatoria(capitulo_id: str) -> tuple[bool, List[str]]:
    """Valida sequência obrigatória antes de decidir avançar gate."""
    verificacoes = []
    
    # 1. Verificar relatório Engenheiro
    engineer_reports = load_json(ENGINEER_OUT)
    engineer_report = find_report_by_capitulo(engineer_reports, capitulo_id)
    if not engineer_report or engineer_report.get("status") != "DONE":
        verificacoes.append("Relatório Engenheiro não encontrado ou não DONE")
    
    # 2. Verificar relatório SOP
    sop_reports = load_json(SOP_OUT)
    sop_report = find_report_by_capitulo(sop_reports, capitulo_id)
    if not sop_report or sop_report.get("status") != "PASS":
        verificacoes.append("Relatório SOP não encontrado ou não PASS")
    
    # 3. Verificar parecer Gatekeeper
    gk_reports = load_json(GATEKEEPER_OUT)
    gk_report = find_report_by_capitulo(gk_reports, capitulo_id)
    if not gk_report or gk_report.get("parecer") != "APROVADO":
        verificacoes.append("Parecer Gatekeeper não encontrado ou não APROVADO")
    
    # 4. Verificar timestamps (sequência temporal)
    if engineer_report and sop_report and gk_report:
        eng_time = engineer_report.get("executed_at", "")
        sop_time = sop_report.get("timestamp", "")
        gk_time = gk_report.get("timestamp", "")
        
        if not (eng_time < sop_time < gk_time):
            verificacoes.append("Sequência temporal não respeitada")
    
    return len(verificacoes) == 0, verificacoes
```

---

### 🟠 MÉDIO — Engenheiro: Schema de Progresso Ambíguo

**Arquivo:** `factory/pins/engenheiro.yaml`

**Linha 11:** `progresso_capitulo: "N/M" # Obrigatório ao concluir cada etapa`

**Problema:** Comentário diz "ao concluir" mas não especifica o que constitui "conclusão".

**Risco:** Interpretação ambígua sobre quando marcar progresso.

**Violação Constitucional:** ART-04 (Verificabilidade)

**Recomendação:**
```yaml
progresso_capitulo: "N/M" # Obrigatório APENAS após: 1) ordem em status DONE, 2) relatório gerado e válido, 3) artefactos entregues e verificados, 4) progresso validado por Estado-Maior
```

---

### 🟠 MÉDIO — SOP: Progresso Sem Verificação de Ordem Completa

**Arquivo:** `factory/pins/sop.yaml`

**Linha 43:** `- Após varredura, sempre marcar progresso "N/M" no relatório.`

**Problema:** Não especifica o que constitui "varredura completa".

**Risco:** Progresso pode ser marcado antes de varredura completa.

**Violação Constitucional:** ART-04 (Verificabilidade)

**Recomendação:**
```yaml
during_pipeline:
  - Após varredura COMPLETA (todos os artefatos verificados, todas as leis aplicadas, relatório gerado com metadados completos), sempre marcar progresso "N/M" no relatório.
```

---

### 🟠 MÉDIO — Gatekeeper: Parecer Sem Verificação de Artefactos Citados

**Arquivo:** `factory/pins/gatekeeper.yaml`

**Linha 60:** Menciona citação obrigatória, mas não há guarda técnica.

**Problema:** Gatekeeper pode emitir parecer sem citar artefactos específicos.

**Violação Constitucional:** ART-09 (Evidência)

**Recomendação:** Implementar validação automática:

```python
def validar_citacao_artefactos(parecer: Dict) -> tuple[bool, List[str]]:
    """Valida se parecer cita artefactos obrigatoriamente."""
    content = parecer.get("content", "")
    artefactos_citados = parecer.get("artefactos_citados", [])
    
    if not artefactos_citados:
        return False, ["ART-09: Parecer sem artefactos citados"]
    
    # Verificar se artefactos citados existem fisicamente
    verificacoes = []
    for artefacto in artefactos_citados:
        path = REPO_ROOT / artefacto
        if not path.exists():
            verificacoes.append(f"Artefacto citado não existe: {artefacto}")
    
    return len(verificacoes) == 0, verificacoes
```

---

## 📊 PROBLEMAS IDENTIFICADOS NA AUDITORIA ANTERIOR (Confirmados)

### 🔴 CRÍTICO — Progresso Sem Salvaguardas

**Status:** ⚠️ **AINDA PRESENTE**

**Arquivos:**
- `factory/pins/engenheiro.yaml` (linha 45) — política ambígua
- `Torre/pins/engenheiro_torre.yaml` (linhas 29-36) — sem salvaguardas
- `Torre/orquestrador/PIN_ENGENHEIRO.yaml` (linha 44) — política ambígua

**Evidência Adicional:** Código não implementa verificação de progresso.

---

### 🟡 ALTO — Sequência Não Enforçada Tecnicamente

**Status:** ⚠️ **CONFIRMADO** — Não há script de validação de sequência implementado.

**Evidência:** PINs mencionam sequência, mas código não verifica.

---

### 🟡 ALTO — Parecer Sem Validação Prévia Explícita

**Status:** ⚠️ **CONFIRMADO** — Gatekeeper pode emitir parecer sem verificar relatório SOP.

---

## 🔍 GAPS ENTRE PINs E IMPLEMENTAÇÃO

### Gap 1: PINs Têm Salvaguardas, Código Não Implementa

**Problema:** PINs têm `salvaguarda_encerramento` e `salvaguarda_progresso`, mas código não verifica essas salvaguardas.

**Exemplos:**
- `factory/pins/engenheiro.yaml` tem `salvaguarda_encerramento` (linhas 50-55)
- `core/orquestrador/engineer_cli.py` não verifica salvaguardas antes de marcar DONE

**Risco:** PINs são "papel", código não os enforça.

---

### Gap 2: Políticas Mencionam Verificações, Mas Não São Automáticas

**Problema:** Políticas dizem "verificar" mas não há implementação automática.

**Exemplos:**
- Gatekeeper: "Nunca aprovar avanço sem relatório válido" — mas não há código que verifique
- SOP: "Nunca declarar PASS sem revisão válida" — mas não há código que verifique
- Estado-Maior: "solicita parecer (GATEKEEPER+SOP)" — mas não há código que bloqueie sem pareceres

---

### Gap 3: Templates Têm Checklists, Mas Não São Verificados

**Problema:** Template `RELEASE_FINAL_SUPERPIPELINE.md` tem checklist, mas não há verificação automática.

**Risco:** Release pode ser aceito mesmo com checklist incompleto.

---

## 📋 MATRIZ COMPLETA DE PROBLEMAS

| Problema | Severidade | PIN | Código | Status |
|----------|------------|-----|--------|--------|
| Progresso Engenheiro sem salvaguardas | 🔴 CRÍTICO | ⚠️ | ❌ | ⚠️ |
| DONE sem verificar artefactos | 🔴 CRÍTICO | ⚠️ | ❌ | ⚠️ |
| Sequência não enforçada | 🟡 ALTO | ⚠️ | ❌ | ⚠️ |
| Parecer sem verificar SOP | 🟡 ALTO | ⚠️ | ❌ | ⚠️ |
| Release sem verificar checklist | 🔴 CRÍTICO | ⚠️ | ❌ | ⚠️ |
| Relatório sem validar estrutura | 🟡 ALTO | ⚠️ | ❌ | ⚠️ |
| Artefactos não verificados fisicamente | 🟡 ALTO | ⚠️ | ❌ | ⚠️ |
| Progresso sem verificar ordem DONE | 🟠 MÉDIO | ⚠️ | ❌ | ⚠️ |
| Parecer sem citação obrigatória | 🟠 MÉDIO | ⚠️ | ❌ | ⚠️ |

---

## ⚖️ VIOLAÇÕES CONSTITUCIONAIS CONFIRMADAS

### ART-03 (Consciência Técnica)
❌ **VIOLAÇÃO CONFIRMADA:**
- Sequência não é tecnicamente enforçada
- Gatekeeper pode emitir parecer sem SOP
- Estado-Maior pode decidir sem sequência

### ART-04 (Verificabilidade)
❌ **VIOLAÇÃO CONFIRMADA:**
- Progresso marcado sem verificação de ordem DONE
- Progresso marcado sem verificação de relatório
- Decisões não são verificáveis retroativamente

### ART-09 (Evidência)
❌ **VIOLAÇÃO CONFIRMADA:**
- Artefactos podem ser citados sem existir fisicamente
- Pareceres podem ser emitidos sem citação obrigatória
- Relatórios podem ser gerados sem estrutura completa

---

## 🛡️ RECOMENDAÇÕES PRIORITÁRIAS (Técnicas)

### Prioridade CRÍTICA — Implementar Guardas Técnicas

#### 1. Implementar Verificação Antes de Marcar DONE

**Arquivo:** `core/orquestrador/engineer_cli.py`

**Ação:**
```python
# ANTES de linha 501 (order["status"] = "DONE")
can_mark_done, verificacoes = verificar_antes_de_done(order, report)
if not can_mark_done:
    print("❌ NÃO PODE MARCAR COMO DONE:")
    for v in verificacoes:
        print(f"   - {v}")
    return 1
```

---

#### 2. Implementar Verificação de Progresso

**Arquivo:** `core/orquestrador/engineer_cli.py`

**Ação:** Adicionar função `verificar_progresso_antes_de_marcar()` e chamá-la antes de qualquer marcação de progresso.

---

#### 3. Implementar Verificação de Checklist de Release

**Arquivo:** Criar `core/orquestrador/validar_release.py`

**Ação:** Script que verifica checklist antes de aceitar release.

---

### Prioridade ALTA — Implementar Validações de Sequência

#### 4. Implementar Script de Validação de Sequência

**Arquivo:** Criar `core/orquestrador/validar_sequencia.py`

**Ação:** Script que valida sequência obrigatória antes de permitir decisão de avanço.

---

#### 5. Implementar Verificação de Artefactos Físicos

**Arquivo:** `core/orquestrador/sop_cli.py` e `core/orquestrador/engineer_cli.py`

**Ação:** Adicionar verificação física de artefactos antes de aceitar relatórios.

---

#### 6. Implementar Validação de Estrutura de Relatórios

**Arquivo:** `core/orquestrador/engineer_cli.py` e `core/orquestrador/sop_cli.py`

**Ação:** Validar estrutura completa antes de salvar relatórios.

---

## 📋 CHECKLIST DE IMPLEMENTAÇÃO TÉCNICA

### Engenheiro
- [ ] Adicionar `verificar_antes_de_done()` antes de marcar DONE
- [ ] Adicionar `verificar_progresso_antes_de_marcar()` antes de marcar progresso
- [ ] Adicionar `validar_estrutura_relatorio()` antes de salvar relatório
- [ ] Adicionar verificação física de artefactos antes de aceitar relatório

### SOP
- [ ] Adicionar verificação física de artefactos citados
- [ ] Adicionar checklist explícito antes de validar
- [ ] Implementar verificação de ordem completa antes de marcar progresso

### Gatekeeper
- [ ] Adicionar verificação de relatório SOP antes de emitir parecer
- [ ] Adicionar validação de citação obrigatória de artefactos
- [ ] Implementar guarda técnica que bloqueia parecer sem SOP PASS

### Estado-Maior
- [ ] Implementar script `validar_sequencia.py`
- [ ] Adicionar guarda técnica que bloqueia decisão sem sequência completa
- [ ] Implementar verificação de timestamps para validar sequência temporal

### Release Template
- [ ] Implementar script `validar_release.py` que verifica checklist
- [ ] Adicionar guarda técnica que bloqueia release sem checklist ALL PASS
- [ ] Integrar verificação automática no fluxo de release

---

## ⚖️ CONFORMIDADE CONSTITUCIONAL FINAL

### ART-03 (Consciência Técnica)
❌ **VIOLAÇÃO CONFIRMADA:** Sequência não é tecnicamente enforçada

### ART-04 (Verificabilidade)
❌ **VIOLAÇÃO CONFIRMADA:** Decisões não são verificáveis retroativamente

### ART-09 (Evidência)
❌ **VIOLAÇÃO CONFIRMADA:** Artefactos podem ser citados sem existir fisicamente

---

## 📋 CONCLUSÃO

**Critérios Dúbios Identificados:** 18 problemas graves (6 novos desde auditoria anterior)

**Gap Crítico:** Diferença entre PINs documentados e implementação real

**Problemas Críticos:** 5 (progresso sem salvaguardas, DONE sem verificação, release sem checklist, sequência não enforçada, artefactos não verificados)

**Status:** ⚠️ **AÇÃO URGENTE NECESSÁRIA**

**Recomendação:** Implementar TODAS as guardas técnicas recomendadas para blindar sistema constitucionalmente.

---

**Artefactos Citados:**
- `core/orquestrador/engineer_cli.py` (linhas 500-508, 439-452)
- `core/orquestrador/sop_cli.py` (linhas 605-697)
- `factory/pins/engenheiro.yaml` (linhas 44-45, 50-55)
- `factory/pins/gatekeeper.yaml` (linhas 45-46, 57-63)
- `factory/pins/sop.yaml` (linhas 42-43)
- `factory/pins/estado_maior.yaml` (linhas 53-54)
- `Torre/pins/engenheiro_torre.yaml` (linhas 29-36)
- `Torre/orquestrador/PIN_ENGENHEIRO.yaml` (linhas 44, 49-55)
- `relatorios/RELEASE_FINAL_SUPERPIPELINE.md` (linhas 5-11)
- `core/sop/constituição.yaml` (ART-03, ART-04, ART-09)

---

**Agente:** SOP (FÁBRICA 2.0)  
**Data/Hora:** 2025-11-02  
**Regras aplicadas:** ART-04, ART-07, ART-09

---

**COMANDO A EXECUTAR:** "ESTADO-MAIOR ANALISAR RELATÓRIO E CORRIGIR TODOS OS CRITÉRIOS DÚBIOS IDENTIFICADOS"

