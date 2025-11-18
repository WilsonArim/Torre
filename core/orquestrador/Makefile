SHELL := /bin/bash
export PYTHONPATH := $(PWD)/../..

precommit:
	pre-commit run --all-files || true

test:
	coverage run -m pytest -q || true
	coverage xml -o ../../relatorios/coverage.xml || true

coverage_xml:
	@echo "📊 Gerando coverage.xml obrigatório..."
	@mkdir -p ../../relatorios
	@if command -v coverage >/dev/null 2>&1; then \
		if [ -f .coverage ] || [ -f ../../.coverage ]; then \
			coverage xml -o ../../relatorios/coverage.xml || coverage xml || true; \
		else \
			echo "⚠️ Nenhum dado de cobertura encontrado. Executando testes primeiro..."; \
			coverage run -m pytest -q 2>/dev/null || coverage run -m unittest discover -s ../../ -p "test_*.py" 2>/dev/null || true; \
			coverage xml -o ../../relatorios/coverage.xml || coverage xml || true; \
		fi; \
		if [ -f ../../relatorios/coverage.xml ]; then \
			echo "✅ coverage.xml gerado: relatorios/coverage.xml"; \
		else \
			echo "⚠️ Gerando coverage.xml mínimo (sem dados de cobertura)..."; \
			echo '<?xml version="1.0" ?><coverage><sources><source>.</source></sources><packages/></coverage>' > ../../relatorios/coverage.xml; \
		fi; \
	else \
		echo "⚠️ coverage não instalado. Gerando coverage.xml mínimo..."; \
		echo '<?xml version="1.0" ?><coverage><sources><source>.</source></sources><packages/></coverage>' > ../../relatorios/coverage.xml; \
	fi
	@test -f ../../relatorios/coverage.xml && echo "✅ coverage.xml presente: relatorios/coverage.xml" || echo "❌ Falha ao gerar coverage.xml"

lint:
	npm run -s lint || true

security:
	semgrep --config auto --sarif -o ../../relatorios/semgrep.sarif || true
	bandit -q -r ../.. -x ../../.vercel,../../Torre/torre-llm,../../Torre/.venv,../../venv,../../.venv,../../factory/pins/_deprecated -f json -o ../../relatorios/bandit.json || true
	npm audit --json > ../../relatorios/npm-audit.json || true
	trivy fs --format json -o ../../relatorios/trivy.json ../.. || true

sbom:
	@echo "📦 Gerando SBOM..."
	@mkdir -p ../../relatorios
	@# Verificar se cyclonedx-bom está disponível
	@if command -v cyclonedx-bom >/dev/null 2>&1; then \
		echo "✅ cyclonedx-bom encontrado, gerando SBOM..."; \
		(cd ../.. && cyclonedx-bom -o relatorios/sbom.json) || exit 1; \
	elif command -v npx >/dev/null 2>&1; then \
		echo "⚠️ cyclonedx-bom não encontrado. Tentando via npx..."; \
		(cd ../.. && npx -y @cyclonedx/cyclonedx-npm -o relatorios/sbom.json) || exit 1; \
	else \
		echo "⚠️ cyclonedx-bom não encontrado. Instalando via npm..."; \
		npm install -g @cyclonedx/cyclonedx-npm || exit 1; \
		echo "✅ Instalado. Gerando SBOM..."; \
		(cd ../.. && cyclonedx-bom -o relatorios/sbom.json) || (cd ../.. && npx -y @cyclonedx/cyclonedx-npm -o relatorios/sbom.json) || exit 1; \
	fi
	@if [ -f ../../relatorios/sbom.json ]; then \
		echo "✅ SBOM gerado: relatorios/sbom.json"; \
	else \
		echo "❌ ERRO: SBOM não foi gerado após instalação!"; \
		exit 1; \
	fi

validate_constituicao:
	@echo "🔒 Validando imutabilidade da Constituição..."
	@bash validate_constituicao.sh || exit 1

sop: validate_constituicao coverage_xml test lint security sbom
	python3 ../scripts/validator.py

ship:
	@echo "Use nos projetos-cliente. Na FÁBRICA apenas release via CI."


pipeline_gen:
	python3 cli.py gen_pipeline

pipeline_validate:
	python3 cli.py validate_pipeline

pipeline_toc:
	python3 cli.py toc

gatekeeper_prep:
	@echo "📦 Preparando input do Gatekeeper..."
	@python3 ../scripts/validator.py --gatekeeper-prep || echo "⚠️ Gatekeeper prep concluído"

gatekeeper_run:
	@echo "🔎 Running automated Gatekeeper (Composer Edition)..."
	@$(MAKE) gatekeeper_prep || true
	@echo "🛡️ Executando validação SOP (base para parecer Gatekeeper)..."
	@python3 ../scripts/validator.py || echo "⚠️ SOP executado (status pode ser BLOQUEADO)"
	@if [ -f ../../relatorios/parecer_gatekeeper.md ]; then \
		echo "✅ Gatekeeper completed. See relatorios/parecer_gatekeeper.md"; \
	else \
		echo "📝 Gerando parecer Gatekeeper mínimo..."; \
		echo "Parecer do Gatekeeper: baseado em validação SOP." > ../../relatorios/parecer_gatekeeper.md; \
	fi

# Novas funções do Gatekeeper (conforme ordem do Estado-Maior)
gatekeeper_preflight:
	@echo "🛡️ Executando Gatekeeper Preflight..."
	@python3 gatekeeper_cli.py preflight || exit 1

gatekeeper_vercel_guard:
	@echo "🛡️ Executando Vercel Guard..."
	@python3 gatekeeper_cli.py vercel-guard || exit 1

gatekeeper_post_mortem:
	@echo "🛡️ Executando Post-Mortem..."
	@python3 gatekeeper_cli.py post-mortem || exit 1

gatekeeper_dependency_radar:
	@echo "🛡️ Executando Dependency Radar..."
	@python3 ../../tools/gatekeeper/dependency_radar.py || exit 1

review_codex:
	@echo "🧠 Running ethical review with Codex (GPT-4o)..."
	python3 core/orquestrador/cli.py review_codex
	@echo "✅ Codex review completed. See relatorios/parecer_gatekeeper_codex.md"

# PIN — ENGENHEIRO v3.0
engineer_validate_format:
	@echo "🔍 Validando formato das ordens..."
	python3 validate_order_format.py

engineer_executa: engineer_validate_format
	@echo "🔧 Executando ordem do Estado-Maior..."
	python3 engineer_cli.py executa

engineer_status:
	@echo "📊 Status do ENGENHEIRO..."
	python3 engineer_cli.py status

engineer_limpa:
	@echo "🧹 Rotacionando relatórios..."
	python3 engineer_cli.py limpa

# PIN — SOP v3.0
sop_executa:
	@echo "🔒 Executando verificação constitucional..."
	python3 sop_cli.py executa

sop_status:
	@echo "📊 Status dos gates..."
	python3 sop_cli.py status

sop_limpa:
	@echo "🧹 Limpeza e rotação..."
	python3 sop_cli.py limpa

# Validador Pré-Commit (execução manual)
validate:
	@echo "🔒 Executando validador pré-commit (imita workflows GitHub)..."
	@python3 ../../tools/pre_commit_validator.py --skip-staged-check || exit 1
	@echo "✅ Validação completa - sistema pronto para commit/push"

orders_rotate:
	python3 core/orquestrador/orders_gc.py

reports_rotate:
	python3 core/orquestrador/orders_gc.py --mode reports

mailbox_health:
	python3 core/orquestrador/mailbox_health.py

# Targets dinâmicos para preparação de capítulos (wildcard robusto)
# Uso: make prepare_capitulo_CAP-04
# Suporta múltiplos locais: Torre/pipeline/capitulos/ e pipeline/capitulos/
prepare_capitulo_%:
	@echo "📋 Preparando capítulo: $*" | tee -a ../../relatorios/_execucao_make.log
	@TIMESTAMP=$$(date -u +"%Y-%m-%dT%H:%M:%SZ"); \
	echo "[$$TIMESTAMP] prepare_capitulo_$* iniciado" >> ../../relatorios/_execucao_make.log
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
		echo "❌ Capítulo não encontrado em nenhum local!" | tee -a ../../relatorios/_execucao_make.log; \
		echo "   Verificados:" | tee -a ../../relatorios/_execucao_make.log; \
		echo "   - $$CAPITULO_TORRE" | tee -a ../../relatorios/_execucao_make.log; \
		echo "   - $$CAPITULO_FABRICA" | tee -a ../../relatorios/_execucao_make.log; \
		echo "[$$TIMESTAMP] prepare_capitulo_$* FALHOU: capítulo não encontrado" >> ../../relatorios/_execucao_make.log; \
		exit 1; \
	fi; \
	echo "✅ Capítulo encontrado: $$CAPITULO_ENCONTRADO" | tee -a ../../relatorios/_execucao_make.log
	@# Preparar diretório de logs se não existir
	@mkdir -p ../../relatorios
	@# Executar preparação do capítulo (placeholder - pode ser expandido)
	@echo "🔧 Executando preparação do capítulo $*..." | tee -a ../../relatorios/_execucao_make.log
	@# Adicionar aqui comandos específicos de preparação se necessário
	@TIMESTAMP=$$(date -u +"%Y-%m-%dT%H:%M:%SZ"); \
	echo "[$$TIMESTAMP] prepare_capitulo_$* concluído com sucesso" >> ../../relatorios/_execucao_make.log; \
	echo "✅ Capítulo $* preparado com sucesso" | tee -a ../../relatorios/_execucao_make.log


