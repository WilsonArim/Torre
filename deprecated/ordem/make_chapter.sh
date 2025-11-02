#!/usr/bin/env bash
set -euo pipefail
# Uso: ./ordem/make_chapter.sh Mxx <slug>
if [ $# -ne 2 ]; then echo "Uso: $0 Mxx <slug>"; exit 1; fi
M="$1"; SLUG="$2"
[[ "$M" =~ ^M[0-9]{2}$ ]] || { echo "Capítulo inválido (ex.: M01)"; exit 1; }
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TPL="$ROOT/pipeline/_templates/CHAPTER.md"
DST_DIR="$ROOT/pipeline/modulos/${M}-${SLUG}"
DST="$DST_DIR/${M}.md"
mkdir -p "$DST_DIR"
ID="$(date +%F)-$(printf "%03d" $(( RANDOM % 900 + 100 )))"
# DEPRECATED — NÃO USAR. Substituído por core/orquestrador/cli.py e Makefile.
exit 1
# HEADER fill
awk -v ID="$ID" -v M="$M" '
BEGIN{FS=OFS="\n"}
{gsub(/YYYY-MM-DD-XXX/, ID)}
1
' "$TPL" > "$DST"
echo "Criado: ${DST}"
