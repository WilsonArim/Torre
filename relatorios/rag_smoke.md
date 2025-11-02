# RAG Externo Filtrado - Smoke Test

**Order ID**: mg2-2025-11-01T16-21-00  
**Gate**: MG2  
**Data**: 2025-11-02T10:29:18.354930Z  
**Status**: ✅ CONCLUÍDO

## Resumo Executivo

Cliente RAG externo read-only implementado com:
- ✅ Deny-lists para arquivos sensíveis (.env, credenciais, etc.)
- ✅ Filtro constitucional para relevância
- ✅ Registro de queries em JSON
- ✅ 5 consultas testadas

## Consultas Testadas

### Consulta 1: "ART-01"

**Query ID**: `ad70192f0deb6ec5`  
**Timestamp**: 2025-11-02T10:29:18.772070Z  
**Resultados**: 5

**Fontes encontradas**:
- `core/orquestrador/sop_cli.py` (score: 16, relevância constitucional: sim)
  - Linha 18: ```
- relatorios/relatorio_sop.md + relatorios/sop_status.json (status PASS/BLOQUEADO + métricas).

Respeita ART-01 (Integridade), ART-02 (Tríade), ART-04 (Verificabilidade), ART-07 (Transparência), ART-0...
```
- `Torre/orquestrador/exec_fase0.py` (score: 12, relevância constitucional: sim)
  - Linha 30: ```
print("🧩 Etapa: Preparação — OK")

# Step 1: Estudar ART-01 a ART-10
print("🧠 Execução técnica — Estudando Constituição...")
constitucao_content = CONSTITUICAO_PATH.read_text(encoding="utf-8") if CONS...
```
- `factory/pins/_deprecated/engineer_executor.py` (score: 11, relevância constitucional: sim)
  - Linha 5: ```
PIN — ENGENHEIRO DA TORRE v1.0
Executor técnico da TORRE - Implementa ciclo completo de execução de ordens
Respeita ART-01, ART-02, ART-03, ART-04, ART-07, ART-09, ART-10
"""
...
```
- `Torre/orquestrador/exec_mg2.py` (score: 11, relevância constitucional: sim)
  - Linha 173: ```

test_queries = [
    "ART-01",
    "Constituição da FÁBRICA",
    "Gatekeeper",...
```
- `Torre/cli/validate_dataset.py` (score: 11, relevância constitucional: sim)
  - Linha 52: ```
    # Verificar que não altera Constituição
    if "constituição.yaml" in str(dataset_path) and "modif" in str(dataset_path).lower():
        violations.append("Tentativa de modificar Constituição (AR...
```

### Consulta 2: "Constituição da FÁBRICA"

**Query ID**: `02bea4049ffd2e20`  
**Timestamp**: 2025-11-02T10:29:20.741610Z  
**Resultados**: 3

**Fontes encontradas**:
- `Torre/orquestrador/exec_mg2.py` (score: 11, relevância constitucional: sim)
  - Linha 174: ```
test_queries = [
    "ART-01",
    "Constituição da FÁBRICA",
    "Gatekeeper",
    "SOP validação",...
```
- `core/sop/constituição.yaml` (score: 11, relevância constitucional: sim)
  - Linha 2: ```
versao: 1
titulo: "CONSTITUIÇÃO DA FÁBRICA"
descricao: >
  Documento supremo da FÁBRICA. Define os princípios imutáveis de integridade,...
```
- `.github/workflows/ci.yml` (score: 11, relevância constitucional: sim)
  - Linha 19: ```
          if git diff --name-only HEAD~1 HEAD 2>/dev/null | grep -q "core/sop/constituição.yaml"; then
            echo "⚠️ ERRO CRÍTICO: Tentativa de modificação da Constituição detectada!"
         ...
```

### Consulta 3: "Gatekeeper"

**Query ID**: `b4053fbdf55448e8`  
**Timestamp**: 2025-11-02T10:29:20.753685Z  
**Resultados**: 5

**Fontes encontradas**:
- `factory/pins/_deprecated/cli_gatekeeper_torre.py` (score: 23, relevância constitucional: sim)
  - Linha 184: ```


def cmd_gatekeeper_run() -> int:
    """Executa Gatekeeper."""
    log_message("Executando Gatekeeper", "INFO")...
```
- `factory/pins/_deprecated/engineer_executor.py` (score: 16, relevância constitucional: sim)
  - Linha 60: ```
CORE_ORQUESTRADOR = REPO_ROOT / "core" / "orquestrador"
ORDENS_INDEX = REPO_ROOT / "relatorios" / "ordens_index.json"
GATEKEEPER_IN = ORDERS_DIR / "gatekeeper.in.yaml"
SOP_IN = ORDERS_DIR / "sop.in.ya...
```
- `Torre/orquestrador/exec_mg2.py` (score: 13, relevância constitucional: sim)
  - Linha 49: ```
    r'Tríade',
    r'SOP',
    r'Gatekeeper',
]
...
```
- `Torre/orquestrador/treino_G2.py` (score: 11, relevância constitucional: sim)
  - Linha 24: ```
METRICS_FILE = TORRE_RELATORIOS / "treino_G2_metrics.json"

print("🛠️ MODO EXECUÇÃO — A executar a tarefa técnica atribuída (sem papéis de Gatekeeper/SOP).")
print()
...
```
- `Torre/orquestrador/treino_G3.py` (score: 11, relevância constitucional: sim)
  - Linha 24: ```
METRICS_FILE = TORRE_RELATORIOS / "treino_G3_metrics.json"

print("🛠️ MODO EXECUÇÃO — A executar a tarefa técnica atribuída (sem papéis de Gatekeeper/SOP).")
print()
...
```

### Consulta 4: "SOP validação"

**Query ID**: `aa1bd165e55eafda`  
**Timestamp**: 2025-11-02T10:29:22.625247Z  
**Resultados**: 1

**Fontes encontradas**:
- `Torre/orquestrador/exec_mg2.py` (score: 11, relevância constitucional: sim)
  - Linha 176: ```
    "Constituição da FÁBRICA",
    "Gatekeeper",
    "SOP validação",
    "Tríade White Paper"
]...
```

### Consulta 5: "Tríade White Paper"

**Query ID**: `74c95fb980f13ca4`  
**Timestamp**: 2025-11-02T10:29:24.612354Z  
**Resultados**: 1

**Fontes encontradas**:
- `Torre/orquestrador/exec_mg2.py` (score: 11, relevância constitucional: sim)
  - Linha 177: ```
    "Gatekeeper",
    "SOP validação",
    "Tríade White Paper"
]
...
```

## Métricas

- **Total de queries**: 5
- **Queries com resultados**: 5
- **Total de fontes únicas**: 10
- **Filtragem ativa**: Deny-lists e filtro constitucional

## Filtros Aplicados

### Deny-lists
- Arquivos `.env*`
- Arquivos com credenciais/secrets/passwords
- Diretórios: `node_modules/`, `__pycache__/`, `.git/`, `.venv/`

### Filtro Constitucional
- Padrões: ART-*, ARTIGO *, Constituição, Tríade, SOP, Gatekeeper
- Relevância constitucional aumenta score dos resultados

## Artefactos Gerados

- `relatorios/rag_queries.json` - Log completo de queries
- `relatorios/rag_smoke.md` - Este relatório

---
*Gerado automaticamente pelo Engenheiro da TORRE*
