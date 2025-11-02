# Atualização TORRE - Padrão de Ordens

**Data**: 2025-11-02  
**Agente**: ENGENHEIRO

## Alterações na TORRE

### PINs Atualizados

1. **`Torre/orquestrador/PIN_ENGENHEIRO.yaml`**
   - ✅ Adicionado `first_file_to_read: "ordem/ordens/engineer.in.yaml"`
   - Status: Atualizado

2. **`Torre/pins/engenheiro_torre.yaml`**
   - ✅ Adicionado `first_file_to_read` na secção `who_acts`
   - Status: Atualizado

### Sistema de Execução

**TORRE agora usa o mesmo sistema que FÁBRICA:**

- `engineer_executor.py` foi movido para `factory/pins/_deprecated/` (saneamento anterior)
- `cli.py` da TORRE faz fallback para `core/orquestrador/engineer_cli.py`
- Todas as validações e guardas do core aplicam-se também à TORRE

### Padrão Unificado

Agora **TODOS** os agentes ENGENHEIRO (FÁBRICA e TORRE) seguem:
- ✅ Mesmo formato de ordens
- ✅ Mesmas validações de formato
- ✅ Mesmas guardas (ACK obrigatório, steps executáveis)
- ✅ Mesmo modelo documentado em `relatorios/modelo_ordem_engenheiro.md`

### Validação

Ambos os sistemas validam:
- Formato YAML padronizado
- ACK obrigatório
- Steps como comandos executáveis
- Progresso reportado (N/M)

---

**Conclusão**: TORRE atualizada para seguir o mesmo padrão da FÁBRICA. Sistema unificado e consistente.

