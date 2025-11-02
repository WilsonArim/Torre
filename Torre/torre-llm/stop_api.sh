#!/bin/bash

echo "🛑 Parando API da Fortaleza..."
echo "=============================="

# Parar processo da API
pkill -f "api_server.py" || true

echo "✅ API parada"
