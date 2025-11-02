#!/usr/bin/env python3
"""
Teste de Integração da Torre
Valida se a Torre está funcionando corretamente para integração com a Fortaleza
"""

import json
import requests
import time
from typing import Dict, Any

class TorreIntegrationTest:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.model = "torre:latest"
        
    def test_health(self) -> bool:
        """Testa se o serviço está respondendo"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Health check falhou: {e}")
            return False
    
    def test_models_endpoint(self) -> bool:
        """Testa o endpoint /v1/models"""
        try:
            response = requests.get(f"{self.base_url}/v1/models", timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = [m["id"] for m in data.get("data", [])]
                # Verifica se o modelo existe (com ou sem :latest)
                model_found = any(m.startswith(self.model.replace(':latest', '')) for m in models)
                if model_found:
                    print(f"✅ Modelo '{self.model}' encontrado")
                    return True
                else:
                    print(f"❌ Modelo '{self.model}' não encontrado. Disponíveis: {models}")
                    return False
            else:
                print(f"❌ /v1/models retornou {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Teste /v1/models falhou: {e}")
            return False
    
    def test_chat_completion(self, stream: bool = False) -> bool:
        """Testa o endpoint de chat completions"""
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": "Diga apenas: 'Torre funcionando!'"}
            ],
            "stream": stream,
            "temperature": 0.7,
            "max_tokens": 50
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload,
                timeout=30,
                stream=stream
            )
            
            if response.status_code == 200:
                if stream:
                    # Teste streaming
                    content = ""
                    for line in response.iter_lines():
                        if line:
                            line_str = line.decode('utf-8')
                            if line_str.startswith('data: '):
                                data_str = line_str[6:]  # Remove 'data: '
                                if data_str == '[DONE]':
                                    break
                                try:
                                    data = json.loads(data_str)
                                    if 'choices' in data and data['choices']:
                                        delta = data['choices'][0].get('delta', {})
                                        if 'content' in delta:
                                            content += delta['content']
                                except json.JSONDecodeError:
                                    continue
                    
                    print(f"✅ Streaming funcionando. Resposta: '{content[:50]}...'")
                    return "Torre" in content
                else:
                    # Teste não-streaming
                    data = response.json()
                    content = data['choices'][0]['message']['content']
                    print(f"✅ Chat completion funcionando. Resposta: '{content[:50]}...'")
                    return "Torre" in content
            else:
                print(f"❌ Chat completion retornou {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Teste chat completion falhou: {e}")
            return False
    
    def test_performance(self) -> Dict[str, Any]:
        """Testa performance básica"""
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": "Responda em uma frase: O que é a Torre?"}
            ],
            "stream": False,
            "temperature": 0.7,
            "max_tokens": 100
        }
        
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload,
                timeout=30
            )
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                latency = (end_time - start_time) * 1000  # ms
                tokens = data['usage']['total_tokens']
                
                return {
                    "latency_ms": round(latency, 2),
                    "total_tokens": tokens,
                    "tokens_per_second": round(tokens / (latency / 1000), 2)
                }
            else:
                return {"error": f"Status {response.status_code}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Executa todos os testes"""
        print("🧪 TESTE DE INTEGRAÇÃO DA TORRE")
        print("=" * 50)
        
        results = {
            "health": False,
            "models": False,
            "chat_completion": False,
            "streaming": False,
            "performance": None,
            "overall": False
        }
        
        # Teste 1: Health check
        print("\n1️⃣ Testando health check...")
        results["health"] = self.test_health()
        
        if not results["health"]:
            print("❌ Serviço não está respondendo. Verifique se o Ollama está rodando.")
            return results
        
        # Teste 2: Endpoint de modelos
        print("\n2️⃣ Testando endpoint de modelos...")
        results["models"] = self.test_models_endpoint()
        
        # Teste 3: Chat completion (não-streaming)
        print("\n3️⃣ Testando chat completion...")
        results["chat_completion"] = self.test_chat_completion(stream=False)
        
        # Teste 4: Chat completion (streaming)
        print("\n4️⃣ Testando streaming...")
        results["streaming"] = self.test_chat_completion(stream=True)
        
        # Teste 5: Performance
        print("\n5️⃣ Testando performance...")
        results["performance"] = self.test_performance()
        
        # Resultado geral
        results["overall"] = all([
            results["health"],
            results["models"], 
            results["chat_completion"],
            results["streaming"]
        ])
        
        # Relatório final
        print("\n" + "=" * 50)
        print("📊 RELATÓRIO FINAL")
        print("=" * 50)
        
        for test_name, result in results.items():
            if test_name == "performance":
                if isinstance(result, dict) and "error" not in result:
                    print(f"⚡ Performance: {result['latency_ms']}ms, {result['total_tokens']} tokens")
                else:
                    print(f"❌ Performance: {result}")
            else:
                status = "✅" if result else "❌"
                print(f"{status} {test_name.title()}")
        
        if results["overall"]:
            print("\n🎉 TORRE PRONTA PARA INTEGRAÇÃO!")
            print("\n📋 Configuração para Cursor:")
            print("   Base URL: http://localhost:11434/v1")
            print("   API Key: local")
            print("   Model: torre")
        else:
            print("\n⚠️  Alguns testes falharam. Verifique a configuração.")
        
        return results

if __name__ == "__main__":
    tester = TorreIntegrationTest()
    results = tester.run_all_tests()
    
    # Exit code baseado no resultado
    exit(0 if results["overall"] else 1)
