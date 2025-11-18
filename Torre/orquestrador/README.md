# Orquestrador da TORRE — Documentação

**Agente**: Engenheiro da TORRE  
**Função**: Executa ordens do Estado-Maior e operações de treino  
**PIN**: v2.0 (ver `PIN.md`)

---

## 🎯 Modos Operacionais (PIN v2.0)

### 🛠️ MODO STANDBY

**Ativação**: quando não há ordens válidas no mailbox

**Frase de Abertura Obrigatória**:

```
🛠️ MODO STANDBY — A aguardar ordens válidas do Estado-Maior.
```

**Ações**:

- Validar formato de ordem (YAML) e schema
- Não executar nada sem `order_id`, `objective` e `deliverables`

### 🛠️ MODO EXECUÇÃO

**Ativação**: quando há ordem válida com `status: OPEN`

**Frase de Abertura Obrigatória**:

```
🛠️ MODO EXECUÇÃO — A executar a tarefa técnica atribuída (sem papéis de Gatekeeper/SOP).
```

**Ciclo de 5 Fases**:

1. **ACK**: marcar ordem como ACCEPTED
2. **Execução**: executar steps técnicos
3. **Validação**: validar artefactos (SOP, pipeline, zero riscos)
4. **Relatório**: gerar relatório JSON
5. **Fecho**: marcar ordem como DONE

**Frase de Fechamento Obrigatória**:

```
✅ RELATÓRIO EMITIDO — Estado-Maior pode avaliar (Gatekeeper+SOP). Avanço de gate só após PASS.
```

---

## 📋 Regra-Mãe de Ownership

### Bootstrap (sem pipeline ativa)

- **Estado-Maior (TORRE)** → estratégia, decisões, criação/alteração de regras/constituição/pipeline, aprovação de gates, emitir ordens
- **Engenheiro (TORRE)** → execução prática: escrever/alterar código, correr `make`/scripts, gerar artefactos, testes, refatoração

### Durante pipeline (quando ativada)

- **G0, G2, G4**: dono = **Estado-Maior** (TORRE)
- **G1, G3**: dono = **Engenheiro** (TORRE)

### Verificar Ownership

```bash
# Verificar quem deve executar uma tarefa
make -C torre/orquestrador who task="criar script para validar código"
make -C torre/orquestrador who task="alterar constituição" gate=G0
```

---

## 📁 Estrutura

```
torre/orquestrador/
  cli.py                # CLI principal
  engineer_executor.py  # Executor completo (ciclo de 5 fases)
  Makefile              # Comandos make
  PIN.md                # PIN do Engenheiro
  PIN_ESTADO_MAIOR.md   # PIN do Estado-Maior
```

---

## 🚀 Comandos Disponíveis

### Via Python

```bash
# Executar treino
python3 torre/orquestrador/cli.py treino fase0|fase1|fase2|fase3|fase4|fase5

# Validações
python3 torre/orquestrador/cli.py pipeline_validate
python3 torre/orquestrador/cli.py sop
python3 torre/orquestrador/cli.py gatekeeper_run

# Ordens do Estado-Maior
python3 torre/orquestrador/cli.py executa
python3 torre/orquestrador/cli.py status
```

### Via Make

```bash
# Executar treino
make -C torre/orquestrador treino PHASE=fase0

# Validações
make -C torre/orquestrador pipeline_validate
make -C torre/orquestrador sop
make -C torre/orquestrador gatekeeper_run

# Ordens do Estado-Maior
make -C torre/orquestrador executa
make -C torre/orquestrador status
```

---

## 📋 Sistema de Ordens

### Entrada (`ordem/ordens/engineer.in.yaml`)

- Ordens do Estado-Maior para o Engenheiro
- Status: `OPEN` → `DONE`

### Saída (`relatorios/para_estado_maior/engineer.out.json`)

- Relatórios de execução
- Métricas e artefactos gerados
- Cita `order_id` correspondente (ART-09)

---

## 🔍 Integração com FÁBRICA

- **Pipeline**: Valida via `core/orquestrador/cli.py validate_pipeline`
- **SOP**: Executa via `core/scripts/validator.py`
- **Gatekeeper**: Executa via `core/orquestrador/cli.py gatekeeper_run`

---

## 📊 Logs

Todos os comandos geram logs em `torre/logs/orquestrador_YYYYMMDD.log`

---

## 🛡️ Conformidade

- ✅ ART-04: Verificabilidade (logs rastreáveis)
- ✅ ART-07: Transparência (metadados em relatórios)
- ✅ ART-09: Evidência (artefactos citados)
- ✅ **Regra Zero Riscos**: Campo `risks` sempre vazio `[]`; bloqueio automático se menção a riscos em artefactos

### Separação de Papéis

- ❌ **Gatekeeper**: Não pode assumir (função do Estado-Maior)
- ❌ **SOP**: Não pode assumir (função do Estado-Maior)
- ✅ **Execução Técnica**: Apenas executa tarefas atribuídas

---

## 📄 Schema de Relatório (PIN v2.0)

```json
{
  "order_id": "uuid-v4",
  "report_id": "uuid-v4",
  "version": 1,
  "from_role": "ENGENHEIRO",
  "to_role": "ESTADO-MAIOR",
  "project": "string",
  "module": "string",
  "gate": "string",
  "started_at": "iso-datetime",
  "finished_at": "iso-datetime",
  "status": ["PASS", "WARN", "BLOCKED"],
  "findings": [],
  "metrics": {},
  "risks": [], // SEMPRE VAZIO
  "artifacts": [],
  "references": [],
  "signature": ""
}
```

---

**Versão**: 2.0  
**PIN**: v2.0  
**Última atualização**: 2025-11-01
