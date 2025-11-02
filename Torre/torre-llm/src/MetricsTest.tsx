// Arquivo de teste para demonstrar métricas da pipeline
export default function MetricsTest() {
  return <div>Test</div>
}

// Import no meio do arquivo (será movido para o topo)
import React from 'react'

// Variável não utilizada (será corrigida pelo ESLint)
const unusedVar = "test"

// Fetch com HTTP inseguro (será corrigido pelo Semgrep)
fetch("http://insecure-api.com/data")
