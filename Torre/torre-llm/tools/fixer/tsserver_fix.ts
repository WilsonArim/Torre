import * as fs from "fs";
import * as path from "path";

import { glob } from "glob";
import ts from "typescript";

/** Executa CodeFix do tsserver em arquivos .ts/.tsx do projeto. */
async function main() {
  const files = (
    await glob("**/*.{ts,tsx}", {
      ignore: ["**/node_modules/**", "**/dist/**"],
    })
  ).map((f) => path.resolve(f));
  if (files.length === 0) return;

  const configPath = ts.findConfigFile(
    process.cwd(),
    ts.sys.fileExists,
    "tsconfig.json",
  );
  const config = configPath
    ? ts.readConfigFile(configPath, ts.sys.readFile).config
    : { compilerOptions: { strict: true } };
  const parsed = ts.parseJsonConfigFileContent(config, ts.sys, process.cwd());
  const host: ts.LanguageServiceHost = {
    getCompilationSettings: () => parsed.options,
    getScriptFileNames: () =>
      Array.from(new Set([...files, ...parsed.fileNames])),
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
    2322,
    2345, // type assign issues
    2552,
    2551, // missing property/rename
  ]);

  let applied = 0;
  for (const f of files) {
    const diags = [
      ...ls.getSyntacticDiagnostics(f),
      ...ls.getSemanticDiagnostics(f),
      ...ls.getSuggestionDiagnostics(f),
    ].filter((d) => {
      const code = typeof d.code === "number" ? d.code : 0;
      return fixable.has(code);
    });

    if (diags.length === 0) continue;

    let content = fs.readFileSync(f, "utf8");
    for (const d of diags) {
      const start = d.start ?? 0;
      const len = d.length ?? 0;
      const fixes = ls.getCodeFixesAtPosition(
        f,
        start,
        start + len,
        [typeof d.code === "number" ? d.code : 0],
        {},
        {},
      );
      if (!fixes.length) continue;

      // usa o 1º fix com CombinedCodeAction quando possível
      const change = fixes[0];
      const changes =
        change && "changes" in change && Array.isArray(change.changes)
          ? fixes.flatMap((x) =>
              "changes" in x && Array.isArray(x.changes) ? x.changes : [],
            )
          : [];
      for (const c of changes) {
        if (c.fileName !== f) continue;
        // aplicar na memória (da última para a primeira para não deslocar offsets)
        const edits = [...c.textChanges].sort(
          (a, b) => b.span.start - a.span.start,
        );
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
  console.log(JSON.stringify({ ok: true, applied }, null, 2));
}
main().catch((e) => {
  console.error(e);
  process.exit(1);
});
