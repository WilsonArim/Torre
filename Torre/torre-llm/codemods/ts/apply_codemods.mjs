// AST codemods com ts-morph (não escreve em disco; devolve JSON {files:[{path,content}]}).
// Se ts-morph não estiver disponível, termina com código != 0.
import { readFileSync, existsSync } from "node:fs";
import { resolve, dirname, relative } from "node:path";

let Project, SyntaxKind;
try {
  ({ Project, SyntaxKind } = await import("ts-morph"));
} catch (e) {
  process.stderr.write("ts-morph not available\n");
  process.exit(2);
}

const plan = JSON.parse(readFileSync(0, "utf8") || "{}");
const ops = Array.isArray(plan.ops) ? plan.ops : [];

function loadProject(files) {
  const project = new Project({ skipAddingFilesFromTsConfig: true, manipulationSettings: { indentationText: "  " } });
  // Adiciona só ficheiros relevantes para performance
  new Set(files).forEach((f) => {
    if (existsSync(f)) project.addSourceFileAtPath(f);
  });
  return project;
}

function setFromImport(sourceFile, symbol, fromPath) {
  const existing = sourceFile.getImportDeclarations().find((d) => {
    const n = d.getNamedImports().map((ni) => ni.getName());
    return n.includes(symbol);
  });
  if (existing) return;
  sourceFile.addImportDeclaration({ moduleSpecifier: fromPath, namedImports: [symbol] });
}

function prefixUnusedInFile(sourceFile, names) {
  let changed = false;
  const set = new Set(names.filter((n) => !n.startsWith("_")));
  if (set.size === 0) return false;
  // variáveis
  sourceFile.getVariableDeclarations().forEach((decl) => {
    const n = decl.getName();
    if (set.has(n)) {
      decl.rename(`_${n}`); changed = true;
    }
  });
  // parâmetros de função
  sourceFile.getFunctions().forEach((fn) => {
    fn.getParameters().forEach((p) => {
      const n = p.getName();
      if (set.has(n)) { p.rename(`_${n}`); changed = true; }
    });
  });
  // parâmetros em arrows
  sourceFile.getDescendantsOfKind(SyntaxKind.ArrowFunction).forEach((af) => {
    af.getParameters().forEach((p) => {
      const n = p.getName();
      if (set.has(n)) { p.rename(`_${n}`); changed = true; }
    });
  });
  return changed;
}

function fixImportPath(sourceFile) {
  let changed = false;
  sourceFile.getImportDeclarations().forEach((d) => {
    const spec = d.getModuleSpecifierValue();
    if (!(spec.startsWith(".") || spec.startsWith("/"))) return;
    const base = resolve(dirname(sourceFile.getFilePath()), spec);
    for (const ext of [".tsx", ".ts", ".jsx", ".js"]) {
      const cand = base + ext;
      if (existsSync(cand)) {
        if (!spec.endsWith(ext)) {
          d.setModuleSpecifier(spec + ext);
          changed = true;
        }
        break;
      }
    }
  });
  return changed;
}

function addMissingImports(project, symbolToFileMap) {
  let changed = false;
  for (const [file, froms] of symbolToFileMap.entries()) {
    const sf = project.getSourceFile(file);
    if (!sf) continue;
    for (const { symbol, from } of froms) {
      const rel = relative(dirname(file), from).replaceAll("\\", "/");
      const module = rel.startsWith(".") ? rel : `./${rel}`;
      const has = sf.getImportDeclarations().some((d) => d.getNamedImports().some((ni) => ni.getName() === symbol));
      if (!has) { setFromImport(sf, symbol, module.replace(/\.(tsx|ts|jsx|js)$/,"")); changed = true; }
    }
  }
  return changed;
}

// Construir conjunto de ficheiros potencialmente afetados
const projectFiles = new Set();
// prefixUnused aplica-se a todos os .ts/.tsx; mas vamos limitar aos ficheiros abertos depois
// addImport/fixImportPath precisam de alvos concretos; vamos tentar todos .ts/.tsx que existam
import { readdirSync } from "node:fs";
import { glob } from "node:fs/promises";
const candidateFiles = await glob("src/**/*.{ts,tsx}", { withFileTypes: false });
candidateFiles.forEach((f) => projectFiles.add(resolve(f)));

const project = loadProject(projectFiles);

// Preparar mapas para addImport
const addImportOps = ops.filter((o) => o.type === "addImport");
const symbolToFileMap = new Map(); // file -> [{symbol, from}]
for (const op of addImportOps) {
  const symbol = op.symbol;
  const from = resolve(op.from);
  // heurística: aplicar aos ficheiros que mencionem o símbolo
  project.getSourceFiles().forEach((sf) => {
    if (sf.getText().includes(symbol)) {
      const arr = symbolToFileMap.get(sf.getFilePath()) || [];
      arr.push({ symbol, from });
      symbolToFileMap.set(sf.getFilePath(), arr);
    }
  });
}

let anyChange = false;
// 1) prefixUnused
const names = ops.filter((o) => o.type === "prefixUnused").map((o) => o.name);
if (names.length) {
  project.getSourceFiles().forEach((sf) => { if (prefixUnusedInFile(sf, names)) anyChange = true; });
}
// 2) addImport
if (addMissingImports(project, symbolToFileMap)) anyChange = true;
// 3) fixImportPath
if (ops.some((o) => o.type === "fixImportPath")) {
  project.getSourceFiles().forEach((sf) => { if (fixImportPath(sf)) anyChange = true; });
}

const files = [];
if (anyChange) {
  project.getSourceFiles().forEach((sf) => {
    if (sf.isSaved()) return; // não usamos save; mas guardamos todos para simplificar
    files.push({ path: sf.getFilePath(), content: sf.getFullText() });
  });
}
process.stdout.write(JSON.stringify({ files }));
