// Torre Models Extension - Versão Avançada
// Conecta à API da Torre para correção automática
/* eslint-disable @typescript-eslint/no-var-requires */

const http = require("http");
// const https = require("https"); // Not used currently

const vscode = require("vscode");

function activate(context) {
  console.log("🏰 Torre Extension Avançada: Ativando...");

  // Configuração da API
  const API_BASE = "http://localhost:8000";
  let _currentModel = "torre-auto";

  // Status bar
  const statusBarItem = vscode.window.createStatusBarItem(
    vscode.StatusBarAlignment.Right,
    100,
  );
  statusBarItem.text = "🏰 Torre";
  statusBarItem.tooltip = "Torre Models - Clique para ativar";
  statusBarItem.show();

  // Função para fazer requisições à API
  async function callTorreAPI(endpoint, data = null) {
    return new Promise((resolve, reject) => {
      const url = `${API_BASE}${endpoint}`;
      const options = {
        method: data ? "POST" : "GET",
        headers: {
          "Content-Type": "application/json",
          "X-API-Key": "dev-key",
        },
      };

      const req = http.request(url, options, (res) => {
        let body = "";
        res.on("data", (chunk) => (body += chunk));
        res.on("end", () => {
          try {
            const result = JSON.parse(body);
            resolve(result);
          } catch (e) {
            resolve({ success: false, error: "Invalid JSON response" });
          }
        });
      });

      req.on("error", (err) => {
        reject({ success: false, error: err.message });
      });

      if (data) {
        req.write(JSON.stringify(data));
      }
      req.end();
    });
  }

  // Função para ativar modelo
  async function activateModel(modelName, modelId) {
    try {
      _currentModel = modelId;
      statusBarItem.text = `🏰 ${modelName}`;

      // Testar conexão com API
      const health = await callTorreAPI("/health");
      if (health.status === "ok") {
        vscode.window.showInformationMessage(
          `🏰 ${modelName} ativado! API conectada.`,
        );
        console.log(`🏰 Modelo ${modelName} ativado com sucesso`);
      } else {
        vscode.window.showWarningMessage(
          `🏰 ${modelName} ativado! API não disponível.`,
        );
      }
    } catch (error) {
      console.error(`Erro ao ativar ${modelName}:`, error);
      vscode.window.showErrorMessage(
        `Erro ao ativar ${modelName}: ${error.message}`,
      );
    }
  }

  // Função para corrigir código automaticamente
  async function autoFixCode() {
    try {
      const editor = vscode.window.activeTextEditor;
      if (!editor) {
        vscode.window.showWarningMessage("Nenhum arquivo aberto para corrigir");
        return;
      }

      const document = editor.document;
      const content = document.getText();
      const filename = document.fileName.split("/").pop();

      vscode.window.showInformationMessage("🔧 Corrigindo código com Torre...");

      // Chamar API para correção
      const result = await callTorreAPI("/editor/patch", {
        logs: { error: "Auto-fix request" },
        files: { [filename]: content },
        return_files: true,
      });

      if (result.diff) {
        // Aplicar diff
        const workspaceEdit = new vscode.WorkspaceEdit();
        const uri = document.uri;

        // Parse diff e aplicar mudanças
        // (Simplificado - em produção seria mais robusto)
        workspaceEdit.replace(
          uri,
          new vscode.Range(0, 0, document.lineCount, 0),
          result.files_out[filename] || content,
        );

        await vscode.workspace.applyEdit(workspaceEdit);
        vscode.window.showInformationMessage("✅ Código corrigido com Torre!");
      } else {
        vscode.window.showInformationMessage("ℹ️ Nenhuma correção necessária");
      }
    } catch (error) {
      console.error("Erro na correção automática:", error);
      vscode.window.showErrorMessage(`Erro na correção: ${error.message}`);
    }
  }

  // Comandos
  let enableAuto = vscode.commands.registerCommand("torre.enableAuto", () => {
    activateModel("Torre Auto", "torre-auto");
  });

  let enableBase = vscode.commands.registerCommand("torre.enableBase", () => {
    activateModel("Torre Base", "torre-base");
  });

  let enableAdvice = vscode.commands.registerCommand(
    "torre.enableAdvice",
    () => {
      activateModel("Torre Advice", "torre-advice");
    },
  );

  let enableReview = vscode.commands.registerCommand(
    "torre.enableReview",
    () => {
      activateModel("Torre Review", "torre-review");
    },
  );

  let enableExplain = vscode.commands.registerCommand(
    "torre.enableExplain",
    () => {
      activateModel("Torre Explain", "torre-explain");
    },
  );

  let autoFix = vscode.commands.registerCommand("torre.autoFix", () => {
    autoFixCode();
  });

  let disableAll = vscode.commands.registerCommand("torre.disableAll", () => {
    _currentModel = null;
    statusBarItem.text = "🏰 Torre";
    vscode.window.showInformationMessage(
      "🏰 Todos os modelos da Torre desativados",
    );
  });

  // Adicionar comandos
  context.subscriptions.push(
    enableAuto,
    enableBase,
    enableAdvice,
    enableReview,
    enableExplain,
    autoFix,
    disableAll,
  );

  console.log("🏰 Torre Extension Avançada: Ativada com sucesso!");
}

function deactivate() {
  console.log("🏰 Torre Extension Avançada: Desativando...");
}

module.exports = {
  activate,
  deactivate,
};
