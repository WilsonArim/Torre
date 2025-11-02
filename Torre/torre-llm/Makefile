SHELL := /bin/bash

bootstrap:
	@echo "Instalando deps JS (local)..."
	npm pkg set type="module" >/dev/null 2>&1 || true
	npm i -D typescript ts-node ts-morph glob eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin eslint-plugin-import \
		@types/node jest ts-jest biome >/dev/null 2>&1 || true
	@echo "Instale também via pip/venv: semgrep schemathesis hypothesis pytest pynguin"

fix: ts-codefix lint-fix semgrep-fix codemods
pre-llm: fix ## alias

pre-llm-metrics:
	@echo ">> medindo correções por etapa (tsserver/eslint/semgrep/codemods) e gravando em .metrics"
	@python3 tools/fixer/metrics_wrapper.py || true

metrics-report:
	@echo ">> gerando relatório de métricas acumuladas"
	@python3 analyze_metrics.py

metrics-up:
	docker compose -f metrics/docker-compose.yml up -d

metrics-down:
	docker compose -f metrics/docker-compose.yml down

metrics-open:
	@echo "Prometheus: http://localhost:9090   Grafana: http://localhost:3000 (admin/admin)"

ts-codefix:
	npx ts-node tools/fixer/tsserver_fix.ts || true

lint-fix:
	npx eslint . --fix || true
	npx biome check . --apply --diagnostic-level=info || true

semgrep-fix:
	semgrep scan --config tools/semgrep/ts-react.yml --autofix || true
	semgrep scan --config tools/semgrep/python-fastapi.yml --autofix || true

codemods:
	npx ts-node tools/codemods/tsmods.ts || true

getafix:
	python3 tools/getafix/miner.py

apr:
	python3 tools/apr/run_apr.py

api-fuzz:
	python3 tools/api/schemathesis_run.py

testgen:
	python3 tools/testgen/hypothesis_skeleton.py || true
	@echo "Para TS, copie tools/testgen/fastcheck.template.ts e ajuste $$MODULE e $$FUNCTION"

mutation:
	npx stryker run || true

static-advanced:
	tools/static/infer/run.sh || true
	tools/static/pysa/run.sh || true

# Pipeline completa (1→11)
fix-all: fix getafix apr api-fuzz testgen mutation static-advanced
