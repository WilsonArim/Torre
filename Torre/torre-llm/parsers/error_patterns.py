from __future__ import annotations
import re
from typing import List, Dict

# Padrões comuns em Vite/React/TypeScript/ESLint/Jest/Pytest
RX = {
    "ref_is_not_defined": re.compile(r"(?:Uncaught\s+)?ReferenceError:\s*(?P<name>[A-Za-z_]\w*)\s+is\s+not\s+defined"),
    "ts_cannot_find_name": re.compile(r"Cannot\s+find\s+name\s+'(?P<name>[^']+)'"),
    "module_not_found": re.compile(r"Module\s+not\s+found:\s*Can't\s+resolve\s+['\"](?P<mod>[^'\"]+)['\"]"),
    "react_hook_rule": re.compile(r"React\s+Hook\s+['\"]?(?P<hook>use\w+)['\"]?\s+is\s+called\s+in\s+function\s+['\"]?(?P<fn>[^'\"()]+)"),
    "eslint_unused": re.compile(r"no-unused-vars"),
    "parsing_error": re.compile(r"Parsing error:\s*(?P<msg>.+)"),
}

def _hint_for_reference(name: str) -> str:
    if name == "base":
        return ("`ReferenceError: base is not defined` → "
                "definir shim seguro (Vite/Tauri) no topo do ficheiro que usa `base`:\n"
                "```ts\n"
                "const base: string = ((globalThis as any).__TORRE_BASE__ as string)\n"
                "  ?? (((import.meta as any)?.env?.BASE_URL as string) ?? '/');\n"
                "(globalThis as any).__TORRE_BASE__ = base;\n"
                "```\n")
    return (f"`ReferenceError: {name} is not defined` → importar/definir `{name}`; "
            "se global, declarar tipo em `global.d.ts`.")

def _hint_for_ts_name(name: str) -> str:
    return (f"TypeScript: `Cannot find name '{name}'` → adicionar import, "
            f"ou declarar como global em `global.d.ts` se aplicável.")

def _hint_for_module(mod: str) -> str:
    return (f"Module not found: `{mod}` → verificar caminho relativo/alias (tsconfig/vite.config) "
            "ou instalar dependência (npm/pnpm).")

def _hint_for_hook(hook: str, fn: str) -> str:
    return (f"Regra React Hooks: `{hook}` usado em `{fn}` → mover hooks para o topo do componente "
            "ou converter função para componente custom hook.")

def extract_hints(log_text: str) -> List[str]:
    """Extrai dicas acionáveis a partir do texto de logs."""
    hints: List[str] = []
    seen: Dict[str, bool] = {}

    for m in RX["ref_is_not_defined"].finditer(log_text):
        name = m.group("name")
        h = _hint_for_reference(name)
        if h not in seen:
            hints.append(h); seen[h] = True

    for m in RX["ts_cannot_find_name"].finditer(log_text):
        name = m.group("name")
        h = _hint_for_ts_name(name)
        if h not in seen:
            hints.append(h); seen[h] = True

    for m in RX["module_not_found"].finditer(log_text):
        mod = m.group("mod")
        h = _hint_for_module(mod)
        if h not in seen:
            hints.append(h); seen[h] = True

    for m in RX["react_hook_rule"].finditer(log_text):
        h = _hint_for_hook(m.group("hook"), m.group("fn"))
        if h not in seen:
            hints.append(h); seen[h] = True

    if RX["eslint_unused"].search(log_text):
        hints.append("ESLint: `no-unused-vars` → remover variáveis não usadas ou prefixar com `_`.")

    for m in RX["parsing_error"].finditer(log_text):
        msg = m.group("msg")
        h = f"Parsing error: {msg} → rever sintaxe/TSConfig/ESLint parser."
        if h not in seen:
            hints.append(h); seen[h] = True

    # Prioridade simples: ReferenceError/Module not found primeiro
    hints.sort(key=lambda s: (0 if "ReferenceError" in s else 1 if "Module not found" in s else 2))
    return hints
