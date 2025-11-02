# Verificação SOP — Correções da Doutrina de Acesso a Ficheiros

**PIPELINE/FORA_PIPELINE:** FORA_PIPELINE

**OWNER: SOP — Próxima ação:** Verificar se TODAS as correções da auditoria extrema foram completamente implementadas

**Data:** 2025-11-02  
**Agente:** SOP v3.0  
**Objetivo:** Verificação pormenorizada de todas as correções identificadas na auditoria extrema

---

## 🚨 RESUMO EXECUTIVO

**Violações Corrigidas:** 10 de 15 problemas

**Violações Restantes:** 5 problemas críticos

**Status:** ⚠️ **PARCIALMENTE CORRIGIDO** — Ainda há violações críticas

---

## ✅ CORREÇÕES IMPLEMENTADAS

### 1. ✅ Doutrina Criada

**Arquivo:** `core/sop/doutrina.yaml`

**Status:** ✅ **CORRIGIDO**

**Evidência:**
- Ficheiro existe e está completo
- Hierarquia documentada (Constituição > Leis > Doutrina)
- Acesso a ficheiros especificado para cada agente
- Formato de relatórios especificado

**Conformidade:** ✅ Conforme recomendação

---

### 2. ✅ Guardas Técnicas Implementadas

**Arquivo:** `core/orquestrador/file_access_guard.py`

**Status:** ✅ **CORRIGIDO**

**Evidência:**
- Função `validar_permissao_escrita()` implementada
- Função `validar_formato_relatorio()` implementada
- Função `log_violacao()` implementada
- Validação conforme doutrina.yaml

**Conformidade:** ✅ Conforme recomendação

---

### 3. ✅ PINs Atualizados com file_access_policy

**Arquivos:**
- `factory/pins/estado_maior.yaml` (linhas 53-73)
- `factory/pins/engenheiro.yaml` (linhas 41-50)
- `factory/pins/sop.yaml` (linhas 39-56)
- `factory/pins/gatekeeper.yaml` (linhas 42-59)

**Status:** ✅ **CORRIGIDO**

**Evidência:**
- Todos os PINs têm seção `file_access_policy`
- Referência a `core/sop/doutrina.yaml` incluída
- Permissões especificadas conforme doutrina

**Conformidade:** ✅ Conforme recomendação

---

### 4. ✅ Engenheiro: Guardas Integradas

**Arquivo:** `core/orquestrador/engineer_cli.py`

**Status:** ✅ **CORRIGIDO**

**Evidência:**
- Linha 39: Importa `validar_permissao_escrita`
- Linha 87: `save_yaml()` valida permissão antes de escrever
- Linha 113: `save_json()` valida permissão antes de escrever
- Linha 519: Chama `save_json()` com `tem_ordem_valida=True`
- Linha 529: Chama `save_yaml()` com `tem_ordem_valida=True`

**Conformidade:** ✅ Conforme recomendação

---

### 5. ✅ SOP: sop_status.json Movido

**Arquivo:** `core/orquestrador/sop_cli.py`

**Status:** ✅ **CORRIGIDO**

**Evidência:**
- Linha 845: `sop_status_path = REPORTS_DIR / "sop_status.json"` (agora em `relatorios/para_estado_maior/`)
- Linha 848: Valida permissão antes de escrever
- `relatorios/sop_status.json` não existe mais
- `relatorios/para_estado_maior/sop_status.json` existe

**Conformidade:** ✅ Conforme recomendação

---

### 6. ✅ SOP: Validação Antes de Escrever sop_status.json

**Arquivo:** `core/orquestrador/sop_cli.py`

**Status:** ✅ **CORRIGIDO**

**Evidência:**
- Linha 848: `permite, mensagem = validar_permissao_escrita("SOP", sop_status_path, tem_ordem_valida=False)`
- Linha 849-851: Bloqueia se não permitir

**Conformidade:** ✅ Conforme recomendação

---

## ❌ VIOLAÇÕES RESTANTES (CRÍTICAS)

### 1. ❌ SOP: save_json() Sem Validação

**Arquivo:** `core/orquestrador/sop_cli.py`

**Linhas 81-85:**
```python
def save_json(path: Path, data: List[Dict[str, Any]]) -> None:
    """Guarda lista de relatórios em JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
```

**Problema:** Função `save_json()` não valida permissão antes de escrever.

**Uso:**
- Linha 698: `save_json(SOP_OUT, reports)` — sem validação
- Linha 868: `save_json(SOP_OUT, reports)` — sem validação

**Violação:** SOP pode escrever JSON sem validação de permissão.

**Recomendação:**
```python
def save_json(path: Path, data: List[Dict[str, Any]]) -> None:
    """Guarda lista de relatórios em JSON."""
    # Validar permissão de escrita conforme doutrina
    permite, mensagem = validar_permissao_escrita("SOP", path, tem_ordem_valida=False)
    if not permite:
        raise PermissionError(f"❌ BLOQUEADO: {mensagem}")
    
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
```

---

### 2. ❌ SOP: write_text() Sem Validação

**Arquivo:** `core/orquestrador/sop_cli.py`

**Linha 825:**
```python
report_path = REL_DIR / "sop_incongruencias_torre.md"
report_path.write_text("\n".join(report_lines), encoding="utf-8")
```

**Problema:** `write_text()` não valida permissão antes de escrever.

**Violação:** SOP pode escrever markdown sem validação de permissão.

**Recomendação:**
```python
report_path = REL_DIR / "sop_incongruencias_torre.md"

# Validar permissão de escrita conforme doutrina
permite, mensagem = validar_permissao_escrita("SOP", report_path, tem_ordem_valida=False)
if not permite:
    print(f"❌ BLOQUEADO: {mensagem}")
    return 1

# Validar formato do relatório
conteudo = "\n".join(report_lines)
formato_ok, formato_msg = validar_formato_relatorio(conteudo)
if not formato_ok:
    print(f"❌ BLOQUEADO: {formato_msg}")
    return 1

report_path.write_text(conteudo, encoding="utf-8")
```

---

### 3. ❌ SOP: Relatórios Sem Validação de Formato

**Arquivo:** `core/orquestrador/sop_cli.py`

**Problema:** Relatórios são gerados e escritos sem validação de formato obrigatório.

**Evidência:**
- Linha 825: `report_path.write_text()` — sem validação de formato
- Função `generate_incongruencias_report()` não garante formato obrigatório
- Função `generate_report()` não garante formato obrigatório

**Violação:** Relatórios podem ser salvos sem formato obrigatório (PIPELINE/FORA_PIPELINE + COMANDO A EXECUTAR).

**Recomendação:** Validar formato antes de salvar usando `validar_formato_relatorio()`.

---

### 4. ❌ Relatórios Existentes Sem Formato Correto

**Arquivos:**
- `relatorios/para_estado_maior/auditoria_criterios_dubios_fabrica_torre_sop.md`
- `relatorios/para_estado_maior/auditoria_profunda_criterios_dubios_fabrica_torre_sop.md`
- `relatorios/sop_incongruencias_torre.md`

**Problema:** Relatórios existentes não seguem formato obrigatório:
- Não começam com `**PIPELINE/FORA_PIPELINE:**`
- Não terminam com `**COMANDO A EXECUTAR:**`

**Violação:** Formato obrigatório não cumprido.

**Recomendação:** Corrigir todos os relatórios existentes para seguir formato obrigatório.

---

### 5. ❌ SOP: Falta Validação em Todos os Pontos de Escrita

**Arquivo:** `core/orquestrador/sop_cli.py`

**Pontos de Escrita Sem Validação:**
1. Linha 825: `report_path.write_text()` — sem validação
2. Linha 698: `save_json(SOP_OUT, reports)` — sem validação
3. Linha 868: `save_json(SOP_OUT, reports)` — sem validação
4. Linha 854: `sop_status_path.write_text()` — ✅ TEM validação (linha 848)

**Problema:** Apenas 1 de 4 pontos de escrita tem validação.

**Violação:** Maioria dos pontos de escrita não valida permissões.

**Recomendação:** Adicionar validação em TODOS os pontos de escrita.

---

## 📊 MATRIZ DE STATUS DAS CORREÇÕES

| Correção | Status | Arquivo | Linha | Conformidade |
|----------|--------|---------|-------|--------------|
| Doutrina criada | ✅ | `core/sop/doutrina.yaml` | - | ✅ |
| Guardas técnicas | ✅ | `core/orquestrador/file_access_guard.py` | - | ✅ |
| PIN EM atualizado | ✅ | `factory/pins/estado_maior.yaml` | 53-73 | ✅ |
| PIN ENG atualizado | ✅ | `factory/pins/engenheiro.yaml` | 41-50 | ✅ |
| PIN SOP atualizado | ✅ | `factory/pins/sop.yaml` | 39-56 | ✅ |
| PIN GK atualizado | ✅ | `factory/pins/gatekeeper.yaml` | 42-59 | ✅ |
| Engenheiro guardas | ✅ | `core/orquestrador/engineer_cli.py` | 87, 113 | ✅ |
| SOP sop_status.json movido | ✅ | `core/orquestrador/sop_cli.py` | 845 | ✅ |
| SOP validação sop_status.json | ✅ | `core/orquestrador/sop_cli.py` | 848 | ✅ |
| SOP save_json() validação | ❌ | `core/orquestrador/sop_cli.py` | 81-85 | ❌ |
| SOP write_text() validação | ❌ | `core/orquestrador/sop_cli.py` | 825 | ❌ |
| Validação formato relatórios | ❌ | `core/orquestrador/sop_cli.py` | 825 | ❌ |
| Relatórios existentes corrigidos | ❌ | `relatorios/**/*.md` | - | ❌ |
| Todos pontos escrita validados | ❌ | `core/orquestrador/sop_cli.py` | Múltiplos | ❌ |

---

## ⚖️ VIOLAÇÕES CONSTITUCIONAIS RESTANTES

### ART-03 (Consciência Técnica)
⚠️ **RISCO:** SOP pode escrever ficheiros sem validação de permissão em alguns pontos.

### ART-04 (Verificabilidade)
⚠️ **RISCO:** Relatórios podem ser salvos sem formato obrigatório.

### ART-09 (Evidência)
⚠️ **RISCO:** Relatórios não seguem formato obrigatório que inclui comando a executar.

---

## 🛡️ CORREÇÕES NECESSÁRIAS (PRIORIDADE CRÍTICA)

### 1. Adicionar Validação a save_json() do SOP

**Arquivo:** `core/orquestrador/sop_cli.py`

**Linhas 81-85:** Adicionar validação antes de escrever.

**Ação:**
```python
def save_json(path: Path, data: List[Dict[str, Any]]) -> None:
    """Guarda lista de relatórios em JSON."""
    # Validar permissão de escrita conforme doutrina
    permite, mensagem = validar_permissao_escrita("SOP", path, tem_ordem_valida=False)
    if not permite:
        raise PermissionError(f"❌ BLOQUEADO: {mensagem}")
    
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
```

---

### 2. Adicionar Validação a write_text() do SOP

**Arquivo:** `core/orquestrador/sop_cli.py`

**Linha 825:** Adicionar validação antes de escrever.

**Ação:**
```python
report_path = REL_DIR / "sop_incongruencias_torre.md"

# Validar permissão de escrita conforme doutrina
permite, mensagem = validar_permissao_escrita("SOP", report_path, tem_ordem_valida=False)
if not permite:
    print(f"❌ BLOQUEADO: {mensagem}")
    return 1

# Validar formato do relatório
conteudo = "\n".join(report_lines)
formato_ok, formato_msg = validar_formato_relatorio(conteudo)
if not formato_ok:
    print(f"❌ BLOQUEADO: {formato_msg}")
    return 1

report_path.write_text(conteudo, encoding="utf-8")
```

---

### 3. Garantir Formato Obrigatório em generate_incongruencias_report()

**Arquivo:** `core/orquestrador/sop_cli.py`

**Problema:** Função não garante que relatório começa com `PIPELINE/FORA_PIPELINE` e termina com `COMANDO A EXECUTAR`.

**Ação:** Modificar função para garantir formato obrigatório.

---

### 4. Garantir Formato Obrigatório em generate_report()

**Arquivo:** `core/orquestrador/sop_cli.py`

**Problema:** Função não garante que relatório começa com `PIPELINE/FORA_PIPELINE` e termina com `COMANDO A EXECUTAR`.

**Ação:** Modificar função para garantir formato obrigatório.

---

### 5. Corrigir Relatórios Existentes

**Ação:** Adicionar formato obrigatório a todos os relatórios existentes em `relatorios/para_estado_maior/*.md`.

---

## 📋 CHECKLIST DE VERIFICAÇÃO

### Doutrina
- [x] Criar `core/sop/doutrina.yaml` ✅
- [x] Documentar hierarquia ✅
- [x] Especificar acesso a ficheiros ✅
- [x] Especificar formato obrigatório ✅

### Guardas Técnicas
- [x] Criar `core/orquestrador/file_access_guard.py` ✅
- [x] Implementar `validar_permissao_escrita()` ✅
- [x] Implementar `validar_formato_relatorio()` ✅
- [ ] Integrar guardas em TODOS os pontos de escrita ❌
- [ ] Validar formato antes de salvar relatórios ❌

### PINs
- [x] Adicionar `file_access_policy` ao PIN do Estado-Maior ✅
- [x] Adicionar `file_access_policy` ao PIN do Engenheiro ✅
- [x] Adicionar `file_access_policy` ao PIN do SOP ✅
- [x] Adicionar `file_access_policy` ao PIN do Gatekeeper ✅

### Código
- [x] Integrar guardas em `engineer_cli.py` ✅
- [ ] Integrar guardas em TODOS os pontos de `sop_cli.py` ❌
- [x] Mover `sop_status.json` para `relatorios/para_estado_maior/` ✅
- [ ] Validar formato antes de salvar relatórios ❌

### Relatórios
- [ ] Corrigir formato de todos os relatórios existentes ❌
- [ ] Adicionar `PIPELINE/FORA_PIPELINE` no início ❌
- [ ] Adicionar `COMANDO A EXECUTAR` no fim ❌
- [ ] Implementar validação automática de formato ❌

---

## ⚖️ CONFORMIDADE CONSTITUCIONAL FINAL

### ART-01 (Integridade)
⚠️ **RISCO PARCIAL:** Estado-Maior ainda pode alterar ficheiros sem guardas técnicas em alguns pontos (mas PINs corrigidos).

### ART-03 (Consciência Técnica)
⚠️ **RISCO PARCIAL:** SOP pode escrever ficheiros sem validação em alguns pontos.

### ART-04 (Verificabilidade)
⚠️ **RISCO PARCIAL:** Relatórios podem ser salvos sem formato obrigatório.

### ART-09 (Evidência)
⚠️ **RISCO PARCIAL:** Relatórios não seguem formato obrigatório.

---

## 📋 CONCLUSÃO

**Violações Corrigidas:** 10 de 15 problemas (67%)

**Violações Restantes:** 5 problemas críticos (33%)

**Status:** ⚠️ **PARCIALMENTE CORRIGIDO**

**Principais Problemas Restantes:**
1. `save_json()` do SOP sem validação
2. `write_text()` do SOP sem validação
3. Relatórios sem validação de formato
4. Relatórios existentes sem formato correto
5. Não todos os pontos de escrita validados

**Recomendação:** Completar as 5 correções restantes antes de considerar sistema totalmente corrigido.

---

**Artefactos Citados:**
- `core/sop/doutrina.yaml` ✅
- `core/orquestrador/file_access_guard.py` ✅
- `factory/pins/estado_maior.yaml` (linhas 53-73) ✅
- `factory/pins/engenheiro.yaml` (linhas 41-50) ✅
- `factory/pins/sop.yaml` (linhas 39-56) ✅
- `factory/pins/gatekeeper.yaml` (linhas 42-59) ✅
- `core/orquestrador/engineer_cli.py` (linhas 87, 113, 519, 529) ✅
- `core/orquestrador/sop_cli.py` (linhas 81-85, 825, 848, 698, 868) ⚠️
- `relatorios/para_estado_maior/auditoria_criterios_dubios_fabrica_torre_sop.md` ❌
- `relatorios/para_estado_maior/auditoria_profunda_criterios_dubios_fabrica_torre_sop.md` ❌
- `relatorios/sop_incongruencias_torre.md` ❌

---

**Agente:** SOP (FÁBRICA 2.0)  
**Data/Hora:** 2025-11-02  
**Regras aplicadas:** ART-01, ART-03, ART-04, ART-09, Doutrina de Acesso a Ficheiros

---

**COMANDO A EXECUTAR:** "ENGENHEIRO CORRIGIR VALIDAÇÕES RESTANTES EM core/orquestrador/sop_cli.py (save_json, write_text, validação de formato) E CORRIGIR FORMATO DE RELATÓRIOS EXISTENTES"

