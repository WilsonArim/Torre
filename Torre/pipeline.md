+# Pipeline Estratégica: Nossa LLM 8x + Turbo

- +## Contra-Análise do ChatGPT (Ajustes Cirúrgicos)
- +### Veredito Curto +_ **Bom**: divisão por fases, foco em contexto, estratégia, aprendizagem e métricas. +_ **A melhorar (crítico)**: falta baseline sólido, critérios de saída mensuráveis por fase, ordem de dependências, e caminho claro de fallback/rollback.
- +### O que foi ajustado (5 pontos)
- +1. **Fase 0 — Baseline & Telemetria (obrigatória antes de Fase 1)**
- - Fixar dataset de referência (10–30 episódios reais) e métricas baseline (nossa LLM vs Claude).
- - Ligar o painel **SLI/SLO**: `success_rate`, `TTG` (time-to-green), `diff_size`, `p95_latency`, `regressões`, `violations(perf,sec)`, `human_interventions`.
- - Definir "score composto" S (0–100) = 0.4·success + 0.25·(TTG↓) + 0.15·diff↓ + 0.1·regressões↓ + 0.1·violations↓.
- > **Gate**: só avança se S ≥ baseline+20%.
- +2. **Trocar "checklists de intenção" por "critérios de saída"**
- - Cada item da pipeline deve ter **saída verificável** (teste/eval).
- - Ex.: "Mapeamento de dependências avançado" → "grafo com ≥95% de imports resolvidos; ≤1% de ciclos novos; cobertura de símbolos ≥90%".
- +3. **Reordenar dependências**
- - **1→2**: Omni-Contexto + Grafo (fundação) → Strategos (priorização) → Aprendizagem → Perf/Sec.
- - "Filosofia/qualidade" e "predição" vêm **depois** de termos TTG e regressões sob controlo.
- +4. **Fallbacks e circuit-breakers**
- - Se `success_rate` < 90% em 30 min → **ADVICE-mode** (sem aplicar patch).
- - Se `p95_latency` > alvo → reduzir contexto e forçar 7B.
- - Se `violations(sec)` > 0 → bloquear apply e emitir relatório.
- +5. **Fase 5 — tornar "turbo" um trilho de I&D (não compromisso de produção)**
- - "Código quântico / paradigmas novos" vão para **backlog R&D** com hipóteses e experimentos, fora do caminho crítico.
- +---
- +## Pipeline Revisada (Enxuta e Mensurável)
- +### Fase 0 — Baseline & Telemetria (D0) +**Objetivo**: Estabelecer linha de base mensurável
- +**Saídas**: +_ Dataset baseline fixado; relatórios `.torre/evals/_`.
  +\* S (score) calculado para nós e Claude.
- +**Gate**: S ≥ baseline+20%.
- +### Fase 1 — Fundação (2×) +**Objetivo**: Base sólida e mensurável
- +**1.1 Omni-Contexto & Grafo** +_ Índice de símbolos/componentes (cobertura ≥90% dos ficheiros `src/**`). +_ Grafo TS (imports resolvidos ≥95%; ciclos mapeados).
- +**1.2 Estratégia Básica (Strategos v1)**
  +\* Ordem de ataque = `build→types→tests→style` ajustada por risco (cálculo ≥ presente em métricas).
- +**1.3 Métricas**
  +\* Painel com `success_rate`, `TTG`, `diff_size`, `p95_latency`, `violations(perf,sec)`.
- +**Gates**:

* ✅ **Cobertura**: índice ≥90% e imports resolvidos ≥95%
* ✅ **Qualidade**: success_rate ≥95% na suite estratégica
* ✅ **Diff size**: p95 ≤ baseline p95 (ou ≤300 linhas, o que for menor)
* ✅ **Tempo**: TTG p95 ↓ ≥15% vs baseline (Fase 1)

- +### Fase 2 — Inteligência Estratégica (4×) +**Objetivo**: Capacidades avançadas mensuráveis
- +**2.1 Strategos v2** (impacto × risco × custo; awareness de módulos) +**2.2 Aprendizagem Persistente v1** (episodes→lessons aplicadas; repetição de erro ↓ ≥60%) +**2.3 Engenheiro Sénior v1** (refactors pequenos guiados; no-regress)
- +**Gates**: `success_rate` ≥95%, `regressões` ≤1%, `human_interventions` ↓ ≥50%.
- +### Fase 3 — Filosofia & Qualidade (6×) +**Objetivo**: Qualidade superior mensurável
- +**3.1 Guardrails Avançados** (anti-padrões, arquitetura, segurança) +**3.2 Documentação/justificativa automática** (report com provas curtas)
- +**Gates**: `violations(sec,perf)` = 0, `diff_size` p95 < 300 linhas, `TTG` p95 ≤ 12.5% do baseline.
- +### Fase 4 — Predição & Inovação (8×) +**Objetivo**: Capacidades preditivas mensuráveis
- +**4.1 Predição de falhas** (com base nos episódios) +**4.2 Pré-checagem de impacto** (simulação leve antes do patch)
- +**Gates**: `incident_prevented` ≥ 30% dos casos sinalizados; `success_rate` ≥97%.
- +### Fase 5 — Turbo I&D (10×) _[off-road]_ +**Objetivo**: Experimentos controlados (não bloqueia produção)
- +\* Experimentos controlados; **não bloqueia** o caminho de produção.
- +---
- +## Métricas-Chave (Objetivas)
- +_ **Success rate** (patch aplica limpo e gates verdes) +_ **TTG** (tempo até verde) +_ **Diff size** (média/p95) +_ **Regressões** por 100 patches +_ **Violations** (sec/perf) por patch +_ **Intervenções humanas** por episódio
  +\* **Custo por patch verde** (tokens/$$ se usar API)
- +---
- +## Circuit-Breakers
- +1. **Se `success_rate` < 90% em 30 min** → ADVICE-mode (sem aplicar patch)
  +2. **Se `p95_latency` > alvo** → reduzir contexto e forçar 7B
  +3. **Se `violations(sec)` > 0** → bloquear apply e emitir relatório
- +---
- +## Status da Execução
- +- [x] **Fase 0**: Baseline & Telemetria ✅ CONCLUÍDA
  +- [x] **Fase 1**: Fundação (2×) ✅ CONCLUÍDA
  +- [x] **Fase 2**: Inteligência Estratégica (4×) ✅ CONCLUÍDA
  +- [x] **Fase 3**: Filosofia & Qualidade (6×) ✅ CONCLUÍDA
  +- [ ] **Fase 4**: Predição & Inovação (8×)
  +- [ ] **Fase 5**: Turbo I&D (10×)

````diff
+# Pipeline — Addendum FASES 6–12 (vanguarda)
+
+> Continuação direta da pipeline existente (Fase 1–5).
+> Cada fase abaixo tem **Objetivo → Entregáveis → Gates (saída mensurável)**.
+> Passar de fase só com todos os **Gates** a verde.
+
+---
+
+## FASE 6 — Cérebro determinista & Pós-processamento blindado ✅ CONCLUÍDA
+
+**Objetivo**: garantir que **toda** saída é “engenharia-only → 1 diff unificado → idempotente”.
+
+### Entregáveis
+1) **Prompts engineer-only** refinados (mínimo patch, sem prosa) + **protocolo de saída** (```diff``` unificado).
+2) **Perfis PATCH / PATCH_B** com **A/B** e **circuit-breaker** (degrada para PATCH_B se qualidade cair).
+3) **Pós-processamento** “à prova de bala”:
+   - extração/validação de diff (unificado, hunks válidos);
+   - recorte de ruído (remove texto fora do bloco);
+   - **hard-deny** a paths sensíveis (.env, .ssh, *.pem, id_rsa, secrets.*);
+   - **limite de linhas** (ex.: ≤1200) + **auto-shrink** (particiona/recorta safe se exceder).
+
+### Gates
+- ≥ **99%** dos outputs contêm **apenas** um bloco ```diff``` válido.
+- **0** violações de paths sensíveis.
+- **SLI-patch-verde ≥95%** com PATCH; se cair <90% por 30 min → **PATCH_B** + **ADVICE-mode**.
+
+---
+
+## FASE 7 — Meta-Aprendizagem ✅ CONCLUÍDA
+
+**Objetivo**: reduzir erros repetidos e adaptar por workspace.
+
+### Entregáveis
+1) **Harness de comparação** contra qualquer provider (Claude/Gemini/OpenAI/vLLM)
+   – mede **SLI1 (patch verde)**, **p95 latência**, **diff_size**, **custo**, **violations** → relatório `.torre/evals/*`.
+2) **Auto-fixes & Codemods AST (TS)** idempotentes acionados por logs (imports, TS, paths).
+3) **ADVICE-mode**: quando risco alto ou gates falham, só aconselha, sem patch.
+
+### Gates
+- **Evals** executam em < **5 min** com dataset amostra (≥12 episódios).
+- **Auto-fixes** reduzem repetição do mesmo erro ≥ **50%** no período.
+- **Advice-mode** dispara automaticamente se `success_rate<90%` (janela 30 min).
+
+---
+
+## FASE 8 — Guardrails Aristotélicos + Omni-Contexto & Strategos v1
+
+**Objetivo**: coerência lógica + plano de ataque disciplinado.
+
+### Entregáveis
+1) **Guardrails Aristotélicos** em runtime:
+   - não-contradição entre métricas (ex.: lint_clean ↔ classification.lint.ok);
+   - terceiro excluído (booleans ∈ {True, False});
+   - silogismo operacional: (validate ∧ dry_run) ⇒ apply.
+2) **Omni-Contexto**: leitura do projeto + **grafo de imports**; cobertura ficheiros ≥**90%**; imports resolvidos ≥**95%**.
+3) **Strategos v1**: **priorização** `build → types → tests → style` por **risco**; plano explica ordem & impacto.
+
+### Gates
+- **0** violações lógicas numa janela de 24 h.
+- **Cobertura** (src/**) ≥90% e **imports resolvidos** ≥95%.
+- **TTG** (time-to-green) ↓ ≥ **20%** vs baseline.
+
+---
+
+## FASE 9 — Strategos v2 + Reranker por execução + Memória episódica
+
+**Objetivo**: escolher **a correção certa** e **aprender** com cada falha.
+
+### Entregáveis
+1) **Strategos v2**: score = **impacto × risco × custo** (awareness de módulos e dependências).
+2) **Reranker n-best**: gerar 2–3 candidatos de patch → executar lint/tests localmente → escolher o que fica **100% verde**.
+3) **Memória episódica (workspace-local, sem PII)**: “se TS2304 em `src/*` + `vite`, aplicar regra X”; re-aplicada automaticamente.
+
+### Gates
+- **Repetição do mesmo erro** ↓ ≥ **60%** em 7 dias.
+- **Success-rate** pós-reranker ≥ **97%** no dataset amostra.
+- **Human-interventions/episódio** ↓ ≥ **50%**.
+
+---
+
+## FASE 10 — Forense & regressão zero + RAG dos Mestres + Otimizador custo/latência
+
+**Objetivo**: zero regressões silenciosas; inteligência curada; eficiência operacional.
+
+### Entregáveis
+1) **Forense de impacto** para cada diff: arquivos tocados → dependências → riscos (duplicação, hotspots, segredos).
+2) **RAG CANON** (curado e versionado): lentes (Aristóteles, Dijkstra, Hoare, Knuth, Saltzer) com **metarregras executáveis**; cada patch cita a lente/regra aplicada.
+3) **Otimizador**: cache de contexto, compressão de logs, **7B ↔ 14B por rota** (curto ↔ pesado), janelas dinâmicas.
+
+### Gates
+- **Regressões/100 patches** ≤ **1**.
+- **Custo por patch verde** ↓ ≥ **30%** sem perda de SLI.
+- **Diff_size p95** < **300** linhas.
+
+---
+
+## FASE 11 — Pesquisa “Vanguarda” (web) com escopo de engenharia
+
+**Objetivo**: incorporar estado-da-arte **só** quando ajuda decisões técnicas.
+
+### Entregáveis
+1) **Charter de pesquisa** (engenharia-only):
+   - Quando pesquisar: temas recentes/instáveis; “melhor método hoje”; licença/segurança; números de desempenho.
+   - Como: docs oficiais, RFCs, repositórios, arXiv, blogposts de engenharia.
+   - **Citações obrigatórias** (links + data).
+   - **Aprovação admin** para promover informação ao **CANON** (anti-poisoning).
+2) **Vanguard Brief**: 5–10 pontos — o que é novo, o que é sólido, armadilhas — + pipeline/gates.
+
+### Gates
+- 100% dos briefs com **fontes citadas** e **data**.
+- **0** violações de escopo (sem conteúdo não-técnico/finanças/opiniões gerais).
+- **Tempo de decisão** ↓ ≥ **25%** em tasks dependentes de pesquisa.
+
+---
+
+## FASE 12 — Governação & Segurança operacional (travões finais)
+
+**Objetivo**: tornar **falhas seguras** e reverter rápido.
+
+### Entregáveis
+1) **Guardrails de fluxo**: branches protegidos + CODEOWNERS + approvals; checks obrigatórios (lint, typecheck, unit/contract, build seco, `git apply --check`, validate→dry-run→apply em staging); canary, feature flags, rollback 1-click; **circuit-breaker** → **ADVICE-mode**.
+2) **Defense-in-depth tests**: unidade→integração→E2E→contract; property-based, fuzzing, mutation; golden snapshots; cobertura mínima por ficheiro tocado.
+3) **Compliance & dados**: DLP/secret scan (deny-merge), **SBOM & license policy**, audit trail (quem gerou patch, prompts, fontes), data minimization/retention + redação de logs.
+4) **Segurança operacional**: RBAC/least-privilege; runners isolados; **no-network by default**; WAF + rate-limit; egress allow-list; **assinatura** de commits/artefactos (proveniência/SLSA).
+5) **Coordenação**: ADR/RFC leve; janela de mudança + freeze se métricas caem; playbook de incidentes (TTR/MTTR).
+
+### Gates
+- **Zero** segredos em PR (scanner como **deny-merge**).
+- **SLOs** mantidos por 7 dias (SLI-patch-verde ≥95%, p95 latência dentro do alvo).
+- **Rollback** testado (DR-drill) trimestral.
+
+---
+
+## Saída padrão do Brainstorming (sempre)
+1) **Feasibility** (score + condicionantes).
+2) **Plano A/B** com pipeline e **gates**.
+3) **Vanguard Brief** (se houve pesquisa) com **citações**.
+4) **Risk register** (probabilidade × impacto, mitigação).
+5) **Próximos 3 passos executáveis** (comandos & artefactos).
+
+---
+
+## Circuit-breakers (globais)
+1) `success_rate < 90%` (30 min) → **ADVICE-mode** + gerar episódios para treino.
+2) `p95_latency > alvo` (10 min) → reduzir contexto + forçar **7B** (tier-down).
+3) `violations(sec) > 0` → bloquear **apply** + relatório forense.
+
+---
+
+## Métricas-chave (telemetria)
+- **SLI1**: patch aplica limpo e gates verdes.
+- **TTG** (time-to-green).
+- **Diff_size** (média/p95).
+- **Regressões** por 100 patches.
+- **Violations** (segurança/perf).
+- **Intervenções humanas** por episódio.
+- **Custo por patch verde** (tokens/$$ quando API).
+
+---
+
+## Vantagens específicas vs Claude/Cursor (escopo engenharia)
+- **Patch mínimo com provas**: diff enxuto + justificativa + métricas (sem conversa).
+- **Orquestração por risco/dependência**: ataca onde mais impacta, não “onde é mais fácil”.
+- **Aprendizagem por workspace**: memória episódica evita repetir bug local.
+- **Gates mensuráveis**: se não atinge SLI/SLO → recua automaticamente (**ADVICE-mode**) e gera episódio.
+- **Plug-and-play**: CLI/HTTP `{logs,files}→{diff,metrics}` + smoke offline.
+
+---
+
+## Anexos (resumo de políticas)
+
+### Escopo de pesquisa web (engenharia-only)
+**Pode pesquisar**: docs oficiais/APIs, repositórios e licenças, benchmarks/releases, segurança (CVEs/OWASP), ADRs/RFCs.
+**Não pesquisa**: conteúdos não-técnicos, finanças/mercado, opiniões gerais, dados sensíveis/paywalls, conselhos legais.
+
+### Garantias de execução
+- **Engenharia-only**; mudanças **mínimas e reversíveis**.
+- Citações obrigatórias quando houver pesquisa.
+- Circuit-breakers ativos; confiança baixa → **ADVICE** em vez de patch.
+
+---
+
+## Roadmap de sprints curtos (ordem sugerida)
+1) **Strategos v2** + integração ao grafo (fase 9).
+2) **Reranker n-best** (fase 9).
+3) **Memória episódica** (fase 9).
+4) **Forense + RAG CANON + Otimizador** (fase 10).
+5) **Pesquisa Vanguarda** (fase 11).
+6) **Governação & segurança** (fase 12).
+
+---
+
+# EOF
````

````diff

+# Pipeline — Fases 13–15 (Reranker • Memória Episódica • Strategos v2)
+
+> Continuação direta da pipeline existente. Estas fases **não alteram** o contrato da LLM: continuam a emitir **um único patch diff** validado pelos gates (validate → dry-run → lint/tests/build).
+> Todas as metas têm **critérios de saída mensuráveis** e **circuit-breakers** alinhados com a Torre.
+
+---
+
+## Fase 13 — Reranker por Execução (n-best)
+
+**Objetivo**: gerar **2–3 candidatos de patch** por pedido, **executar gates localmente** (lint/tests/build) e **selecionar automaticamente** o que fica **verde**. Ganho esperado: +3–7 p.p. em *success rate* e redução de regressões.
+
+### Escopo
+- Gerar até **K=3** candidatos com perfis de decodificação diferentes (ex.: `PATCH`, `PATCH_B`, `PATCH@low_top_p`).
+- Para cada candidato:
+  - Validar **formato** (diff unificado, paths seguros, tamanho ≤ gate).
+  - **Aplicar em árvore efémera** (sandbox) e correr:
+    - `lint` (eslint/ruff),
+    - `typecheck` (tsc/mypy),
+    - `tests` (pytest/jest),
+    - `build seco` (vite/tsc/pyproject).
+- **Política de seleção**:
+  1) Primeiro patch que **passa todos os gates**;
+  2) Se **>1** passa: escolher **menor `diff_size`**;
+  3) *Tie-breaker*: **menor TTG** (time-to-green).
+  4) Se **nenhum** passa → **ADVICE-mode** (sem aplicar).
+
+### Saídas (done = verificável)
+- [ ] Runner de n-best com **registo por candidato**: `{diff_size, ttg_ms, gates_passed, logs_resumo}`.
+- [ ] **Relatório** por pedido com comparação dos candidatos e **justificativa** do vencedor.
+- [ ] Métricas expostas: `n_best_win_rate`, `avg_candidates`, `selection_ttg_ms`, `selected_diff_size`, `discard_reasons`.
+
+### Gates / Circuit-breakers
+- **Gate sucesso**: `success_rate` ↑ **≥3 p.p.** vs. baseline local em 48h.
+- **Gate regressão**: `regressões/100 patches` ≤ **1**.
+- **CB tempo**: se `selection_ttg_ms` p95 > **+30%** vs. baseline, reduzir **K** (p.ex., de 3→2) automaticamente.
+
+### Notas de integração
+- Não altera API externa. O reranker vive **atrás** do endpoint/CLI e mantém **um único patch** como saída.
+- Usa o **sandbox** da Torre (validate→dry-run) e **não toca** em `.env`, `.ssh`, `*.pem`, `id_rsa`, `secrets.*`.
+
+---
+
+## Fase 14 — Memória Episódica por Workspace (sem PII)
+
+**Objetivo**: **aprender com erros recorrentes** no mesmo repositório/workspace para reduzir repetição e acelerar correções. Ganho esperado: −50–70% em reincidência de padrões simples (ex.: TS2304, import path).
+
+### Escopo
+- Armazenar **episódios** em `.torre/memory/episodes.jsonl` com:
+  - chaves **não-PII** (hash de repo, trilha de ficheiros relativa),
+  - **sinais**: erro/lint/build, stack curta, tech stack inferida (vite/next/pytest),
+  - **ação aplicada** (patch/ADVICE) e **outcome** (verde/falha).
+- **Learner** leve:
+  - Regras **if-this-then-that** idempotentes por padrão (ex.: *“TS2304 + src/components + vite → inserir import local”*).
+  - *Backoff*/confiança: só promover regra após **N≥3** confirmações com **0 regressões**.
+- **Aplica** sugestões **antes** da geração (como *priors*) e **depois** (como *auto-fix*), sempre sob gates.
+
+### Saídas (done = verificável)
+- [ ] Esquema de episódio versionado e **validador** (rejeita PII e campos fora de escopo).
+- [ ] **Learner** com políticas: promoção, *decay* de regras velhas, *backoff* após falha.
+- [ ] Métricas expostas: `repeat_error_rate`, `rules_promoted`, `rules_hit_rate`, `avoidance_saves`.
+
+### Gates / Circuit-breakers
+- **Gate repetição**: `repeat_error_rate` ↓ **≥50%** em 7 dias no workspace.
+- **Gate segurança**: 0 violações de escopo/paths; **todas** as regras são **idempotentes** (com prova simples).
+- **CB regras**: se `rules_hit_regression` > **0**, **despromover** regra e abrir **episode** de investigação.
+
+### Notas de integração
+- A memória é **local ao workspace** (por pasta `.torre/`), sob controlo do utilizador/admin.
+- Sem armazenamento de PII, *prompts* nem código sensível; apenas **sinais e hash**.
+
+---
+
+## Fase 15 — Strategos v2 (impacto × risco × custo) com Grafo de Imports
+
+**Objetivo**: **onde atacar primeiro** com base em **impacto**, **risco** e **custo**, apoiado pelo **grafo de dependências** do projeto. Ganho esperado: menos *thrash*, mais *patch verde* à primeira.
+
+### Escopo
+- **Modelo de pontuação**:
+  - **Impacto**: centralidade no grafo (in-degree/out-degree), superfícies públicas (exports), criticidade (módulos “core”).
+  - **Risco**: antecedentes de regressões, *hotspots* (churn), complexidade/cobertura de testes, *blast radius* (fan-out).
+  - **Custo**: linhas a tocar, dependências a re-construir, tempo de *build/tests* esperado.
+- **Plano**:
+  - Priorizar **build → types → tests → style**, filtrado por módulos com **maior (impacto×risco)/custo**.
+  - Emitir *playbook* curto por etapa com **critérios de saída** (verificáveis).
+- **Justificativa** no `report.md`:
+  - Top-N nós do grafo (com métricas), riscos, e porquê desta ordem (1–2 frases cada).
+
+### Saídas (done = verificável)
+- [ ] Serviço leve que expõe **grafo** (nós/arestas) com atributos (centralidades, churn, cobertura se disponível).
+- [ ] **Scorer** (impacto×risco×custo) com pesos configuráveis e *caps* por etapa.
+- [ ] Report do **plano** com links/IDs para nós do grafo tocados.
+
+### Gates / Circuit-breakers
+- **Gate eficiência**: `attempts_to_green` p50 ↓ **≥25%** vs. baseline; `TTG` p95 ↓ **≥20%**.
+- **Gate risco**: `regressões` ≤ **1%**; **0** violações de guardrails.
+- **CB confiança**: se *score* empata sem vencedor claro, cair para **Strategos v1** e **ADVICE** (sem patch invasivo).
+
+### Notas de integração
+- Consome o grafo de **Omni-Contexto**; se indisponível, degrada com heurísticas locais (ex.: fan-out aproximado).
+- Pesos por tipo de projeto (web, lib, backend) controlados por **config** do workspace.
+
+---
+
+## Métricas Comuns (acrescentadas aos dashboards)
+
+- **Reranker**: `n_best_win_rate`, `selected_diff_size`, `selection_ttg_ms`, `discard_reasons`.
+- **Memória**: `repeat_error_rate`, `rules_promoted`, `rules_hit_rate`, `rules_hit_regression`.
+- **Strategos v2**: `attempts_to_green`, `prio_win_rate` (quando o 1º alvo escolhido leva ao *green*), `ttg_delta`.
+
+> **Regra de ouro**: se **qualquer** fase nova reduzir `success_rate` global < **90%** em 30 min ou aumentar `violations(sec)` > **0**, **ativar ADVICE-mode** e abrir **incident/episode** para reversão/análise.
+
+---
+
+## Comandos & Integração (sugestões operacionais)
+
+> Os comandos exatos podem variar; mantêm-se como **referência** para automação na Torre.
+
+### Reranker (K candidatos)
+```bash
+# gerar K candidatos (perfis diferentes) e avaliar em sandbox
+python3 -m torre-llm.llm.cli < input.json > .torre/out/candidate_1.json
+LLM_PROFILE=PATCH_B python3 -m torre-llm.llm.cli < input.json > .torre/out/candidate_2.json
+LLM_TOP_P=0.15 LLM_TEMPERATURE=0.05 python3 -m torre-llm.llm.cli < input.json > .torre/out/candidate_3.json
+
+# selecionar vencedor (lint/tests/build) → diff final
+python3 -m torre-llm.tools.select_rerank --in .torre/out/ --out .torre/out/selected.diff
+```
+
+### Memória Episódica (episódios)
+```bash
+# anexar episódio (sem PII) após cada execução
+python3 -m torre-llm.tools.episodes.append --file .torre/memory/episodes.jsonl --data run_meta.json
+
+# treinar/promover regras seguras
+python3 -m torre-llm.tools.episodes.learn --from .torre/memory/episodes.jsonl --to .torre/memory/rules.json
+```
+
+### Strategos v2 (priorização)
+```bash
+# gerar grafo e pontuar módulos/etapas
+python3 -m torre-llm.tools.graph.build --root . --out .torre/graph.json
+python3 -m torre-llm.tools.graph.score --graph .torre/graph.json --out .torre/plan.json
+```
+
+---
+
+## Riscos & Mitigações
+
+- **Tempo extra por n-best** → Mitigar com **K adaptativo** (2↔3) e cache de *build/tests*.
+- **Memória enviesada** → Aprovação automática só após **N** confirmações; *decay* de regras antigas; despromoção ao 1º sinal de regressão.
+- **Priorização enganosa** (grafo incompleto) → *Fallback* para Strategos v1; pesos conservadores; evidências no report.
+
+---
+
+## Critérios de Fecho das Fases
+
+- **F13 (Reranker)**: `success_rate` global **+≥3 p.p.**, `regressões/100` ≤ **1**, `selection_ttg_ms` p95 ≤ **+30%** do baseline.
+- **F14 (Memória)**: `repeat_error_rate` **−≥50%**, `rules_hit_regression` = **0**, regras idempotentes auditadas.
+- **F15 (Strategos v2)**: `attempts_to_green` p50 **−≥25%**, `TTG` p95 **−≥20%**, **0** novas violações.
+
+> Quando os três gates estiverem **verdes por 7 dias**, promover estas capacidades a **default** no workspace.
````

## Fase 16 — Contrato I/O Fechado + Observabilidade

+**Objetivo:** contrato JSON esquemado e rastreabilidade end-to-end.

- +**Entregas:**
  +- `llm/contracts/input.schema.json` e `llm/contracts/output.schema.json` publicados.
  +- `trace_id` por pedido + logs estruturados + export CSV/JSON.
  +- Dashboard inclui `trace_id` e custo (tokens) por patch.
- +**Gate:** 100% dos pedidos validam contra schema; 0% de eventos sem `trace_id`.
- +## Fase 17 — Rollback on Red + Sandbox & Quotas +**Objetivo:** segurança operacional na aplicação de patches.
- +**Entregas:**
  +- Política “Rollback on red”: se pós-apply qualquer gate falhar ⇒ `git revert` automático + bloqueio.
  +- Sandbox por workspace: CPU/mem/time quotas, FS allowlist, **rede off** por padrão.
  +- Rate-limit/WAF no endpoint da LLM.
- +**Gate:** 0 incidentes sem rollback automático; jobs isolados por cgroup/namespace.
- +## Fase 18 — Golden Set + Red-Team + PR Gate + Impact Analysis + Memory Policy +**Objetivo:** fechar o ciclo de regressão e segurança.
- +**Entregas:**
  +- **Golden set** (50–100 tarefas reais TS/React/FastAPI/Vite) com cron diário de KPIs.
  +- **Red-team seeds** (ex.: `.env`, symlink, traversal) → deny-merge se dispararem.
  +- **PR Gate GitHub Actions**: merge apenas com SLOs verdes.
  +- **Impact analysis**: roda apenas testes afetados + smoke de vizinhança; cobertura diferencial mínima.
  +- **MEMORY_POLICY.md**: política formal de persistência (sem PII/código bruto).
- +**Gate:** `success_rate(golden) ≥ 95%`, `regressões/100 patches ≤ 1`, `violations(sec)=0`.
- +---
- +### Micro-naming (aplicado)
  +- “SMOKE mode” → **Healthcheck**  
  +- “Advice mode” → **Advisory (read-only)**
- +## Fase 19 — Cursor e vscode
  Extensão Cursor: Interface entre Cursor e Torre
  Protocolo: Como Cursor envia context (files, errors)
  Response Handling: Como Cursor aplica os patches
  Real-time: Integração com o editor em tempo real

  +## Fase 20 —

1. Adapters de provedores
   Interface única Provider.generate(req) -> resp com drivers:

openai/_ (meu “estilo”), anthropic/_ (Claude), google/\* (Gemini),

local/\* (vLLM/Ollama/Qt-7B, etc).
Respeita PII/data policy (F14) e secrets (F12) por rota.

2. Router + Perfis (chave: não é “quem é melhor?”, é “quem é melhor nesta tarefa”)

Regra simples e auditável (começo):

build/types ⇒ Claude (contextão) ↔ GPT (precisão/estrutura).

tests/estilo/documentação ⇒ GPT/professor.

multimodal/assets ⇒ Gemini.

refactors curtos/custo baixo ⇒ local 7B.

Sinaliza no request: meta.router_decision = {provider, reason}.

3. n-best entre provedores (reuso da F13)
   Cada provedor vira mais um candidato; o teu Execution Reranker já mede: formato → gates (lint/types/tests/build) → seleciona verde → tie-break por diff_size/TTG. Se nenhum passa, cai para Advisory-mode (F17).

4. Telemetria e governance

Estende trace (F16): provider, tokens_in/out, win_rate.

Quotas por provedor (F17): max_rpm, daily_budget_usd.

Política por repositório: providers.yaml (quem pode ver código onde)
