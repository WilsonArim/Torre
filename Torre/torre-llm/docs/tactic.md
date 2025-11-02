---
pipeline: quality
stage: 1
objective: "Remover crash 'ReferenceError: base is not defined' em SettingsPage via shim local e validar render"
context_mode: smart
max_kb: 256
commit_style: "conv"
lang: pt
constraints:
  - "NÃO editar: .env, .ssh, *.pem, id_rsa, secrets.*"
  - "Gerar APENAS um bloco ```diff``` no final"
  - "Mudanças mínimas e cirúrgicas"
acceptance:
  - "App deixa de lançar ReferenceError em SettingsPage"
  - "Lint clean no escopo tocado"
  - "UM único diff aplicável"
repo_root: "."
fallback_strategy: "Se bloqueado → MISSING:<item> e parar"
notes:
  - "Shim de base com fallback: __FORTALEZA_BASE__ → import.meta.env.BASE_URL → '/'"
---
## Premissas & Invariantes
- Projeto Vite/Tauri expõe `import.meta.env.BASE_URL`.
- Evitar alterações globais fora do ficheiro afetado.

## Contratos (funções críticas)
- Pré: `src/components/SettingsPage.tsx` existe (ou será criado).
- Pós: `base` definido em runtime; componente renderiza sem crash.

## Esboço Algorítmico
- Inserir shim no topo do ficheiro; persistir em `globalThis.__FORTALEZA_BASE__`.
- Smoke manual: arrancar app, abrir Settings, confirmar ausência de erro.

## Threat Model (curto)
- Regressão: Garantir idempotência do shim (verificação de global antes de set).

## Plano de Testes
- smoke: `npm run dev` → abrir Settings → consola sem `ReferenceError`.
- unit (futuro): helper para normalizar base.
