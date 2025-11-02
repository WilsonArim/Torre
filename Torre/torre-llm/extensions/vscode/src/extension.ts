import fetch from 'node-fetch';
import * as vscode from 'vscode';

import { applyFilesOut } from './patch';

let lastResponse: any = null;

export function activate(context: vscode.ExtensionContext) {
  context.subscriptions.push(
    vscode.commands.registerCommand('fortaleza.patch', async () => {
      const cfg = vscode.workspace.getConfiguration('fortaleza');
      const apiUrl = cfg.get<string>('apiUrl') || 'http://localhost:8765';
      const apiKey = cfg.get<string>('apiKey') || '';
      const returnFiles = !!cfg.get<boolean>('returnFiles');

      const editor = vscode.window.activeTextEditor;
      if (!editor) { vscode.window.showWarningMessage('Abra um ficheiro.'); return; }

      // coleta ficheiros abertos (máx 12 para leveza)
      const openDocs = vscode.workspace.textDocuments.slice(0, 12);
      const files: Record<string,string> = {};
      for (const d of openDocs) {
        const rel = vscode.workspace.asRelativePath(d.uri);
        files[rel] = d.getText();
      }

      // diagnósticos
      const diagnostics: any[] = [];
      const coll = vscode.languages.getDiagnostics();
      for (const [uri, diags] of coll) {
        const rel = vscode.workspace.asRelativePath(uri);
        for (const d of diags.slice(0, 20)) {
          diagnostics.push({ file: rel, code: (d.code||'')+'', message: d.message });
        }
      }

      const body = {
        logs: {}, files,
        context: { ide: (vscode.env.appName.toLowerCase().includes('cursor')?'cursor':'vscode'), diagnostics },
        workspace: "default",
        return_files: returnFiles
      };

      const headers: any = { 'Content-Type': 'application/json' };
      if (apiKey) headers['x-api-key'] = apiKey;

      let res;
      try {
        res = await fetch(`${apiUrl}/editor/patch`, { method:'POST', headers, body: JSON.stringify(body) });
      } catch (e:any) {
        vscode.window.showErrorMessage(`Fortaleza: erro de rede: ${e?.message||e}`);
        return;
      }
      const json = await res.json().catch(()=> ({}));
      lastResponse = json;

      if (json.mode === 'PATCH' && json.files_out && Object.keys(json.files_out).length) {
        await applyFilesOut(json.files_out);
        vscode.window.showInformationMessage('Fortaleza: alterações aplicadas.');
      } else if (json.diff) {
        const doc = await vscode.workspace.openTextDocument({ content: json.diff, language: 'diff' });
        vscode.window.showTextDocument(doc, { preview: true });
        vscode.window.showInformationMessage('Fortaleza: diff gerado (revise e aceite).');
      } else {
        vscode.window.showWarningMessage('Fortaleza: sem patch seguro — modo Advisory.');
      }
    }),

    vscode.commands.registerCommand('fortaleza.apply', async () => {
      if (!lastResponse || !lastResponse.files_out) {
        vscode.window.showWarningMessage('Sem resposta aplicável.');
        return;
      }
      await applyFilesOut(lastResponse.files_out);
      vscode.window.showInformationMessage('Fortaleza: alterações aplicadas.');
    })
  );
}

export function deactivate() {}
