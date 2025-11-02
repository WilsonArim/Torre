#!/usr/bin/env bash
set -e

echo "==> Verificando Ollama..."
if ! command -v ollama >/dev/null 2>&1; then
  echo "ERRO: Ollama não encontrado. Instale em https://ollama.com/download"
  exit 1
fi

echo "==> Iniciando servidor (se ainda não estiver)..."
# Em muitos sistemas o 'ollama serve' é gerenciado pelo app; tentamos iniciar em background se possível
(ollama serve >/dev/null 2>&1 &) || true
sleep 2

echo "==> Baixando Qwen2.5 7B Instruct (pode demorar)"
ollama pull qwen2.5:7b-instruct

echo "==> Criando modelo-aliás 'torre' a partir do Modelfile local"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ollama create torre -f "$SCRIPT_DIR/Modelfile" || true

echo "==> Testando API OpenAI-compatível em http://localhost:11434/v1"
set +e
RESP=$(curl -s http://localhost:11434/v1/chat/completions       -H "Content-Type: application/json"       -d '{"model":"torre","messages":[{"role":"user","content":"Diga: Sou a Torre."}]}' )
set -e

if echo "$RESP" | grep -q '"choices"'; then
  echo "OK: resposta recebida da Torre."
else
  echo "ATENÇÃO: não recebi resposta esperada. Conteúdo:"
  echo "$RESP"
fi

echo ""
echo "==> Próximo passo no Cursor:"
echo "1) Settings → Models → API Keys → OpenAI-compatible → Override Base URL: http://localhost:11434/v1"
echo "2) API Key: local"
echo "3) Add model → Display Name: Torre, Model (ID): torre"
echo "4) Abra um chat e selecione o modelo 'Torre'."
