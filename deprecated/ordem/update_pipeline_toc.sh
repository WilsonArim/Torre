#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BASE="$ROOT/pipeline/modulos"
TOC="$ROOT/pipeline/PIPELINE_TOC.md"
echo "# PIPELINE TOC" > "$TOC"
echo "" >> "$TOC"
shopt -s nullglob
for MOD in "$BASE"/M*-*; do
  [ -d "$MOD" ] || continue
  M="$(basename "$MOD")"
  MFILE="$MOD/${M%%-*}.md"
  MSTATUS="$(grep -iE '^STATUS:\s*' "$MFILE" 2>/dev/null | awk -F': ' '{print $2}' || echo '')"
  echo "## ${M} ${MSTATUS:+(${MSTATUS})}" >> "$TOC"
  [ -d "$MOD/etapas" ] || { echo "" >> "$TOC"; continue; }
  for STG in "$MOD/etapas"/E*-*; do
    [ -d "$STG" ] || continue
    E="$(basename "$STG")"
    EFILE="$STG/${E%%-*}.md"
    ESTATUS="$(grep -iE '^STATUS:\s*' "$EFILE" 2>/dev/null | awk -F': ' '{print $2}' || echo '')"
    REL_E="${EFILE#$ROOT/pipeline/}"
    echo "- [${E} ${ESTATUS:+(${ESTATUS})}](./${REL_E})" >> "$TOC"
    [ -d "$STG/tarefas" ] || continue
    for TSK in "$STG/tarefas"/T*-*; do
      [ -d "$TSK" ] || continue
      T="$(basename "$TSK")"
      TFILE="$TSK/${T%%-*}.md"
      TSTATUS="$(grep -iE '^STATUS:\s*' "$TFILE" 2>/dev/null | awk -F': ' '{print $2}' || echo '')"
      REL_T="${TFILE#$ROOT/pipeline/}"
      echo "  - [${T} ${TSTATUS:+(${TSTATUS})}](./${REL_T})" >> "$TOC"
    done
  done
  echo "" >> "$TOC"
done
echo "TOC atualizado em $TOC"
