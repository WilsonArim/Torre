/* eslint-disable import/no-unresolved */
import * as fs from "fs";

import { Project, SyntaxKind } from "ts-morph";

type Result = { codemod: string; file: string; edits: number };

export async function missingSymbolImport(
  project: Project,
  file: string,
): Promise<Result> {
  const src = project.getSourceFileOrThrow(file);
  let edits = 0;

  // Heurística simples: se há JSX e não tem React import, adiciona
  const hasJSX = !!src.getDescendantsOfKind(SyntaxKind.JsxOpeningElement)
    .length;
  const hasReactImport = src
    .getImportDeclarations()
    .some((i) => i.getModuleSpecifierValue() === "react");

  if (hasJSX && !hasReactImport) {
    src.insertText(0, "import React from 'react';\n");
    edits++;
  }

  // Corrigir imports no meio do arquivo - mover para o topo
  const imports = src.getImportDeclarations();
  if (imports.length > 0) {
    const firstStatement = src.getFirstChild();
    if (
      firstStatement &&
      firstStatement.getKind() !== SyntaxKind.ImportDeclaration
    ) {
      // Mover todos os imports para o topo
      const importTexts = imports.map((imp) => imp.getText());
      imports.forEach((imp) => imp.remove());
      src.insertText(0, importTexts.join("\n") + "\n");
      edits++;
    }
  }

  return { codemod: "missingSymbolImport", file, edits };
}

export async function createRelativeImportIfExists(
  project: Project,
  file: string,
): Promise<Result> {
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

// ES module main check
if (import.meta.url === `file://${process.argv[1]}`) {
  const globs = process.argv.slice(2);
  const project = new Project({
    tsConfigFilePath: "tsconfig.json",
    skipAddingFilesFromTsConfig: false,
  });
  const files = globs.length
    ? globs
    : project.getSourceFiles().map((f) => f.getFilePath());
  const tasks: Promise<Result>[] = [];
  for (const f of files) {
    tasks.push(missingSymbolImport(project, f));
    tasks.push(createRelativeImportIfExists(project, f));
  }
  Promise.all(tasks)
    .then((results) => {
      return project.save().then(() => results);
    })
    .then((results) => {
      const per: Record<string, number> = {};
      let edits_total = 0;
      for (const r of results) {
        per[r.codemod] = (per[r.codemod] ?? 0) + r.edits;
        edits_total += r.edits;
      }
      console.log(
        JSON.stringify(
          { ok: true, files: files.length, edits_total, per_codemod: per },
          null,
          2,
        ),
      );
    });
}
