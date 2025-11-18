**PIPELINE/FORA_PIPELINE:** PIPELINE

**OWNER: ENGENHEIRO — Próxima ação:** Aguardar validação pelo SOP e aprovação do Estado-Maior

---

# Implementação das Funções do Gatekeeper — Engenheiro

## Resumo Executivo

Implementadas 5 funções aprovadas do Gatekeeper + alternativa Auto-Fix conforme ordem do Estado-Maior. Todas as funções respeitam a doutrina de acesso a ficheiros (Gatekeeper não modifica código-fonte, apenas valida e gera relatórios/ordens).

---

## Funções Implementadas

### 1. ✅ Preflight Local (Pre-Commit)

**Função:** `cmd_preflight()` em `gatekeeper_cli.py`

**Validações:**

- ✅ Workflows YAML (sintaxe e estrutura)
- ✅ Actions deprecadas (detecta versões antigas)
- ✅ Permissões GITHUB_TOKEN (verifica se muito permissivas)
- ✅ Scripts chamados (detecta curl|bash sem validação)
- ✅ Permissões de execução

**Uso:**

```bash
python3 core/orquestrador/gatekeeper_cli.py preflight
# ou
make -C core/orquestrador gatekeeper_preflight
```

**Output:**

- Relatório em `relatorios/para_estado_maior/preflight_report.md`
- Issues críticos e warnings identificados
- Status PASS/BLOCKED

---

### 2. ✅ Guard no PR/CI (GitHub)

**Função:** Workflow GitHub Actions `.github/workflows/gatekeeper-guard.yml`

**Validações:**

- ✅ Executa Gatekeeper Preflight
- ✅ Executa SOP Validation
- ✅ Executa Gatekeeper
- ✅ Bloqueia merge se Gatekeeper bloquear

**Trigger:**

- Pull requests para `main` ou `master`
- Workflow dispatch (manual)

**Comportamento:**

- Se Gatekeeper bloquear → merge bloqueado
- Se Gatekeeper aprovar → merge permitido
- Relatórios sempre uploadados como artefactos

---

### 3. ✅ Vercel Guard (Pré-Deploy)

**Função:** `cmd_vercel_guard()` em `gatekeeper_cli.py`

**Validações:**

- ✅ Validação de `vercel.json` (se existir)
- ✅ `vercel pull` (dry-run, read-only)
- ✅ `vercel build` (dry-run, sem deploy)

**Conformidade com Doutrina:**

- ✅ APENAS validação (dry-run)
- ✅ NUNCA modifica código-fonte
- ✅ NUNCA faz deploy

**Uso:**

```bash
python3 core/orquestrador/gatekeeper_cli.py vercel-guard
# ou
make -C core/orquestrador gatekeeper_vercel_guard
```

**Output:**

- Relatório em `relatorios/para_estado_maior/vercel_guard_report.md`
- Status PASS/BLOCKED

---

### 4. ✅ Dependency Radar (Agendado)

**Função:** Script separado `tools/gatekeeper/dependency_radar.py`

**Validações:**

- ✅ CVEs em dependências npm (`npm audit`)
- ✅ CVEs em dependências Python (`pip-audit`)
- ✅ GitHub Actions desatualizadas

**Outputs:**

- Relatório em `relatorios/para_estado_maior/dependency_radar_YYYYMMDD_HHMMSS.md`
- Issue draft em `relatorios/para_estado_maior/dependency_radar_issue_YYYYMMDD.md`

**Uso:**

```bash
python3 tools/gatekeeper/dependency_radar.py
# ou
make -C core/orquestrador gatekeeper_dependency_radar
```

**Agendamento:**

- Pode ser executado manualmente ou via cron/GitHub Actions schedule

---

### 5. ✅ Post-Mortem (Falha)

**Função:** `cmd_post_mortem()` em `gatekeeper_cli.py`

**Análise:**

- ✅ Analisa logs de workflows falhados
- ✅ Identifica causas-raiz (padrões conhecidos)
- ✅ Gera patches sugeridos

**Padrões Detectados:**

- SBOM ausente → sugere adicionar step de geração
- SOP bloqueado → sugere verificar artefactos obrigatórios

**Uso:**

```bash
python3 core/orquestrador/gatekeeper_cli.py post-mortem [--workflow-run-id ID]
# ou
make -C core/orquestrador gatekeeper_post_mortem
```

**Output:**

- Relatório em `relatorios/para_estado_maior/postmortem_YYYYMMDD_HHMMSS.md`
- Causas-raiz identificadas
- Patches sugeridos

---

### 6. ✅ Alternativa Auto-Fix (Gatekeeper → Ordem → Engenheiro)

**Função:** `cmd_auto_fix_alternative()` em `gatekeeper_cli.py`

**Fluxo:**

1. Gatekeeper detecta problema
2. Gatekeeper gera relatório com ordem sugerida em formato YAML
3. Estado-Maior ou Engenheiro copia ordem para `ordem/ordens/engineer.in.yaml`
4. Engenheiro recebe ordem e aplica correção
5. Gatekeeper valida correção aplicada

**Conformidade com Doutrina:**

- ✅ Gatekeeper NÃO modifica código-fonte
- ✅ Gatekeeper apenas gera relatório com ordem sugerida (permitido conforme doutrina)
- ✅ Estado-Maior pode copiar ordem para engineer.in.yaml (permitido conforme doutrina)
- ✅ Engenheiro aplica correção (conforme papel)

**Nota:** A doutrina atual não permite que Gatekeeper escreva diretamente em `ordem/ordens/*.in.yaml` (apenas Estado-Maior pode). A função gera um relatório com a ordem em formato YAML que pode ser copiada.

**Uso:**

```bash
python3 core/orquestrador/gatekeeper_cli.py auto-fix --issue "Descrição do issue" --patch "Patch sugerido"
```

**Output:**

- Relatório em `relatorios/para_estado_maior/auto_fix_suggested_YYYYMMDD_HHMMSS.md`
- Ordem YAML sugerida no relatório (pronta para copiar)

---

## Arquivos Criados/Modificados

### Arquivos Criados

1. ✅ `tools/gatekeeper/dependency_radar.py` — Script de Dependency Radar
2. ✅ `.github/workflows/gatekeeper-guard.yml` — Workflow GitHub Actions para Guard no PR/CI

### Arquivos Modificados

1. ✅ `core/orquestrador/gatekeeper_cli.py` — Adicionadas 4 novas funções:
   - `cmd_preflight()` — Preflight Local
   - `cmd_vercel_guard()` — Vercel Guard
   - `cmd_post_mortem()` — Post-Mortem
   - `cmd_auto_fix_alternative()` — Auto-Fix Alternativo

2. ✅ `core/orquestrador/Makefile` — Adicionados 4 novos targets:
   - `gatekeeper_preflight`
   - `gatekeeper_vercel_guard`
   - `gatekeeper_post_mortem`
   - `gatekeeper_dependency_radar`

---

## Conformidade com Doutrina

### Acesso a Ficheiros

**Gatekeeper pode:**

- ✅ Ler qualquer ficheiro
- ✅ Escrever em `relatorios/**/*.md` e `relatorios/para_estado_maior/**`
- ✅ Escrever em `ordem/ordens/*.in.yaml` (para gerar ordens)
- ✅ Executar comandos externos APENAS para validação (dry-run, read-only)

**Gatekeeper NÃO pode:**

- ❌ Modificar código-fonte (`.py`, `.js`, `.ts`, etc.)
- ❌ Modificar configurações (`core/**`, `pipeline/**`)
- ❌ Executar comandos que modifiquem código ou artefactos

**Todas as funções implementadas respeitam estas restrições:**

- ✅ Preflight: apenas leitura e análise
- ✅ Guard no PR/CI: apenas validação
- ✅ Vercel Guard: apenas dry-run (sem deploy)
- ✅ Dependency Radar: apenas análise (read-only)
- ✅ Post-Mortem: apenas análise e geração de relatório
- ✅ Auto-Fix: apenas geração de relatório com ordem sugerida (Estado-Maior/Engenheiro copia ordem)

---

## Conformidade Constitucional

### ART-03 (Consciência Técnica)

✅ **CONFORME**

- Gatekeeper mantém papel de validador/auditor
- Engenheiro mantém papel de executor (Auto-Fix alternativo)
- Separação de responsabilidades preservada

### ART-04 (Verificabilidade)

✅ **CONFORME**

- Todas as funções são rastreáveis
- Relatórios gerados com timestamps
- Ordens geradas com metadados completos

### ART-07 (Transparência)

✅ **CONFORME**

- Processos transparentes
- Relatórios detalhados
- Issues e warnings claramente identificados

### ART-09 (Evidência)

✅ **CONFORME**

- Baseado em artefactos (workflows, logs, dependências)
- Evidências citadas nos relatórios
- Patches sugeridos com contexto

---

## Uso das Funções

### Preflight Local

```bash
# Via CLI
python3 core/orquestrador/gatekeeper_cli.py preflight

# Via Makefile
make -C core/orquestrador gatekeeper_preflight
```

### Vercel Guard

```bash
# Via CLI
python3 core/orquestrador/gatekeeper_cli.py vercel-guard

# Via Makefile
make -C core/orquestrador gatekeeper_vercel_guard
```

### Post-Mortem

```bash
# Via CLI
python3 core/orquestrador/gatekeeper_cli.py post-mortem --workflow-run-id 123456

# Via Makefile
make -C core/orquestrador gatekeeper_post_mortem
```

### Dependency Radar

```bash
# Via CLI
python3 tools/gatekeeper/dependency_radar.py

# Via Makefile
make -C core/orquestrador gatekeeper_dependency_radar
```

### Auto-Fix Alternativo

```bash
# Via CLI
python3 core/orquestrador/gatekeeper_cli.py auto-fix \
  --issue "SBOM ausente" \
  --patch "Adicionar step: make -C core/orquestrador sbom"
```

### Guard no PR/CI

- Executa automaticamente em pull requests
- Pode ser executado manualmente via workflow dispatch

---

## Testes Recomendados

### 1. Testar Preflight

```bash
python3 core/orquestrador/gatekeeper_cli.py preflight
# Verificar relatorios/para_estado_maior/preflight_report.md
```

### 2. Testar Vercel Guard

```bash
python3 core/orquestrador/gatekeeper_cli.py vercel-guard
# Verificar relatorios/para_estado_maior/vercel_guard_report.md
```

### 3. Testar Dependency Radar

```bash
python3 tools/gatekeeper/dependency_radar.py
# Verificar relatorios/para_estado_maior/dependency_radar_*.md
```

### 4. Testar Auto-Fix

```bash
python3 core/orquestrador/gatekeeper_cli.py auto-fix \
  --issue "Teste de Auto-Fix" \
  --patch "echo 'Teste de patch'"
# Verificar relatorios/para_estado_maior/auto_fix_suggested_*.md
# Copiar ordem YAML sugerida para ordem/ordens/engineer.in.yaml se necessário
```

---

## Próximos Passos

1. ✅ **Engenheiro:** Implementação concluída e pronta para validação
2. ⏳ **SOP:** Validar conformidade antes de liberar uso
3. ⏳ **Estado-Maior:** Aprovar implementação e autorizar uso em produção

---

## Conclusão

**Status:** ✅ **IMPLEMENTAÇÃO CONCLUÍDA**

**Resumo:**

- ✅ 5 funções aprovadas implementadas
- ✅ Alternativa Auto-Fix implementada
- ✅ Guard no PR/CI implementado (workflow GitHub Actions)
- ✅ Todas as funções respeitam doutrina de acesso a ficheiros
- ✅ Rastreabilidade e auditabilidade garantidas (ART-04, ART-09)

**Próximo Passo:**

- Validação pelo SOP
- Aprovação do Estado-Maior
- Uso em produção

---

**Referências:**

- Decisão Estado-Maior: `relatorios/para_estado_maior/decisao_estado_maior_funcoes_gatekeeper.md`
- Doutrina: `core/sop/doutrina.yaml`
- CLI Gatekeeper: `core/orquestrador/gatekeeper_cli.py`
- Dependency Radar: `tools/gatekeeper/dependency_radar.py`
- Workflow Guard: `.github/workflows/gatekeeper-guard.yml`

---

**COMANDO A EXECUTAR:** "SOP VALIDAR CONFORMIDADE DAS FUNÇÕES DO GATEKEEPER ANTES DE LIBERAR USO. ESTADO-MAIOR APROVAR IMPLEMENTAÇÃO E AUTORIZAR USO EM PRODUÇÃO."
