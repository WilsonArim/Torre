# Análise SOP — Parâmetros da Torre vs FÁBRICA

**OWNER: SOP — Próxima ação:** Verificar conformidade da Torre com parâmetros implementados

**Data:** 2025-11-02  
**Agente:** SOP v3.0  
**Análise:** Compatibilidade Torre vs FÁBRICA para targets dinâmicos

---

## 🔍 Análise da Situação Atual

### ✅ Estrutura de Capítulos

**Torre:**
- Localização: `Torre/pipeline/capitulos/`
- Capítulos: CAP-01.yaml, CAP-02.yaml, CAP-03.yaml, CAP-04.yaml, CAP-05.yaml
- Formato: YAML direto (não há subdiretórios `CAP-XX/capitulo.yaml`)

**FÁBRICA:**
- Localização: `pipeline/capitulos/` (não existe ainda)
- Capítulos definidos em: `pipeline/superpipeline.yaml`

---

## ⚠️ Problema Identificado

### Target Implementado no FÁBRICA

**Localização:** `core/orquestrador/Makefile` (linhas 119-141)

**Caminho Verificado:**
```makefile
@CAPITULO_YAML="../../Torre/pipeline/capitulos/$*.yaml"; \
```

**Status:** ✅ **FUNCIONA PARA TORRE**

O target em `core/orquestrador/Makefile` já aponta para `Torre/pipeline/capitulos/$*.yaml`, então a Torre está usando o mesmo target da FÁBRICA.

---

## 📊 Comparação: Torre vs FÁBRICA

### Makefile da Torre

**Localização:** `Torre/orquestrador/Makefile`

**Status:** ❌ **NÃO TEM target `prepare_capitulo_%`**

**Comandos Existentes:**
- `treino` (para fases)
- `pipeline_validate`
- `sop`
- `gatekeeper_run`
- `executa`
- `status`

### Makefile da FÁBRICA

**Localização:** `core/orquestrador/Makefile`

**Status:** ✅ **TEM target `prepare_capitulo_%`**

**Caminho Verificado:**
- Aponta para `../../Torre/pipeline/capitulos/$*.yaml`
- Funciona para capítulos da Torre

---

## ✅ Resposta: Torre Está Usando os Mesmos Parâmetros?

### Resposta: ✅ **SIM, PARCIALMENTE**

**Explicação:**

1. **Target Único Compartilhado:**
   - O target `prepare_capitulo_%` está implementado em `core/orquestrador/Makefile`
   - Este target aponta para `Torre/pipeline/capitulos/$*.yaml`
   - A Torre pode usar este target via `make -C core/orquestrador prepare_capitulo_CAP-XX`

2. **Makefile da Torre Não Tem o Target:**
   - `Torre/orquestrador/Makefile` não tem o target próprio
   - A Torre depende do Makefile central da FÁBRICA

3. **Funcionalidade:**
   - ✅ Funciona para capítulos da Torre
   - ✅ Logging compartilhado em `relatorios/_execucao_make.log`
   - ✅ Validação de existência funciona corretamente

---

## 📋 Recomendações

### Opção 1: Manter Configuração Atual (Recomendado)

**Vantagens:**
- Target centralizado e único ponto de manutenção
- Logging unificado
- Conformidade com arquitetura FÁBRICA (Torre é parte da FÁBRICA)

**Desvantagens:**
- Torre depende de `core/orquestrador/Makefile`
- Comando mais longo: `make -C core/orquestrador prepare_capitulo_CAP-XX`

### Opção 2: Adicionar Target no Makefile da Torre

**Implementação:**
```makefile
# Adicionar em Torre/orquestrador/Makefile
prepare_capitulo_%:
	@echo "📋 Preparando capítulo da Torre: $*" | tee -a ../../relatorios/_execucao_make.log
	@TIMESTAMP=$$(date -u +"%Y-%m-%dT%H:%M:%SZ"); \
	echo "[$$TIMESTAMP] prepare_capitulo_$* iniciado" >> ../../relatorios/_execucao_make.log
	@CAPITULO_YAML="../pipeline/capitulos/$*.yaml"; \
	if [ ! -f "$$CAPITULO_YAML" ]; then \
		echo "❌ Capítulo não encontrado: $$CAPITULO_YAML" | tee -a ../../relatorios/_execucao_make.log; \
		echo "[$$TIMESTAMP] prepare_capitulo_$* FALHOU: capítulo não encontrado" >> ../../relatorios/_execucao_make.log; \
		exit 1; \
	fi
	@echo "✅ Capítulo encontrado: $$CAPITULO_YAML" | tee -a ../../relatorios/_execucao_make.log
	@mkdir -p ../../relatorios
	@echo "🔧 Executando preparação do capítulo $*..." | tee -a ../../relatorios/_execucao_make.log
	@TIMESTAMP=$$(date -u +"%Y-%m-%dT%H:%M:%SZ"); \
	echo "[$$TIMESTAMP] prepare_capitulo_$* concluído com sucesso" >> ../../relatorios/_execucao_make.log; \
	echo "✅ Capítulo $* preparado com sucesso" | tee -a ../../relatorios/_execucao_make.log
```

**Vantagens:**
- Comando mais curto: `make -C Torre/orquestrador prepare_capitulo_CAP-XX`
- Independência relativa da Torre

**Desvantagens:**
- Duplicação de código
- Dois pontos de manutenção

---

## ⚖️ Conformidade Constitucional

### ART-04 (Verificabilidade)
✅ **CONFORME:** Torre pode usar o target via `core/orquestrador/Makefile`

### ART-07 (Transparência)
✅ **CONFORME:** Logging compartilhado garante rastreabilidade

### ART-10 (Continuidade)
⚠️ **CONSIDERAÇÃO:** Torre depende do Makefile central (arquitetura OK, mas pode ser melhorada)

---

## ✅ Conclusão

**Status Atual:** ✅ **TORRE FUNCIONA COM OS MESMOS PARÂMETROS**

**Via:** Target compartilhado em `core/orquestrador/Makefile`

**Comando para Torre:**
```bash
make -C core/orquestrador prepare_capitulo_CAP-XX
```

**Recomendação:** Manter configuração atual (target centralizado) OU adicionar target específico na Torre para conveniência.

---

**Artefactos Citados:**
- `core/orquestrador/Makefile` (linhas 119-141 - target implementado)
- `Torre/orquestrador/Makefile` (target ausente)
- `Torre/pipeline/capitulos/` (estrutura de capítulos)
- `relatorios/_execucao_make.log` (log compartilhado)

---

**Agente:** SOP (FÁBRICA 2.0)  
**Data/Hora:** 2025-11-02  
**Regras aplicadas:** ART-04, ART-07, ART-10

