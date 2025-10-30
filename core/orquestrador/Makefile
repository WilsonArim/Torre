SHELL := /bin/bash
export PYTHONPATH := $(PWD)/../..

precommit:
	pre-commit run --all-files || true

test:
	coverage run -m pytest -q || true
	coverage xml || true

lint:
	npm run -s lint || true

security:
	semgrep --config auto --sarif -o ../../relatorios/semgrep.sarif || true
	bandit -q -r ../.. -f json -o ../../relatorios/bandit.json || true
	npm audit --json > ../../relatorios/npm-audit.json || true
	trivy fs --format json -o ../../relatorios/trivy.json ../.. || true

sbom:
	cyclonedx-bom -o ../../relatorios/sbom.json || true

sop: test lint security sbom
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
	python3 cli.py gatekeeper_prep

gatekeeper_run:
	@echo "🔎 Running automated Gatekeeper (Composer Edition)..."
	make -C core/orquestrador gatekeeper_prep
	bash ordem/gatekeeper.sh
	@echo "✅ Gatekeeper completed. See relatorios/parecer_gatekeeper.md"

review_codex:
	@echo "🧠 Running ethical review with Codex (GPT-4o)..."
	python3 core/orquestrador/cli.py review_codex
	@echo "✅ Codex review completed. See relatorios/parecer_gatekeeper_codex.md"


