#!/usr/bin/env bash

set -euo pipefail

TS="$(date +"%Y%m%d-%H%M%S")"
ARCHIVE_DIR="deprecated/pins-archive/$TS"

mkdir -p "$ARCHIVE_DIR"

# Locais onde normalmente guardamos pins
PIN_DIRS=("factory/pins" "fabrica/pins" "core/pins" "pins" "torre/pins")
found_any=false

for d in "${PIN_DIRS[@]}"; do
  if [ -d "$d" ]; then
    shopt -s nullglob
    files=( "$d"/*.yml "$d"/*.yaml )
    if [ ${#files[@]} -gt 0 ]; then
      found_any=true
      mkdir -p "$ARCHIVE_DIR/$d"
      for f in "${files[@]}"; do
        mv "$f" "$ARCHIVE_DIR/$d/"
      done
    fi
    shopt -u nullglob
  fi
done

# Gera índice simples com hashes
if [ "$found_any" = true ]; then
  ( cd "$ARCHIVE_DIR" && \
    find . -type f -name "*.y*ml" -print0 | xargs -0 sha256sum | sed 's# \*# #' > pins_checksums.sha256 \
  )
fi

echo "✔︎ PINs antigos arquivados em: $ARCHIVE_DIR"
echo "ℹ︎ Coloca agora os 6 PINs v3 nas respetivas pastas."
