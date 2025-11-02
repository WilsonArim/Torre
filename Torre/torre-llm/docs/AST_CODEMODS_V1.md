# AST Codemods v1 (TypeScript)

Regras implementadas:

1. **no-unused → prefixar `_`** em variáveis/param declaradas e não usadas.
2. **Missing import** (`Cannot find name 'X'`) → adiciona `import { X } from '<path-relativo>'` se o símbolo existir no índice (`.fortaleza/code_index.json`).
3. **Fix import path** (module not found) → corrige `from './Foo'` para `from './Foo.tsx'` quando o ficheiro existe.

Execução:
- Preferência por **AST (Node + ts-morph)** via `codemods/ts/apply_codemods.mjs`.
- Se Node/ts-morph não disponíveis, aplica **fallback Python** (heurístico) apenas quando seguro.

Garantias:
- **Idempotência**: não duplica `_` nem imports; verifica antes de alterar.
- **Escopo**: só `.ts/.tsx` em `src/**`; sem tocar em paths sensíveis.
- **Reversível**: diffs pequenos e claros.

Limitações v1:
- O mapeamento de imports usa o índice de símbolos (melhorar com AST completo no v2).
- `no-unused` em destructuring complexos é ignorado no fallback.

Como validar:
```bash
python -m fortaleza-llm.run_offline
git apply -p0 .fortaleza/outbox/patch-apply-*.diff --check
```
