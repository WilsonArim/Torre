#!/usr/bin/env python3
"""
Torre Chat - Interface para selecionar e usar o modelo da Torre
Como ChatGPT/Claude, mas com a tua LLM
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, List
import subprocess
import asyncio
from datetime import datetime

class TorreChat:
    def __init__(self):
        self.models = {
            "auto": {
                "name": "Auto (Seleção Automática)",
                "description": "Seleciona automaticamente o melhor modelo para cada tarefa",
                "command": ["python3", "-m", "llm.cli", "--model", "auto"],
                "type": "auto"
            },
            "gemini": {
                "name": "Google Gemini",
                "description": "Modelo avançado do Google para tarefas gerais",
                "command": ["python3", "-m", "llm.cli", "--model", "gemini"],
                "type": "gemini"
            },
            "torre": {
                "name": "Torre (Tua LLM)",
                "description": "Tua LLM especializada da Torre para correção de código",
                "command": ["python3", "-m", "llm.cli", "--model", "torre"],
                "type": "torre"
            },
            "torre-base": {
                "name": "Torre Base",
                "description": "Modelo base da Torre para correção de erros",
                "command": ["python3", "-m", "llm.cli", "--model", "torre", "--mode", "correction"],
                "type": "correction"
            },
            "torre-advice": {
                "name": "Torre Advice",
                "description": "Modelo especializado em dar conselhos de código",
                "command": ["python3", "-m", "llm.cli", "--model", "torre", "--mode", "advice"],
                "type": "advice"
            },
            "torre-review": {
                "name": "Torre Review",
                "description": "Modelo para revisão e análise de código",
                "command": ["python3", "-m", "llm.cli", "--model", "torre", "--mode", "review"],
                "type": "review"
            },
            "torre-explain": {
                "name": "Torre Explain",
                "description": "Modelo para explicar conceitos e código",
                "command": ["python3", "-m", "llm.cli", "--model", "torre", "--mode", "explain"],
                "type": "explain"
            }
        }
        
        self.current_model = None
        self.chat_history = []
        self.config_file = Path(".torre/torre_chat_config.json")
        
        # Criar diretório de configuração
        self.config_file.parent.mkdir(exist_ok=True)
        
        # Carregar configuração
        self.load_config()
    
    def load_config(self):
        """Carrega configuração salva"""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    config = json.load(f)
                    self.current_model = config.get("current_model")
            except Exception as e:
                print(f"⚠️ Erro ao carregar configuração: {e}")
    
    def save_config(self):
        """Salva configuração atual"""
        try:
            config = {
                "current_model": self.current_model,
                "last_used": datetime.now().isoformat()
            }
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"⚠️ Erro ao salvar configuração: {e}")
    
    def show_models(self):
        """Mostra modelos disponíveis"""
        print("\n🤖 MODELOS DISPONÍVEIS:")
        print("=" * 50)
        
        for model_id, model_info in self.models.items():
            status = "✅ SELECIONADO" if model_id == self.current_model else ""
            print(f"\n{model_id}:")
            print(f"  Nome: {model_info['name']}")
            print(f"  Descrição: {model_info['description']}")
            print(f"  Tipo: {model_info['type']}")
            if status:
                print(f"  Status: {status}")
        
        print("\n" + "=" * 50)
    
    def select_model(self):
        """Permite selecionar modelo"""
        self.show_models()
        
        print("\n🎯 SELECIONAR MODELO:")
        print("Digite o ID do modelo ou 'q' para sair:")
        
        while True:
            choice = input("> ").strip().lower()
            
            if choice == 'q':
                return False
            
            if choice in self.models:
                self.current_model = choice
                self.save_config()
                print(f"\n✅ Modelo selecionado: {self.models[choice]['name']}")
                return True
            else:
                print("❌ Modelo não encontrado. Tente novamente:")
    
    def chat_with_model(self):
        """Inicia chat com modelo selecionado"""
        if not self.current_model:
            print("❌ Nenhum modelo selecionado!")
            return
        
        model_info = self.models[self.current_model]
        print(f"\n💬 CHAT COM {model_info['name'].upper()}")
        print("=" * 50)
        print(f"Modelo: {model_info['name']}")
        print(f"Tipo: {model_info['type']}")
        print(f"Descrição: {model_info['description']}")
        print("\nDigite 'quit' para sair, 'clear' para limpar histórico")
        print("=" * 50)
        
        while True:
            try:
                user_input = input("\n🤔 Tu: ").strip()
                
                if user_input.lower() == 'quit':
                    break
                elif user_input.lower() == 'clear':
                    self.chat_history = []
                    print("🧹 Histórico limpo!")
                    continue
                elif not user_input:
                    continue
                
                # Adicionar ao histórico
                self.chat_history.append({
                    "user": user_input,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Enviar para modelo
                response = self.send_to_model(user_input)
                
                if response:
                    print(f"\n🤖 {model_info['name']}: {response}")
                    
                    # Adicionar resposta ao histórico
                    self.chat_history[-1]["assistant"] = response
                else:
                    print(f"\n❌ Erro ao obter resposta do modelo")
                
            except KeyboardInterrupt:
                print("\n\n👋 Chat interrompido!")
                break
            except Exception as e:
                print(f"\n❌ Erro: {e}")
    
    def send_to_model(self, prompt: str) -> str:
        """Envia prompt para modelo selecionado"""
        try:
            model_info = self.models[self.current_model]
            
            # Preparar input para LLM
            llm_input = {
                "prompt": prompt,
                "model": self.current_model,
                "mode": model_info["type"],
                "context": {
                    "chat_history": self.chat_history[-5:],  # Últimas 5 mensagens
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            # Executar LLM
            result = subprocess.run(
                model_info["command"],
                input=json.dumps(llm_input),
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                try:
                    # Tentar parsear JSON
                    response_data = json.loads(result.stdout)
                    return response_data.get("response", result.stdout.strip())
                except json.JSONDecodeError:
                    # Se não for JSON, retornar stdout direto
                    return result.stdout.strip()
            else:
                print(f"⚠️ Erro do modelo: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            print("⏰ Timeout - modelo demorou muito para responder")
            return None
        except Exception as e:
            print(f"❌ Erro ao enviar para modelo: {e}")
            return None
    
    def show_help(self):
        """Mostra ajuda"""
        print("\n📖 AJUDA - TORRE CHAT:")
        print("=" * 40)
        print("Comandos disponíveis:")
        print("  models    - Mostrar modelos disponíveis")
        print("  select    - Selecionar modelo")
        print("  chat      - Iniciar chat com modelo")
        print("  history   - Mostrar histórico")
        print("  config    - Mostrar configuração")
        print("  help      - Mostrar esta ajuda")
        print("  quit      - Sair")
        print("=" * 40)
    
    def show_history(self):
        """Mostra histórico do chat"""
        if not self.chat_history:
            print("📝 Nenhuma conversa no histórico")
            return
        
        print(f"\n📝 HISTÓRICO DO TORRE CHAT ({len(self.chat_history)} mensagens):")
        print("=" * 50)
        
        for i, msg in enumerate(self.chat_history, 1):
            print(f"\n{i}. Tu: {msg['user']}")
            if 'assistant' in msg:
                print(f"   {self.models[self.current_model]['name']}: {msg['assistant']}")
            print(f"   Timestamp: {msg['timestamp']}")
        
        print("=" * 50)
    
    def show_config(self):
        """Mostra configuração atual"""
        print("\n⚙️ CONFIGURAÇÃO ATUAL:")
        print("=" * 30)
        print(f"Modelo atual: {self.current_model or 'Nenhum'}")
        if self.current_model:
            model_info = self.models[self.current_model]
            print(f"Nome: {model_info['name']}")
            print(f"Tipo: {model_info['type']}")
        print(f"Arquivo de config: {self.config_file}")
        print("=" * 30)
    
    def run(self):
        """Executa interface principal"""
        print("🤖 TORRE CHAT - Seleção de Modelos")
        print("=" * 50)
        
        # Se não há modelo selecionado, selecionar
        if not self.current_model:
            print("⚠️ Nenhum modelo selecionado!")
            if not self.select_model():
                return
        
        while True:
            try:
                print(f"\n🎯 Modelo atual: {self.models[self.current_model]['name']}")
                command = input("Digite comando (help para ajuda): ").strip().lower()
                
                if command == 'quit':
                    print("👋 Até logo!")
                    break
                elif command == 'help':
                    self.show_help()
                elif command == 'models':
                    self.show_models()
                elif command == 'select':
                    self.select_model()
                elif command == 'chat':
                    self.chat_with_model()
                elif command == 'history':
                    self.show_history()
                elif command == 'config':
                    self.show_config()
                else:
                    print("❌ Comando não reconhecido. Digite 'help' para ajuda.")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Até logo!")
                break
            except Exception as e:
                print(f"❌ Erro: {e}")

def main():
    """Função principal"""
    chat = TorreChat()
    chat.run()

if __name__ == "__main__":
    main()
