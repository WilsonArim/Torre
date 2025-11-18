# PIN — ENGENHEIRO v3.0 — Documentação

## Comandos Disponíveis

### Via Makefile

```bash
make -C core/orquestrador engineer_executa   # Executa última ordem aberta
make -C core/orquestrador engineer_status     # Mostra status atual
make -C core/orquestrador engineer_limpa       # Rotaciona relatórios antigos
```

### Via CLI Direto

```bash
python3 core/orquestrador/engineer_cli.py executa
python3 core/orquestrador/engineer_cli.py status
python3 core/orquestrador/engineer_cli.py limpa
```

## Formato de Ordens (engineer.in.yaml)

```yaml
- id: "ORD-001"
  title: "Validar SOP e gerar relatórios"
  status: "OPEN"
  created_at: "2025-10-30T10:00:00"
  created_by: "Estado-Maior"
  steps:
    - id: "step-1"
      type: "validation"
      validation: "sop"
      description: "Executar validação SOP completa"
    - id: "step-2"
      type: "make"
      target: "gatekeeper_prep"
      description: "Preparar inputs do Gatekeeper"
    - id: "step-3"
      type: "command"
      command: "ls -la relatorios/"
      description: "Listar artefactos gerados"
```

## Tipos de Steps Suportados

1. **`type: "command"`** — Executa comando shell genérico

   ```yaml
   - id: "step-name"
     type: "command"
     command: "echo 'Hello World'"
     timeout: 300 # opcional, segundos
   ```

2. **`type: "make"`** — Executa target do Makefile

   ```yaml
   - id: "step-name"
     type: "make"
     target: "sop"
     timeout: 300 # opcional
   ```

3. **`type: "validation"`** — Executa validação específica
   ```yaml
   - id: "step-name"
     type: "validation"
     validation: "sop" # ou "pipeline"
     timeout: 300 # opcional
   ```

## Relatórios Gerados

Relatórios são salvos em `relatorios/para_estado_maior/engineer.out.json` com estrutura:

```json
{
  "order_id": "ORD-001",
  "order_title": "Título da Ordem",
  "status": "DONE",
  "executed_at": "2025-10-30T10:05:00",
  "executed_by": "ENGENHEIRO-v3.0",
  "metrics": {
    "steps_total": 3,
    "steps_success": 3,
    "steps_failed": 0,
    "success_rate": 100.0
  },
  "artefacts": ["Relatórios gerados", "SBOM"],
  "failures": [],  # POLÍTICA ZERO RISCO: não existem riscos, apenas falhas graves
  "recommendations": ["Ordem executada com sucesso..."],
  "step_results": [...]
}
```

**Nota importante**: POLÍTICA ZERO RISCO — Não existem "riscos" no sistema. Qualquer problema identificado é uma **falha grave** que bloqueia imediatamente o processo até correção.

## Rastreabilidade (ART-04, ART-09)

- ✅ Todos os relatórios incluem timestamps e assinatura do agente
- ✅ Links para ficheiros de origem e destino
- ✅ Métricas e evidências técnicas documentadas
- ✅ Logs de execução preservados

## Fluxo de Execução

1. **Estado-Maior cria ordem** em `ordem/ordens/engineer.in.yaml` com `status: OPEN`
2. **ENGENHEIRO executa** comando `executa`
3. **ENGENHEIRO marca** ordem como `ack: ACCEPTED`
4. **ENGENHEIRO executa** todos os steps sequencialmente
5. **ENGENHEIRO gera** relatório em `relatorios/para_estado_maior/engineer.out.json`
6. **ENGENHEIRO atualiza** ordem para `status: DONE`
7. **Estado-Maior lê** relatório e toma decisões

## Conformidade Constitucional

- ✅ **ART-04 (Verificabilidade)**: Todos os outputs são rastreáveis
- ✅ **ART-09 (Evidência)**: Decisões baseadas em artefactos verificáveis
- ✅ **ART-03 (Consciência Técnica)**: ENGENHEIRO executa apenas, não cria políticas
- ✅ **ART-07 (Transparência)**: Relatórios incluem agente, data, objetivo e regras aplicadas
