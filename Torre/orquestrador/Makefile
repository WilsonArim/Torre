# Makefile do Orquestrador da TORRE

# Caminhos
TORRE_DIR := ..
ORQUESTRADOR_DIR := .
REPO_ROOT := ../..
CORE_ORQUESTRADOR := $(REPO_ROOT)/core/orquestrador

.PHONY: treino pipeline_validate sop gatekeeper_run executa status

# Executa treino de uma fase
treino:
	@echo "🚀 Executando treino..."
	@echo "Uso: make treino PHASE=fase0|fase1|fase2|fase3|fase4|fase5"
	@if [ -z "$(PHASE)" ]; then \
		echo "❌ ERRO: Especifique PHASE (fase0 a fase5)"; \
		exit 1; \
	fi
	@python3 cli.py treino $(PHASE)

# Valida pipeline
pipeline_validate:
	@echo "🔍 Validando pipeline..."
	@python3 cli.py pipeline_validate

# Executa validação SOP
sop:
	@echo "📋 Executando validação SOP..."
	@python3 cli.py sop

# Executa Gatekeeper
gatekeeper_run:
	@echo "🔎 Executando Gatekeeper..."
	@python3 cli.py gatekeeper_run

# Executa ordem do Estado-Maior (ciclo completo v1.0)
executa:
	@echo "📋 Executando ordem do Estado-Maior..."
	@python3 engineer_executor.py executa

# Mostra status
status:
	@echo "📊 Status da TORRE..."
	@python3 cli.py status

# Quem age (roteador de direção)
who:
	@python3 cli.py who_acts "$(task)" $(if $(gate),--gate $(gate),)

# Help
help:
	@echo "📚 Comandos disponíveis do Orquestrador da TORRE:"
	@echo ""
	@echo "  make treino PHASE=fase0|fase1|fase2|fase3|fase4|fase5"
	@echo "  make pipeline_validate"
	@echo "  make sop"
	@echo "  make gatekeeper_run"
	@echo "  make executa"
	@echo "  make status"
	@echo "  make who task=\"<descrição>\" [gate=Gx]  # Verificar ownership"
	@echo ""
	@echo "📖 Ver torre/curriculum/PLAN.md para detalhes do plano de treino"
	@echo "📖 Ver PIN.md e PIN_ESTADO_MAIOR.md para regras de ownership"

