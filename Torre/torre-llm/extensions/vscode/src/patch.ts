/* eslint-disable import/no-unresolved */
import * as vscode from "vscode";

export async function applyFilesOut(filesOut: Record<string, string>) {
  const edit = new vscode.WorkspaceEdit();
  for (const [rel, content] of Object.entries(filesOut)) {
    const uri = vscode.Uri.joinPath(
      vscode.workspace.workspaceFolders![0].uri,
      rel,
    );
    const exists = await fileExists(uri);
    if (!exists) {
      edit.createFile(uri, { ignoreIfExists: true });
      edit.insert(uri, new vscode.Position(0, 0), content);
    } else {
      const doc = await vscode.workspace.openTextDocument(uri);
      const full = new vscode.Range(
        doc.positionAt(0),
        doc.positionAt(doc.getText().length),
      );
      edit.replace(uri, full, content);
    }
  }
  await vscode.workspace.applyEdit(edit);
}

async function fileExists(uri: vscode.Uri): Promise<boolean> {
  try {
    await vscode.workspace.fs.stat(uri);
    return true;
  } catch {
    return false;
  }
}
