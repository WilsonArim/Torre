#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export REPO_ROOT="${REPO_ROOT:-$ROOT}"
export LLM_SMOKE=1

echo ">> Smoke (offline) — usando fortaleza-llm/llm/cli.py"
python3 -m fortaleza-llm.llm.cli < "$ROOT/fortaleza-llm/examples/smoke_cli.json" | jq .

echo ">> Desative o smoke com: unset LLM_SMOKE"
