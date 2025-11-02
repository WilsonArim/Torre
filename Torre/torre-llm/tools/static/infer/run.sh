#!/usr/bin/env bash
set -euo pipefail
if ! command -v infer >/dev/null; then echo "infer não instalado"; exit 0; fi
infer run --reactive -- flutter || true
infer run -- javac $(git ls-files '*.java') || true
