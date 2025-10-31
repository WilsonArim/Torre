#!/usr/bin/env bash
set -euo pipefail
# Uso: ./ordem/make_task.sh Mxx Eyy Tzzz <slug>
if [ $# -ne 4 ]; then echo "Uso: $0 Mxx Eyy Tzzz <slug>"; exit 1; fi
M="$1"; E="$2"; T="$3"; SLUG="$4"
[[ "$M" =~ ^M[0-9]{2}$ ]] || { echo "Capítulo inválido (ex.: M01)"; exit 1; }
[[ "$E" =~ ^E[0-9]{2}$ ]] || { echo "Etapa inválida (ex.: E01)"; exit 1; }
[[ "$T" =~ ^T[0-9]{3}$ ]] || { echo "Tarefa inválida (ex.: T001)"; exit 1; }
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TPL="$ROOT/pipeline/_templates/TASK.md"
BASE="$ROOT/pipeline/modulos"
MOD_DIR="$(find "$BASE" -maxdepth 1 -type d -name "${M}-*" | head -n1)"
[ -n "$MOD_DIR" ] || { echo "Capítulo ${M} não encontrado. Crie-o primeiro."; exit 1; }
STG_DIR="$(find "$MOD_DIR/etapas" -maxdepth 1 -type d -name "${E}-*" | head -n1)"
[ -n "$STG_DIR" ] || { echo "Etapa ${E} não encontrada. Crie-a primeiro."; exit 1; }
DST_DIR="$STG_DIR/tarefas/${T}-${SLUG}"
DST="$DST_DIR/${T}.md"
mkdir -p "$DST_DIR"
ID="$(date +%F)-$(printf "%03d" $(( RANDOM % 900 + 100 )))"
awk -v ID="$ID" -v M="$M" -v E="$E" '
{gsub(/YYYY-MM-DD-XXX/, ID);
 gsub(/CAPITULO_PAI: Mxx/, "CAPITULO_PAI: " M);
 gsub(/ETAPA_PAI: Eyy/, "ETAPA_PAI: " E)}1
' "$TPL" > "$DST"
echo "Criado: ${DST}"
