import re
from typing import Tuple, Optional

# AUTO: imports "seguros" (idempotentes) por símbolo
SAFE_IMPORTS = {
    "React": "react",
    "useState": "react",
    "useEffect": "react",
    "useMemo": "react",
    "useRef": "react",
    "useCallback": "react",
    "useLayoutEffect": "react",
    "useContext": "react",
    "useReducer": "react",
    # React 18 createRoot
    "createRoot": "react-dom/client",
    # test globals — por omissão vitest; pode ser sobreposto via prefer_pkg
    "describe": "vitest",
    "it": "vitest",
    "test": "vitest",
    "expect": "vitest",
    "vi": "vitest",
}

_RE_IMPORT_LINE = re.compile(r"^\s*import\s+.+?from\s+['\"][^'\"]+['\"];?\s*$")

def _has_symbol_in_any_import(source: str, symbol: str) -> bool:
    # Procura símbolo já importado (named ou default) de forma simples
    sym_re = re.compile(rf"\b{re.escape(symbol)}\b")
    for line in source.splitlines()[:100]:  # só cabeçalho
        if _RE_IMPORT_LINE.match(line) and sym_re.search(line):
            return True
    return False

def _merge_or_add_named_import(source: str, symbol: str, pkg: str) -> str:
    """
    Se já existir import do mesmo pacote, funde o símbolo no bloco named.
    Caso contrário, adiciona uma nova linha import.
    """
    lines = source.splitlines()
    pkg_re = re.compile(rf"^\s*import\s+(?P<body>.+?)\s+from\s+['\"]{re.escape(pkg)}['\"];?\s*$")
    for i, line in enumerate(lines[:100]):
        m = pkg_re.match(line)
        if not m:
            continue
        body = m.group("body")
        # import React from 'react'
        if "{" not in body and "}" not in body:
            # já existe default; se símbolo != default, converte para default + named
            default_sym = body.strip()
            if default_sym == symbol:
                return source  # nada a fazer
            new_line = f"import {default_sym}, {{ {symbol} }} from '{pkg}';"
            lines[i] = new_line
            return "\n".join(lines)
        # import { a, b } from 'react'
        body_clean = body.strip().strip("{}").strip()
        parts = [p.strip() for p in body_clean.split(",") if p.strip()]
        if symbol in parts:
            return source
        parts.append(symbol)
        parts_sorted = sorted(set(parts))
        lines[i] = f"import {{ {', '.join(parts_sorted)} }} from '{pkg}';"
        return "\n".join(lines)
    # não há import do pacote → adicionar no topo, após bloco de imports existente
    insert_at = 0
    for i, line in enumerate(lines[:200]):
        if _RE_IMPORT_LINE.match(line):
            insert_at = i + 1
    lines.insert(insert_at, f"import {{ {symbol} }} from '{pkg}';")
    return "\n".join(lines)

def ensure_import(source: str, symbol: str, *, prefer_pkg: Optional[str] = None) -> Tuple[str, bool]:
    """
    Garante import idempotente do `symbol` se estiver no SAFE_IMPORTS.
    Retorna (novo_source, changed).
    """
    pkg = prefer_pkg or SAFE_IMPORTS.get(symbol)
    if not pkg:
        return source, False
    if _has_symbol_in_any_import(source, symbol):
        return source, False
    # Caso React em .tsx sem import — preferir default React para setups antigos
    if symbol == "React":
        # se já houver import {..} from 'react', fazer merge como default + named
        # senão, adicionar default direto
        lines = source.splitlines()
        pkg_re = re.compile(r"^\s*import\s+(.+?)\s+from\s+['\"]react['\"];?\s*$")
        for i, line in enumerate(lines[:100]):
            m = pkg_re.match(line)
            if m:
                body = m.group(1)
                if "{" in body or "}" in body:
                    lines[i] = f"import React, {body} from 'react';".replace(", {", ", {")
                else:
                    # já há default mas não é React? (raro) — substituir com React
                    lines[i] = "import React from 'react';"
                return "\n".join(lines), True
        # adicionar default import React no topo
        insert_at = 0
        for i, line in enumerate(lines[:200]):
            if _RE_IMPORT_LINE.match(line):
                insert_at = i + 1
        lines.insert(insert_at, "import React from 'react';")
        return "\n".join(lines), True
    # Demais símbolos → named import seguro
    return _merge_or_add_named_import(source, symbol, pkg), True
