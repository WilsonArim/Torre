# Padrão de Ordens - ENGENHEIRO v3.0

**Status:** ✅ Implementado e protegido

## Validação Automática

O ENGENHEIRO agora valida automaticamente o formato de todas as ordens antes da execução:

1. **Validador standalone**: `core/orquestrador/validate_order_format.py`
   - Valida todas as ordens no mailbox
   - Reporta erros de formato claramente
   - Referencia modelo documentado

2. **Validação integrada**: `engineer_cli.py`
   - Valida formato inline antes de executar
   - Bloqueia execução se formato inválido
   - Retorna código de erro 2 para formato inválido

3. **Makefile**: `make engineer_validate_format`
   - Validação manual antes de executar
   - Integrado em `make engineer_executa`

## Regras Enforçadas

✅ **Campos obrigatórios**: order_id, version, from_role, to_role, project, objective, ack, status  
✅ **ACK obrigatório**: ack.status deve ser ACCEPTED para execução  
✅ **Steps executáveis**: Não aceita steps como descrições ambíguas  
✅ **Tipos válidos**: command, make, validation apenas  
✅ **Comandos completos**: Steps do tipo "command" devem ter campo "command" preenchido

## Como Usar

**Estado-Maior e outros agentes devem:**

1. Consultar `relatorios/modelo_ordem_engenheiro.md` antes de criar ordens
2. Validar formato manualmente: `make -C core/orquestrador engineer_validate_format`
3. Garantir ACK=ACCEPTED antes de esperar execução
4. Usar sempre comandos executáveis completos nos steps

**Ordens fora do padrão serão bloqueadas automaticamente.**

## Referências

- **Modelo completo**: `relatorios/modelo_ordem_engenheiro.md`
- **Validador**: `core/orquestrador/validate_order_format.py`
- **PIN oficial**: `factory/pins/engenheiro.yaml`

---

**Conclusão:** Padrão documentado, validação automática implementada, bloqueios de segurança ativos. Estado-Maior e demais agentes devem seguir este padrão para todas as ordens futuras.

