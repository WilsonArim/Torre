# ADVICE — Fortaleza LLM-Engenheira

## Dicas priorizadas

- `ReferenceError: base is not defined` → definir shim seguro (Vite/Tauri) no topo do ficheiro que usa `base`:

```ts
const base: string =
  ((globalThis as any).__FORTALEZA_BASE__ as string) ??
  ((import.meta as any)?.env?.BASE_URL as string) ??
  "/";
(globalThis as any).__FORTALEZA_BASE__ = base;
```

- Module not found: `./components/Button` → verificar caminho relativo/alias (tsconfig/vite.config) ou instalar dependência (npm/pnpm).
