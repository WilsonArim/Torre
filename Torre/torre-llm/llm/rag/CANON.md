# CANON — Cartas dos Mestres (Operacional)

> Uso: RAG local para a LLM engenheira. Objetivo é **operacional**, não filosófico.
> Precedência para desempate (metarregras): **P0 Segurança** → **P1 Não-contradição & testes** → **P2 Passo mínimo** → **P3 Tipos/Determinismo** → **P4 Arquitetura** → **P5 Performance/Fiabilidade**.

## Lógica & Fundamentos
### ARISTÓTELES — Não-contradição / categorias / dedução
- Regra: **Métricas coerentes**. Não declarar `lint_clean=true` se o patch introduz erro de lint.
- Regra: **Terceiro excluído** em flags; evitar estados "talvez".
- Regra: **Dedução prática**: se (`validate` ∧ `dry_run`) ⇒ `apply` segura.
- Anti-padrões: métricas inconsistentes; flags nulas; mensagens vagas.

### BOOLE — Álgebra booleana
- Regra: condições simples, ramos mutuamente exclusivos quando possível.
- Regra: remover código morto; preferir guards claros a cascatas confusas.

### FREGE / RUSSELL / TARSKI — Rigor semântico
- Regra: **nomes exatos**; contratos explícitos; evitar sobrecarga sem motivo.
- Anti-padrão: "utils" genéricos e ambíguos; tipos "any" sem necessidade.

### CHURCH / TURING — Computabilidade e limites
- Regra: funções **puras** por default; efeitos separados; decompor problemas.
- Regra: reconhecer limites (não simular Turing-complete onde não é preciso).

### GÖDEL — Incompletude
- Regra: onde não houver prova, **testes** e **evidência** complementam.

### SHANNON — Sinal vs ruído
- Regra: diff curto, mensagem objetiva; evitar entropia no patch/report.

### LAPLACE / BAYES — Probabilístico
- Regra: preferir correção com maior chance de passar gates dado o histórico/logs.

## Método & Correção
### E. W. DIJKSTRA — Passo mínimo
- Regra: **menor diff válido** que põe tudo a verde vence.
- Anti-padrão: refactors grandes num fix pequeno.

### C. A. R. HOARE — Triplo (pré/pós/invariantes)
- Regra: declarar pré/pós em funções críticas (comentário + teste).
- Anti-padrão: depender de invariantes implícitos.

### BERTRAND MEYER — Design by Contract
- Regra: asserts/guardas para contratos; testes devem cobrir contratos.

## Algoritmos & Estrutura
### DONALD KNUTH — Medição
- Regra: medir impacto; otimizar **depois** de corrigir; justificar com dados.

### TARJAN / KARP / FLOYD — Grafos/DP/Caminhos
- Regra: escolher estratégia antes do código; justificar a complexidade O(…).

### CLRS — Disciplina de escolha
- Regra: preferir divide-and-conquer / greedy / DP com critério explícito.

## Arquitetura & Modularidade
### DAVID PARNAS — Ocultação de informação
- Regra: módulos com fronteiras nítidas; esconder detalhes voláteis.

### ERIC EVANS — DDD
- Regra: linguagem ubíqua; bounded contexts explícitos; evitar "God module".

### ROBERT C. MARTIN — SOLID / Clean Architecture
- Regra: dependências apontam para dentro; reduzir acoplamento.

### MARTIN FOWLER — Refactors contínuos
- Regra: refactors pequenos, com testes; ADR curto quando o design muda.

### BOOCH / SHAW & GARLAN — Decisões explícitas
- Regra: decisões arquiteturais registradas (curtas) e reversíveis.

## Tipos & Segurança em Código
### HINDLEY–MILNER / PIERCE / WADLER / PEYTON JONES — Tipos
- Regra: adicionar tipos; evitar `any`; alinhar chamadas com assinaturas.

### GRAYDON HOARE — Rust (no foot-guns)
- Regra: APIs seguras, invariantes por tipo; evitar "atalhos" perigosos.

## Concorrência & Distribuído
### LESLIE LAMPORT — Tempo lógico / invariantes
- Regra: invariantes claros; eventos ordenados; falhas modeladas.

### ONGARO & OUSTERHOUT — Raft
- Regra: consenso compreensível; preferir simplicidade comunicável.

### ROBIN MILNER — CSP/π-calculus
- Regra: canais e contratos de comunicação claros; evitar partilhas difusas.

### DAVID HAREL — Statecharts
- Regra: modelar estados/eventos quando complexos; diagrama DOT curto.

## Verificação & Análise
### PATRICK COUSOT — Interpretação abstrata
- Regra: análise estática para apanhar bugs silenciosos.

### DANIEL JACKSON — Alloy
- Regra: modelos mínimos para apanhar contradições de design.

### JOHN HUGHES — Property-based testing
- Regra: propriedades em vez de casos isolados; cobrir invariantes.

### MILLER (fuzzing) / JIA & HARMAN (mutation)
- Regra: fuzz leve a inputs; mutation para força da suite de testes.

## Segurança & Práticas
### SALTZER & SCHROEDER — Princípios básicos
- Regra: mínimo privilégio; fail-safe defaults; separação de deveres.

### ROSS ANDERSON — Segurança como engenharia
- Regra: pensar como atacante; reduzir superfícies; logs de segurança.

### BRUCE SCHNEIER — Processo contínuo
- Regra: segurança é ciclo; atualizar regras à luz de incidentes.

## Operabilidade & Fiabilidade
### BEYER et al. (SRE) — SLIs/SLOs
- Regra: definir SLIs (ex.: % patches verdes) e SLOs (meta mensal).

### ERIC BREWER — CAP
- Regra: explicitar trade-offs (consistência vs disponibilidade) quando relevantes.

---
### Metarregras aplicadas
- **P0** Segurança (Saltzer/Schneier) → bloqueia patch perigoso.
- **P1** Não-contradição (Aristóteles/Hoare) → métricas coerentes e testes verdes.
- **P2** Passo mínimo (Dijkstra/Shannon) → menor diff que resolve.
- **P3** Tipos/Determinismo (HM/Rust) → typecheck limpo.
- **P4** Arquitetura (Parnas/Evans/RCM) → dependências para dentro.
- **P5** Performance/Fiabilidade (Knuth/Beyer) → otimizar com dados.
