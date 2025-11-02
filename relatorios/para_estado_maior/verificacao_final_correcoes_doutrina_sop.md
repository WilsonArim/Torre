# Verificação Final SOP — Correções da Doutrina de Acesso a Ficheiros

**PIPELINE/FORA_PIPELINE:** FORA_PIPELINE

**OWNER: SOP — Próxima ação:** Verificação pormenorizada completa — 5 violações críticas restantes

**Data:** 2025-11-02  
**Agente:** SOP v3.0  
**Objetivo:** Verificação completa e detalhada de todas as correções

---

## 🚨 RESUMO EXECUTIVO

**Violações Corrigidas:** 10 de 15 problemas (67%)

**Violações Restantes:** 5 problemas críticos (33%)

**Status:** ⚠️ **PARCIALMENTE CORRIGIDO** — Ainda há violações críticas que impedem conformidade total

---

## ✅ CORREÇÕES IMPLEMENTADAS (10/15)

### 1. ✅ Doutrina Criada — `core/sop/doutrina.yaml`
**Status:** ✅ **COMPLETO**  
**Evidência:** Ficheiro existe, completo, hierarquia documentada, acesso especificado

### 2. ✅ Guardas Técnicas — `core/orquestrador/file_access_guard.py`
**Status:** ✅ **COMPLETO**  
**Evidência:** `validar_permissao_escrita()`, `validar_formato_relatorio()`, `log_violacao()` implementadas

### 3. ✅ PINs Atualizados — Todos os 4 PINs
**Status:** ✅ **COMPLETO**  
**Evidência:** Todos têm `file_access_policy` com referência a `doutrina.yaml`

### 4. ✅ Engenheiro: Guardas Integradas
**Status:** ✅ **COMPLETO**  
**Evidência:** `save_yaml()` e `save_json()` validam permissões antes de escrever

### 5. ✅ SOP: sop_status.json Movido
**Status:** ✅ **COMPLETO**  
**Evidência:** Agora em `relatorios/para_estado_maior/sop_status.json`

### 6. ✅ SOP: Validação sop_status.json
**Status:** ✅ **COMPLETO**  
**Evidência:** Linha 848 valida permissão antes de escrever

---

## ❌ VIOLAÇÕES CRÍTICAS RESTANTES (5/15)

### 1. ❌ SOP: save_json() Sem Validação

**Arquivo:** `core/orquestrador/sop_cli.py`  
**Linhas:** 81-85

**Código Atual:**
```python
def save_json(path: Path, data: List[Dict[str, Any]]) -> None:
    """Guarda lista de relatórios em JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
```

**Problema:** Não valida permissão antes de escrever.

**Uso Sem Validação:**
- Linha 698: `save_json(SOP_OUT, reports)` em `cmd_executa()`
- Linha 868: `save_json(SOP_OUT, reports)` em `cmd_varredura_incongruencias()`

**Violação:** SOP pode escrever JSON sem validação de permissão, violando doutrina.

**Severidade:** 🔴 **CRÍTICO**

**Correção Necessária:**
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
**Linha:** 825

**Código Atual:**
```python
report_path = REL_DIR / "sop_incongruencias_torre.md"
report_path.write_text("\n".join(report_lines), encoding="utf-8")
```

**Problema:** Não valida permissão nem formato antes de escrever.

**Violação:** SOP pode escrever markdown sem validação, violando doutrina.

**Severidade:** 🔴 **CRÍTICO**

**Correção Necessária:**
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

### 3. ❌ Relatórios Sem Formato Obrigatório

**Arquivo:** `core/orquestrador/sop_cli.py`  
**Funções:** `generate_incongruencias_report()`, `generate_report()`

**Problema:** Funções não garantem que relatórios começam com `**PIPELINE/FORA_PIPELINE:**` e terminam com `**COMANDO A EXECUTAR:**`.

**Evidência:**
- `relatorios/sop_incongruencias_torre.md` — não tem formato obrigatório
- Relatórios gerados não seguem formato obrigatório

**Violação:** Formato obrigatório não cumprido, violando doutrina.

**Severidade:** 🔴 **CRÍTICO**

**Correção Necessária:** Modificar funções para garantir formato obrigatório.

---

### 4. ❌ Relatórios Existentes Sem Formato Correto

**Arquivos Afetados:**
- `relatorios/para_estado_maior/auditoria_criterios_dubios_fabrica_torre_sop.md`
- `relatorios/para_estado_maior/auditoria_profunda_criterios_dubios_fabrica_torre_sop.md`
- `relatorios/sop_incongruencias_torre.md`
- `relatorios/para_estado_maior/auditoria_extrema_doutrina_acesso_ficheiros_sop.md`

**Problema:** Relatórios não começam com `**PIPELINE/FORA_PIPELINE:**` nem terminam com `**COMANDO A EXECUTAR:**`.

**Violação:** Formato obrigatório não cumprido.

**Severidade:** 🟡 **ALTO**

**Correção Necessária:** Adicionar formato obrigatório a todos os relatórios existentes.

---

### 5. ❌ Validação de Formato Não Implementada

**Arquivo:** `core/orquestrador/sop_cli.py`

**Problema:** Função `validar_formato_relatorio()` existe em `file_access_guard.py`, mas não é chamada antes de salvar relatórios.

**Violação:** Relatórios podem ser salvos sem formato obrigatório.

**Severidade:** 🔴 **CRÍTICO**

**Correção Necessária:** Chamar `validar_formato_relatorio()` antes de salvar todos os relatórios.

---

## 📊 ANÁLISE DETALHADA

### Pontos de Escrita no SOP

| Função | Linha | Validação Permissão | Validação Formato | Status |
|--------|-------|---------------------|-------------------|--------|
| `save_json()` | 81-85 | ❌ | ❌ | ❌ |
| `write_text()` (sop_incongruencias) | 825 | ❌ | ❌ | ❌ |
| `write_text()` (sop_status.json) | 854 | ✅ (848) | ❌ | ⚠️ |
| `save_json()` (cmd_executa) | 698 | ❌ | ❌ | ❌ |
| `save_json()` (cmd_varredura) | 868 | ❌ | ❌ | ❌ |

**Total:** 1 de 5 pontos tem validação parcial (20%)

---

### Funções de Geração de Relatórios

| Função | Garante PIPELINE/FORA_PIPELINE | Garante COMANDO A EXECUTAR | Status |
|--------|-------------------------------|---------------------------|--------|
| `generate_report()` | ❌ | ❌ | ❌ |
| `generate_incongruencias_report()` | ❌ | ❌ | ❌ |

**Total:** 0 de 2 funções garantem formato (0%)

---

## ⚖️ VIOLAÇÕES CONSTITUCIONAIS RESTANTES

### ART-03 (Consciência Técnica)
❌ **VIOLAÇÃO:** SOP pode escrever ficheiros sem validação de permissão em 4 de 5 pontos.

### ART-04 (Verificabilidade)
❌ **VIOLAÇÃO:** Relatórios podem ser salvos sem formato obrigatório, não são verificáveis.

### ART-09 (Evidência)
❌ **VIOLAÇÃO:** Relatórios não seguem formato obrigatório que inclui comando a executar.

---

## 🛡️ CORREÇÕES PRIORITÁRIAS (5 Restantes)

### Prioridade CRÍTICA

#### 1. Adicionar Validação a save_json()

**Arquivo:** `core/orquestrador/sop_cli.py`  
**Linhas:** 81-85

**Ação:** Adicionar validação de permissão antes de escrever.

---

#### 2. Adicionar Validação a write_text()

**Arquivo:** `core/orquestrador/sop_cli.py`  
**Linha:** 825

**Ação:** Adicionar validação de permissão e formato antes de escrever.

---

#### 3. Garantir Formato em generate_incongruencias_report()

**Arquivo:** `core/orquestrador/sop_cli.py`  
**Função:** `generate_incongruencias_report()`

**Ação:** Modificar para garantir que relatório começa com `**PIPELINE/FORA_PIPELINE:**` e termina com `**COMANDO A EXECUTAR:**`.

---

#### 4. Garantir Formato em generate_report()

**Arquivo:** `core/orquestrador/sop_cli.py`  
**Função:** `generate_report()`

**Ação:** Modificar para garantir que relatório começa com `**PIPELINE/FORA_PIPELINE:**` e termina com `**COMANDO A EXECUTAR:**`.

---

#### 5. Validar Formato Antes de Salvar

**Arquivo:** `core/orquestrador/sop_cli.py`

**Ação:** Chamar `validar_formato_relatorio()` antes de salvar todos os relatórios.

---

## 📋 CHECKLIST FINAL

### Doutrina
- [x] Criar `core/sop/doutrina.yaml` ✅
- [x] Documentar hierarquia ✅
- [x] Especificar acesso a ficheiros ✅
- [x] Especificar formato obrigatório ✅

### Guardas Técnicas
- [x] Criar `core/orquestrador/file_access_guard.py` ✅
- [x] Implementar `validar_permissao_escrita()` ✅
- [x] Implementar `validar_formato_relatorio()` ✅
- [ ] Integrar guardas em TODOS os pontos de escrita ❌ (1/5 pontos)
- [ ] Validar formato antes de salvar relatórios ❌

### PINs
- [x] Adicionar `file_access_policy` ao PIN do Estado-Maior ✅
- [x] Adicionar `file_access_policy` ao PIN do Engenheiro ✅
- [x] Adicionar `file_access_policy` ao PIN do SOP ✅
- [x] Adicionar `file_access_policy` ao PIN do Gatekeeper ✅

### Código
- [x] Integrar guardas em `engineer_cli.py` ✅
- [ ] Integrar guardas em TODOS os pontos de `sop_cli.py` ❌ (1/5 pontos)
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
⚠️ **RISCO PARCIAL:** Estado-Maior PIN corrigido, mas código ainda pode permitir violações sem guardas técnicas completas.

### ART-03 (Consciência Técnica)
❌ **VIOLAÇÃO:** SOP pode escrever ficheiros sem validação em 4 de 5 pontos (80% dos pontos sem validação).

### ART-04 (Verificabilidade)
❌ **VIOLAÇÃO:** Relatórios podem ser salvos sem formato obrigatório, não são verificáveis.

### ART-09 (Evidência)
❌ **VIOLAÇÃO:** Relatórios não seguem formato obrigatório que inclui comando a executar.

---

## 📋 CONCLUSÃO

**Violações Corrigidas:** 10 de 15 problemas (67%)

**Violações Restantes:** 5 problemas críticos (33%)

**Status:** ⚠️ **PARCIALMENTE CORRIGIDO**

**Principais Problemas Restantes:**
1. ❌ `save_json()` do SOP sem validação (usado em 2 pontos)
2. ❌ `write_text()` do SOP sem validação (1 ponto)
3. ❌ Funções de geração não garantem formato obrigatório (2 funções)
4. ❌ Relatórios existentes sem formato correto (4 relatórios)
5. ❌ Validação de formato não implementada antes de salvar

**Impacto:** Sistema ainda pode violar doutrina em 80% dos pontos de escrita do SOP.

**Recomendação:** Completar as 5 correções restantes antes de considerar sistema totalmente corrigido e em conformidade com a doutrina.

---

**Artefactos Citados:**
- `core/sop/doutrina.yaml` ✅
- `core/orquestrador/file_access_guard.py` ✅
- `factory/pins/estado_maior.yaml` (linhas 53-73) ✅
- `factory/pins/engenheiro.yaml` (linhas 41-50) ✅
- `factory/pins/sop.yaml` (linhas 39-56) ✅
- `factory/pins/gatekeeper.yaml` (linhas 42-59) ✅
- `core/orquestrador/engineer_cli.py` (linhas 87, 113) ✅
- `core/orquestrador/sop_cli.py` (linhas 81-85, 825, 848, 698, 868) ⚠️
- `relatorios/sop_incongruencias_torre.md` ❌
- `relatorios/para_estado_maior/auditoria_criterios_dubios_fabrica_torre_sop.md` ❌
- `relatorios/para_estado_maior/auditoria_profunda_criterios_dubios_fabrica_torre_sop.md` ❌
- `relatorios/para_estado_maior/auditoria_extrema_doutrina_acesso_ficheiros_sop.md` ✅

---

**Agente:** SOP (FÁBRICA 2.0)  
**Data/Hora:** 2025-11-02  
**Regras aplicadas:** ART-01, ART-03, ART-04, ART-09, Doutrina de Acesso a Ficheiros

---

**COMANDO A EXECUTAR:** "ENGENHEIRO CORRIGIR VALIDAÇÕES RESTANTES: 1) Adicionar validação a save_json() (linhas 81-85), 2) Adicionar validação a write_text() (linha 825), 3) Garantir formato obrigatório em generate_incongruencias_report() e generate_report(), 4) Validar formato antes de salvar todos os relatórios, 5) Corrigir formato de relatórios existentes"

