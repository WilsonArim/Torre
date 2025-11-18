# PLANO DE ESTUDO E TREINO — LLM-Engenheira da FÁBRICA

**Agente**: Engenheiro da TORRE  
**Data/Hora**: 2025-01-27 (gerado automaticamente)  
**Objetivo**: Definir currículo completo para treinar LLM especializada no ecossistema FÁBRICA  
**Regras aplicadas**: Constituição (ART-01 a ART-10), ART-07 (Transparência), ART-09 (Evidência)

---

## 1. VISÃO GERAL

A LLM-Engenheira da FÁBRICA deve ser capaz de:

- **Compreender** código Python, TypeScript/JavaScript, Java, YAML, JSON dentro do contexto FÁBRICA
- **Testar** e validar conformidade com SOP/Gatekeeper automaticamente
- **Refatorar** código mantendo integridade constitucional
- **Auditar** pipelines, módulos e capítulos conforme Constituição
- **Integrar-se** com Estado-Maior, SOP e Gatekeeper sem violar ART-03 (Consciência Técnica)

---

## 2. FASES DE TREINO

### FASE 0: FUNDAÇÃO (Semana 1-2)

**Objetivo**: Compreensão profunda da Constituição e estrutura base

**Conteúdo**:

- 10 Artigos da Constituição (`core/sop/constituição.yaml`)
- Tríade de Fundamentação (ART-02): White Paper, Arquitetura, Base Operacional
- Estrutura de diretórios do núcleo (`core/`, `pipeline/`, `relatorios/`, `docs/`)
- Sistema de Gates (G0-G5) e requisitos (`core/sop/leis.yaml`)
- RACI e papéis (Estado-Maior, SOP, Gatekeeper, Engenheiro)

**Métricas**:

- Teste de compreensão: 100% de precisão em identificar violações ART-01 a ART-10
- Teste de estrutura: mapear corretamente todos os caminhos do núcleo
- Teste de gates: associar requisitos corretos a cada gate

**Falhas Graves Potenciais (DEVEM SER ELIMINADAS)**:

- ⛔ Falha Grave: Confusão entre papéis (ART-03) → **ELIMINAÇÃO OBRIGATÓRIA**: Validação automática bloqueia execução se papel incorreto
- ⛔ Falha Grave: Interpretação incorreta de leis → **ELIMINAÇÃO OBRIGATÓRIA**: Dataset validado pelo Estado-Maior, sem exceções

---

### FASE 1: COMPREENSÃO DE CÓDIGO (Semana 3-4)

**Objetivo**: Ler e entender código Python/TS/JS/YAML/JSON específico da FÁBRICA

**Conteúdo**:

- `core/orquestrador/cli.py`: comandos, validações, gatekeeper_run
- `core/scripts/validator.py`: lógica SOP, métricas, conformidade
- `core/scripts/plugins/*.py`: integrações (bandit, semgrep, trivy, sbom, etc.)
- `pipeline/superpipeline.yaml`: estrutura de módulos e capítulos
- Templates de pipeline (`pipeline/_templates/`)
- Workflows CI/CD (`.github/workflows/`)

**Dataset**:

- Código anotado com comentários explicativos (função, contexto, dependências)
- Casos de uso reais (validações, correções, auditorias)
- Violações intencionais para treino de detecção

**Métricas**:

- Compreensão sintática: parse correto de todos os formatos (100%)
- Compreensão semântica: identificar propósito de funções/modules (95%+)
- Rastreamento de dependências: mapear relações entre módulos/pipelines (90%+)

**Falhas Graves Potenciais (DEVEM SER ELIMINADAS)**:

- ⛔ Falha Grave: Overfitting em código específico → **ELIMINAÇÃO OBRIGATÓRIA**: Dataset diversificado obrigatório, validação bloqueia se não diversificado
- ⛔ Falha Grave: Falta de contexto externo → **ELIMINAÇÃO OBRIGATÓRIA**: Documentação (`docs/`) e relatórios históricos obrigatórios, sistema bloqueia sem contexto completo

---

### FASE 2: VALIDAÇÃO E CONFORMIDADE (Semana 5-6)

**Objetivo**: Executar validações SOP e detectar violações constitucionais

**Conteúdo**:

- Lógica de validação (`validator.py`)
- Regras de gates e políticas (`leis.yaml`)
- Exceções e expirações (`exceptions.yaml`)
- Geração de relatórios (formato `relatorio_sop.md`, `sop_status.json`)
- Integração com pipeline (`gatekeeper_prep`, `gatekeeper_run`)

**Dataset**:

- Projetos válidos (PASS) vs inválidos (BLOQUEADO)
- Casos edge: exceções temporárias, violações parciais
- Histórico de relatórios reais (`relatorios/`)

**Métricas**:

- Detecção de violações: recall 98%+, precision 95%+
- Classificação de gates: acurácia 100% (crítico)
- Geração de relatórios: conformidade com ART-07 e ART-09 (100%)

**Falhas Graves Potenciais (DEVEM SER ELIMINADAS)**:

- ⛔ Falha Grave: Falsos positivos bloqueando projetos válidos → **ELIMINAÇÃO OBRIGATÓRIA**: Validação cruzada obrigatória, sistema bloqueia execução sem validação cruzada
- ⛔ Falha Grave: Não detectar violações sutis → **ELIMINAÇÃO OBRIGATÓRIA**: Dataset com padrões ocultos obrigatório, sistema bloqueia se não detectar todos os padrões

---

### FASE 3: REFATORAÇÃO SEGURA (Semana 7-8)

**Objetivo**: Refatorar código mantendo integridade e conformidade

**Conteúdo**:

- Princípios de refatoração mínima (ART-08: Proporcionalidade)
- Preservação de lógica de negócio
- Manutenção de interfaces públicas
- Atualização de testes e documentação
- Validação pós-refatoração (re-run SOP)

**Dataset**:

- Pares (código_antes, código_depois) validados
- Refatorações que violaram regras (para aprender o que NÃO fazer)
- Refatorações que melhoraram conformidade

**Métricas**:

- Preservação funcional: testes passam após refatoração (100%)
- Conformidade mantida: nenhuma violação introduzida (100%)
- Melhoria de métricas: coverage/lint melhoram ou mantêm (target: 80%+ melhoria)

**Falhas Graves Potenciais (DEVEM SER ELIMINADAS)**:

- ⛔ Falha Grave: Quebrar funcionalidade existente → **ELIMINAÇÃO OBRIGATÓRIA**: Testes automatizados obrigatórios, sistema bloqueia se testes falharem
- ⛔ Falha Grave: Introduzir violações → **ELIMINAÇÃO OBRIGATÓRIA**: Validação SOP obrigatória pós-refatoração, sistema bloqueia se validação falhar

---

### FASE 4: AUDITORIA E ANÁLISE (Semana 9-10)

**Objetivo**: Auditar pipelines, módulos e estrutura completa

**Conteúdo**:

- Validação de pipeline (`validate_pipeline`)
- Detecção de dependências ausentes, ciclos, módulos não cobertos
- Análise de conformidade estrutural (Constituição, Tríade)
- Geração de relatórios de auditoria forense
- Integração com Gatekeeper (preparação de inputs)

**Dataset**:

- Pipelines válidas vs inválidas
- Casos históricos de auditoria (`relatorios/Auditoria Forense Estrutural.md`)
- Relatórios de parecer Gatekeeper

**Métricas**:

- Detecção de issues estruturais: recall 95%+, precision 90%+
- Rastreabilidade: todos os achados citam artefactos (ART-09)
- Conformidade de relatórios: formato Gatekeeper (100%)

**Falhas Graves Potenciais (DEVEM SER ELIMINADAS)**:

- ⛔ Falha Grave: Falta de contexto histórico → **ELIMINAÇÃO OBRIGATÓRIA**: Relatórios de auditorias passadas obrigatórios, sistema bloqueia sem contexto histórico
- ⛔ Falha Grave: Análise superficial → **ELIMINAÇÃO OBRIGATÓRIA**: Profundidade mínima obrigatória (3 níveis de dependências), sistema bloqueia se profundidade insuficiente

---

### FASE 5: INTEGRAÇÃO E OPERAÇÃO (Semana 11-12)

**Objetivo**: Operar em produção integrada com Estado-Maior/SOP/Gatekeeper

**Conteúdo**:

- API `torre_bridge.py`: perguntar, ensinar, validar
- Fluxos de aprovação (Estado-Maior → SOP → Gatekeeper)
- Geração de checkpoints e logs de treino
- Rollback e recuperação (ART-10: Continuidade)
- Monitorização de desempenho em produção

**Dataset**:

- Interações simuladas com Estado-Maior
- Casos de veto/aprovação do Gatekeeper
- Logs de execução reais (se disponíveis)

**Métricas**:

- Latência de resposta: <500ms para validações simples (ART-09: latência_alvo_ms)
- Precisão operacional: 0 violações de ART-03 (Consciência Técnica)
- Disponibilidade: 99.9% (logs preservados sempre)

**Falhas Graves Potenciais (DEVEM SER ELIMINADAS)**:

- ⛔ Falha Grave: Loop de decisão sem supervisão (ART-05) → **ELIMINAÇÃO OBRIGATÓRIA**: Timeout e escalação obrigatórios, sistema bloqueia automaticamente após timeout
- ⛔ Falha Grave: Perda de logs (ART-10) → **ELIMINAÇÃO OBRIGATÓRIA**: Sistema de checkpointing robusto obrigatório, sistema bloqueia se checkpointing falhar

---

## 3. METODOLOGIA DE TREINO

### 3.1 Supervisionado (Fases 0-3)

- **Input**: Código + contexto + objetivo
- **Output esperado**: Ação + justificativa + artefactos citados
- **Feedback**: Correção explícita de erros + reforço de padrões corretos

### 3.2 Auto-avaliação (Fases 2-4)

- **Input**: Código + ação proposta
- **Output**: Score de confiança + lista de riscos identificados
- **Validação**: Comparar com avaliação humana (Estado-Maior)

### 3.3 RLHF Interno (Fase 5)

- **Recompensa**: Aprovação do Gatekeeper, sucesso em validações SOP
- **Punição**: Violação de Constituição, veto do Gatekeeper
- **Fine-tuning contínuo**: Atualização semanal com novos casos

---

## 4. DATASETS E FONTES

### 4.1 Fontes Primárias (ver `torre/data/SOURCES.md`)

- Código do núcleo (`core/`, `pipeline/`)
- Documentação oficial (`docs/`)
- Relatórios históricos (`relatorios/`)
- Configurações (`tools/`, `.github/`)

### 4.2 Curação

- **Anonimização**: Remover informações sensíveis (tokens, keys, paths absolutos)
- **Validação**: Estado-Maior aprova todos os datasets antes do treino (SOP)
- **Versionamento**: Cada dataset versionado com hash e metadata

### 4.3 Expansão Contínua

- Novos módulos → adicionar ao dataset
- Novas violações detectadas → casos de treino
- Feedback do Gatekeeper → ajustes no modelo

---

## 5. CHECKPOINTS E VALIDAÇÃO

### 5.1 Checkpoints por Fase

- **Checkpoint 0**: Fim da Fase 0 (fundação)
- **Checkpoint 1**: Fim da Fase 1 (compreensão)
- **Checkpoint 2**: Fim da Fase 2 (validação)
- **Checkpoint 3**: Fim da Fase 3 (refatoração)
- **Checkpoint 4**: Fim da Fase 4 (auditoria)
- **Checkpoint 5**: Fim da Fase 5 (integração)

### 5.2 Validação de Checkpoints

- **Teste automatizado**: Suite de validação executada automaticamente
- **Revisão Estado-Maior**: Aprovação manual antes de avançar
- **Gatekeeper**: Valida conformidade antes de produção

### 5.3 Rollback

- Se checkpoint falhar → rollback para anterior
- Logs preservados (ART-10)
- Análise de causa raiz obrigatória

---

## 6. MÉTRICAS DE SUCESSO GLOBAIS

### 6.1 Técnicas

- **Precisão constitucional**: 100% (zero violações ART-01 a ART-10)
- **Compreensão de código**: 95%+ em todos os formatos
- **Validação SOP**: 98%+ recall, 95%+ precision
- **Latência**: <500ms para operações simples

### 6.2 Operacionais

- **Disponibilidade**: 99.9%
- **Rastreabilidade**: 100% (todos os outputs citam artefactos)
- **Conformidade**: 100% (todos os relatórios seguem ART-07)

### 6.3 Evolutivas

- **Melhoria contínua**: Métricas melhoram a cada checkpoint
- **Novos casos**: Capacidade de generalizar para novos módulos/pipelines

---

## 7. FALHAS GRAVES POTENCIAIS (ELIMINAÇÃO OBRIGATÓRIA)

**REGRA CONSTITUCIONAL CRÍTICA**:

> **NUNCA, MAS NUNCA DEVE HAVER RISCOS. RISCOS AGORA SÃO FALHAS GRAVES NO FUTURO.**

**Diretriz**:

- ⛔ Qualquer "risco" identificado = FALHA GRAVE POTENCIAL
- ⛔ Não há mitigação, apenas ELIMINAÇÃO COMPLETA
- ⛔ Sistema BLOQUEIA automaticamente se detectar qualquer falha grave potencial
- ⛔ Gatekeeper BLOQUEIA qualquer artefacto que contenha menção a "riscos" (mesmo mitigados)

| Falha Grave Potencial                   | Impacto     | Eliminação Obrigatória                       | Bloqueio Automático                              |
| --------------------------------------- | ----------- | -------------------------------------------- | ------------------------------------------------ |
| Overfitting em código específico        | **CRÍTICO** | Dataset diversificado OBRIGATÓRIO            | ✅ Sistema bloqueia se dataset não diversificado |
| Violação de ART-03 (papéis)             | **CRÍTICO** | Validação explícita OBRIGATÓRIA em cada ação | ✅ Sistema bloqueia se papel incorreto detectado |
| Perda de logs (ART-10)                  | **CRÍTICO** | Sistema de checkpointing robusto OBRIGATÓRIO | ✅ Sistema bloqueia se checkpointing falhar      |
| Falsos positivos em validação           | **ALTO**    | Validação cruzada OBRIGATÓRIA                | ✅ Sistema bloqueia sem validação cruzada        |
| Loop de decisão sem supervisão (ART-05) | **CRÍTICO** | Timeout + escalação OBRIGATÓRIOS             | ✅ Sistema bloqueia automaticamente após timeout |
| Qualquer menção a "risco" em artefactos | **CRÍTICO** | Eliminação completa da palavra "risco"       | ✅ Gatekeeper bloqueia artefactos com "risco"    |

---

## 8. PRÓXIMOS PASSOS

1. **Aprovação Estado-Maior**: Este plano deve ser aprovado antes de iniciar
2. **Preparação de datasets**: Começar curadoria das fontes (Fase 0)
3. **Setup de infraestrutura**: Ambiente de treino isolado
4. **Checkpoint 0**: Validação inicial de compreensão constitucional

---

**Referências**:

- `core/sop/constituição.yaml` - ART-01 a ART-10
- `core/sop/leis.yaml` - Gates e políticas
- `core/orquestrador/cli.py` - Orquestração
- `core/scripts/validator.py` - Validação SOP
- `docs/MAPA_DA_FÁBRICA.md` - Estrutura do núcleo

---

**Assinado**: Engenheiro da TORRE  
**Data**: 2025-01-27  
**Versão**: 1.0
