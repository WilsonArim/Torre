perfeito — aqui vai o patch “2-em-1”: cria o ficheiro **Blocos Partidos & Proteção de Dados** e **insere o link no README**.

> Cola no Cursor como _Apply Patch_. Se a segunda parte (README) não aplicar por diferenças de formatação, deixo logo abaixo um “plano B” de 1 linha para acrescentar o link.

---

### Patch (pronto a colar)

````diff
*** Begin Patch
*** Add File: .torre/docs/BLOCOS_PARTIDOS_E_PROTECAO_DE_DADOS.md
+# Blocos Partidos & Proteção de Dados — Base do Castelo
+
+> Como a Torre aplica mudanças reais com **risco mínimo**, **auditoria total** e **respeito por dados**.
+
+## 0) Objetivo (em 1 linha)
+Aplicar patches em repositórios reais **sem partir nada** e **sem expor dados**, usando limites técnicos fortes, validações antes de tocar no repo, e trilho de auditoria completo.
+
+---
+
+## 1) Princípios que regem tudo
+- **Menor privilégio**: a Torre só vê a **raiz de projetos** que escolhes; nada fora.
+- **Passos pequenos e reversíveis**: tudo é `diff` unificado → dá para *dry-run*, *review* e *reverter*.
+- **Validação obrigatória**: *validator* + limites + *dry-run* antes de aplicar.
+- **Humano no circuito**: operações destrutivas pedem confirmação (ou PR-only).
+- **Privacidade por defeito**: minimizar, redigir segredos/PII, e guardar o mínimo de logs.
+- **Transparência**: cada ação sai registada em `.torre/history`.
+
+---
+
+## 2) Âmbito & Limites de Acesso
+- **Raiz de trabalho**: definido por ti ao registar o workspace.
+  Caminhos absolutos e `../` são **bloqueados**.
+- **Egress de rede**: por defeito, **OFF** (modo offline). Só sai para a internet em endpoints **explicitamente** permitidos.
+- **LLMs externas**: só com consentimento e **redação automática** de segredos/PII.
+- **Workflows/CI**: só dentro de pastas permitidas; ficheiros sensíveis são *hard-deny*.
+
+---
+
+## 3) Guardião de Patches (o “porteiro”)
+**O que valida antes de qualquer apply:**
+- **Estrutura do diff**: unificado, linhas de contexto, sem binários escondidos.
+- **Caminhos**: dentro do workspace, sem absolutos, sem `..`.
+- **Tamanho**: limites de bytes/ficheiros (configurável).
+- **Ficheiros proibidos (hard-deny)**: `.env`, `.ssh/**`, `id_rsa`, `*.pem`, `*.key`, `secrets.*`, `*token*`, `*credential*`, `*passwd*`, etc.
+  _Hard-deny = ninguém consegue forçar._
+- **Dry-run**: aplica num modo simulado; se falhar → **não aplica**.
+
+---
+
+## 4) Fluxo Seguro (end-to-end)
+1. **Ingestão**: recebes patch do engenheiro (LLM/humano) → Torre normaliza.
+2. **Validação**: Guardião analisa (estrutura, caminhos, hard-deny, tamanho).
+3. **Dry-run**: simula aplicação; corre `lint/tests/build` no *sandbox*.
+4. **Aplicação**: preferencialmente **PR-only** (cria branch/PR).
+   (Write direto a `main` pode ser desativado por política.)
+5. **Auditoria**: evento gravado com métricas (tempo, ficheiros, resultado).
+6. **Rollback**: em caso de falha pós-merge, reverte o commit/PR.
+
+---
+
+## 5) Riscos → Antídotos (mapa rápido)
+
+| Risco | Exemplo | Antídoto técnico | Antídoto processual |
+|---|---|---|---|
+| **Partir o build** | `tsc`/`pytest` falha | Dry-run + `tsc/pytest/eslint/vite build` **antes** de aplicar | PR-only + obrigar aprovação |
+| **Expor segredo** | `.env` no diff | *Hard-deny*, scanner de segredos, **redação** | Política de commit e revisão |
+| **Violação RGPD** | PII enviada para LLM externa | Minimização, redacção, **consentimento explícito por feature** | DPA + registo de finalidades |
+| **Path traversal** | `../../etc/passwd` | Normalização de caminho + bloqueio | N/A |
+| **CI/Workflows perigosos** | `.github/workflows` malicioso | Allowlist por pasta; bloquear execução por defeito | Política “dois cliques” para áreas críticas |
+| **Downtime pós-merge** | script apaga assets | PR-only + staging; rollback rápido | Processo de aprovação com checklist |
+
+---
+
+## 6) Definições “Enterprise” (ativar já)
+- **PR-only** por defeito (sem write direto a `main`).
+- **Validação obrigatória** (não desativável).
+- **Redação de segredos/PII** sempre ON.
+- **Assinatura de commits** (GPG/SSH) + `Signed-off-by`.
+- **Runner sandbox** (limites de CPU/RAM/tempo/rede).
+- **Políticas por pasta** (`.torre/policy.yml`): allow/deny globais, áreas críticas com 2 aprovações.
+- **Logs com retenção curta** (ex.: 14 dias) e sem PII por defeito.
+
+---
+
+## 7) Variáveis & Política (exemplos)
+**Ambiente (defaults seguros):**
+```bash
+TORRE_AUTH_MODE=required
+TORRE_PR_ONLY=true
+TORRE_OFFLINE_DEFAULT=true
+TORRE_REDACT_SECRETS=true
+TORRE_POLICY_PATH=.torre/policy.yml
+TORRE_LOG_RETENTION_DAYS=14
+TORRE_NETWORK_EGRESS=deny   # deny | allowlist
+```
+
+**`.torre/policy.yml` (exemplo)**
+```yaml
+version: 1
+allow_write:
+  - "src/**"
+  - "api/**"
+  - "tests/**"
+deny_write:
+  - ".env"
+  - ".ssh/**"
+  - "**/*.pem"
+  - "**/*.key"
+  - "**/secrets.*"
+critical_paths:
+  - ".github/workflows/**"
+  - "infra/**"
+  - "deploy/**"
+require_review:
+  critical_paths: 2
+apply_mode:
+  default: "pr_only"
+egress:
+  default: "deny"
+  allowlist:
+    - "https://api.github.com"
+    - "https://registry.npmjs.org"
+```
+
+---
+
+## 8) SOPs (procedimentos simples)
+
+### 8.1 Onboarding de Repositório
+1) Criar pasta raiz do workspace.
+2) `policy.yml` com allow/deny.
+3) Ativar `PR-only` + assinatura de commits.
+4) Correr **haystack scan** (segredos, conflitos, CRLF, binários).
+5) Guardar baseline de métricas.
+
+### 8.2 Antes de aplicar qualquer patch
+- Validar diff (guardião) → **OK**?
+- Correr `lint/tests/build` em *dry-run* → **OK**?
+- Áreas críticas? → pedir aprovação dupla.
+- Criar **PR** com escopo pequeno e descrição objetiva.
+
+### 8.3 Depois de aplicar
+- Atualizar **pipeline_state** (etapa concluída).
+- Guardar métricas: `apply_clean`, `tests_pass`, `lint_clean`, `perf_p95`.
+- Registrar em `.torre/history`.
+
+### 8.4 Incidentes (resumo do playbook)
+- **Build partiu**: rollback PR/commit → abrir issue com log → hotfix via patch mínimo.
+- **Segredo exposto**: revogar chave → rodar secret scan → pós-mortem com causa-raiz.
+- **RGPD – direito do titular**: localizar artefactos, apagar/anonimizar, responder no prazo legal, registar.
+
+---
+
+## 9) Proteção de Dados (RGPD) — “o essencial”
+- **Minimização**: só processamos o necessário para gerar/validar patches.
+- **Base legal**: execução do serviço solicitado (contratual) + legítimo interesse (segurança/qualidade), quando aplicável.
+- **Consentimento explícito**: para envio de artefactos a LLMs externas.
+- **Direitos**: acesso/retificação/apagamento/portabilidade/oposição — processo documentado.
+- **Retenção**: logs mínimos e por tempo curto (ex.: 14 dias, configurável).
+- **Sub-processadores**: listados e contratualizados (DPA).
+- **Registos**: `.torre/history` + export de auditoria.
+
+> Nota: isto é **ponto de partida técnico**. Para produção, ter **DPA**, política de privacidade e checklist de segurança assinados.
+
+---
+
+## 10) Auditoria & Logs
+- **Evento por operação**: quem, quando, o quê, resultado, métricas.
+- **Sem PII por defeito**; hash para correlacionar sem identificar.
+- **Export on-demand** (ZIP assinado) para auditorias externas.
+
+---
+
+## 11) Segurança Operacional
+- **Sandbox**: limites de CPU/RAM/tempo; rede desligada salvo allowlist.
+- **Kill-switch**: “parar aplicações” e “modo leitura” imediatos.
+- **Assinatura**: commits, tags e artefactos assinados.
+
+---
+
+## 12) Diferença face ao mercado
+- A maioria **sugere** (chat); nós **aplicamos** com segurança e rasto.
+- Tudo é **medido e reversível**: `diff → dry-run → PR → métricas`.
+- **Privacy-first** por design: escopo limitado, redacção, consentimento, retenção mínima.
+
+---
+
+## 13) Checklists rápidas
+
+**Novo repo**
+- [ ] Definir raiz e `policy.yml`
+- [ ] Ativar PR-only + assinatura
+- [ ] Haystack scan sem segredos
+- [ ] Baseline de lint/tests/perf
+
+**Antes de aplicar**
+- [ ] Guardião OK
+- [ ] Dry-run OK (lint/tests/build)
+- [ ] Áreas críticas aprovadas
+- [ ] PR criado (pequeno, reversível)
+
+**Após aplicar**
+- [ ] Pipeline atualizada
+- [ ] Métricas guardadas
+- [ ] Logs/auditoria OK
+
+---
+
+## 14) Anexos úteis
+
+**Comandos úteis (exemplo)**
+```bash
+# validar
+curl -X POST :8765/workspaces/default/patch/validate -d '{"diff":"..."}' -H 'Content-Type: application/json'
+
+# dry-run
+curl -X POST :8765/workspaces/default/reports/ingest?mode=dry_run -H 'Content-Type: text/plain' --data-binary @report.md
+
+# aplicar via endpoint seguro
+curl -X POST :8765/workspaces/default/patch/apply_safe -d '{"diff":"..."}' -H 'Content-Type: application/json'
+```
+
+**Hard-deny (resumo)**
+```
+.env, .ssh/**, id_rsa, *.pem, *.key, secrets.*, *token*, *credential*, *passwd*
+```
+
+---
+
+**Em 1 frase final:**
+A Torre torna **aplicar** tão seguro quanto **sugerir** — com limites fortes, validação obrigatória e respeito por dados — e dá-te sempre um caminho de **backout** se algo fugir do plano.
+
*** End Patch
````

```diff
*** Begin Patch
*** Update File: README.md
@@
+## Documentação — Segurança & Dados
+
+- [Blocos Partidos & Proteção de Dados](.torre/docs/BLOCOS_PARTIDOS_E_PROTECAO_DE_DADOS.md)
+
*** End Patch
```

---

### Plano B (se o patch do README não aplicar)

Corre esta 1-linha no terminal, que **apenas acrescenta** o bloco ao fim do `README.md`:

```bash
printf "\n## Documentação — Segurança & Dados\n\n- [Blocos Partidos & Proteção de Dados](.torre/docs/BLOCOS_PARTIDOS_E_PROTECAO_DE_DADOS.md)\n" >> README.md
```

Queres que eu também ponha este documento linkado no **menu da UI** (por exemplo, em “Ajuda / Segurança” e na página **Definições → Privacidade**)?
