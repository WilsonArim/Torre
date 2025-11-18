// Arquivo de teste para demonstrar métricas da pipeline
// import React from "react"; // Commented out - unused import
export default function MetricsTest() {
  return <div>Test</div>;
}

// Variável não utilizada (será corrigida pelo ESLint)
// const unusedVar = "test"; // Commented out - unused variable

// Fetch com HTTP inseguro (será corrigido pelo Semgrep)
fetch("http://insecure-api.com/data");
