# Modelo Ideal de Ordem para ENGENHEIRO v3.0

**OWNER: ENGENHEIRO — Próxima ação:** Documentar formato ideal de ordens executáveis

## Resposta ao Estado-Maior

### Formato YAML Padrão

O ENGENHEIRO executa ordens via mailbox `ordem/ordens/engineer.in.yaml` com o seguinte formato:

```yaml
- order_id: "uuid-v4-unico"
  version: 1
  from_role: "ESTADO-MAIOR"
  to_role: "ENGENHEIRO"
  project: "FABRICA"  # ou "TORRE"
  module: "MODULO_ESPECIFICO"
  gate: "G0"  # Gate atual
  urgency: "normal"  # normal, alta, critical, informativa
  created_at: "2025-11-02T12:00:00Z"
  expires_at: "2025-11-09T23:59:59Z"
  context_refs:
    - "path/to/file1.yaml"
    - "path/to/file2.md"
  objective: "Descrição clara e objetiva do que deve ser feito"
  constraints:
    - "ART-01: Integridade"
    - "Não alterar core/sop/constituição.yaml"
  steps:
    - id: "step-1"
      type: "command"
      command: "comando shell executável completo"
      description: "Descrição do que este step faz"
      timeout: 300  # opcional, segundos
    - id: "step-2"
      type: "make"
      target: "nome_do_target"
      description: "Executar target do Makefile"
    - id: "step-3"
      type: "validation"
      validation: "sop"  # ou "pipeline"
      description: "Executar validação específica"
  deliverables:
    - path: "relatorios/arquivo.md"
      type: "markdown"
    - path: "core/scripts/arquivo.py"
      type: "code"
  success_criteria:
    - "Criterio 1 claro e verificável"
    - "Criterio 2 mensurável"
  escalation:
    owner: "@EstadoMaior"
    when: "Condições de escalação"
  ack:
    by: "ESTADO-MAIOR"
    at: "2025-11-02T12:05:00Z"
    status: "ACCEPTED"  # OBRIGATÓRIO para execução
  status: "OPEN"  # OPEN, DONE, CANCELLED
```

### Campos Obrigatórios

1. **`order_id`**: UUID único identificador
2. **`ack.status`**: **DEVE ser "ACCEPTED"** antes da execução (guarda implementada)
3. **`steps`**: Lista de steps executáveis (não descrições)

### Tipos de Steps Aceites

#### 1. Tipo `command` (Comando Shell)
```yaml
- id: "step-install"
  type: "command"
  command: "brew install aquasecurity/trivy/trivy"
  description: "Instalar trivy via Homebrew"
```

**✅ BOM:** Comando executável completo  
**❌ EVITAR:** Descrições sem comando (`"Instalar trivy"` sem o comando real)

#### 2. Tipo `make` (Makefile Target)
```yaml
- id: "step-sop"
  type: "make"
  target: "sop"
  description: "Executar validação SOP completa"
```

**✅ BOM:** Target claro do Makefile  
**❌ EVITAR:** `make sop` como string (use `type: make`)

#### 3. Tipo `validation` (Validação Específica)
```yaml
- id: "step-validate"
  type: "validation"
  validation: "sop"
  description: "Validar conformidade SOP"
```

### Exemplos Práticos

#### Exemplo 1: Comando Python com Processamento
```yaml
- id: "step-fix-status"
  type: "command"
  command: "python3 -c \"import json; f=open('relatorios/torre_status.json','r'); d=json.load(f); f.close(); d['constitution_ok']=True; d['triade_ok']=True; f=open('relatorios/torre_status.json','w'); json.dump(d,f,indent=2); f.close()\""
  description: "Corrigir constitution_ok e triade_ok para true"
```

#### Exemplo 2: Comando Shell com Pipe
```yaml
- id: "step-verify"
  type: "command"
  command: "cat relatorios/torre_status.json | grep -E '(constitution_ok|triade_ok)'"
  description: "Verificar que constitution_ok e triade_ok estão true"
```

#### Exemplo 3: Makefile com Progresso
```yaml
- id: "step-pipeline"
  type: "make"
  target: "sop"
  description: "Executar validação SOP e reportar progresso"
```

**Com progresso reportado:**
```yaml
progresso_capitulo: "2/5"  # Obrigatório ao concluir etapa conforme PIN
```

### Formato de Relatório Gerado

O ENGENHEIRO gera relatório em `relatorios/para_estado_maior/engineer.out.json`:

```json
{
  "order_id": "uuid-v4",
  "report_id": "uuid-v4",
  "status": "PASS",
  "executed_at": "2025-11-02T12:10:00Z",
  "executed_by": "ENGENHEIRO-v3.0",
  "metrics": {
    "steps_total": 3,
    "steps_success": 3,
    "steps_failed": 0,
    "success_rate": 100.0
  },
  "artefacts": ["relatorios/arquivo.md", "core/scripts/arquivo.py"],
  "failures": [],
  "progresso_capitulo": "3/5",
  "recommendations": ["Ordem executada com sucesso"]
}
```

### Boas Práticas

1. **Steps explícitos**: Sempre fornecer comandos executáveis completos
2. **ACK obrigatório**: Marcar `ack.status: ACCEPTED` antes de executar
3. **Progresso claro**: Incluir `progresso_capitulo: N/M` ao concluir etapas
4. **Descrições úteis**: Cada step deve ter `description` clara
5. **Timeouts**: Definir `timeout` para comandos longos (>300s)

### Erros Comuns a Evitar

❌ **Steps como descrições:**
```yaml
steps:
  - "Instalar trivy"  # ❌ Não funciona
```

✅ **Steps como comandos:**
```yaml
steps:
  - id: "step-1"
    type: "command"
    command: "brew install aquasecurity/trivy/trivy"
    description: "Instalar trivy"
```

❌ **ACK ausente:**
```yaml
ack:
  status: "PENDING"  # ❌ Execução bloqueada
```

✅ **ACK explícito:**
```yaml
ack:
  by: "ESTADO-MAIOR"
  at: "2025-11-02T12:05:00Z"
  status: "ACCEPTED"  # ✅ Execução permitida
```

### Conclusão

O formato ideal maximiza a execução automatizada quando:
- Steps são comandos executáveis completos (não descrições)
- ACK está marcado como ACCEPTED
- Tipos de step são explícitos (`command`, `make`, `validation`)
- Progresso é reportado com `progresso_capitulo: N/M`

**Este modelo garante execução eficiente e rastreável, conforme ART-04 (Verificabilidade) e ART-09 (Evidência).**

