# INVENTÁRIO DE FONTES INTERNAS — LLM-Engenheira da FÁBRICA

**Agente**: Engenheiro da TORRE  
**Data/Hora**: 2025-01-27 (gerado automaticamente)  
**Objetivo**: Catalogar todas as fontes de dados internas para treino da LLM-Engenheira  
**Regras aplicadas**: ART-04 (Verificabilidade), ART-07 (Transparência), ART-09 (Evidência)

---

## 1. CATEGORIZAÇÃO DE FONTES

### 1.1 Código Fonte (Primário)

**Localização**: `core/`, `pipeline/`, `tools/`, `.github/`

#### Núcleo Operacional (`core/`)

- **`core/orquestrador/cli.py`** (763 linhas)
  - Comandos: `init`, `sync`, `validate`, `report`
  - Pipeline: `gen_pipeline`, `validate_pipeline`, `toc`
  - Gatekeeper: `gatekeeper_prep`, `gatekeeper_run`, `review_codex`
  - **Uso**: Compreensão de orquestração, lógica de gates, integração CI/CD

- **`core/scripts/validator.py`** (763 linhas)
  - Validação SOP completa
  - Métricas: coverage, semgrep, bandit, trivy, sbom, junit
  - Validação constitucional e Tríade
  - **Uso**: Treino de validação e conformidade

- **`core/scripts/plugins/`** (8 plugins)
  - `bandit.py`, `cov.py`, `junit.py`, `licenses.py`
  - `npm_audit.py`, `sbom.py`, `semgrep.py`, `trivy.py`
  - **Uso**: Compreensão de integrações de segurança e qualidade

- **`core/sop/constituição.yaml`** (110 linhas)
  - 10 Artigos fundamentais (ART-01 a ART-10)
  - **Uso**: Fundação constitucional (Fase 0)

- **`core/sop/leis.yaml`** (28 linhas)
  - Gates G0-G5 e requisitos
  - Políticas (coverage, latência, licenças)
  - RACI (Estado-Maior, SOP, Gatekeeper)
  - **Uso**: Compreensão de regras operacionais

- **`core/sop/exceptions.yaml`**
  - Exceções temporárias com `expires_at`
  - **Uso**: Casos edge de validação

- **`core/orquestrador/config.yaml`**
  - Configurações do orquestrador
  - **Uso**: Contexto de configuração

- **`core/orquestrador/Makefile`**
  - Comandos make para validação
  - **Uso**: Fluxos de build e validação

#### Pipeline (`pipeline/`)

- **`pipeline/superpipeline.yaml`** (42 linhas)
  - Estrutura de módulos (IDENTIDADE, DEVSECOPS, OBSERVABILIDADE, ALVORA, HORUS)
  - Capítulos (CAP-01, CAP-02, CAP-03)
  - Dependências e gates alvo
  - **Uso**: Compreensão de arquitetura de pipeline

- **`pipeline/capitulos/`**
  - `CAP-01/capitulo.yaml`, `CAP-02/capitulo.yaml`, `CAP-03/capitulo.yaml`
  - **Uso**: Estrutura de capítulos e módulos

- **`pipeline/modulos/`**
  - `M01-exemplo/`, `M02-autenticacao/`
  - Estrutura: `etapas/E01-*/tarefas/T001-*/`
  - **Uso**: Compreensão de granularidade de módulos

- **`pipeline/_templates/`**
  - `CHAPTER.md`, `STAGE.md`, `TASK.md`
  - **Uso**: Padrões de documentação

- **`pipeline/PIPELINE_TOC.md`**, `pipeline/README.md`
  - **Uso**: Navegação e contexto

#### Configuração (`tools/`, `.github/`)

- **`tools/CODEOWNERS`**
  - Ownership de código
  - **Uso**: Contexto de responsabilidades

- **`tools/pre-commit-config.yaml`**
  - Hooks de pre-commit
  - **Uso**: Fluxos de validação local

- **`tools/commitlint.config.cjs`**
  - Regras de commit
  - **Uso**: Padrões de mensagens

- **`.github/workflows/`** (templates em `core/templates/github/`)
  - `ci.yml`, `release.yml`
  - **Uso**: Integração CI/CD

---

### 1.2 Documentação (Secundário)

**Localização**: `docs/`

- **`docs/MAPA_DA_FÁBRICA.md`** (62 linhas)
  - Estrutura após auditoria forense
  - Núcleo vs auxiliares vs gerados
  - **Uso**: Compreensão estrutural geral

- **`docs/SOP_MANUAL.md`** (18 linhas)
  - Manual operacional do SOP
  - **Uso**: Contexto de operação

- **`docs/GATEKEEPER_MANUAL.md`**
  - Manual do Gatekeeper (se existir)
  - **Uso**: Compreensão de pareceres e vistos

---

### 1.3 Relatórios e Artefactos (Terciário)

**Localização**: `relatorios/`

- **`relatorios/relatorio_sop.md`**
  - Relatório SOP completo (gerado por `validator.py`)
  - **Uso**: Padrões de relatórios, casos de PASS/BLOQUEADO

- **`relatorios/sop_status.json`**
  - Status estruturado (máquina-legível)
  - **Uso**: Integração com sistemas, formato de dados

- **`relatorios/parecer_gatekeeper.md`**
  - Pareceres do Gatekeeper (APROVADO/VETO)
  - **Uso**: Casos de decisão, padrões de avaliação

- **`relatorios/pipeline_audit.json`**
  - Auditoria de pipeline (deps_missing, cycles, not_covered)
  - **Uso**: Casos de validação estrutural

- **`relatorios/pipeline_gate_input.json`**
  - Input para Gatekeeper
  - **Uso**: Formato de comunicação com Gatekeeper

- **`relatorios/Auditoria Forense Estrutural.md`** (28 linhas)
  - Auditoria histórica
  - **Uso**: Casos reais de análise estrutural

- **`relatorios/Auditoria_Docs_e_Scripts.md`**
  - Auditoria de documentação
  - **Uso**: Padrões de auditoria

- **`relatorios/semgrep.sarif`**
  - Resultados Semgrep (formato SARIF)
  - **Uso**: Padrões de análise de segurança

- **`relatorios/sbom.json`**
  - Software Bill of Materials
  - **Uso**: Rastreabilidade de dependências

- **`relatorios/npm-audit.json`**
  - Vulnerabilidades npm
  - **Uso**: Casos de segurança

- **`relatorios/sop_status.json`**
  - Status do SOP
  - **Uso**: Estado atual do sistema

---

### 1.4 Templates e Schemas

**Localização**: `core/templates/`

- **`core/templates/github/ci.yml`, `release.yml`**
  - Templates de workflows
  - **Uso**: Padrões de CI/CD

- **`core/templates/project_skeleton/`**
  - `package.json`, `README.md`
  - **Uso**: Estrutura inicial de projetos

---

## 2. PROCESSAMENTO E CURAGÃO

### 2.1 Extração

- **Código**: Parse direto (Python AST, YAML parser, JSON parser)
- **Documentação**: Markdown parsing + extração de estrutura
- **Relatórios**: Parse de formatos específicos (SARIF, JSON, Markdown)

### 2.2 Anonimização

- **Paths absolutos**: Substituir por placeholders (`<REPO_ROOT>`, `<REL_DIR>`)
- **Tokens/Keys**: Remover ou substituir por `<REDACTED>`
- **Informações pessoais**: Remover nomes de desenvolvedores (se aplicável)
- **Timestamps**: Normalizar para formato padrão ou relativizar

### 2.3 Enriquecimento

- **Anotações**: Adicionar comentários explicativos em código complexo
- **Metadados**: Adicionar tags (tipo, fase de treino, dificuldade)
- **Casos de uso**: Associar cada fonte a casos de uso específicos

### 2.4 Validação

- **Integridade**: Verificar que nenhuma informação crítica foi perdida
- **Conformidade**: Validar que datasets seguem ART-07 (transparência)
- **Aprovação**: Estado-Maior aprova todos os datasets antes do treino

---

## 3. ESTRUTURA DE DATASETS

### 3.1 Dataset por Fase

#### Fase 0: Fundação

- `datasets/fase0/constitucao.yaml` (constituição completa)
- `datasets/fase0/leis.yaml` (leis e políticas)
- `datasets/fase0/estrutura.md` (MAPA_DA_FÁBRICA)
- `datasets/fase0/casos_edge.yaml` (casos de violação para treino)

#### Fase 1: Compreensão

- `datasets/fase1/codigo/` (código anotado)
  - `cli.py.annotated`
  - `validator.py.annotated`
  - `plugins/*.py.annotated`
- `datasets/fase1/pipeline/` (estruturas de pipeline)
- `datasets/fase1/templates/` (templates e schemas)

#### Fase 2: Validação

- `datasets/fase2/projetos_validos/` (PASS)
- `datasets/fase2/projetos_invalidos/` (BLOQUEADO)
- `datasets/fase2/relatorios/` (relatórios históricos)
- `datasets/fase2/excecoes/` (casos de exceção)

#### Fase 3: Refatoração

- `datasets/fase3/pares/` (antes/depois)
- `datasets/fase3/violacoes/` (refatorações que violaram regras)
- `datasets/fase3/melhorias/` (refatorações que melhoraram)

#### Fase 4: Auditoria

- `datasets/fase4/pipelines_validas/`
- `datasets/fase4/pipelines_invalidas/`
- `datasets/fase4/auditorias_historicas/`

#### Fase 5: Integração

- `datasets/fase5/interacoes/` (simulações de interação)
- `datasets/fase5/checkpoints/` (logs de execução)
- `datasets/fase5/aprovacoes_vetos/` (casos de decisão)

---

### 3.2 Versionamento

Cada dataset versionado com:

- **Hash SHA256**: Integridade
- **Metadata**: Data, agente, fase, fonte original
- **Validação**: Checksum e assinatura (se aplicável)

Formato:

```yaml
dataset:
  id: "fase0_constitucao_v1"
  hash: "sha256:abc123..."
  source: "core/sop/constituição.yaml"
  phase: 0
  created: "2025-01-27"
  agent: "Engenheiro da TORRE"
  approved_by: "Estado-Maior"
  metadata:
    lines: 110
    articles: 10
```

---

## 4. MANUTENÇÃO CONTÍNUA

### 4.1 Atualização Automática

- **Monitorização**: Detectar mudanças em fontes primárias
- **Regeneração**: Re-gerar datasets quando código muda
- **Validação**: Re-validar com Estado-Maior após mudanças

### 4.2 Expansão

- **Novos módulos**: Adicionar automaticamente ao dataset Fase 1
- **Novas violações**: Adicionar a datasets de treino (Fase 2)
- **Feedback**: Incorporar feedback do Gatekeeper (Fase 5)

### 4.3 Purga

- **Dados obsoletos**: Remover após 6 meses (manter histórico)
- **Exceções expiradas**: Remover após expiração
- **Relatórios antigos**: Arquivar após 1 ano

---

## 5. COMPLIANCE E SEGURANÇA

### 5.1 Acesso

- **Aprovadores**: Apenas Estado-Maior pode aprovar datasets
- **Processadores**: Engenheiro da TORRE (com supervisão)
- **Consumidores**: LLM-Engenheira (isolada)

### 5.2 Auditoria

- **Logs**: Todas as operações em datasets são logadas
- **Rastreabilidade**: Cada dataset rastreável até fonte original
- **Verificabilidade**: Checksums e assinaturas (ART-09)

### 5.3 Confidencialidade

- **Anonimização**: Dados sensíveis removidos/anonimizados
- **Isolamento**: Datasets em ambiente isolado
- **Backup**: Backups criptografados (ART-10: Continuidade)

---

## 6. ESTATÍSTICAS ATUAIS

- **Fontes primárias**: ~15 arquivos de código
- **Linhas de código**: ~2000+ linhas
- **Documentação**: ~100 linhas
- **Relatórios**: ~10 arquivos históricos
- **Templates**: ~5 arquivos

**Estimativa de datasets**:

- Fase 0: ~500 exemplos
- Fase 1: ~2000 exemplos
- Fase 2: ~1000 exemplos
- Fase 3: ~500 exemplos
- Fase 4: ~300 exemplos
- Fase 5: ~200 exemplos

**Total estimado**: ~4500 exemplos de treino

---

## 7. PRÓXIMOS PASSOS

1. **Aprovação Estado-Maior**: Validar este inventário
2. **Extração inicial**: Começar processamento de fontes primárias
3. **Curadoria**: Anotar e enriquecer datasets
4. **Validação**: Aprovar datasets antes de uso

---

**Referências**:

- `core/sop/constituição.yaml` - ART-04, ART-07, ART-09
- `docs/MAPA_DA_FÁBRICA.md` - Estrutura do núcleo
- `relatorios/` - Artefactos históricos

---

**Assinado**: Engenheiro da TORRE  
**Data**: 2025-01-27  
**Versão**: 1.0
