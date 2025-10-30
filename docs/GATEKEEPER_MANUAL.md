## GATEKEEPER_MANUAL

Critérios de veto/aprovação para G4/G5 e leitura dos relatórios SOP.

### Leituras
- `relatorios/relatorio_sop.md` para contexto geral
- `relatorios/sop_status.json` para status e métricas
- `relatorios/parecer_gatekeeper.md` para registrar decisão
 - `relatorios/pipeline_gate_input.json` para `pipeline_ok` e `issues`
 - `pipeline/PIPELINE_TOC.md` como mapa navegável

### Decisão
Validar SLAs/SLOs, plano de DR, on-call, formação e rollback.

### Critério obrigatório de Pipeline
- `pipeline_ok == true`. Caso `false`, emitir VETO com referência a `relatorios/pipeline_audit.json`.

### Secção “Pipeline” no parecer
```
## Pipeline
- Estado: OK / INVÁLIDA
- Issues: ver relatorios/pipeline_audit.json
- TOC: pipeline/PIPELINE_TOC.md
```


