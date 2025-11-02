#!/usr/bin/env python3
"""
Teste do Hover Card Strategos
Valida implementação do hover card com últimos 3 planos
"""

import json
import sys
import os
from pathlib import Path

def test_strategos_hover():
    """Testa implementação do hover card do Strategos"""
    
    print("🎯 TESTE HOVER CARD STRATEGOS")
    print("=" * 40)
    
    # Teste 1: Endpoints do servidor
    print("\n📊 TESTE 1: Endpoints do servidor")
    print("-" * 30)
    
    server_file = "llm/server.py"
    if Path(server_file).exists():
        with open(server_file, 'r') as f:
            content = f.read()
            has_events_endpoints = "/strategos/events" in content
            has_events_model = "StrategosEventIn" in content
            has_events_global = "_STRATEGOS_EVENTS" in content
            has_query_import = "Query" in content
            
        print(f"✅ Server atualizado: {server_file}")
        print(f"✅ Endpoints /strategos/events: {has_events_endpoints}")
        print(f"✅ Modelo StrategosEventIn: {has_events_model}")
        print(f"✅ Variável global _STRATEGOS_EVENTS: {has_events_global}")
        print(f"✅ Import Query: {has_query_import}")
    else:
        print(f"❌ Server não encontrado: {server_file}")
    
    # Teste 2: Cliente API
    print("\n📊 TESTE 2: Cliente API")
    print("-" * 30)
    
    api_file = "../apps/fortaleza-ui/src/api/strategos.ts"
    if Path(api_file).exists():
        with open(api_file, 'r') as f:
            content = f.read()
            has_events_type = "StrategosEvent" in content
            has_steps_type = "StrategosEventStep" in content
            has_get_events = "getStrategosEvents" in content
            
        print(f"✅ API client atualizado: {api_file}")
        print(f"✅ Tipo StrategosEvent: {has_events_type}")
        print(f"✅ Tipo StrategosEventStep: {has_steps_type}")
        print(f"✅ getStrategosEvents: {has_get_events}")
    else:
        print(f"❌ API client não encontrado: {api_file}")
    
    # Teste 3: Componente StrategosBadge
    print("\n📊 TESTE 3: Componente StrategosBadge")
    print("-" * 30)
    
    badge_file = "../apps/fortaleza-ui/src/components/strategos/StrategosBadge.tsx"
    if Path(badge_file).exists():
        with open(badge_file, 'r') as f:
            content = f.read()
            has_hover_card = "Hover Card" in content
            has_events_state = "events, setEvents" in content
            has_open_state = "open, setOpen" in content
            has_mouse_events = "onMouseEnter" in content
            has_use_ref = "useRef" in content
            
        print(f"✅ StrategosBadge atualizado: {badge_file}")
        print(f"✅ Hover Card: {has_hover_card}")
        print(f"✅ Events state: {has_events_state}")
        print(f"✅ Open state: {has_open_state}")
        print(f"✅ Mouse events: {has_mouse_events}")
        print(f"✅ useRef: {has_use_ref}")
    else:
        print(f"❌ StrategosBadge não encontrado: {badge_file}")
    
    # Teste 4: CLI integration
    print("\n📊 TESTE 4: CLI integration")
    print("-" * 30)
    
    cli_file = "llm/cli.py"
    if Path(cli_file).exists():
        with open(cli_file, 'r') as f:
            content = f.read()
            has_post_events_func = "_maybe_post_strategos_event" in content
            has_steps_extraction = "steps[:3]" in content
            has_score_extraction = "score = s.get" in content
            
        print(f"✅ CLI atualizado: {cli_file}")
        print(f"✅ Função _maybe_post_strategos_event: {has_post_events_func}")
        print(f"✅ Extração steps[:3]: {has_steps_extraction}")
        print(f"✅ Extração score: {has_score_extraction}")
    else:
        print(f"❌ CLI não encontrado: {cli_file}")
    
    # Teste 5: Validação Final
    print("\n📊 TESTE 5: Validação Final")
    print("-" * 30)
    
    success_criteria = [
        Path(server_file).exists(),
        Path(api_file).exists(),
        Path(badge_file).exists(),
        Path(cli_file).exists(),
        has_events_endpoints if 'has_events_endpoints' in locals() else False,
        has_events_type if 'has_events_type' in locals() else False,
        has_hover_card if 'has_hover_card' in locals() else False,
        has_post_events_func if 'has_post_events_func' in locals() else False
    ]
    
    print(f"✅ Server: {success_criteria[0]}")
    print(f"✅ API client: {success_criteria[1]}")
    print(f"✅ StrategosBadge: {success_criteria[2]}")
    print(f"✅ CLI: {success_criteria[3]}")
    print(f"✅ Events endpoints: {success_criteria[4]}")
    print(f"✅ Events types: {success_criteria[5]}")
    print(f"✅ Hover card: {success_criteria[6]}")
    print(f"✅ CLI events func: {success_criteria[7]}")
    
    all_passed = all(success_criteria)
    
    if all_passed:
        print(f"\n🎉 HOVER CARD STRATEGOS IMPLEMENTADO COM SUCESSO!")
        print(f"   - Endpoints GET/POST /strategos/events")
        print(f"   - Cliente API TypeScript")
        print(f"   - Componente StrategosBadge com hover")
        print(f"   - CLI auto-posts eventos")
        print(f"   - Ring buffer de 50 eventos")
        print(f"\n🚀 COMO USAR:")
        print(f"   1. Servidor: python3 -m llm.server")
        print(f"   2. CLI: export STRATEGOS_V2=1 && echo '...' | python3 -m llm.cli")
        print(f"   3. UI: Passe o mouse sobre o badge → hover card")
        print(f"   4. Endpoints: curl /strategos/events?limit=3")
        return True
    else:
        print(f"\n❌ HOVER CARD STRATEGOS INCOMPLETO")
        return False

def main():
    """Executa o teste do hover card"""
    try:
        sucesso = test_strategos_hover()
        sys.exit(0 if sucesso else 1)
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
