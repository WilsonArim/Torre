#!/usr/bin/env bash
set -euo pipefail
if ! command -v pyre >/dev/null; then echo "pyre não instalado"; exit 0; fi
pyre analyze --no-verify | tee .fortaleza/out/pysa.txt || true
