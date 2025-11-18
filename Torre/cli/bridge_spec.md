# ESPECIFICAÇÃO DA API — torre_bridge.py

**Agente**: Engenheiro da TORRE  
**Data/Hora**: 2025-01-27 (gerado automaticamente)  
**Objetivo**: Definir API e contratos para comunicação entre FÁBRICA e LLM-Engenheira  
**Regras aplicadas**: ART-03 (Consciência Técnica), ART-07 (Transparência), ART-09 (Evidência)

---

## 1. VISÃO GERAL

`torre_bridge.py` é a interface de comunicação entre:

- **FÁBRICA** (Estado-Maior, SOP, Gatekeeper, Engenheiros)
- **LLM-Engenheira** (sistema especializado de IA)

**Propósito**: Permitir perguntar, ensinar e validar com a LLM sem violar ART-03 (papéis) e ART-05 (autonomia).

---

## 2. ARQUITETURA DA API

### 2.1 Localização

- **Caminho**: `torre/cli/torre_bridge.py`
- **Executável**: `python torre/cli/torre_bridge.py <comando> [args]`
- **Integração**: Pode ser chamado por `core/orquestrador/cli.py` ou diretamente

### 2.2 Padrão de Design

- **Síncrono**: Respostas imediatas (timeout de 30s)
- **Idempotente**: Mesmos inputs produzem mesmos outputs
- **Rastreável**: Todas as operações logadas (ART-04, ART-09)
- **Isolado**: Execução em sandbox (sem acesso a `deprecated/`, `node_modules/`)

---

## 3. COMANDOS DA API

### 3.1 `ask` — Perguntar à LLM

**Sintaxe**:

```bash
torre_bridge.py ask --query "<pergunta>" [--context "<contexto>"] [--format json|markdown]
```

**Descrição**: Faz uma pergunta à LLM-Engenheira sobre código, estrutura ou conformidade.

**Parâmetros**:

- `--query` (obrigatório): Pergunta em linguagem natural
- `--context` (opcional): Caminho de arquivo ou módulo para contexto adicional
- `--format` (opcional): Formato de saída (`json` ou `markdown`, padrão: `markdown`)

**Exemplos**:

```bash
# Pergunta simples
torre_bridge.py ask --query "Qual é o propósito do módulo DEVSECOPS?"

# Pergunta com contexto
torre_bridge.py ask --query "Esta função viola ART-08?" --context "core/scripts/validator.py:250-300"

# Pergunta com saída JSON
torre_bridge.py ask --query "Lista todas as dependências do módulo ALVORA" --format json
```

**Resposta (Markdown)**:

```markdown
# Resposta da LLM-Engenheira

[Conteúdo da resposta]

## Artefactos Citados (ART-09)

- `pipeline/superpipeline.yaml:15-20`
- `core/sop/leis.yaml:5-10`

## Confiança

- Score: 0.95
- Regras aplicadas: ART-02, ART-06

---

**Agente**: LLM-Engenheira da FÁBRICA
**Data/Hora**: 2025-01-27 10:30:00 UTC
```

**Resposta (JSON)**:

```json
{
  "response": "Conteúdo da resposta",
  "artefactos_citados": [
    "pipeline/superpipeline.yaml:15-20",
    "core/sop/leis.yaml:5-10"
  ],
  "confianca": 0.95,
  "regras_aplicadas": ["ART-02", "ART-06"],
  "agente": "LLM-Engenheira da FÁBRICA",
  "timestamp": "2025-01-27T10:30:00Z"
}
```

**Limites**:

- Tamanho máximo de query: 2000 caracteres
- Tamanho máximo de contexto: 10.000 linhas
- Timeout: 30 segundos

**Validação**:

- Verifica que pergunta está dentro do domínio Engenheiro (ART-03)
- Escala para Estado-Maior se pergunta requer aprovação/veto

---

### 3.2 `teach` — Ensinar à LLM

**Sintaxe**:

```bash
torre_bridge.py teach --input "<caminho>" --objective "<objetivo>" [--approve]
```

**Descrição**: Adiciona novo conhecimento à LLM (código, documentação, casos de uso). Requer aprovação do Estado-Maior se `--approve` não for fornecido.

**Parâmetros**:

- `--input` (obrigatório): Caminho de arquivo ou diretório a processar
- `--objective` (obrigatório): Objetivo do ensino (ex: "Aprender novo módulo", "Casos de violação")
- `--approve` (opcional): Token de aprovação do Estado-Maior (se não fornecido, pede aprovação)

**Exemplos**:

```bash
# Ensinar novo módulo
torre_bridge.py teach --input "pipeline/modulos/M03-novo-modulo/" --objective "Aprender estrutura do módulo M03"

# Ensinar casos de violação (com aprovação)
torre_bridge.py teach --input "relatorios/casos_violacao/" --objective "Aprender padrões de violação" --approve "<token>"
```

**Resposta**:

```json
{
  "status": "success",
  "processed": 15,
  "added_to_dataset": "fase2_projetos_invalidos_v2",
  "requires_validation": true,
  "agente": "LLM-Engenheira da FÁBRICA",
  "timestamp": "2025-01-27T10:30:00Z"
}
```

**Limites**:

- Tamanho máximo por operação: 100 arquivos
- Requer aprovação Estado-Maior para datasets de produção
- Timeout: 60 segundos

**Validação**:

- Verifica que input está dentro do núcleo (não `deprecated/`, etc.)
- Valida formato antes de processar
- Gera checksum para rastreabilidade (ART-09)

---

### 3.3 `validate` — Validar com LLM

**Sintaxe**:

```bash
torre_bridge.py validate --artefacto "<caminho>" [--gate G0|G1|G2|G3|G4|G5] [--strict]
```

**Descrição**: Valida artefacto (código, pipeline, módulo) usando LLM-Engenheira. Complementa validação oficial do SOP.

**Parâmetros**:

- `--artefacto` (obrigatório): Caminho de arquivo ou diretório a validar
- `--gate` (opcional): Gate alvo (G0-G5). Se não fornecido, detecta automaticamente
- `--strict` (opcional): Modo estrito (falha em qualquer violação)

**Exemplos**:

```bash
# Validação automática
torre_bridge.py validate --artefacto "pipeline/modulos/M02-autenticacao/"

# Validação para gate específico
torre_bridge.py validate --artefacto "core/scripts/validator.py" --gate G2

# Validação estrita
torre_bridge.py validate --artefacto "pipeline/superpipeline.yaml" --strict
```

**Resposta**:

```json
{
  "status": "PASS",
  "gate": "G2",
  "violations": [],
  "metrics": {
    "constitutional": true,
    "triade": true,
    "coverage_ok": true
  },
  "artefactos_citados": [
    "core/sop/constituição.yaml",
    "core/sop/leis.yaml:10-15"
  ],
  "llm_confidence": 0.98,
  "recommendations": [],
  "agente": "LLM-Engenheira da FÁBRICA",
  "timestamp": "2025-01-27T10:30:00Z"
}
```

**Limites**:

- Tamanho máximo: 10.000 linhas por artefacto
- Timeout: 30 segundos
- Modo estrito: Falha imediatamente na primeira violação

**Validação**:

- Compara com resultados de `validator.py` (ferramenta oficial)
- Reporta discrepâncias se houver
- Gera relatório formatado (ART-07)

---

### 3.4 `refactor` — Refatorar com LLM

**Sintaxe**:

```bash
torre_bridge.py refactor --input "<caminho>" --objective "<objetivo>" [--dry-run] [--approve]
```

**Descrição**: Refatora código usando LLM-Engenheira. Requer aprovação do Estado-Maior para mudanças >50 linhas.

**Parâmetros**:

- `--input` (obrigatório): Caminho de arquivo a refatorar
- `--objective` (obrigatório): Objetivo da refatoração (ex: "Melhorar cobertura", "Corrigir violação ART-08")
- `--dry-run` (opcional): Apenas mostra mudanças propostas (não aplica)
- `--approve` (opcional): Token de aprovação do Estado-Maior (obrigatório se mudanças >50 linhas)

**Exemplos**:

```bash
# Refatoração dry-run
torre_bridge.py refactor --input "core/scripts/validator.py" --objective "Melhorar cobertura de testes" --dry-run

# Refatoração com aprovação
torre_bridge.py refactor --input "pipeline/modulos/M02/etapas/E01/" --objective "Corrigir violação ART-06" --approve "<token>"
```

**Resposta**:

```json
{
  "status": "success",
  "changes": {
    "lines_added": 10,
    "lines_removed": 5,
    "files_modified": 1
  },
  "diff": "--- a/core/scripts/validator.py\n+++ b/core/scripts/validator.py\n...",
  "validation_post_refactor": {
    "status": "PASS",
    "tests_passed": true
  },
  "requires_approval": false,
  "agente": "LLM-Engenheira da FÁBRICA",
  "timestamp": "2025-01-27T10:30:00Z"
}
```

**Limites**:

- Máximo 100 linhas alteradas por operação (sem aprovação)
- Requer aprovação Estado-Maior para mudanças >50 linhas
- Timeout: 60 segundos

**Validação**:

- Validação SOP obrigatória pós-refatoração
- Preserva funcionalidade (testes devem passar)
- Gera checkpoint antes de aplicar (ART-10)

---

### 3.5 `audit` — Auditar com LLM

**Sintaxe**:

```bash
torre_bridge.py audit --target "<caminho>" [--depth <n>] [--format json|markdown]
```

**Descrição**: Audita estrutura (pipeline, módulo, diretório) usando LLM-Engenheira.

**Parâmetros**:

- `--target` (obrigatório): Caminho de pipeline, módulo ou diretório a auditar
- `--depth` (opcional): Profundidade de análise (padrão: 5 níveis)
- `--format` (opcional): Formato de saída (`json` ou `markdown`, padrão: `markdown`)

**Exemplos**:

```bash
# Auditoria de pipeline
torre_bridge.py audit --target "pipeline/superpipeline.yaml"

# Auditoria profunda
torre_bridge.py audit --target "pipeline/modulos/" --depth 10

# Auditoria com saída JSON
torre_bridge.py audit --target "core/" --format json
```

**Resposta (Markdown)**:

```markdown
# Relatório de Auditoria — LLM-Engenheira

## Sumário

- Status: ✅ VÁLIDA
- Issues encontradas: 0
- Profundidade analisada: 5 níveis

## Análise Estrutural

- Dependências: ✅ Todas presentes
- Ciclos: ✅ Nenhum detectado
- Módulos cobertos: ✅ 100%

## Conformidade Constitucional

- ART-01: ✅ Validado
- ART-02: ✅ Tríade presente
- ART-06: ✅ Sem contradições

## Artefactos Citados (ART-09)

- `pipeline/superpipeline.yaml:1-42`
- `core/sop/constituição.yaml`
- `relatorios/pipeline_audit.json`

---

**Agente**: LLM-Engenheira da FÁBRICA
**Data/Hora**: 2025-01-27 10:30:00 UTC
```

**Resposta (JSON)**:

```json
{
  "status": "VALID",
  "issues": [],
  "depth_analyzed": 5,
  "structural": {
    "dependencies_ok": true,
    "cycles_detected": 0,
    "modules_covered": 1.0
  },
  "constitutional": {
    "ART-01": true,
    "ART-02": true,
    "ART-06": true
  },
  "artefactos_citados": [
    "pipeline/superpipeline.yaml:1-42",
    "core/sop/constituição.yaml",
    "relatorios/pipeline_audit.json"
  ],
  "agente": "LLM-Engenheira da FÁBRICA",
  "timestamp": "2025-01-27T10:30:00Z"
}
```

**Limites**:

- Profundidade máxima: 10 níveis
- Timeout: 60 segundos
- Tamanho máximo: 100 módulos/arquivos

**Validação**:

- Compara com `validate_pipeline` (ferramenta oficial)
- Gera relatório conforme formato Gatekeeper (ART-07)

---

## 4. CÓDIGOS DE RETORNO

- **0**: Sucesso
- **1**: Erro de validação (violação detectada, input inválido)
- **2**: Erro de permissão (requer aprovação Estado-Maior)
- **3**: Erro de timeout
- **4**: Erro interno (LLM indisponível, erro de processamento)

---

## 5. LOGGING E RASTREABILIDADE

### 5.1 Logs

Todos os comandos geram logs em `torre/logs/bridge_YYYY-MM-DD.log`:

```
2025-01-27 10:30:00 UTC | ask | query="Qual é o propósito do módulo DEVSECOPS?" | context=null | status=success | latency=250ms
2025-01-27 10:31:00 UTC | validate | artefacto="pipeline/superpipeline.yaml" | gate=G2 | status=PASS | violations=0
```

### 5.2 Metadados

Cada operação inclui:

- Timestamp (UTC)
- Agente (LLM-Engenheira da FÁBRICA)
- Artefactos citados (ART-09)
- Regras aplicadas (ART-07)

---

## 6. INTEGRAÇÃO COM FÁBRICA

### 6.1 Integração com `cli.py`

`core/orquestrador/cli.py` pode chamar `torre_bridge.py`:

```python
# Exemplo de integração
result = subprocess.run([
    "python", "torre/cli/torre_bridge.py", "validate",
    "--artefacto", artefacto_path,
    "--gate", gate
], capture_output=True, text=True)
```

### 6.2 Integração com Estado-Maior

- **Aprovações**: Estado-Maior emite tokens de aprovação
- **Diretrizes**: Estado-Maior pode atualizar conhecimento via `teach`
- **Monitorização**: Estado-Maior monitora logs e relatórios

### 6.3 Integração com Gatekeeper

- **Inputs**: Gatekeeper pode usar `audit` para análise complementar
- **Pareceres**: LLM pode gerar rascunhos de pareceres (validados por Gatekeeper)

---

## 7. SEGURANÇA E LIMITES

### 7.1 Sandbox

- Execução isolada (sem acesso a `deprecated/`, `node_modules/`)
- Apenas leitura/escrita em `relatorios/` e logs aprovados
- Sem acesso a sistema de arquivos fora do workspace

### 7.2 Rate Limiting

- Máximo 100 requisições/minuto por usuário
- Máximo 10 requisições simultâneas
- Backoff automático em caso de sobrecarga

### 7.3 Validação de Papéis (ART-03)

- Verifica que operação está dentro do domínio Engenheiro
- Escala para Estado-Maior se operação requer aprovação/veto
- Bloqueia operações que violam ART-03 automaticamente

---

## 8. EXEMPLOS DE USO COMPLETOS

### 8.1 Fluxo de Validação

```bash
# 1. Perguntar sobre conformidade
torre_bridge.py ask --query "Este módulo está pronto para gate G2?" --context "pipeline/modulos/M02/"

# 2. Validar oficialmente
torre_bridge.py validate --artefacto "pipeline/modulos/M02/" --gate G2

# 3. Se houver issues, auditar profundamente
torre_bridge.py audit --target "pipeline/modulos/M02/" --depth 10
```

### 8.2 Fluxo de Ensino

```bash
# 1. Estado-Maior aprova novo conhecimento
token=$(get_approval_token)

# 2. Ensinar à LLM
torre_bridge.py teach --input "pipeline/modulos/M03-novo/" --objective "Aprender M03" --approve "$token"

# 3. Validar que LLM aprendeu
torre_bridge.py ask --query "Qual é a estrutura do módulo M03?"
```

### 8.3 Fluxo de Refatoração

```bash
# 1. Dry-run primeiro
torre_bridge.py refactor --input "core/scripts/validator.py" --objective "Melhorar cobertura" --dry-run

# 2. Se aprovado, aplicar
token=$(get_approval_token)
torre_bridge.py refactor --input "core/scripts/validator.py" --objective "Melhorar cobertura" --approve "$token"

# 3. Validar pós-refatoração
torre_bridge.py validate --artefacto "core/scripts/validator.py" --gate G2
```

---

## 9. PRÓXIMOS PASSOS

1. **Implementação**: Desenvolver `torre/cli/torre_bridge.py` conforme esta especificação
2. **Testes**: Suite de testes para todos os comandos
3. **Documentação**: Guia de uso para Estado-Maior e Engenheiros
4. **Integração**: Conectar com `cli.py` e workflows CI/CD

---

**Referências**:

- `core/sop/constituição.yaml` - ART-03, ART-07, ART-09
- `core/orquestrador/cli.py` - Integração
- `torre/models/ARCHITECTURE.md` - Arquitetura da LLM

---

**Assinado**: Engenheiro da TORRE  
**Data**: 2025-01-27  
**Versão**: 1.0
