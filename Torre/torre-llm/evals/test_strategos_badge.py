#!/usr/bin/env python3
"""
Teste do StrategosBadge
Valida implementação do mini-badge Strategos na UI
"""

import json
import sys
import os
from pathlib import Path

def test_strategos_badge():
    """Testa implementação do StrategosBadge"""
    
    print("🎯 TESTE STRATEGOS BADGE")
    print("=" * 40)
    
    # Teste 1: Endpoints do servidor
    print("\n📊 TESTE 1: Endpoints do servidor")
    print("-" * 30)
    
    server_file = "llm/server.py"
    if Path(server_file).exists():
        with open(server_file, 'r') as f:
            content = f.read()
            has_badge_endpoints = "/strategos/badge" in content
            has_badge_model = "StrategosBadgeIn" in content
            has_global_badge = "_STRATEGOS_BADGE" in content
            
        print(f"✅ Server atualizado: {server_file}")
        print(f"✅ Endpoints /strategos/badge: {has_badge_endpoints}")
        print(f"✅ Modelo StrategosBadgeIn: {has_badge_model}")
        print(f"✅ Variável global _STRATEGOS_BADGE: {has_global_badge}")
    else:
        print(f"❌ Server não encontrado: {server_file}")
    
    # Teste 2: Cliente API
    print("\n📊 TESTE 2: Cliente API")
    print("-" * 30)
    
    api_file = "../apps/fortaleza-ui/src/api/strategos.ts"
    if Path(api_file).exists():
        with open(api_file, 'r') as f:
            content = f.read()
            has_badge_type = "StrategosBadge" in content
            has_get_badge = "getStrategosBadge" in content
            has_post_badge = "postStrategosBadge" in content
            
        print(f"✅ API client atualizado: {api_file}")
        print(f"✅ Tipo StrategosBadge: {has_badge_type}")
        print(f"✅ getStrategosBadge: {has_get_badge}")
        print(f"✅ postStrategosBadge: {has_post_badge}")
    else:
        print(f"❌ API client não encontrado: {api_file}")
    
    # Teste 3: Componente StrategosBadge
    print("\n📊 TESTE 3: Componente StrategosBadge")
    print("-" * 30)
    
    badge_file = "../apps/fortaleza-ui/src/components/strategos/StrategosBadge.tsx"
    if Path(badge_file).exists():
        with open(badge_file, 'r') as f:
            content = f.read()
            has_use_effect = "useEffect" in content
            has_color_logic = "color =" in content
            has_a2g_logic = "attempts_to_green_est" in content
            has_auto_refresh = "setInterval" in content
            
        print(f"✅ StrategosBadge criado: {badge_file}")
        print(f"✅ useEffect para carregamento: {has_use_effect}")
        print(f"✅ Lógica de cores: {has_color_logic}")
        print(f"✅ Lógica A2G: {has_a2g_logic}")
        print(f"✅ Auto-refresh: {has_auto_refresh}")
    else:
        print(f"❌ StrategosBadge não encontrado: {badge_file}")
    
    # Teste 4: Integração LeftSidebar
    print("\n📊 TESTE 4: Integração LeftSidebar")
    print("-" * 30)
    
    sidebar_file = "../apps/fortaleza-ui/src/components/layout/LeftSidebar.tsx"
    if Path(sidebar_file).exists():
        with open(sidebar_file, 'r') as f:
            content = f.read()
            has_badge_import = "StrategosBadge" in content
            has_badge_component = "<StrategosBadge" in content
            has_flex_layout = "justify-between" in content
            
        print(f"✅ LeftSidebar atualizado: {sidebar_file}")
        print(f"✅ Import do StrategosBadge: {has_badge_import}")
        print(f"✅ Componente StrategosBadge: {has_badge_component}")
        print(f"✅ Layout flex com justify-between: {has_flex_layout}")
    else:
        print(f"❌ LeftSidebar não encontrado: {sidebar_file}")
    
    # Teste 5: CLI integration
    print("\n📊 TESTE 5: CLI integration")
    print("-" * 30)
    
    cli_file = "llm/cli.py"
    if Path(cli_file).exists():
        with open(cli_file, 'r') as f:
            content = f.read()
            has_post_badge_func = "_maybe_post_strategos_badge" in content
            has_urlopen_import = "urlopen" in content
            has_datetime_import = "datetime" in content
            has_fire_forget = "fire-and-forget" in content
            
        print(f"✅ CLI atualizado: {cli_file}")
        print(f"✅ Função _maybe_post_strategos_badge: {has_post_badge_func}")
        print(f"✅ Import urlopen: {has_urlopen_import}")
        print(f"✅ Import datetime: {has_datetime_import}")
        print(f"✅ Fire-and-forget: {has_fire_forget}")
    else:
        print(f"❌ CLI não encontrado: {cli_file}")
    
    # Teste 6: Validação Final
    print("\n📊 TESTE 6: Validação Final")
    print("-" * 30)
    
    success_criteria = [
        Path(server_file).exists(),
        Path(api_file).exists(),
        Path(badge_file).exists(),
        Path(sidebar_file).exists(),
        Path(cli_file).exists(),
        has_badge_endpoints if 'has_badge_endpoints' in locals() else False,
        has_badge_type if 'has_badge_type' in locals() else False,
        has_badge_component if 'has_badge_component' in locals() else False,
        has_post_badge_func if 'has_post_badge_func' in locals() else False
    ]
    
    print(f"✅ Server: {success_criteria[0]}")
    print(f"✅ API client: {success_criteria[1]}")
    print(f"✅ StrategosBadge: {success_criteria[2]}")
    print(f"✅ LeftSidebar: {success_criteria[3]}")
    print(f"✅ CLI: {success_criteria[4]}")
    print(f"✅ Endpoints: {success_criteria[5]}")
    print(f"✅ Types: {success_criteria[6]}")
    print(f"✅ Component: {success_criteria[7]}")
    print(f"✅ CLI func: {success_criteria[8]}")
    
    all_passed = all(success_criteria)
    
    if all_passed:
        print(f"\n🎉 STRATEGOS BADGE IMPLEMENTADO COM SUCESSO!")
        print(f"   - Endpoints GET/POST /strategos/badge")
        print(f"   - Cliente API TypeScript")
        print(f"   - Componente StrategosBadge")
        print(f"   - Integração LeftSidebar")
        print(f"   - CLI auto-posts badge")
        print(f"\n🚀 COMO USAR:")
        print(f"   1. Servidor: python3 -m llm.server")
        print(f"   2. CLI: export STRATEGOS_V2=1 && echo '...' | python3 -m llm.cli")
        print(f"   3. UI: Badge aparece automaticamente na sidebar")
        return True
    else:
        print(f"\n❌ STRATEGOS BADGE INCOMPLETO")
        return False

def main():
    """Executa o teste do StrategosBadge"""
    try:
        sucesso = test_strategos_badge()
        sys.exit(0 if sucesso else 1)
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
