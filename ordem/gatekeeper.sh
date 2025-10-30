#!/bin/bash
set -e
ROOT=$(dirname "$0")/..
cd "$ROOT"
echo "🔎 Gatekeeper audit started..."
make -C core/orquestrador gatekeeper_prep
SOP_JSON="relatorios/sop_status.json"
PIPE_JSON="relatorios/pipeline_gate_input.json"
OUT="relatorios/parecer_gatekeeper.md"
SOP_STATUS=$(jq -r '.status' "$SOP_JSON")
PIPE_OK=$(jq -r '.pipeline_ok' "$PIPE_JSON")
if [[ "$SOP_STATUS" != "PASS" || "$PIPE_OK" != "true" ]]; then
  echo "DECISÃO: VETO" > "$OUT"
  echo "Motivo: SOP bloqueado ou pipeline inválida." >> "$OUT"
  echo "Ver relatórios: $SOP_JSON, $PIPE_JSON" >> "$OUT"
  echo "❌ Gatekeeper VETO emitido."
  exit 1
fi
echo "DECISÃO: APROVADO" > "$OUT"
echo "Risco residual: Nenhum identificado." >> "$OUT"
echo "Justificação: Cobertura, SBOM e pipeline em conformidade com as Leis SOP v2." >> "$OUT"
echo "Assinado: Gatekeeper (Composer Edition)" >> "$OUT"
echo "✅ Gatekeeper aprovado com sucesso."

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
