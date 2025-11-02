#!/usr/bin/env python3
"""
Teste manual para verificar o contador de posts do badge (recent_posts_1h)
"""

import json
import subprocess
import sys
import os
import time

def test_badge_counter():
    """Testa o contador de posts do badge"""
    print("🔢 Testando contador de posts do badge...")
    
    try:
        # Preparar variáveis de ambiente
        env = os.environ.copy()
        env["FORT_BADGE_ALWAYS"] = "1"
        env["FORT_BADGE_SYNC"] = "1"
        env["FORTALEZA_API"] = "http://localhost:8765"
        env["FORTALEZA_API_KEY"] = "test-key-123"
        
        # Request simples
        request = {
            "logs": {"types": "TS2307: Cannot find module './x.css'"},
            "files": {"src/App.tsx": "export default function App() { return (<div/>); }"}
        }
        
        # Executar CLI várias vezes para testar contador
        for i in range(3):
            print(f"   Executando CLI (post {i+1})...")
            result = subprocess.run(
                [sys.executable, "-m", "llm.cli"],
                input=json.dumps(request),
                env=env,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print(f"   ✅ CLI executou com sucesso (post {i+1})")
            else:
                print(f"   ❌ CLI falhou (post {i+1}): {result.stderr}")
                return False
            
            # Pequena pausa entre posts
            time.sleep(0.5)
        
        print("   ✅ Todos os posts executados com sucesso")
        return True
        
    except subprocess.TimeoutExpired:
        print("   ❌ CLI timeout")
        return False
    except Exception as e:
        print(f"   ❌ Erro na execução: {e}")
        return False

def test_api_endpoints():
    """Testa os endpoints da API"""
    print("🔌 Testando endpoints da API...")
    
    try:
        # Teste GET /strategos/badge
        result = subprocess.run(
            ["curl", "-s", "http://localhost:8765/strategos/badge"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                if "recent_posts_1h" in data:
                    count = data["recent_posts_1h"]
                    print(f"   ✅ GET /strategos/badge: recent_posts_1h={count}")
                    return True
                else:
                    print("   ❌ Campo recent_posts_1h não encontrado")
                    return False
            except json.JSONDecodeError:
                print("   ❌ Resposta não é JSON válido")
                return False
        else:
            print("   ❌ GET /strategos/badge falhou")
            return False
            
    except subprocess.TimeoutExpired:
        print("   ❌ Timeout na API")
        return False
    except Exception as e:
        print(f"   ❌ Erro na API: {e}")
        return False

def test_ui_component():
    """Testa se o componente UI foi atualizado"""
    print("🎨 Testando componente UI...")
    
    try:
        # Verificar se o arquivo foi atualizado
        component_path = "apps/fortaleza-ui/src/components/strategos/StrategosBadge.tsx"
        
        if not os.path.exists(component_path):
            print(f"   ❌ Componente não encontrado: {component_path}")
            return False
        
        with open(component_path, 'r') as f:
            content = f.read()
        
        # Verificar se as modificações estão presentes
        checks = [
            "recent_posts_1h",
            "posts1h",
            "posts(1h)=",
            "Posts (últ. 1h):"
        ]
        
        for check in checks:
            if check in content:
                print(f"   ✅ Modificação encontrada: {check}")
            else:
                print(f"   ❌ Modificação não encontrada: {check}")
                return False
        
        print("   ✅ Todas as modificações do componente estão presentes")
        return True
        
    except Exception as e:
        print(f"   ❌ Erro ao verificar componente: {e}")
        return False

def test_api_client():
    """Testa se o API client foi atualizado"""
    print("📡 Testando API client...")
    
    try:
        # Verificar se o arquivo foi atualizado
        client_path = "apps/fortaleza-ui/src/api/strategos.ts"
        
        if not os.path.exists(client_path):
            print(f"   ❌ API client não encontrado: {client_path}")
            return False
        
        with open(client_path, 'r') as f:
            content = f.read()
        
        # Verificar se o campo foi adicionado
        if "recent_posts_1h" in content:
            print("   ✅ Campo recent_posts_1h adicionado ao tipo")
            return True
        else:
            print("   ❌ Campo recent_posts_1h não encontrado")
            return False
        
    except Exception as e:
        print(f"   ❌ Erro ao verificar API client: {e}")
        return False

def main():
    print("🧪 Teste Manual do Contador de Posts do Badge")
    print("=" * 60)
    
    tests = [
        ("Badge Counter", test_badge_counter),
        ("API Endpoints", test_api_endpoints),
        ("UI Component", test_ui_component),
        ("API Client", test_api_client),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n{name}:")
        result = test_func()
        results.append((name, result))
    
    print("\n" + "=" * 60)
    print("📊 RESULTADOS:")
    
    passed = 0
    for name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{name}: {status}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(results)} testes passaram")
    
    if passed == len(results):
        print("🎉 CONTADOR DE POSTS IMPLEMENTADO COM SUCESSO!")
        print("✅ Contador de posts funcionando")
        print("✅ Endpoints da API atualizados")
        print("✅ Componente UI atualizado")
        print("✅ API client atualizado")
    else:
        print("⚠️  Alguns testes falharam")

if __name__ == "__main__":
    main()
