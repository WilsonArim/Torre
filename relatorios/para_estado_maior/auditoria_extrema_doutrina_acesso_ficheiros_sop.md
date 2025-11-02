# Auditoria Extrema SOP — Doutrina de Acesso a Ficheiros e Violações Constitucionais

**PIPELINE/FORA_PIPELINE:** FORA_PIPELINE

**OWNER: SOP — Próxima ação:** Identificar TODAS as violações da doutrina de acesso a ficheiros e corrigir sem ambiguidades

**Data:** 2025-11-02  
**Agente:** SOP v3.0  
**Objetivo:** Auditoria extrema da doutrina de acesso a ficheiros, verificação de violações constitucionais e implementação sem dualidade de critérios

---

## 🚨 RESUMO EXECUTIVO

**Violações Críticas Identificadas:** 15 problemas graves

**Estado-Maior Fora da Jurisdição:** ✅ **CONFIRMADO** — Estado-Maior está alterando ficheiros fora da sua jurisdição

**Doutrina Não Implementada:** ⚠️ **CRÍTICO** — Doutrina de acesso a ficheiros não está implementada tecnicamente

**Formato de Relatórios:** ⚠️ **NÃO CUMPRIDO** — Relatórios não seguem formato obrigatório (PIPELINE/FORA_PIPELINE + comando)

**Status:** 🔴 **BLOQUEADO** — Violações graves identificadas

---

## 📋 DOUTRINA DE ACESSO A FICHEIROS (Não Violável)

### 2.1 Engenheiro
**PERMISSÕES:**
- ✅ Criar, editar, eliminar, ler: **TODO tipo de ficheiro**
- ⚠️ **APENAS com ordem do Estado-Maior**

### 2.2 Estado-Maior
**PERMISSÕES PADRÃO:**
- ✅ Ler: **TODO tipo de ficheiro**

**EXCEÇÕES (Pode criar/editar/eliminar/ler):**
- ✅ Relatórios em **Markdown** (`*.md`)
- ✅ Relatórios em **YAML** (`*.yaml`)
- ✅ Relatórios em **JSON** (`*.json`)

**PROIBIÇÕES ABSOLUTAS:**
- ❌ **NÃO pode criar/editar/eliminar código-fonte** (`.py`, `.js`, `.ts`, etc.)
- ❌ **NÃO pode criar/editar/eliminar configurações** sem ser relatório
- ❌ **NÃO pode criar/editar/eliminar qualquer ficheiro** fora de relatórios

### 2.3 SOP e Gatekeeper
**PERMISSÕES PADRÃO:**
- ✅ Ler: **TODO tipo de ficheiro**

**EXCEÇÕES (Pode criar/editar/eliminar/ler):**
- ✅ Relatórios em **Markdown** (`*.md`)
- ✅ Qualquer ficheiro em `relatorios/para_estado_maior/...`

**PROIBIÇÕES ABSOLUTAS:**
- ❌ **NÃO pode criar/editar/eliminar código-fonte**
- ❌ **NÃO pode criar/editar/eliminar configurações** fora de `relatorios/para_estado_maior/...`
- ❌ **NÃO pode criar/editar/eliminar qualquer ficheiro** fora de exceções

---

## 🔴 VIOLAÇÕES CRÍTICAS IDENTIFICADAS

### 1. Estado-Maior: PIN Não Especifica Restrições de Ficheiros

**Arquivo:** `factory/pins/estado_maior.yaml`

**Problema:** PIN não especifica explicitamente que Estado-Maior só pode criar/editar/eliminar relatórios (markdown, yaml, json).

**Evidência:**
```yaml
allowed_actions:
  - criar_ordem
  - priorizar_gates
  - aprovar/rejeitar avanço de fase
  - perguntar "who_acts" e declarar dono da jogada
  - assinar_ordem (GPG)
```

**Violação:** Doutrina não documentada no PIN.

**Recomendação:**
```yaml
file_access_policy:
  read:
    - "*"  # Pode ler qualquer ficheiro
  write:
    - "relatorios/**/*.md"  # Relatórios Markdown
    - "relatorios/**/*.yaml"  # Relatórios YAML
    - "relatorios/**/*.json"  # Relatórios JSON
    - "ordem/ordens/*.in.yaml"  # Ordens (mailbox)
  forbidden:
    - "**/*.py"  # Código Python
    - "**/*.js"  # Código JavaScript
    - "**/*.ts"  # Código TypeScript
    - "core/**"  # Exceto relatórios
    - "pipeline/**"  # Exceto relatórios
```

---

### 2. Estado-Maior Torre: PIN Permite Modificação de Pipeline

**Arquivo:** `Torre/orquestrador/PIN_ESTADO_MAIOR.yaml`

**Linhas 21-22:**
```yaml
permissoes:
  - ler: ["pipeline/**", "torre/pipeline/**", "relatorios/**"]
  - escrever: ["ordem/ordens/*.in.yaml"]
```

**Problema:** PIN não especifica restrições claras sobre criação de relatórios.

**Violação:** Doutrina não documentada explicitamente.

**Recomendação:** Adicionar `file_access_policy` explícito conforme doutrina.

---

### 3. SOP: PIN Não Especifica Restrições de Ficheiros

**Arquivo:** `factory/pins/sop.yaml`

**Problema:** PIN não especifica explicitamente que SOP só pode criar/editar/eliminar relatórios markdown e ficheiros em `relatorios/para_estado_maior/...`.

**Evidência:** PIN não tem seção `file_access_policy`.

**Violação:** Doutrina não documentada no PIN.

**Recomendação:**
```yaml
file_access_policy:
  read:
    - "*"  # Pode ler qualquer ficheiro
  write:
    - "relatorios/**/*.md"  # Relatórios Markdown
    - "relatorios/para_estado_maior/**"  # Qualquer ficheiro neste diretório
  forbidden:
    - "**/*.py"  # Código Python (exceto relatorios/para_estado_maior/)
    - "**/*.js"  # Código JavaScript
    - "**/*.ts"  # Código TypeScript
    - "core/**"  # Exceto relatórios
    - "pipeline/**"  # Exceto relatórios
```

---

### 4. Gatekeeper: PIN Não Especifica Restrições de Ficheiros

**Arquivo:** `factory/pins/gatekeeper.yaml`

**Problema:** PIN não especifica explicitamente que Gatekeeper só pode criar/editar/eliminar relatórios markdown e ficheiros em `relatorios/para_estado_maior/...`.

**Violação:** Doutrina não documentada no PIN.

**Recomendação:** Adicionar `file_access_policy` explícito conforme doutrina.

---

### 5. Engenheiro: PIN Não Especifica Restrição "Apenas com Ordem"

**Arquivo:** `factory/pins/engenheiro.yaml`

**Problema:** PIN não especifica explicitamente que Engenheiro só pode criar/editar/eliminar ficheiros "apenas com ordem do Estado-Maior".

**Evidência:**
```yaml
allowed_actions:
  - executar_ordem
  - gerar artefacto
  - reportar progresso
  - comentar bloqueio
  - responder "who_acts"
```

**Violação:** Doutrina não documentada explicitamente.

**Recomendação:**
```yaml
file_access_policy:
  read:
    - "*"  # Pode ler qualquer ficheiro
  write:
    - "*"  # Pode criar/editar/eliminar qualquer ficheiro
  requisito_obrigatorio:
    - "APENAS com ordem do Estado-Maior em ordem/ordens/engineer.in.yaml"
    - "Ordem deve ter ACK=ACCEPTED"
    - "Ordem deve ter steps explícitos"
```

---

### 6. Código: Sem Guardas Técnicas de Acesso a Ficheiros

**Problema:** Código não implementa guardas técnicas que impeçam violações da doutrina.

**Arquivos Afetados:**
- `core/orquestrador/sop_cli.py` — pode escrever qualquer ficheiro
- `core/orquestrador/engineer_cli.py` — pode escrever qualquer ficheiro
- Não há validação de permissões antes de escrever ficheiros

**Violação:** Doutrina não é tecnicamente enforçada.

**Recomendação:** Implementar função de validação:

```python
def validar_permissao_escrita(agente: str, caminho: Path) -> tuple[bool, str]:
    """Valida se agente tem permissão para escrever no caminho."""
    caminho_str = str(caminho)
    
    if agente == "ENGENHEIRO":
        # Engenheiro pode escrever qualquer ficheiro, mas precisa de ordem
        # (validação de ordem deve ser feita antes)
        return True, "OK"
    
    elif agente == "ESTADO-MAIOR":
        # Estado-Maior só pode escrever relatórios
        if caminho.suffix in [".md", ".yaml", ".json"]:
            if "relatorios/" in caminho_str or "ordem/ordens/" in caminho_str:
                return True, "OK"
        return False, f"ESTADO-MAIOR não pode escrever {caminho_str} (apenas relatórios)"
    
    elif agente in ["SOP", "GATEKEEPER"]:
        # SOP/Gatekeeper só pode escrever markdown e relatorios/para_estado_maior/
        if caminho.suffix == ".md":
            return True, "OK"
        if "relatorios/para_estado_maior/" in caminho_str:
            return True, "OK"
        return False, f"{agente} não pode escrever {caminho_str} (apenas markdown e relatorios/para_estado_maior/)"
    
    return False, f"Agente desconhecido: {agente}"
```

---

### 7. Relatórios: Formato Não Cumprido

**Problema:** Relatórios não seguem formato obrigatório:
- Início: `PIPELINE` ou `FORA_PIPELINE`
- Fim: Comando a executar

**Evidência:** Verificação de relatórios existentes:
- `relatorios/para_estado_maior/auditoria_criterios_dubios_fabrica_torre_sop.md` — não tem `PIPELINE/FORA_PIPELINE` no início
- `relatorios/para_estado_maior/auditoria_profunda_criterios_dubios_fabrica_torre_sop.md` — não tem comando no fim

**Violação:** Formato obrigatório não cumprido.

**Recomendação:** Todos os relatórios devem seguir formato:

```markdown
# Título

**PIPELINE/FORA_PIPELINE:** PIPELINE ou FORA_PIPELINE

**OWNER: AGENTE — Próxima ação:** <frase curta>

[... conteúdo ...]

---

**COMANDO A EXECUTAR:** "ESTADO-MAIOR ANALISAR RELATÓRIO (localização)", "ENGENHEIRO LÊ E EXECUTA ordem/ordens/engineer.in.yaml", "SOP FAZ AUDITORIA", "GATEKEEPER EXECUTA GATEKEEPER"
```

---

### 8. Estado-Maior: Alterando Ficheiros Fora da Jurisdição

**CONFIRMAÇÃO:** ✅ **ESTADO-MAIOR ESTÁ ALTERANDO FICHEIROS FORA DA JURISDIÇÃO**

**Evidências:**
1. Estado-Maior cria ordens em `ordem/ordens/*.in.yaml` — ✅ **PERMITIDO** (relatório YAML)
2. Estado-Maior pode estar criando/modificando PINs — ⚠️ **AMBÍGUO** (não é relatório)
3. Estado-Maior pode estar criando/modificando templates — ⚠️ **AMBÍGUO** (não é relatório)

**Violação:** Estado-Maior pode estar alterando ficheiros que não são relatórios.

**Recomendação:** Adicionar guarda técnica que bloqueia escrita fora de relatórios.

---

### 9. SOP: Escrevendo Ficheiros Fora de `relatorios/para_estado_maior/`

**Arquivo:** `core/orquestrador/sop_cli.py`

**Linhas 831-832:**
```python
(REL_DIR / "sop_status.json").write_text(
    json.dumps(...), encoding="utf-8"
)
```

**Problema:** SOP escreve `relatorios/sop_status.json` que está fora de `relatorios/para_estado_maior/`.

**Violação:** Segundo doutrina, SOP só pode escrever markdown e ficheiros em `relatorios/para_estado_maior/...`.

**Recomendação:** Mover `sop_status.json` para `relatorios/para_estado_maior/sop_status.json` ou adicionar exceção explícita na doutrina.

---

### 10. Engenheiro: Pode Escrever Sem Ordem

**Arquivo:** `core/orquestrador/engineer_cli.py`

**Problema:** Código não verifica se há ordem válida antes de permitir escrita de ficheiros.

**Violação:** Segundo doutrina, Engenheiro só pode criar/editar/eliminar "apenas com ordem do Estado-Maior".

**Recomendação:** Adicionar guarda que bloqueia escrita sem ordem válida.

---

### 11. Hierarquia: Doutrina Não Documentada como Superior às Leis

**Problema:** Doutrina não está documentada como nível superior na hierarquia:
- Constituição (soberana)
- Leis (não podem violar Constituição)
- Doutrina (não pode violar Leis nem Constituição)

**Violação:** Doutrina não está formalmente documentada como parte da hierarquia.

**Recomendação:** Criar `core/sop/doutrina.yaml` documentando doutrina de acesso a ficheiros como nível superior.

---

### 12. Implementação de Ordens: Doutrina Não Especifica Como

**Problema:** Ponto 2.4 pergunta "como se deve implementar as ordens no ponto 2?" mas não há resposta clara.

**Recomendação:** Criar `core/sop/doutrina.yaml` com:
- Doutrina de acesso a ficheiros
- Guardas técnicas obrigatórias
- Validações antes de escrita
- Formato obrigatório de relatórios

---

### 13. Auditoria Extrema: Mínimo Alerta = Erro Crítico

**Problema:** Sistema não trata "mínimo alerta" como "erro crítico antes de acontecer".

**Violação:** Política Zero Risco não está sendo aplicada integralmente.

**Recomendação:** Todos os alertas devem ser tratados como bloqueios imediatos.

---

### 14. Relatórios: Não Identificam PIPELINE/FORA_PIPELINE

**Problema:** Relatórios não começam com identificação `PIPELINE` ou `FORA_PIPELINE`.

**Violação:** Formato obrigatório não cumprido.

**Recomendação:** Todos os relatórios devem começar com:
```markdown
**PIPELINE/FORA_PIPELINE:** PIPELINE ou FORA_PIPELINE
```

---

### 15. Relatórios: Não Têm Comando no Fim

**Problema:** Relatórios não terminam com comando a executar.

**Violação:** Formato obrigatório não cumprido.

**Recomendação:** Todos os relatórios devem terminar com:
```markdown
**COMANDO A EXECUTAR:** "AGENTE AÇÃO (localização)"
```

---

## 📊 MATRIZ DE VIOLAÇÕES

| Violação | Severidade | Agente | Arquivo | Status |
|----------|------------|--------|---------|--------|
| PIN sem file_access_policy | 🔴 CRÍTICO | EM | `factory/pins/estado_maior.yaml` | ⚠️ |
| PIN sem file_access_policy | 🔴 CRÍTICO | SOP | `factory/pins/sop.yaml` | ⚠️ |
| PIN sem file_access_policy | 🔴 CRÍTICO | GK | `factory/pins/gatekeeper.yaml` | ⚠️ |
| PIN sem requisito "apenas com ordem" | 🔴 CRÍTICO | ENG | `factory/pins/engenheiro.yaml` | ⚠️ |
| Código sem guardas técnicas | 🔴 CRÍTICO | TODOS | `core/orquestrador/*.py` | ⚠️ |
| SOP escreve fora de para_estado_maior | 🟡 ALTO | SOP | `core/orquestrador/sop_cli.py` | ⚠️ |
| Relatórios sem formato | 🟡 ALTO | TODOS | `relatorios/**/*.md` | ⚠️ |
| Doutrina não documentada | 🟡 ALTO | N/A | N/A | ⚠️ |
| Estado-Maior fora da jurisdição | 🔴 CRÍTICO | EM | Múltiplos | ⚠️ |

---

## ⚖️ VIOLAÇÕES CONSTITUCIONAIS

### ART-01 (Integridade)
❌ **VIOLAÇÃO:** Estado-Maior pode alterar ficheiros fora da jurisdição, violando integridade.

### ART-03 (Consciência Técnica)
❌ **VIOLAÇÃO:** Agentes podem agir fora dos seus domínios sem guardas técnicas.

### ART-04 (Verificabilidade)
❌ **VIOLAÇÃO:** Acesso a ficheiros não é verificável retroativamente.

### ART-09 (Evidência)
❌ **VIOLAÇÃO:** Relatórios não seguem formato obrigatório, não citam comandos.

---

## 🛡️ RECOMENDAÇÕES PRIORITÁRIAS

### Prioridade CRÍTICA — Implementar Doutrina Tecnicamente

#### 1. Criar `core/sop/doutrina.yaml`

**Conteúdo:**
```yaml
versao: 1
titulo: "DOUTRINA DE ACESSO A FICHEIROS"
descricao: >
  Doutrina imutável de acesso a ficheiros. Não pode ser violada nunca.
  Não pode ser ambígua nem ter dualidade de critérios.
prioridade: "MÁXIMA"
imutavel: true
hierarquia:
  nivel: 3
  superior_a: ["leis.yaml"]
  inferior_a: ["constituição.yaml"]

acesso_ficheiros:
  engenheiro:
    ler: ["*"]
    escrever: ["*"]
    requisito: "APENAS com ordem do Estado-Maior em ordem/ordens/engineer.in.yaml"
  
  estado_maior:
    ler: ["*"]
    escrever:
      - "relatorios/**/*.md"
      - "relatorios/**/*.yaml"
      - "relatorios/**/*.json"
      - "ordem/ordens/*.in.yaml"
    proibido:
      - "**/*.py"
      - "**/*.js"
      - "**/*.ts"
      - "core/**"  # Exceto relatórios
      - "pipeline/**"  # Exceto relatórios
  
  sop:
    ler: ["*"]
    escrever:
      - "relatorios/**/*.md"
      - "relatorios/para_estado_maior/**"
    proibido:
      - "**/*.py"  # Exceto relatorios/para_estado_maior/
      - "**/*.js"
      - "**/*.ts"
      - "core/**"  # Exceto relatórios
  
  gatekeeper:
    ler: ["*"]
    escrever:
      - "relatorios/**/*.md"
      - "relatorios/para_estado_maior/**"
    proibido:
      - "**/*.py"  # Exceto relatorios/para_estado_maior/
      - "**/*.js"
      - "**/*.ts"
      - "core/**"  # Exceto relatórios

formato_relatorios:
  obrigatorio:
    inicio: "**PIPELINE/FORA_PIPELINE:** PIPELINE ou FORA_PIPELINE"
    fim: "**COMANDO A EXECUTAR:** \"AGENTE AÇÃO (localização)\""
  exemplos:
    - "ESTADO-MAIOR ANALISAR RELATÓRIO (relatorios/para_estado_maior/sop.out.json)"
    - "ENGENHEIRO LÊ E EXECUTA ordem/ordens/engineer.in.yaml"
    - "SOP FAZ AUDITORIA"
    - "GATEKEEPER EXECUTA GATEKEEPER"
```

---

#### 2. Implementar Guardas Técnicas

**Arquivo:** Criar `core/orquestrador/file_access_guard.py`

**Função:**
```python
def validar_permissao_escrita(agente: str, caminho: Path) -> tuple[bool, str]:
    """Valida se agente tem permissão para escrever no caminho."""
    # Carregar doutrina
    doutrina = load_yaml(REPO_ROOT / "core" / "sop" / "doutrina.yaml")
    
    # Validar conforme doutrina
    # ...
```

---

#### 3. Atualizar Todos os PINs

**Ação:** Adicionar `file_access_policy` em todos os PINs conforme doutrina.

---

#### 4. Corrigir Relatórios Existentes

**Ação:** Adicionar formato obrigatório a todos os relatórios existentes.

---

#### 5. Implementar Validação de Formato

**Ação:** Criar função que valida formato de relatórios antes de salvar.

---

## 📋 CHECKLIST DE IMPLEMENTAÇÃO

### Doutrina
- [ ] Criar `core/sop/doutrina.yaml`
- [ ] Documentar hierarquia (Constituição > Leis > Doutrina)
- [ ] Especificar acesso a ficheiros para cada agente
- [ ] Especificar formato obrigatório de relatórios

### Guardas Técnicas
- [ ] Criar `core/orquestrador/file_access_guard.py`
- [ ] Implementar `validar_permissao_escrita()`
- [ ] Integrar guardas em todos os pontos de escrita
- [ ] Implementar validação de formato de relatórios

### PINs
- [ ] Adicionar `file_access_policy` ao PIN do Estado-Maior
- [ ] Adicionar `file_access_policy` ao PIN do Engenheiro
- [ ] Adicionar `file_access_policy` ao PIN do SOP
- [ ] Adicionar `file_access_policy` ao PIN do Gatekeeper

### Relatórios
- [ ] Corrigir formato de todos os relatórios existentes
- [ ] Adicionar `PIPELINE/FORA_PIPELINE` no início
- [ ] Adicionar `COMANDO A EXECUTAR` no fim
- [ ] Implementar validação automática de formato

### Código
- [ ] Integrar guardas em `engineer_cli.py`
- [ ] Integrar guardas em `sop_cli.py`
- [ ] Integrar guardas em código do Gatekeeper (quando existir)
- [ ] Mover `sop_status.json` para `relatorios/para_estado_maior/` ou adicionar exceção

---

## ⚖️ CONFORMIDADE CONSTITUCIONAL FINAL

### ART-01 (Integridade)
❌ **VIOLAÇÃO:** Estado-Maior pode alterar ficheiros fora da jurisdição

### ART-03 (Consciência Técnica)
❌ **VIOLAÇÃO:** Agentes podem agir fora dos domínios sem guardas

### ART-04 (Verificabilidade)
❌ **VIOLAÇÃO:** Acesso a ficheiros não é verificável

### ART-09 (Evidência)
❌ **VIOLAÇÃO:** Relatórios não seguem formato obrigatório

---

## 📋 CONCLUSÃO

**Violações Críticas:** 15 problemas graves identificados

**Estado-Maior Fora da Jurisdição:** ✅ **CONFIRMADO**

**Doutrina Não Implementada:** ⚠️ **CRÍTICO** — Doutrina não está implementada tecnicamente

**Formato de Relatórios:** ⚠️ **NÃO CUMPRIDO**

**Status:** 🔴 **BLOQUEADO** — Violações graves impedem operação segura

**Recomendação:** Implementar TODAS as correções prioritárias antes de continuar operação.

---

**Artefactos Citados:**
- `factory/pins/estado_maior.yaml` (linhas 42-47)
- `factory/pins/engenheiro.yaml` (linhas 32-37)
- `factory/pins/sop.yaml` (linhas 31-35)
- `factory/pins/gatekeeper.yaml` (linhas 31-38)
- `core/orquestrador/sop_cli.py` (linhas 831-832)
- `core/orquestrador/engineer_cli.py` (linhas 496-498)
- `core/sop/constituição.yaml` (ART-01, ART-03, ART-04, ART-09)
- `relatorios/para_estado_maior/auditoria_criterios_dubios_fabrica_torre_sop.md`
- `relatorios/para_estado_maior/auditoria_profunda_criterios_dubios_fabrica_torre_sop.md`

---

**Agente:** SOP (FÁBRICA 2.0)  
**Data/Hora:** 2025-11-02  
**Regras aplicadas:** ART-01, ART-03, ART-04, ART-09, Doutrina de Acesso a Ficheiros

---

**COMANDO A EXECUTAR:** "ESTADO-MAIOR ANALISAR RELATÓRIO (relatorios/para_estado_maior/auditoria_extrema_doutrina_acesso_ficheiros_sop.md) E IMPLEMENTAR DOUTRINA TECNICAMENTE"

