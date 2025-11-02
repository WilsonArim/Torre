#!/usr/bin/env python3
"""
Teste de Integração Cursor-Fortaleza
Testa a conexão entre a extensão do Cursor e a API da Fortaleza
"""

import requests
import json
import time
import subprocess
import sys
from pathlib import Path

# Configurações
API_URL = "http://localhost:8000"
TEST_FILE = "test_error.tsx"

def create_test_file():
    """Cria arquivo de teste com erro"""
    content = """
import React from 'react';

export default function TestComponent() {
    return (
        <div>
            <h1>Test Component</h1>
            <p>{undefinedVariable}</p>
        </div>
    );
}
"""
    
    with open(TEST_FILE, "w") as f:
        f.write(content)
    
    print(f"✅ Arquivo de teste criado: {TEST_FILE}")

def test_api_health():
    """Testa se a API está funcionando"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API da Fortaleza está funcionando")
            return True
        else:
            print(f"❌ API retornou status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao conectar com API: {e}")
        return False

def test_error_fix():
    """Testa correção de erro via API"""
    # Payload simulado da extensão do Cursor
    payload = {
        "error": {
            "type": "typescript",
            "code": "TS2304",
            "message": "Cannot find name 'undefinedVariable'",
            "file": TEST_FILE,
            "line": 8,
            "column": 13,
            "severity": "error"
        },
        "context": {
            "workspace": {
                "path": "/test/workspace",
                "name": "Test Project",
                "type": "cursor"
            },
            "timestamp": "2025-08-26T14:00:00Z",
            "cursor_version": "1.0.0"
        }
    }
    
    try:
        print("🔄 Enviando erro para correção...")
        response = requests.post(
            f"{API_URL}/fix",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Correção processada com sucesso!")
            print(f"   Sucesso: {result.get('success')}")
            print(f"   Método: {result.get('method')}")
            print(f"   Confiança: {result.get('confidence')}")
            print(f"   Duração: {result.get('duration_ms')}ms")
            
            if result.get('advice'):
                print(f"   Conselho: {result.get('advice')}")
            
            return result.get('success', False)
        else:
            print(f"❌ API retornou erro: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao enviar para API: {e}")
        return False

def test_metrics():
    """Testa endpoint de métricas"""
    try:
        response = requests.get(f"{API_URL}/metrics", timeout=5)
        if response.status_code == 200:
            metrics = response.json()
            print("✅ Métricas obtidas com sucesso!")
            print(f"   Total de execuções: {metrics.get('total_runs', 0)}")
            return True
        else:
            print(f"❌ Erro ao obter métricas: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao conectar com API: {e}")
        return False

def start_api_server():
    """Inicia o servidor da API"""
    print("🚀 Iniciando servidor da API da Fortaleza...")
    
    try:
        # Iniciar servidor em background
        process = subprocess.Popen(
            [sys.executable, "api_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Aguardar servidor inicializar
        time.sleep(3)
        
        # Verificar se está rodando
        if process.poll() is None:
            print("✅ Servidor da API iniciado")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Erro ao iniciar servidor: {stderr.decode()}")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        return None

def cleanup():
    """Limpa arquivos de teste"""
    try:
        if Path(TEST_FILE).exists():
            Path(TEST_FILE).unlink()
            print(f"🧹 Arquivo de teste removido: {TEST_FILE}")
    except Exception as e:
        print(f"⚠️ Erro ao limpar: {e}")

def main():
    """Função principal de teste"""
    print("🧪 TESTE DE INTEGRAÇÃO CURSOR-FORTALEZA")
    print("=" * 50)
    
    api_process = None
    
    try:
        # 1. Criar arquivo de teste
        create_test_file()
        
        # 2. Iniciar servidor da API
        api_process = start_api_server()
        if not api_process:
            print("❌ Falha ao iniciar servidor da API")
            return False
        
        # 3. Testar saúde da API
        if not test_api_health():
            print("❌ API não está funcionando")
            return False
        
        # 4. Testar correção de erro
        if not test_error_fix():
            print("❌ Falha na correção de erro")
            return False
        
        # 5. Testar métricas
        if not test_metrics():
            print("❌ Falha ao obter métricas")
            return False
        
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Integração Cursor-Fortaleza funcionando corretamente")
        
        return True
        
    except KeyboardInterrupt:
        print("\n⚠️ Teste interrompido pelo usuário")
        return False
        
    except Exception as e:
        print(f"\n❌ Erro durante teste: {e}")
        return False
        
    finally:
        # Limpar
        cleanup()
        
        # Parar servidor
        if api_process:
            print("🛑 Parando servidor da API...")
            api_process.terminate()
            api_process.wait()
            print("✅ Servidor parado")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
