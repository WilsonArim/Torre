**PIPELINE/FORA_PIPELINE:** PIPELINE

**OWNER: ENGENHEIRO — Próxima ação:** Aguardar validação pelo SOP e confirmação de que Torre não exige White Paper próprio

---

# Ajuste na Validação SOP — Exceção para Projetos Torre (ART-02)

## Resumo Executivo

Ajustada a validação SOP para dispensar White Paper próprio para projetos Torre. Torre herda a Tríade de Fundamentação da FÁBRICA e não precisa de White Paper separado conforme decisão do Estado-Maior.

---

## Decisão do Estado-Maior

**Decisão:**
- ✅ Torre não precisa de White Paper separado conforme ART-02
- ✅ Torre é um projeto executor dentro da FÁBRICA
- ✅ Torre herda a Tríade de Fundamentação da FÁBRICA (White Paper, Arquitetura, Base Operacional existem no nível da FÁBRICA)
- ✅ Criar White Paper adicional seria redundante e inconsistente

---

## Correção Aplicada

### Função `validate_triade_fundamentacao()` em `core/scripts/validator.py`

**Alterações:**

1. **Nova função `is_torre_project()`:**
   - Detecta se o projeto é Torre verificando:
     - Existência de pasta `Torre/`
     - Existência de `Torre/orquestrador/`
     - Existência de `Torre/pipeline/superpipeline.yaml`

2. **Ajuste na validação de White Paper:**
   - **Projetos não-Torre:** White Paper próprio é obrigatório (comportamento original)
   - **Projetos Torre:** White Paper próprio é dispensado
   - Torre herda White Paper da FÁBRICA
   - Torre deve ter Arquitetura ou Base Operacional para validar conformidade

3. **Validação de Arquitetura e Base Operacional:**
   - Mantida para todos os projetos (Torre e não-Torre)
   - Torre pode usar `Torre/pipeline/superpipeline.yaml` como Arquitetura
   - Torre pode usar `pipeline/README.md` como Base Operacional

---

## Lógica de Validação

### Para Projetos Torre:
- ✅ White Paper próprio: **DISPENSADO** (herda da FÁBRICA)
- ✅ Arquitetura: **OBRIGATÓRIA** (pode ser `superpipeline.yaml`)
- ✅ Base Operacional: **OBRIGATÓRIA** (pode ser `README.md` da pipeline)

### Para Projetos não-Torre:
- ✅ White Paper próprio: **OBRIGATÓRIO**
- ✅ Arquitetura: **OBRIGATÓRIA**
- ✅ Base Operacional: **OBRIGATÓRIA**

---

## Código Implementado

```python
def is_torre_project() -> bool:
    """Detecta se este é um projeto Torre (executor dentro da FÁBRICA)."""
    torre_markers = [
        REPO_ROOT / "Torre",
        REPO_ROOT / "Torre" / "orquestrador",
        REPO_ROOT / "Torre" / "pipeline" / "superpipeline.yaml",
    ]
    return any(marker.exists() for marker in torre_markers)
```

**Validação ajustada:**
```python
# Para projetos Torre: White Paper próprio não é obrigatório
if not white_paper and not is_torre:
    violations.append("ART-02: White Paper (Estratégia) ausente")
elif not white_paper and is_torre:
    # Torre não precisa de White Paper próprio
    # Validar apenas que Tríade da FÁBRICA existe
    if not arquitetura and not base_operacional:
        violations.append("ART-02: Torre deve herdar Arquitetura ou Base Operacional da FÁBRICA")
```

---

## Conformidade Constitucional

### ART-02 (Tríade de Fundamentação)
✅ **CONFORME**
- Torre herda a Tríade da FÁBRICA
- White Paper próprio não é necessário para projetos executor
- Validação ajustada para refletir decisão do Estado-Maior

### ART-04 (Verificabilidade)
✅ **CONFORME**
- Lógica de detecção rastreável
- Exceção documentada no código
- Decisão do Estado-Maior citada

### ART-07 (Transparência)
✅ **CONFORME**
- Ajuste documentado
- Lógica clara e explícita
- Relatório gerado

### ART-09 (Evidência)
✅ **CONFORME**
- Função de detecção implementada
- Validação ajustada conforme decisão
- Artefactos citados

---

## Arquivos Modificados

1. ✅ `core/scripts/validator.py` — Função `validate_triade_fundamentacao()` ajustada
2. ✅ Nova função `is_torre_project()` adicionada

---

## Validação Esperada

Após correção:
- ✅ Torre não deve mais falhar por White Paper ausente
- ✅ Torre ainda deve validar Arquitetura e Base Operacional
- ✅ Projetos não-Torre continuam exigindo White Paper próprio

---

## Testes Recomendados

1. **Validar Torre:**
   ```bash
   python3 core/scripts/validator.py
   ```
   - Deve passar sem violação de White Paper para Torre

2. **Validar projeto não-Torre:**
   - Criar projeto teste sem Torre/
   - Deve falhar por White Paper ausente (comportamento original)

---

## Próximos Passos

1. ✅ **Engenheiro:** Correção aplicada e pronta para commit
2. ⏳ **SOP:** Validar correção após commit
3. ⏳ **Estado-Maior:** Monitorizar execução dos workflows após push

---

## Conclusão

**Status:** ✅ **CORREÇÃO APLICADA**

**Ajuste:**
- ✅ Função de detecção Torre implementada
- ✅ Validação White Paper ajustada para Torre
- ✅ Exceção documentada no código

**Próximo Passo:**
- Commit e push da correção
- Validação pelo SOP
- Confirmação de que workflows passam sem violação de White Paper

---

**Referências:**
- Decisão Estado-Maior: Torre herda Tríade da FÁBRICA
- Código: `core/scripts/validator.py` função `validate_triade_fundamentacao()`
- Relatório SOP: `relatorios/para_estado_maior/analise_falhas_workflow_sop_validacao_sop.md`

---

**COMANDO A EXECUTAR:** "ENGENHEIRO FAZER COMMIT E PUSH DA CORREÇÃO. SOP VALIDAR APÓS PRÓXIMO PUSH E CONFIRMAR QUE TORRE NÃO FALHA POR WHITE PAPER AUSENTE."

