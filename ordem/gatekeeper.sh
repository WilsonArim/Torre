#!/usr/bin/env bash
set -euo pipefail

# preparar inputs do Gatekeeper
make -C core/orquestrador gatekeeper_prep

PIPE_INPUT="relatorios/pipeline_gate_input.json"
if [ -f "$PIPE_INPUT" ]; then
  PIPE_OK=$(jq -r '.pipeline_ok' "$PIPE_INPUT" 2>/dev/null || echo "false")
else
  PIPE_OK="false"
fi

if grep -q "DECISÃO_SOP: BLOQUEADO" relatorios/relatorio_sop.md 2>/dev/null || [ "$PIPE_OK" != "true" ]; then
  echo -e "DECISÃO: VETO\nMotivo: SOP BLOQUEADO ou pipeline inválida.\nVer: relatorios/pipeline_audit.json" > relatorios/parecer_gatekeeper.md
  exit 1
fi

echo -e "DECISÃO: APROVADO\nPipeline: OK\nVer: pipeline/PIPELINE_TOC.md" > relatorios/parecer_gatekeeper.md
echo "Parecer Gatekeeper emitido em relatorios/parecer_gatekeeper.md"

#!/usr/bin/env bash
set -euo pipefail

echo "🚦 Início do Gatekeeper"

tests=(
  "ESLint::npx eslint ."
  "Prettier::npx prettier -c ."
  "Semgrep::semgrep --config auto"
  "Gitleaks::gitleaks detect --no-git"
  "npm audit::npm audit --audit-level=high"
  "pip-audit::pip-audit -r requirements.txt"
  "Sentry::grep -Riq 'sentry' . && grep -q 'SENTRY_DSN' .env.example"
)

i=1
for test in "${tests[@]}"; do
  name="${test%%::*}"
  cmd="${test##*::}"

  echo "[${i}/7] $name → RUNNING..."
  if eval $cmd; then
    echo "[${i}/7] $name → ✅ PASSOU"
  else
    echo "[${i}/7] $name → ❌ FALHOU"
    echo "   Motivo: comando '$cmd' devolveu erro."
    exit 1
  fi
  i=$((i+1))
done

echo "✅ GATEKEEPER: TODOS OS TESTES PASSARAM"
