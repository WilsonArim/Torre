# QUALITY GATES — Fase 3

**Objetivo:** elevar padrão de *segurança, arquitetura, performance e duplicação* sem travar fluxo quando não é crítico.

## Severidades
- **block**: impede aplicar (segurança/segredos/paths sensíveis).
- **advisory**: segue com aviso (arquitetura/perf/duplicação).

## Regras (v1)
1) **Segurança (block)**  
   - Qualquer indício de segredo/privado nas adições.  
   - Referência a paths sensíveis (.env, .ssh, id_rsa, *.pem, secrets.*).
2) **Arquitetura (advisory)**  
   - UI/Components importando infra/db diretamente.
3) **Performance (advisory)**  
   - Heurística de *nested loops* ou `map().map()` na mesma região alterada.
4) **Duplicação (advisory)**  
   - Símbolo novo com mesmo nome já existente noutro ficheiro.

## Saídas
- `report.md` com justificativa + provas de princípios.
- Métrica `advisory_mode=true` quando houver apenas avisos.
