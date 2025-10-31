#!/usr/bin/env bash
set -euo pipefail
# Uso: ./ordem/make_stage.sh Mxx Eyy <slug>
if [ $# -ne 3 ]; then echo "Uso: $0 Mxx Eyy <slug>"; exit 1; fi
M="$1"; E="$2"; SLUG="$3"
[[ "$M" =~ ^M[0-9]{2}$ ]] || { echo "Capítulo inválido (ex.: M01)"; exit 1; }
[[ "$E" =~ ^E[0-9]{2}$ ]] || { echo "Etapa inválida (ex.: E01)"; exit 1; }
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TPL="$ROOT/pipeline/_templates/STAGE.md"
BASE="$ROOT/pipeline/modulos"
MOD_DIR="$(find "$BASE" -maxdepth 1 -type d -name "${M}-*" | head -n1)"
[ -n "$MOD_DIR" ] || { echo "Capítulo ${M} não encontrado. Crie-o primeiro."; exit 1; }
DST_DIR="$MOD_DIR/etapas/${E}-${SLUG}"
DST="$DST_DIR/${E}.md"
mkdir -p "$DST_DIR"
ID="$(date +%F)-$(printf "%03d" $(( RANDOM % 900 + 100 )))"
awk -v ID="$ID" -v M="$M" '
{gsub(/YYYY-MM-DD-XXX/, ID); gsub(/CAPITULO_PAI: Mxx/, "CAPITULO_PAI: " M)}1
' "$TPL" > "$DST"
echo "Criado: ${DST}"
