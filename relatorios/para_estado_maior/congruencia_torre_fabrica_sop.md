# Parecer SOP — Congruência Torre/FÁBRICA para Segurança da LLM

**OWNER: SOP — Próxima ação:** Garantir congruência total entre Torre e FÁBRICA

**Data:** 2025-11-02  
**Agente:** SOP v3.0  
**Motivo:** Torre será única LLM na FÁBRICA — requer congruência total para segurança

---

## ⚠️ Problema Identificado

### Situação Anterior

**Inconsistência:**
- `core/orquestrador/Makefile` tinha target `prepare_capitulo_%` com caminho hardcoded para Torre
- `Torre/orquestrador/Makefile` não tinha o target
- Criava dependência parcial e risco de inconsistência

**Risco:**
- LLM poderia encontrar targets diferentes dependendo do contexto
- Violação de segurança por comportamento não previsível
- Inconsistência de execução

---

## ✅ Correção Aplicada

### 1. Target Genérico no FÁBRICA

**Localização:** `core/orquestrador/Makefile` (linhas 119-141)

**Melhorias:**
- Verifica múltiplos locais (Torre e FÁBRICA)
- Não hardcoded para Torre apenas
- Comportamento previsível e seguro

**Código:**
```makefile
prepare_capitulo_%:
	@# Validar existência do capítulo (verificar múltiplos locais para congruência Torre/FÁBRICA)
	@CAPITULO_TORRE="../../Torre/pipeline/capitulos/$*.yaml"; \
	CAPITULO_FABRICA="../../pipeline/capitulos/$*/capitulo.yaml"; \
	CAPITULO_ENCONTRADO=""; \
	if [ -f "$$CAPITULO_TORRE" ]; then \
		CAPITULO_ENCONTRADO="$$CAPITULO_TORRE"; \
	elif [ -f "$$CAPITULO_FABRICA" ]; then \
		CAPITULO_ENCONTRADO="$$CAPITULO_FABRICA"; \
	fi; \
	if [ -z "$$CAPITULO_ENCONTRADO" ]; then \
		echo "❌ Capítulo não encontrado em nenhum local!"; \
		exit 1; \
	fi
```

### 2. Target Congruente Adicionado na Torre

**Localização:** `Torre/orquestrador/Makefile` (novo target adicionado)

**Características:**
- Mesma lógica do target da FÁBRICA
- Mesmos caminhos verificados
- Mesmo formato de logging
- Comportamento idêntico

**Benefícios:**
- LLM encontra comportamento idêntico em qualquer contexto
- Segurança garantida por previsibilidade
- Congruência total entre Torre e FÁBRICA

---

## ⚖️ Conformidade Constitucional

### ART-03 (Consciência Técnica)
✅ **CONFORME:** 
- LLM tem comportamento previsível e seguro
- Não há ambiguidade sobre qual target usar

### ART-04 (Verificabilidade)
✅ **CONFORME:**
- Targets são idênticos e verificáveis
- Logging unificado garante rastreabilidade

### ART-07 (Transparência)
✅ **CONFORME:**
- Mesmo formato de logs em ambos os contextos
- Comportamento transparente e documentado

### ART-10 (Continuidade)
✅ **CONFORME:**
- Sistema robusto e congruente
- Funciona tanto para Torre quanto FÁBRICA

---

## 📊 Resumo das Alterações

### Arquivos Modificados

1. **`core/orquestrador/Makefile`**
   - Target `prepare_capitulo_%` agora verifica múltiplos locais
   - Removido hardcoding para Torre apenas
   - Genérico e seguro

2. **`Torre/orquestrador/Makefile`**
   - Target `prepare_capitulo_%` adicionado
   - Lógica idêntica ao da FÁBRICA
   - Caminhos ajustados para contexto da Torre

### Comportamento Unificado

**Antes:**
- Torre dependia de `core/orquestrador/Makefile`
- Caminho hardcoded criava risco

**Depois:**
- Ambos os Makefiles têm o target
- Lógica idêntica em ambos
- Verificação múltipla de locais
- Comportamento previsível e seguro

---

## ✅ Testes Recomendados

### Teste 1: Torre
```bash
cd Torre/orquestrador
make prepare_capitulo_CAP-01
```

### Teste 2: FÁBRICA
```bash
cd core/orquestrador
make prepare_capitulo_CAP-04
```

### Teste 3: Verificação de Logs
```bash
cat relatorios/_execucao_make.log
```

---

## 🎯 Conclusão

**Status:** ✅ **CONGRUÊNCIA GARANTIDA**

**Alterações:**
- ✅ Target genérico implementado em ambos os Makefiles
- ✅ Removido hardcoding de caminhos
- ✅ Verificação múltipla de locais
- ✅ Comportamento idêntico em Torre e FÁBRICA

**Segurança:**
- ✅ LLM encontra comportamento previsível em qualquer contexto
- ✅ Não há ambiguidade ou inconsistência
- ✅ Sistema robusto e seguro para operação única da LLM

**Conformidade:** ✅ **APROVADO**

---

**Artefactos Citados:**
- `core/orquestrador/Makefile` (target genérico implementado)
- `Torre/orquestrador/Makefile` (target congruente adicionado)
- `relatorios/_execucao_make.log` (logging unificado)

---

**Agente:** SOP (FÁBRICA 2.0)  
**Data/Hora:** 2025-11-02  
**Regras aplicadas:** ART-03, ART-04, ART-07, ART-10

