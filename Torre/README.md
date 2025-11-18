# TORRE — Sistema de Treino da LLM-Engenheira da FÁBRICA

**Agente**: Engenheiro da TORRE  
**Função**: Executa treinos, gera checkpoints, mede resultados e reporta ao Estado-Maior

---

## 📁 Estrutura

```
torre/
  checkpoints/          # Checkpoints de treino (.ckpt)
  logs/                 # Logs de execução (.log)
  datasets/             # Datasets de treino
  reports/              # Relatórios técnicos
  cli/                  # Scripts de execução
    train.py            # Executor de treino
    eval.py             # Avaliador de checkpoints
    generate_report.py  # Gerador de relatórios
    create_checkpoint.py # Criador de checkpoints
    update_status.py    # Atualizador de status
    validate_dataset.py # Validador de datasets
  orquestrador/         # Orquestrador (sistema de ordens)
    cli.py              # CLI principal
    Makefile            # Comandos make
  curriculum/
    PLAN.md             # Plano de treino (5 fases)
  data/
    SOURCES.md          # Inventário de fontes
  models/
    ARCHITECTURE.md     # Arquitetura técnica
  reports/
    EVAL_CRITERIA.md    # Critérios de avaliação
```

---

## 🚀 Comandos Principais

### Orquestrador (Sistema de Ordens)

```bash
# Executar treino de uma fase
python3 torre/orquestrador/cli.py treino fase0|fase1|fase2|fase3|fase4|fase5
# ou via make:
make -C torre/orquestrador treino PHASE=fase0

# Validações
make -C torre/orquestrador pipeline_validate
make -C torre/orquestrador sop
make -C torre/orquestrador gatekeeper_run

# Executar ordem do Estado-Maior
make -C torre/orquestrador executa
make -C torre/orquestrador status
```

### Treino (CLI Direto)

```bash
# Executar treino da Fase 0
make torre_train PHASE=0

# Executar treino com dataset específico
make torre_train PHASE=1 DATASET=torre/datasets/fase1/

# Executar treino com epochs customizados
make torre_train PHASE=2 EPOCHS=20
```

### Avaliação

```bash
# Avaliar checkpoint
make torre_eval CHECKPOINT=checkpoint_phase0_epoch10_20250127_103000.ckpt

# Avaliar com dataset de validação
make torre_eval CHECKPOINT=checkpoint_phase1_epoch10_*.ckpt DATASET=torre/eval_datasets/fase1/
```

### Relatórios e Status

```bash
# Gerar relatório técnico
make torre_report

# Criar checkpoint manual
make torre_checkpoint

# Atualizar status
make torre_status

# Listar checkpoints
make torre_list_checkpoints

# Listar logs
make torre_list_logs
```

### Validação

```bash
# Validar dataset
make torre_validate_dataset DATASET=torre/datasets/fase0/
```

### Help

```bash
# Ver todos os comandos
make torre_help
```

---

## 📋 Regras Operacionais

### Domínio de Ação

- ✅ **Permitido**: Trabalhar apenas dentro de `torre/`
- ❌ **Proibido**: Criar ou alterar ficheiros fora de `torre/`
- ✅ **Leitura**: Pode ler código da FÁBRICA para aprender (não modificar)

### Sistema de Ordens

- ✅ **Entrada**: `ordem/ordens/engineer.in.yaml` (ordens do Estado-Maior)
- ✅ **Saída**: `relatorios/para_estado_maior/engineer.out.json` (relatórios)
- ✅ **Citação**: Todos os relatórios citam `order_id` correspondente (ART-09)

### Treino

- ✅ Só executa treinos com base em planos aprovados pelo Estado-Maior
- ✅ Cada treino gera logs, métricas e checkpoints rastreáveis
- ✅ Valida datasets antes do treino (conformidade constitucional)

### Outputs

- ✅ Todos os outputs em `torre/reports/` ou `relatorios/`
- ✅ Checkpoints em `torre/checkpoints/`
- ✅ Logs em `torre/logs/`

### Conformidade

- ✅ ART-04: Verificabilidade (logs e checkpoints rastreáveis)
- ✅ ART-07: Transparência (metadados em todos os outputs)
- ✅ ART-09: Evidência (artefactos citados)

---

## 🔍 Exemplos de Uso

### Fluxo Completo de Treino

```bash
# 1. Validar dataset
make torre_validate_dataset DATASET=torre/datasets/fase0/

# 2. Executar treino
make torre_train PHASE=0 EPOCHS=10

# 3. Criar checkpoint
make torre_checkpoint

# 4. Avaliar checkpoint
make torre_eval CHECKPOINT=checkpoint_phase0_epoch10_*.ckpt

# 5. Gerar relatório
make torre_report

# 6. Atualizar status
make torre_status
```

### Verificar Progresso

```bash
# Ver checkpoints disponíveis
make torre_list_checkpoints

# Ver logs recentes
make torre_list_logs

# Ver relatório completo
cat torre/reports/train_summary.md

# Ver status atual
cat relatorios/torre_status.json
```

---

## 📊 Saídas Esperadas

### Checkpoints (`torre/checkpoints/*.ckpt`)

- Formato JSON com estado do treino
- Métricas por epoch
- Conformidade constitucional

### Logs (`torre/logs/*.log`)

- Timestamp de cada operação
- Nível de log (INFO, WARNING, ERROR)
- Mensagens detalhadas

### Relatórios (`torre/reports/train_summary.md`)

- Status atual da TORRE
- Checkpoints recentes
- Métricas de performance
- Artefactos citados (ART-09)

### Status (`relatorios/torre_status.json`)

- Última atualização
- Estatísticas (checkpoints, logs)
- Estado atual do treino

---

## 🛡️ Limites Constitucionais

- ❌ Não pode alterar planos de treino (apenas executar)
- ❌ Não pode editar ficheiros fora de `torre/`
- ✅ Toda execução documentada e auditável
- ✅ Erros críticos reportados ao Estado-Maior

---

## 📚 Referências

- `torre/curriculum/PLAN.md` - Plano completo de treino
- `torre/models/ARCHITECTURE.md` - Arquitetura técnica
- `torre/reports/EVAL_CRITERIA.md` - Critérios de avaliação
- `core/sop/constituição.yaml` - Regras fundamentais

---

**Versão**: 1.0  
**Última atualização**: 2025-01-27
