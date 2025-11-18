// Cursor Extension - Fortaleza LLM Integration
// Esta extensão conecta o Cursor à API da Fortaleza para correção automática

const FORTALEZA_API_URL = "http://localhost:8000/fix";
const FORTALEZA_ENABLED = true;

class FortalezaCursorExtension {
  constructor() {
    this.isEnabled = FORTALEZA_ENABLED;
    this.apiUrl = FORTALEZA_API_URL;
    this.errorQueue = [];
    this.isProcessing = false;

    // Configurações
    this.config = {
      autoFix: true,
      showNotifications: true,
      minConfidence: 0.8,
      maxRetries: 3,
      timeout: 30000,
    };

    this.init();
  }

  init() {
    if (!this.isEnabled) {
      console.log("Fortaleza: Extensão desabilitada");
      return;
    }

    console.log("Fortaleza: Extensão inicializada");
    this.setupEventListeners();
    this.startErrorMonitoring();
  }

  setupEventListeners() {
    // Intercepta erros do TypeScript
    if (window.monaco) {
      this.setupMonacoListeners();
    }

    // Intercepta erros do ESLint
    this.setupESLintListeners();

    // Intercepta comandos do Cursor
    this.setupCursorListeners();
  }

  setupMonacoListeners() {
    // Monitora mudanças no editor
    if (window.monaco.editor) {
      window.monaco.editor.onDidChangeModelContent((event) => {
        this.onCodeChange(event);
      });
    }
  }

  setupESLintListeners() {
    // Intercepta erros de linting
    const originalLint = window.eslint?.lint || (() => {});
    window.eslint = window.eslint || {};
    window.eslint.lint = async (...args) => {
      const result = await originalLint(...args);
      this.processLintErrors(result);
      return result;
    };
  }

  setupCursorListeners() {
    // Intercepta comandos do Cursor
    document.addEventListener("keydown", (event) => {
      if (event.ctrlKey && event.key === "f") {
        this.triggerFortalezaFix();
      }
    });
  }

  startErrorMonitoring() {
    // Monitora erros em tempo real
    setInterval(() => {
      this.checkForErrors();
    }, 2000);
  }

  async onCodeChange(_event) {
    // Quando o código muda, verifica por erros
    setTimeout(() => {
      this.checkForErrors();
    }, 1000);
  }

  async checkForErrors() {
    if (this.isProcessing) return;

    try {
      const errors = this.collectErrors();
      if (errors.length > 0) {
        await this.processErrors(errors);
      }
    } catch (error) {
      console.error("Fortaleza: Erro ao verificar erros:", error);
    }
  }

  collectErrors() {
    const errors = [];

    // Coleta erros do TypeScript
    if (window.monaco?.editor) {
      const models = window.monaco.editor.getModels();
      models.forEach((model) => {
        const markers = window.monaco.editor.getModelMarkers({
          resource: model.uri,
        });
        markers.forEach((marker) => {
          if (marker.severity === window.monaco.MarkerSeverity.Error) {
            errors.push({
              type: "typescript",
              code: marker.code?.value || "UNKNOWN",
              message: marker.message,
              file: model.uri.fsPath,
              line: marker.startLineNumber,
              column: marker.startColumn,
              severity: "error",
            });
          }
        });
      });
    }

    // Coleta erros do ESLint
    const lintErrors = this.getLintErrors();
    errors.push(...lintErrors);

    return errors;
  }

  getLintErrors() {
    // Simula coleta de erros do ESLint
    // Na implementação real, conectaria ao ESLint do Cursor
    return [];
  }

  async processErrors(errors) {
    if (errors.length === 0) return;

    this.isProcessing = true;

    try {
      for (const error of errors) {
        await this.sendErrorToFortaleza(error);
      }
    } catch (error) {
      console.error("Fortaleza: Erro ao processar erros:", error);
    } finally {
      this.isProcessing = false;
    }
  }

  async sendErrorToFortaleza(error) {
    try {
      const payload = {
        error: {
          type: error.type,
          code: error.code,
          message: error.message,
          file: error.file,
          line: error.line,
          column: error.column,
          severity: error.severity,
        },
        context: {
          workspace: this.getWorkspaceInfo(),
          timestamp: new Date().toISOString(),
          cursor_version: this.getCursorVersion(),
        },
      };

      console.log("Fortaleza: Enviando erro:", payload);

      const response = await fetch(this.apiUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
        timeout: this.config.timeout,
      });

      if (response.ok) {
        const result = await response.json();
        await this.applyFix(result);
      } else {
        console.error("Fortaleza: Erro na API:", response.status);
      }
    } catch (error) {
      console.error("Fortaleza: Erro ao enviar para API:", error);
    }
  }

  async applyFix(fixResult) {
    if (!fixResult.success) {
      console.log("Fortaleza: Nenhuma correção aplicada");
      return;
    }

    try {
      if (fixResult.diff) {
        await this.applyDiff(fixResult.diff);
      }

      if (fixResult.advice) {
        this.showAdvice(fixResult.advice);
      }

      this.showNotification("Correção aplicada com sucesso!", "success");
    } catch (error) {
      console.error("Fortaleza: Erro ao aplicar correção:", error);
      this.showNotification("Erro ao aplicar correção", "error");
    }
  }

  async applyDiff(diff) {
    // Aplica o diff no editor
    if (window.monaco?.editor) {
      const models = window.monaco.editor.getModels();
      const targetModel = models.find(
        (model) => model.uri.fsPath === diff.file,
      );

      if (targetModel) {
        const edits = this.parseDiff(diff);
        await targetModel.pushEditOperations([], edits, () => null);
      }
    }
  }

  parseDiff(diff) {
    // Converte diff em operações do Monaco
    const edits = [];

    if (diff.changes) {
      diff.changes.forEach((change) => {
        edits.push({
          range: new window.monaco.Range(
            change.startLine,
            change.startColumn,
            change.endLine,
            change.endColumn,
          ),
          text: change.newText,
        });
      });
    }

    return edits;
  }

  showAdvice(advice) {
    if (this.config.showNotifications) {
      this.showNotification(`Conselho: ${advice}`, "info");
    }
  }

  showNotification(message, type = "info") {
    if (this.config.showNotifications) {
      // Usa notificações do Cursor se disponível
      if (window.showNotification) {
        window.showNotification(message, type);
      } else {
        console.log(`Fortaleza: ${message}`);
      }
    }
  }

  async triggerFortalezaFix() {
    // Trigger manual para correção
    this.showNotification("Iniciando correção manual...", "info");
    await this.checkForErrors();
  }

  getWorkspaceInfo() {
    // Obtém informações do workspace
    return {
      path: window.location.pathname,
      name: document.title,
      type: "cursor",
    };
  }

  getCursorVersion() {
    // Obtém versão do Cursor
    return window.cursorVersion || "unknown";
  }

  // Métodos de configuração
  enable() {
    this.isEnabled = true;
    this.showNotification("Fortaleza habilitada", "success");
  }

  disable() {
    this.isEnabled = false;
    this.showNotification("Fortaleza desabilitada", "warning");
  }

  updateConfig(newConfig) {
    this.config = { ...this.config, ...newConfig };
    this.showNotification("Configuração atualizada", "info");
  }
}

// Inicializa a extensão
let fortalezaExtension;

document.addEventListener("DOMContentLoaded", () => {
  fortalezaExtension = new FortalezaCursorExtension();
});

// Expõe para uso global
window.FortalezaExtension = fortalezaExtension;

console.log("Fortaleza Cursor Extension carregada!");
