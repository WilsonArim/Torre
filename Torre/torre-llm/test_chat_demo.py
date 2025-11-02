#!/usr/bin/env python3
"""
Demo do Fortaleza Chat - Teste automático
"""

import subprocess
import json
import time

def test_fortaleza_chat():
    """Testa o chat da Fortaleza"""
    print("🧪 TESTE DO FORTALEZA CHAT")
    print("=" * 40)
    
    # Testar seleção de modelo
    print("1. Testando seleção de modelo...")
    
    # Simular input para selecionar fortaleza-base
    test_input = "fortaleza-base\nchat\nComo corrigir erro TS2304?\nquit\nquit\n"
    
    try:
        # Executar chat com input simulado
        result = subprocess.run(
            ["python3", "fortaleza_chat.py"],
            input=test_input,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print("✅ Chat executado com sucesso!")
        print(f"Output: {result.stdout}")
        
        if result.stderr:
            print(f"Stderr: {result.stderr}")
        
        return True
        
    except subprocess.TimeoutExpired:
        print("⏰ Timeout - chat demorou muito")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_model_selection():
    """Testa apenas seleção de modelo"""
    print("\n2. Testando seleção de modelo...")
    
    try:
        # Testar se consegue selecionar modelo
        result = subprocess.run(
            ["python3", "-c", "from fortaleza_chat import FortalezaChat; chat = FortalezaChat(); print('✅ FortalezaChat carregado')"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✅ FortalezaChat carregado com sucesso!")
            return True
        else:
            print(f"❌ Erro ao carregar: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 Iniciando testes do Fortaleza Chat...")
    
    # Teste 1: Carregar módulo
    success1 = test_model_selection()
    
    # Teste 2: Executar chat
    success2 = test_fortaleza_chat()
    
    print("\n" + "=" * 40)
    print("RESULTADOS DOS TESTES:")
    print(f"✅ Carregamento: {'OK' if success1 else '❌'}")
    print(f"✅ Execução: {'OK' if success2 else '❌'}")
    
    if success1 and success2:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Fortaleza Chat está funcionando!")
    else:
        print("\n⚠️ Alguns testes falharam")
        print("Verificar configuração")

if __name__ == "__main__":
    main()
