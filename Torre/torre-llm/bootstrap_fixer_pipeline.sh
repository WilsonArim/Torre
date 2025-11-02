#!/usr/bin/env bash
set -euo pipefail

echo "==> Bootstrap da pipeline de correção (11 pontos)..."

mkdir -p tools/fixer tools/codemods tools/semgrep rules tools/getafix tools/apr tools/api tools/testgen tsconfig .github/workflows
mkdir -p tools/static/infer tools/static/pysa
mkdir -p tests/api tests/generated
mkdir -p .fortaleza/memory .fortaleza/out

########################################
# 1) TypeScript CodeFix (tsserver)
########################################
cat > tools/fixer/tsserver_fix.ts <<'TS'
import ts from "typescript";
import { glob } from "glob";
import * as fs from "fs";
import * as path from "path";

/** Executa CodeFix do tsserver em arquivos .ts/.tsx do projeto. */
async function main() {
  const files = (await glob("**/*.{ts,tsx}", { ignore: ["**/node_modules/**", "**/dist/**"] }))
    .map(f => path.resolve(f));
  if (files.length === 0) return;

  const configPath = ts.findConfigFile(process.cwd(), ts.sys.fileExists, "tsconfig.json");
  const config = configPath ? ts.readConfigFile(configPath, ts.sys.readFile).config : { compilerOptions: { strict: true } };
  const parsed = ts.parseJsonConfigFileContent(config, ts.sys, process.cwd());
  const host: ts.LanguageServiceHost = {
    getCompilationSettings: () => parsed.options,
    getScriptFileNames: () => Array.from(new Set([...files, ...parsed.fileNames])),
    getScriptVersion: () => "1",
    getScriptSnapshot: (fileName) => {
      if (!fs.existsSync(fileName)) return undefined;
      return ts.ScriptSnapshot.fromString(fs.readFileSync(fileName, "utf8"));
    },
    getCurrentDirectory: () => process.cwd(),
    getDefaultLibFileName: (opts) => ts.getDefaultLibFilePath(opts),
    fileExists: ts.sys.fileExists,
    readFile: ts.sys.readFile,
    readDirectory: ts.sys.readDirectory,
    directoryExists: ts.sys.directoryExists,
    getDirectories: ts.sys.getDirectories,
  };
  const ls = ts.createLanguageService(host, ts.createDocumentRegistry());

  const fixable = new Set<number>([
    2304, // Cannot find name
    2307, // Cannot find module
    2322, 2345, // type assign issues
    2552, 2551, // missing property/rename
  ]);

  let applied = 0;
  for (const f of files) {
    const diags = [
      ...ls.getSyntacticDiagnostics(f),
      ...ls.getSemanticDiagnostics(f),
      ...ls.getSuggestionDiagnostics(f),
    ].filter(d => fixable.has((d as any).code));

    if (diags.length === 0) continue;

    let content = fs.readFileSync(f, "utf8");
    for (const d of diags) {
      const start = d.start ?? 0;
      const len = d.length ?? 0;
      const fixes = ls.getCodeFixesAtPosition(
        f, start, start + len, [ (d as any).code ],
        {}, {}
      );
      if (!fixes.length) continue;

      // usa o 1º fix com CombinedCodeAction quando possível
      const change = fixes[0];
      const changes = (change as any).changes ?? change.fixName ? fixes.flatMap(x => (x as any).changes) : [];
      for (const c of changes) {
        if (c.fileName !== f) continue;
        // aplicar na memória (da última para a primeira para não deslocar offsets)
        const edits = [...c.textChanges].sort((a,b)=> (b.span.start - a.span.start));
        for (const e of edits) {
          const head = content.slice(0, e.span.start);
          const tail = content.slice(e.span.start + e.span.length);
          content = head + e.newText + tail;
          applied++;
        }
      }
    }
    if (applied > 0) fs.writeFileSync(f, content, "utf8");
  }
  console.log(JSON.stringify({ ok:true, applied }, null, 2));
}
main().catch(e => { console.error(e); process.exit(1); });
TS

########################################
# 2) ESLint / Biome autofix
########################################
cat > .eslintrc.cjs <<'ESL'
module.exports = {
  root: true,
  parser: '@typescript-eslint/parser',
  plugins: ['@typescript-eslint','import'],
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:import/recommended',
    'plugin:import/typescript'
  ],
  rules: {
    'no-unused-vars': 'off',
    '@typescript-eslint/no-unused-vars': ['error',{ argsIgnorePattern: '^_', varsIgnorePattern: '^_' }],
    'import/order': ['warn', { 'newlines-between':'always','alphabetize':{order:'asc'} }],
  },
  ignorePatterns: ['dist','node_modules','**/*.d.ts']
}
ESL

cat > biome.json <<'BIOME'
{
  "$schema": "https://biomejs.dev/schemas/1.6.0/schema.json",
  "formatter": { "enabled": true },
  "linter": { "enabled": true, "rules": { "suspicious": { "noDuplicateObjectKeys": "error" } } }
}
BIOME

########################################
# 3) Semgrep com autofix (TS/React + FastAPI)
########################################
cat > tools/semgrep/ts-react.yml <<'YAML'
rules:
  - id: ts-missing-react-import
    languages: [typescript, javascript]
    message: "Add missing React import (auto-fix)"
    pattern: |
      export default function $COMP($ARGS...) { ... }
    fix: |
      import React from 'react';
      export default function $COMP($ARGS...) { ... }
    severity: INFO

  - id: fetch-no-unsafe-http
    languages: [typescript, javascript]
    message: "Use https in fetch URLs"
    pattern: fetch("http://$HOST/$PATH", ...)
    fix: fetch("https://$HOST/$PATH", ...)
    severity: WARNING
YAML

cat > tools/semgrep/python-fastapi.yml <<'YAML'
rules:
  - id: fastapi-path-join
    languages: [python]
    message: "Use os.path.join or pathlib for path concatenation (auto-fix)"
    pattern: os.path.dirname(__file__) + "/$SUF"
    fix: os.path.join(os.path.dirname(__file__), "$SUF")
    severity: WARNING
YAML

########################################
# 4) ts-morph codemods (registry)
########################################
cat > tools/codemods/registry.json <<'JSON'
{
  "TS2304": ["missingSymbolImport"],
  "TS2307": ["createRelativeImportIfExists"]
}
JSON

cat > tools/codemods/tsmods.ts <<'TS'
import { Project, SyntaxKind } from "ts-morph";
import * as fs from "fs";

type Result = { codemod: string, file: string, edits: number };

export async function missingSymbolImport(project: Project, file: string): Promise<Result> {
  const src = project.getSourceFileOrThrow(file);
  let edits = 0;
  // Heurística simples: se há JSX e não tem React import, adiciona
  const hasJSX = !!src.getDescendantsOfKind(SyntaxKind.JsxOpeningElement).length;
  const hasReactImport = src.getImportDeclarations().some(i => i.getModuleSpecifierValue() === "react");
  if (hasJSX && !hasReactImport) {
    src.insertText(0, "import React from 'react';\n");
    edits++;
  }
  return { codemod: "missingSymbolImport", file, edits };
}

export async function createRelativeImportIfExists(project: Project, file: string): Promise<Result> {
  const src = project.getSourceFileOrThrow(file);
  let edits = 0;
  // Corrige imports "./X" ausentes quando o arquivo existe
  for (const imp of src.getImportDeclarations()) {
    const spec = imp.getModuleSpecifierValue();
    if (spec.startsWith(".")) {
      // no-op
    } else if (!spec.includes("/")) {
      // tenta localizar arquivo ao lado
      const base = src.getDirectoryPath();
      const guess = `${base}/${spec}.ts`;
      if (fs.existsSync(guess)) {
        imp.setModuleSpecifier(`./${spec}`);
        edits++;
      }
    }
  }
  return { codemod: "createRelativeImportIfExists", file, edits };
}

if (require.main === module) {
  const globs = process.argv.slice(2);
  const project = new Project({ tsConfigFilePath: "tsconfig.json", skipAddingFilesFromTsConfig: false });
  const files = globs.length ? globs : project.getSourceFiles().map(f => f.getFilePath());
  const tasks: Promise<Result>[] = [];
  for (const f of files) {
    tasks.push(missingSymbolImport(project, f));
    tasks.push(createRelativeImportIfExists(project, f));
  }
  Promise.all(tasks).then(() => project.save()).then(()=> {
    console.log(JSON.stringify({ ok:true, files: files.length }));
  });
}
TS

########################################
# 5) CodeQL (JS/TS + Python) — workflow
########################################
cat > .github/workflows/codeql.yml <<'YML'
name: codeql
on:
  pull_request:
  push:
    branches: [ main, master ]
jobs:
  analyze:
    runs-on: ubuntu-latest
    permissions:
      security-events: write
      actions: read
      contents: read
    strategy:
      matrix:
        language: [ 'javascript-typescript', 'python' ]
    steps:
      - uses: actions/checkout@v4
      - uses: github/codeql-action/init@v3
        with: { languages: ${{ matrix.language }} }
      - uses: github/codeql-action/autobuild@v3
      - uses: github/codeql-action/analyze@v3
YML

########################################
# 6) Getafix-lite (minerador de padrões de edição)
########################################
cat > tools/getafix/miner.py <<'PY'
#!/usr/bin/env python3
# Lê .fortaleza/memory/episodes.jsonl e minera "edit patterns" simples (diff hunks) por código de erro.
import json, re, sys, os
from collections import defaultdict, Counter
EP_FILE = ".fortaleza/memory/episodes.jsonl"
OUT_FILE = ".fortaleza/memory/patterns.json"

def normalize_hunk(h):
  # remove nomes e números muito específicos
  h = re.sub(r'([A-Za-z_][A-Za-z0-9_]{2,})', '<ID>', h)
  h = re.sub(r'\b\d+\b', '<NUM>', h)
  return h

def main():
  if not os.path.exists(EP_FILE):
    print(json.dumps({"ok":True,"patterns":0,"note":"no episodes"})); return
  pats = defaultdict(Counter)
  with open(EP_FILE) as f:
    for line in f:
      try:
        ep = json.loads(line)
      except: 
        continue
      err = ep.get("err_code") or ep.get("error_code") or "UNKNOWN"
      diff = ep.get("diff") or ep.get("patch") or ""
      for h in re.findall(r'(^@@.*?$\n(?:[ +\-].*?\n)+)', diff, flags=re.M|re.S):
        pats[err][normalize_hunk(h)] += 1
  top = {k: [h for h,_ in v.most_common(8)] for k,v in pats.items()}
  os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
  with open(OUT_FILE,"w") as f: json.dump(top,f,indent=2)
  print(json.dumps({"ok":True,"rules":sum(len(v) for v in top.values())}))
if __name__=="__main__": main()
PY
chmod +x tools/getafix/miner.py

########################################
# 7) SapFix-style APR (templates + validação)
########################################
cat > tools/apr/run_apr.py <<'PY'
#!/usr/bin/env python3
import json, os, subprocess, sys, tempfile, time
from pathlib import Path

TEMPLATES = ".fortaleza/memory/patterns.json"
def run(cmd, timeout=120):
  try:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
  except subprocess.TimeoutExpired as e:
    return e

def try_templates(files_glob="src/**/*.ts*"):
  if not os.path.exists(TEMPLATES):
    return {"ok": True, "attempts":0, "applied":0}
  patterns = json.load(open(TEMPLATES))
  applied = 0; attempts = 0
  # simples: procurar símbolos óbvios
  for err, hunks in patterns.items():
    for h in hunks[:4]:
      attempts += 1
      # aqui poderíamos aplicar codemods equivalentes; guardamos placeholder
  return {"ok":True,"attempts":attempts,"applied":applied}

def validate():
  # valida com npm test se houver; senão, pytest; senão build
  cmds = [["npm","test","--silent","--","-w", "1"], ["pytest","-q"], ["npm","run","-s","build"]]
  for c in cmds:
    r = run(c, timeout=600)
    if isinstance(r, subprocess.TimeoutExpired): return {"ok":False,"stage":"timeout","code":124}
    if r.returncode == 0: return {"ok":True,"stage":"tests"}
  return {"ok":False,"stage":"all_failed"}

if __name__=="__main__":
  out = {"templates": try_templates(), "validation": validate()}
  print(json.dumps(out))
PY
chmod +x tools/apr/run_apr.py

########################################
# 8) Schemathesis (FastAPI/OpenAPI fuzz)
########################################
cat > tools/api/schemathesis_run.py <<'PY'
#!/usr/bin/env python3
import os, json, subprocess, sys
OPENAPI = os.environ.get("OPENAPI_URL","http://localhost:8765/openapi.json")
CMD = ["schemathesis","run", OPENAPI, "--checks","all", "--hypothesis-max-examples=50", "--report","./.fortaleza/out/schemathesis.json"]
rc = subprocess.call(CMD)
print(json.dumps({"ok": rc==0, "rc": rc, "openapi": OPENAPI}))
sys.exit(0)
PY
chmod +x tools/api/schemathesis_run.py

########################################
# 9) Test-gen (Hypothesis/Pynguin/fast-check)
########################################
cat > tools/testgen/hypothesis_skeleton.py <<'PY'
# Gera esqueleto de property tests para funções puras detectadas rapidamente.
import inspect, importlib, sys, json, os
from pathlib import Path
TGT = os.environ.get("PY_MODULE","app.utils")  # ajusta no uso
mod = importlib.import_module(TGT)
tests=[]
for name, fn in inspect.getmembers(mod, inspect.isfunction):
    src = inspect.getsource(fn)
    if "requests" in src or "os." in src: 
        continue
    tests.append(f"""
from hypothesis import given, strategies as st
from {TGT} import {name}
def test_{name}_no_crash():
    # TODO: refinar geradores conforme assinatura
    {name}(*[])
""")
Path("tests/generated").mkdir(parents=True, exist_ok=True)
Path(f"tests/generated/test_{TGT.replace('.','_')}_props.py").write_text("\\n".join(tests))
print(json.dumps({"ok":True,"generated":len(tests)}))
PY

cat > tools/testgen/fastcheck.template.ts <<'TS'
import fc from "fast-check";
import { $$FUNCTION$$ } from "$$MODULE$$";

test("property: $$FUNCTION$$ no throw", () => {
  fc.assert(
    fc.property(fc.anything(), (x:any) => {
      $$FUNCTION$$(x);
      return true;
    })
  );
});
TS

########################################
# 10) Mutation Testing (Stryker)
########################################
cat > stryker.conf.json <<'JSON'
{
  "$schema": "https://stryker-mutator.io/schema/stryker.schema.json",
  "mutate": ["src/**/*.ts?(x)"],
  "testRunner": "jest",
  "coverageAnalysis": "off",
  "reporters": ["html","clear-text","progress"],
  "tsconfigFile": "tsconfig.json",
  "jest": { "projectType": "custom", "configFile": "jest.config.js" }
}
JSON

########################################
# 11) Infer & Pysa (estática avançada) — scripts
########################################
cat > tools/static/infer/run.sh <<'SH'
#!/usr/bin/env bash
set -euo pipefail
if ! command -v infer >/dev/null; then echo "infer não instalado"; exit 0; fi
infer run --reactive -- flutter || true
infer run -- javac $(git ls-files '*.java') || true
SH
chmod +x tools/static/infer/run.sh

cat > tools/static/pysa/run.sh <<'SH'
#!/usr/bin/env bash
set -euo pipefail
if ! command -v pyre >/dev/null; then echo "pyre não instalado"; exit 0; fi
pyre analyze --no-verify | tee .fortaleza/out/pysa.txt || true
SH
chmod +x tools/static/pysa/run.sh

########################################
# Makefile — orquestra tudo (Fixer Cascade + avançados)
########################################
cat > Makefile <<'MK'
SHELL := /bin/bash

bootstrap:
	@echo "Instalando deps JS (local)..."
	npm pkg set type="module" >/dev/null 2>&1 || true
	npm i -D typescript ts-node ts-morph glob eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin eslint-plugin-import \
		@types/node jest ts-jest biome >/dev/null 2>&1 || true
	@echo "Instale também via pip/venv: semgrep schemathesis hypothesis pytest pynguin"

fix: ts-codefix lint-fix semgrep-fix codemods
pre-llm: fix ## alias

ts-codefix:
	npx ts-node tools/fixer/tsserver_fix.ts || true

lint-fix:
	npx eslint . --ext .ts,.tsx --fix || true
	npx biome check . --apply --diagnostic-level=info || true

semgrep-fix:
	semgrep --config tools/semgrep/ts-react.yml --fix || true
	semgrep --config tools/semgrep/python-fastapi.yml --fix || true

codemods:
	npx ts-node tools/codemods/tsmods.ts || true

getafix:
	python3 tools/getafix/miner.py

apr:
	python3 tools/apr/run_apr.py

api-fuzz:
	python3 tools/api/schemathesis_run.py

testgen:
	python3 tools/testgen/hypothesis_skeleton.py || true
	@echo "Para TS, copie tools/testgen/fastcheck.template.ts e ajuste $$MODULE e $$FUNCTION"

mutation:
	npx stryker run || true

static-advanced:
	tools/static/infer/run.sh || true
	tools/static/pysa/run.sh || true

# Pipeline completa (1→11)
fix-all: fix getafix apr api-fuzz testgen mutation static-advanced
MK

########################################
# Jest config mínimo (necessário p/ Stryker)
########################################
cat > jest.config.js <<'JS'
module.exports = {
  testEnvironment: "node",
  transform: { "^.+\\.(ts|tsx)$": ["ts-jest", { tsconfig: "tsconfig.json" }] },
  testMatch: ["**/?(*.)+(spec|test).[tj]s?(x)"]
};
JS

########################################
# tsconfig base (se não existir)
########################################
if [ ! -f tsconfig.json ]; then
cat > tsconfig.json <<'JSON'
{
  "compilerOptions": {
    "target": "ES2021",
    "module": "ES2020",
    "moduleResolution": "Node",
    "jsx": "react-jsx",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "outDir": "dist"
  },
  "include": ["src","tools"]
}
JSON
fi

echo "==> Pronto. Use:  make pre-llm   # executa 1→4 antes do LLM"
