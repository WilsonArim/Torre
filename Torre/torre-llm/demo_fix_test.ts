// Arquivo de demonstração com erros TypeScript para testar a pipeline de correção

// Erro TS2307: Cannot find module 'missing-module'
import { something } from 'missing-module';

// Imports que podem ser relativos
import { utils } from 'utils';

// Erro TS2304: Cannot find name 'undefinedVariable'
const result = undefinedVariable + 10;

// Erro TS2322: Type 'string' is not assignable to type 'number'
const numberValue: number = "not a number";

// Erro TS2552: Cannot find name 'console' (será corrigido automaticamente)
console.log("Hello World");

// Componente React sem import do React (será corrigido pelo codemod)
export default function DemoComponent() {
  return React.createElement('div', null, 'Hello World');
}

// Fetch com HTTP inseguro (será corrigido pelo Semgrep)
fetch("http://insecure-api.com/data");
