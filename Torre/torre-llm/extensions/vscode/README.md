# Fortaleza LLM Bridge

Extensão VS Code/Cursor para integração com Fortaleza LLM.

## Instalação

### Desenvolvimento

```bash
cd extensions/vscode
npm install
npm run compile
# Abra esta pasta no VS Code e tecle F5 para abrir uma janela de extensão
```

### Produção

```bash
npm install -g vsce
vsce package
# Instale o .vsix gerado
```

## Configuração

```json
{
  "fortaleza.apiUrl": "http://localhost:8765",
  "fortaleza.apiKey": "OPCIONAL",
  "fortaleza.returnFiles": true
}
```

## Comandos

- **Fortaleza: Patch (Editor)** — coleta arquivos abertos+diagnósticos e chama `/editor/patch`
- **Fortaleza: Apply Last Response** — aplica o último `files_out` recebido

## Funcionalidades

- ✅ Compatível com VSCode e Cursor
- ✅ Aplica edições dentro do workspace
- ✅ Fallback para diff quando `files_out` não disponível
- ✅ Rate limiting e autenticação
- ✅ Diagnósticos automáticos
