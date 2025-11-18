# ARQUITETURA DA LLM-ENGENHEIRA DA FÁBRICA

**Agente**: Engenheiro da TORRE  
**Data/Hora**: 2025-01-27 (gerado automaticamente)  
**Objetivo**: Definir arquitetura técnica da LLM especializada no ecossistema FÁBRICA  
**Regras aplicadas**: ART-02 (Tríade de Fundamentação), ART-03 (Consciência Técnica), ART-07 (Transparência)

---

## 1. VISÃO GERAL DA ARQUITETURA

A LLM-Engenheira da FÁBRICA é um sistema especializado composto por:

- **Modelo base**: LLM geral (ex: GPT-4, Claude Sonnet) com fine-tuning específico
- **Módulos especializados**: Componentes dedicados a tarefas específicas
- **Memória contextual**: Sistema de embeddings e retrieval para conhecimento FÁBRICA
- **Ferramentas**: Integração com validadores, pipelines e Gatekeeper
- **Limites e guardrails**: Proteções contra violações constitucionais

---

## 2. COMPONENTES PRINCIPAIS

### 2.1 Core Engine (Motor Principal)

#### 2.1.1 Modelo Base

- **Tipo**: Transformer-based LLM (fine-tuned)
- **Capacidades**:
  - Compreensão de código multi-linguagem (Python, TS/JS, YAML, JSON)
  - Raciocínio sobre estrutura e dependências
  - Geração de código e documentação
  - Análise de conformidade constitucional

#### 2.1.2 Sistema de Memória

- **Embeddings**: Vetores de código, documentação, relatórios
- **Retrieval**: RAG (Retrieval-Augmented Generation) para contexto FÁBRICA
- **Índices**:
  - `index_constitucao`: Artigos da Constituição
  - `index_codigo`: Código fonte do núcleo
  - `index_pipeline`: Estrutura de pipelines e módulos
  - `index_relatorios`: Relatórios históricos

**Tecnologia**: Similarity search (cosine similarity) em embeddings
**Limite**: 10.000 documentos indexados (expansível)

---

### 2.2 Módulos Especializados

#### 2.2.1 Módulo de Compreensão (`ComprehensionModule`)

**Responsabilidade**: Entender código e estrutura

**Entrada**:

- Código fonte (texto)
- Contexto (módulo, pipeline, gate)

**Processamento**:

1. Parse sintático (AST para Python/TS, YAML/JSON parser)
2. Análise semântica (identificar propósito, dependências)
3. Enriquecimento contextual (buscar em `index_codigo`)

**Saída**:

- Estrutura parseada
- Dependências identificadas
- Propósito inferido (com confiança)

**Limites**:

- Tamanho máximo de arquivo: 10.000 linhas
- Profundidade de análise: 5 níveis de dependências

---

#### 2.2.2 Módulo de Validação (`ValidationModule`)

**Responsabilidade**: Validar conformidade com SOP e Constituição

**Entrada**:

- Artefactos (código, pipeline, configuração)
- Gate alvo (G0-G5)

**Processamento**:

1. Carregar regras relevantes (`leis.yaml`, `constituição.yaml`)
2. Aplicar validadores (`validator.py` logic)
3. Verificar requisitos do gate
4. Detectar violações (ART-01 a ART-10)

**Saída**:

- Status: PASS / BLOQUEADO
- Violações identificadas (com artefactos citados)
- Métricas calculadas

**Limites**:

- Validação síncrona: máximo 30 segundos
- Timeout automático: escalação para Estado-Maior

---

#### 2.2.3 Módulo de Refatoração (`RefactoringModule`)

**Responsabilidade**: Refatorar código mantendo integridade

**Entrada**:

- Código original
- Objetivo de refatoração
- Contexto (testes, dependências)

**Processamento**:

1. Análise de impacto (identificar dependências)
2. Preservação de lógica (garantir equivalência funcional)
3. Aplicação de mudanças mínimas (ART-08: Proporcionalidade)
4. Validação pós-refatoração (re-run validadores)

**Saída**:

- Código refatorado
- Diferenças (diff)
- Validação pós-refatoração (PASS/BLOQUEADO)

**Limites**:

- Mudanças por refatoração: máximo 100 linhas alteradas
- Requer aprovação Estado-Maior para mudanças >50 linhas

---

#### 2.2.4 Módulo de Auditoria (`AuditModule`)

**Responsabilidade**: Auditar estrutura completa (pipelines, módulos)

**Entrada**:

- Pipeline ou módulo a auditar
- Contexto histórico (relatórios anteriores)

**Processamento**:

1. Validação estrutural (`validate_pipeline` logic)
2. Detecção de dependências ausentes, ciclos
3. Análise de conformidade (Tríade, Constituição)
4. Geração de relatório forense

**Saída**:

- Relatório de auditoria (formato `parecer_gatekeeper.md`)
- Issues identificadas (com prioridade)
- Recomendações

**Limites**:

- Profundidade de análise: 10 níveis de dependências
- Tempo máximo: 60 segundos

---

### 2.3 Sistema de Ferramentas (Tool-Use)

#### 2.3.1 Ferramentas Disponíveis

A LLM pode chamar ferramentas externas via `torre_bridge.py`:

1. **`validate_sop(artefactos)`**
   - Chama `validator.py` internamente
   - Retorna status e violações

2. **`validate_pipeline(pipeline_path)`**
   - Chama `cli.py validate_pipeline`
   - Retorna audit JSON

3. **`query_constitution(artigo_id)`**
   - Busca artigo específico na Constituição
   - Retorna texto completo + contexto

4. **`search_code(query)`**
   - Busca semântica em código indexado
   - Retorna trechos relevantes

5. **`generate_report(tipo, dados)`**
   - Gera relatório formatado (SOP, Gatekeeper)
   - Retorna caminho do arquivo gerado

**Limites**:

- Máximo 10 chamadas de ferramentas por requisição
- Timeout de 5 segundos por ferramenta

---

### 2.4 Guardrails e Limites

#### 2.4.1 Proteções Constitucionais

- **ART-03 (Consciência Técnica)**: LLM não pode assumir papel de Estado-Maior/Gatekeeper
  - **Enforcement**: Validação explícita de papel antes de ações críticas
  - **Escalação**: Ações fora do domínio escalam para Estado-Maior

- **ART-05 (Não-Autonomia Absoluta)**: Sem loops de decisão sem supervisão
  - **Enforcement**: Contador de iterações (máximo 3)
  - **Timeout**: 30 segundos por ciclo completo

- **ART-08 (Proporcionalidade)**: Mudanças mínimas e reversíveis
  - **Enforcement**: Limite de linhas alteradas por ação
  - **Checkpoint**: Estado salvo antes de mudanças

#### 2.4.2 Limites Técnicos

- **Tamanho de contexto**: 128K tokens (expansível)
- **Latência alvo**: <500ms para operações simples (ART-09)
- **Throughput**: 100 requisições/minuto (rate limiting)

#### 2.4.3 Isolamento

- **Ambiente**: Execução em sandbox isolado
- **Acesso**: Apenas aos diretórios do núcleo (não `deprecated/`, `node_modules/`)
- **Saída**: Apenas para `relatorios/` e logs aprovados

---

## 3. FLUXO DE RACIOCÍNIO

### 3.1 Pipeline de Processamento

```
Input (requisição)
  ↓
1. Análise de Intenção
   - Identificar tipo de tarefa (compreensão/validação/refatoração/auditoria)
   - Validar papel (ART-03)
   ↓
2. Enriquecimento Contextual
   - Buscar contexto relevante (RAG)
   - Carregar regras aplicáveis (Constituição, leis)
   ↓
3. Seleção de Módulo
   - Escolher módulo especializado apropriado
   - Verificar limites e guardrails
   ↓
4. Execução
   - Processar com módulo selecionado
   - Chamar ferramentas se necessário
   ↓
5. Validação Pós-Execução
   - Verificar conformidade (ART-01 a ART-10)
   - Validar saídas (formato, rastreabilidade)
   ↓
6. Geração de Output
   - Formatar resposta
   - Adicionar metadados (ART-07)
   - Citar artefactos (ART-09)
   ↓
Output (resposta + artefactos)
```

### 3.2 Raciocínio com Evidências (ART-09)

Cada conclusão deve ser justificada com:

- **Artefactos citados**: Caminhos de arquivos, linhas de código
- **Métricas**: Valores numéricos quando aplicável
- **Regras aplicadas**: Artigos da Constituição, políticas

**Formato de justificativa**:

```
Conclusão: [status/resultado]
Evidências:
  - Artefacto: `core/sop/constituição.yaml:15-20` (ART-01)
  - Métrica: coverage=85% (requisito: >=80%)
  - Regra: `leis.yaml:10` (coverage_min.python=80)
```

---

## 4. INTEGRAÇÃO COM ECOSSISTEMA FÁBRICA

### 4.1 Estado-Maior

- **Input**: Diretrizes, aprovações, vetos
- **Output**: Relatórios, pedidos de aprovação
- **Protocolo**: API via `torre_bridge.py` (ver `bridge_spec.md`)

### 4.2 SOP (Sistema Operacional da Política)

- **Input**: Métricas, artefactos para validação
- **Output**: Status PASS/BLOQUEADO, relatórios
- **Integração**: Chama `validator.py` internamente

### 4.3 Gatekeeper

- **Input**: Preparação de inputs (`gatekeeper_prep`)
- **Output**: Pareceres estruturados
- **Integração**: Gera `pipeline_gate_input.json` e `parecer_gatekeeper.md`

---

## 5. MEMÓRIA E PERSISTÊNCIA

### 5.1 Checkpoints

- **Frequência**: Após cada fase de treino (Fase 0-5)
- **Conteúdo**: Estado do modelo, embeddings, índices
- **Localização**: `torre/checkpoints/` (versionado)

### 5.2 Logs

- **Tipo**: Operações, decisões, erros
- **Formato**: JSON estruturado (conforme ART-07)
- **Retenção**: 1 ano (ART-10: Continuidade)
- **Localização**: `torre/logs/`

### 5.3 Cache

- **Contexto frequente**: Constituição, leis (sempre em memória)
- **Código indexado**: Cache LRU (últimos 1000 arquivos)
- **TTL**: 24 horas para código, infinito para Constituição

---

## 6. ESCALABILIDADE E PERFORMANCE

### 6.1 Otimizações

- **Batch processing**: Processar múltiplos arquivos em lote
- **Parallelização**: Módulos independentes em paralelo
- **Caching**: Resultados de validação cacheados (1 hora)

### 6.2 Monitorização

- **Métricas**: Latência, throughput, taxa de erro
- **Alertas**: Violações de limites, timeouts
- **Dashboard**: Status em tempo real (se aplicável)

### 6.3 Escala Futura

- **Horizontal**: Múltiplas instâncias (load balancing)
- **Vertical**: Aumento de capacidade (GPU, memória)
- **Distribuição**: Embeddings distribuídos (se necessário)

---

## 7. SEGURANÇA E COMPLIANCE

### 7.1 Acesso

- **Autenticação**: Tokens/API keys (se aplicável)
- **Autorização**: Apenas operações dentro do domínio Engenheiro
- **Auditoria**: Todas as ações logadas (ART-04)

### 7.2 Dados

- **Confidencialidade**: Dados sensíveis anonimizados
- **Integridade**: Checksums em checkpoints e datasets
- **Rastreabilidade**: Logs completos (ART-09)

### 7.3 Recovery

- **Backup**: Checkpoints diários
- **Rollback**: Capacidade de voltar a checkpoint anterior
- **Continuidade**: Preservação de logs e estado (ART-10)

---

## 8. EVOLUÇÃO E MANUTENÇÃO

### 8.1 Fine-tuning Contínuo

- **Frequência**: Semanal (com novos casos)
- **Aprovação**: Estado-Maior antes de deploy
- **Validação**: Testes automatizados antes de produção

### 8.2 Expansão de Capacidades

- **Novos módulos**: Adicionar conforme necessidade
- **Novas ferramentas**: Integrar via `torre_bridge.py`
- **Novos formatos**: Suporte a novos tipos de código/artefactos

### 8.3 Deprecação

- **Versões antigas**: Manter compatibilidade por 3 meses
- **Migração**: Processo documentado para atualizações
- **Histórico**: Preservar logs e checkpoints (ART-10)

---

## 9. DIAGRAMA DE ARQUITETURA

```
┌─────────────────────────────────────────────────────────┐
│                  LLM-Engenheira da FÁBRICA              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Core Engine  │  │   Memória    │  │  Guardrails  │ │
│  │  (LLM Base)  │←→│  (RAG/Index) │←→│  (Limites)   │ │
│  └──────┬───────┘  └──────────────┘  └──────────────┘ │
│         │                                               │
│         ├─→ ComprehensionModule                         │
│         ├─→ ValidationModule                            │
│         ├─→ RefactoringModule                           │
│         └─→ AuditModule                                 │
│                                                         │
│  ┌──────────────────────────────────────────────────┐ │
│  │           Tool-Use Interface                      │ │
│  │  (torre_bridge.py: validate, query, generate)    │ │
│  └───────────────────┬──────────────────────────────┘ │
└──────────────────────┼─────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
    ┌───▼───┐    ┌───▼───┐    ┌───▼───┐
    │Estado │    │  SOP  │    │Gate-  │
    │Maior  │    │       │    │keeper │
    └───────┘    └───────┘    └───────┘
```

---

## 10. PRÓXIMOS PASSOS

1. **Implementação**: Desenvolver `torre_bridge.py` conforme `bridge_spec.md`
2. **Treino**: Executar fases 0-5 conforme `PLAN.md`
3. **Validação**: Testar integração com SOP e Gatekeeper
4. **Deploy**: Rollout gradual com monitorização

---

**Referências**:

- `torre/curriculum/PLAN.md` - Plano de treino
- `torre/cli/bridge_spec.md` - Especificação da API
- `core/sop/constituição.yaml` - Regras fundamentais
- `core/orquestrador/cli.py` - Orquestração

---

**Assinado**: Engenheiro da TORRE  
**Data**: 2025-01-27  
**Versão**: 1.0
