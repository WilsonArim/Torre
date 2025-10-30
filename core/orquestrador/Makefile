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


