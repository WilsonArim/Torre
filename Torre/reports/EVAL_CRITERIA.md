# CRITÉRIOS DE AVALIAÇÃO — LLM-Engenheira da FÁBRICA

**Agente**: Engenheiro da TORRE  
**Data/Hora**: 2025-01-27 (gerado automaticamente)  
**Objetivo**: Definir critérios top-tier para avaliar desempenho da LLM-Engenheira  
**Regras aplicadas**: ART-09 (Evidência), ART-07 (Transparência), ART-04 (Verificabilidade)

---

## 1. FILOSOFIA DE AVALIAÇÃO

A avaliação da LLM-Engenheira deve ser:
- **Objetiva**: Métricas quantificáveis, não subjetivas
- **Reprodutível**: Mesmos inputs produzem mesmos outputs
- **Abrangente**: Cobre todas as capacidades (compreensão, validação, refatoração, auditoria)
- **Alinhada com FÁBRICA**: Conformidade constitucional é pré-requisito

**Padrão "Top-Tier"**: Melhor do mundo no domínio específico FÁBRICA = 100% de conformidade + excelência técnica

---

## 2. MÉTRICAS POR CAPACIDADE

### 2.1 Compreensão de Código

#### 2.1.1 Compreensão Sintática
**Métrica**: Taxa de parse correto

- **Teste**: Parse de 1000 arquivos (Python, TS/JS, YAML, JSON)
- **Target**: 100% de sucesso (zero erros de parse)
- **Benchmark**: Igual ou superior a ferramentas especializadas (AST parsers, YAML validators)

**Dataset de validação**:
- `eval_datasets/comprehension/syntax/` (1000 arquivos)
- Inclui casos edge: código mal formatado, comentários complexos, estruturas aninhadas

**Avaliação**:
- ✅ **Top-Tier**: 100% de sucesso
- ⚠️ **Aceitável**: 95-99% (requer análise de casos falhados)
- ❌ **Inaceitável**: <95%

---

#### 2.1.2 Compreensão Semântica
**Métrica**: Precisão na identificação de propósito e dependências

- **Teste**: 500 funções/módulos anotados manualmente
- **Target**: 95%+ de precisão (F1-score)
- **Benchmark**: Comparável a análise estática profissional (TypeScript compiler, Python type checker)

**Dataset de validação**:
- `eval_datasets/comprehension/semantic/` (500 exemplos)
- Cada exemplo: código + propósito real + dependências reais

**Avaliação**:
- ✅ **Top-Tier**: F1 >= 0.95
- ⚠️ **Aceitável**: F1 >= 0.90 (requer análise de erros)
- ❌ **Inaceitável**: F1 < 0.90

---

#### 2.1.3 Rastreamento de Dependências
**Métrica**: Precisão no mapeamento de relações entre módulos/pipelines

- **Teste**: 200 módulos com dependências conhecidas
- **Target**: 90%+ de precisão (recall 95%+, precision 90%+)
- **Benchmark**: Igual ou superior a `validate_pipeline` (ferramenta oficial)

**Dataset de validação**:
- `eval_datasets/comprehension/dependencies/` (200 módulos)
- Dependências reais validadas manualmente

**Avaliação**:
- ✅ **Top-Tier**: Recall >= 0.95, Precision >= 0.90
- ⚠️ **Aceitável**: Recall >= 0.90, Precision >= 0.85
- ❌ **Inaceitável**: Recall < 0.90 ou Precision < 0.85

---

### 2.2 Validação e Conformidade

#### 2.2.1 Detecção de Violações Constitucionais
**Métrica**: Recall e Precision na detecção de violações ART-01 a ART-10

- **Teste**: 300 casos (150 válidos, 150 com violações)
- **Target**: Recall 98%+, Precision 95%+
- **Benchmark**: Igual ou superior a `validator.py` (ferramenta oficial)

**Dataset de validação**:
- `eval_datasets/validation/constitutional/` (300 casos)
- Violações reais identificadas pelo Gatekeeper

**Avaliação**:
- ✅ **Top-Tier**: Recall >= 0.98, Precision >= 0.95
- ⚠️ **Aceitável**: Recall >= 0.95, Precision >= 0.90
- ❌ **Inaceitável**: Recall < 0.95 ou Precision < 0.90

**Critério crítico**: Zero falsos negativos em violações ART-01 (Integridade) e ART-02 (Tríade)

---

#### 2.2.2 Classificação de Gates
**Métrica**: Acurácia na classificação de gates (G0-G5)

- **Teste**: 200 projetos com gate conhecido
- **Target**: 100% de acurácia (crítico)
- **Benchmark**: Igual a `determine_gate()` em `validator.py`

**Dataset de validação**:
- `eval_datasets/validation/gates/` (200 projetos)
- Gates validados manualmente pelo Estado-Maior

**Avaliação**:
- ✅ **Top-Tier**: 100% de acurácia
- ❌ **Inaceitável**: Qualquer erro (requer correção imediata)

---

#### 2.2.3 Geração de Relatórios
**Métrica**: Conformidade com ART-07 (Transparência) e ART-09 (Evidência)

- **Teste**: 100 relatórios gerados vs padrão esperado
- **Target**: 100% de conformidade (todos os campos obrigatórios presentes)
- **Benchmark**: Formato idêntico a `relatorio_sop.md` e `parecer_gatekeeper.md`

**Dataset de validação**:
- `eval_datasets/validation/reports/` (100 casos)
- Padrão esperado definido pelo Estado-Maior

**Avaliação**:
- ✅ **Top-Tier**: 100% de conformidade (todos os campos presentes)
- ⚠️ **Aceitável**: 95-99% (campos opcionais podem faltar)
- ❌ **Inaceitável**: <95% ou campos obrigatórios ausentes

**Campos obrigatórios** (ART-07):
- Agente que produziu
- Data e hora
- Objetivo
- Resumo das regras aplicadas

**Campos obrigatórios** (ART-09):
- Artefactos citados (caminhos de arquivos)
- Métricas quando aplicável
- Regras aplicadas (artigos da Constituição)

---

### 2.3 Refatoração Segura

#### 2.3.1 Preservação Funcional
**Métrica**: Taxa de testes que passam após refatoração

- **Teste**: 100 refatorações em código com testes
- **Target**: 100% de preservação (todos os testes passam)
- **Benchmark**: Igual a refatorações manuais por desenvolvedores seniores

**Dataset de validação**:
- `eval_datasets/refactoring/preservation/` (100 pares código_antes/código_depois)
- Todos com suites de testes completas

**Avaliação**:
- ✅ **Top-Tier**: 100% de preservação
- ⚠️ **Aceitável**: 95-99% (requer análise de casos falhados)
- ❌ **Inaceitável**: <95%

---

#### 2.3.2 Conformidade Mantida
**Métrica**: Zero violações introduzidas após refatoração

- **Teste**: 100 refatorações validadas pós-refatoração
- **Target**: 100% (zero violações introduzidas)
- **Benchmark**: Validação SOP pós-refatoração deve manter status PASS

**Dataset de validação**:
- `eval_datasets/refactoring/compliance/` (100 refatorações)
- Validação SOP antes e depois

**Avaliação**:
- ✅ **Top-Tier**: 100% (zero violações)
- ❌ **Inaceitável**: Qualquer violação introduzida

---

#### 2.3.3 Melhoria de Métricas
**Métrica**: Melhoria em coverage/lint após refatoração

- **Teste**: 100 refatorações com métricas antes/depois
- **Target**: 80%+ das refatorações melhoram ou mantêm métricas
- **Benchmark**: Melhoria média >= 5% em coverage

**Dataset de validação**:
- `eval_datasets/refactoring/improvement/` (100 refatorações)
- Métricas calculadas antes e depois

**Avaliação**:
- ✅ **Top-Tier**: 80%+ melhoram, média >= 5%
- ⚠️ **Aceitável**: 70-79% melhoram, média >= 3%
- ❌ **Inaceitável**: <70% ou média < 3%

---

### 2.4 Auditoria e Análise

#### 2.4.1 Detecção de Issues Estruturais
**Métrica**: Recall e Precision na detecção de dependências ausentes, ciclos, módulos não cobertos

- **Teste**: 150 pipelines (75 válidas, 75 com issues)
- **Target**: Recall 95%+, Precision 90%+
- **Benchmark**: Igual ou superior a `validate_pipeline` (ferramenta oficial)

**Dataset de validação**:
- `eval_datasets/audit/structural/` (150 pipelines)
- Issues reais identificadas em auditorias históricas

**Avaliação**:
- ✅ **Top-Tier**: Recall >= 0.95, Precision >= 0.90
- ⚠️ **Aceitável**: Recall >= 0.90, Precision >= 0.85
- ❌ **Inaceitável**: Recall < 0.90 ou Precision < 0.85

---

#### 2.4.2 Rastreabilidade
**Métrica**: 100% dos achados citam artefactos (ART-09)

- **Teste**: 200 relatórios de auditoria gerados
- **Target**: 100% de rastreabilidade (todos os achados citam arquivos/linhas)
- **Benchmark**: Formato idêntico a `parecer_gatekeeper.md`

**Dataset de validação**:
- `eval_datasets/audit/traceability/` (200 relatórios)
- Validação manual de citações

**Avaliação**:
- ✅ **Top-Tier**: 100% de rastreabilidade
- ❌ **Inaceitável**: Qualquer achado sem citação

---

#### 2.4.3 Conformidade de Relatórios
**Métrica**: Formato conforme Gatekeeper (100%)

- **Teste**: 100 relatórios vs formato esperado
- **Target**: 100% de conformidade
- **Benchmark**: Formato idêntico a `parecer_gatekeeper.md`

**Dataset de validação**:
- `eval_datasets/audit/format/` (100 relatórios)
- Padrão definido pelo Gatekeeper

**Avaliação**:
- ✅ **Top-Tier**: 100% de conformidade
- ❌ **Inaceitável**: Qualquer desvio do formato

---

### 2.5 Integração e Operação

#### 2.5.1 Latência
**Métrica**: Tempo de resposta para operações

- **Teste**: 1000 requisições (mix de operações simples/complexas)
- **Target**: <500ms para operações simples (ART-09: latência_alvo_ms)
- **Benchmark**: Igual ou superior a `validator.py` em operações equivalentes

**Dataset de validação**:
- `eval_datasets/integration/latency/` (1000 requisições)
- Medição em ambiente de produção simulado

**Avaliação**:
- ✅ **Top-Tier**: P95 < 500ms (95% das requisições < 500ms)
- ⚠️ **Aceitável**: P95 < 1000ms
- ❌ **Inaceitável**: P95 >= 1000ms

---

#### 2.5.2 Precisão Operacional
**Métrica**: Zero violações de ART-03 (Consciência Técnica)

- **Teste**: 500 operações monitoradas
- **Target**: 100% (zero violações de papel)
- **Benchmark**: Validação manual por Estado-Maior

**Dataset de validação**:
- `eval_datasets/integration/roles/` (500 operações)
- Validação de que cada ação está dentro do domínio Engenheiro

**Avaliação**:
- ✅ **Top-Tier**: 100% (zero violações)
- ❌ **Inaceitável**: Qualquer violação de ART-03

---

#### 2.5.3 Disponibilidade
**Métrica**: Taxa de disponibilidade do sistema

- **Teste**: Monitorização contínua por 30 dias
- **Target**: 99.9% de disponibilidade
- **Benchmark**: SLA de produção

**Avaliação**:
- ✅ **Top-Tier**: >= 99.9%
- ⚠️ **Aceitável**: >= 99.5%
- ❌ **Inaceitável**: < 99.5%

---

## 3. DATASETS DE VALIDAÇÃO

### 3.1 Estrutura
Todos os datasets em `torre/eval_datasets/`:
```
eval_datasets/
  comprehension/
    syntax/        (1000 arquivos)
    semantic/      (500 exemplos)
    dependencies/  (200 módulos)
  validation/
    constitutional/ (300 casos)
    gates/          (200 projetos)
    reports/        (100 relatórios)
  refactoring/
    preservation/   (100 pares)
    compliance/     (100 refatorações)
    improvement/     (100 refatorações)
  audit/
    structural/      (150 pipelines)
    traceability/    (200 relatórios)
    format/          (100 relatórios)
  integration/
    latency/        (1000 requisições)
    roles/           (500 operações)
```

### 3.2 Versionamento
Cada dataset versionado com:
- Hash SHA256
- Data de criação
- Agente que criou
- Aprovação Estado-Maior

### 3.3 Expansão
- Novos casos adicionados semanalmente
- Datasets atualizados após cada fase de treino
- Validação cruzada com casos reais de produção

---

## 4. BENCHMARKS EXTERNOS

### 4.1 Comparação com Ferramentas Especializadas
- **AST Parsers**: Python `ast`, TypeScript compiler
- **Linters**: ESLint, Pylint, Semgrep
- **Validators**: `validator.py` (ferramenta oficial FÁBRICA)
- **Pipeline Tools**: `validate_pipeline` (ferramenta oficial)

**Objetivo**: Igualar ou superar ferramentas especializadas em seus domínios específicos

### 4.2 Comparação com LLMs Genéricas
- **GPT-4**, **Claude Sonnet**: Baseline de capacidade geral
- **Objetivo**: Superar em domínio específico FÁBRICA (especialização)

---

## 5. PROCESSO DE AVALIAÇÃO

### 5.1 Avaliação por Fase
- **Checkpoint 0**: Avaliação após Fase 0 (fundação)
- **Checkpoint 1**: Avaliação após Fase 1 (compreensão)
- **Checkpoint 2**: Avaliação após Fase 2 (validação)
- **Checkpoint 3**: Avaliação após Fase 3 (refatoração)
- **Checkpoint 4**: Avaliação após Fase 4 (auditoria)
- **Checkpoint 5**: Avaliação após Fase 5 (integração)

### 5.2 Avaliação Contínua
- **Semanal**: Testes automatizados em datasets de validação
- **Mensal**: Avaliação completa com relatório para Estado-Maior
- **Trimestral**: Revisão de benchmarks e atualização de datasets

### 5.3 Critérios de Aprovação
- **Top-Tier**: Todas as métricas em nível Top-Tier
- **Aprovação para Produção**: Todas as métricas críticas em Top-Tier
- **Requer Correção**: Qualquer métrica crítica abaixo de Aceitável

---

## 6. RELATÓRIOS DE AVALIAÇÃO

### 6.1 Formato
Relatórios em `torre/reports/eval/`:
- `eval_checkpoint_N.md` (após cada checkpoint)
- `eval_weekly_YYYY-MM-DD.md` (avaliações semanais)
- `eval_monthly_YYYY-MM.md` (avaliações mensais)

### 6.2 Conteúdo
- Resumo executivo (métricas principais)
- Análise detalhada por capacidade
- Comparação com benchmarks
- Recomendações e próximos passos

### 6.3 Conformidade
- Todos os relatórios seguem ART-07 (transparência)
- Todos os resultados citam artefactos (ART-09)
- Todos os datasets são rastreáveis (ART-04)

---

## 7. PRÓXIMOS PASSOS

1. **Preparação de Datasets**: Criar todos os datasets de validação
2. **Automação**: Scripts de avaliação automatizada
3. **Baseline**: Estabelecer baseline com modelo não-treinado
4. **Iteração**: Avaliar após cada fase de treino

---

**Referências**:
- `torre/curriculum/PLAN.md` - Fases de treino
- `core/sop/constituição.yaml` - ART-04, ART-07, ART-09
- `core/scripts/validator.py` - Ferramenta oficial de validação

---

**Assinado**: Engenheiro da TORRE  
**Data**: 2025-01-27  
**Versão**: 1.0

