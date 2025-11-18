# Relatório SOP — Ajuste da Doutrina de Acesso (Comandos Externos)

**PIPELINE/FORA_PIPELINE:** FORA_PIPELINE

**OWNER: SOP — Próxima ação:** Ajuste da doutrina concluído — Gatekeeper pode executar comandos externos para validação

**Data:** 2025-11-02  
**Agente:** SOP v3.0  
**Ordem:** `sop-ajustar-doutrina-comandos-externos-2025-11-02`  
**Status:** ✅ CONCLUÍDO

---

## Resumo Executivo

**Status:** ✅ **AJUSTE CONCLUÍDO**

**Conformidade Constitucional:** ✅ **CONFORME** (ART-04, ART-07, ART-09)

**Doutrina Atualizada:** `core/sop/doutrina.yaml` (secção `gatekeeper.executar_comandos_externos`)

---

## Ajuste Realizado

### Secção Adicionada: `executar_comandos_externos`

**Localização:** `core/sop/doutrina.yaml` (linhas 93-115)

**Conteúdo Adicionado:**

```yaml
executar_comandos_externos:
  permitido: true
  condicoes:
    - "APENAS para validação (dry-run, smoke tests, read-only)"
    - "NUNCA modificar código-fonte ou configurações"
    - "NUNCA modificar artefactos ou ficheiros do repositório"
  exemplos_permitidos:
    - "vercel build (dry-run, sem deploy)"
    - "npm audit (read-only, apenas análise)"
    - "git diff (read-only, apenas leitura)"
    - "yaml-lint (validação sem modificação)"
    - "shellcheck (validação sem modificação)"
  exemplos_proibidos:
    - "git commit (modifica repositório)"
    - "npm install (modifica node_modules)"
    - "make build (modifica artefactos)"
    - "vercel deploy (modifica produção)"
    - "git push (modifica remoto)"
  explicacao: >
    O Gatekeeper pode executar comandos externos APENAS para validação e análise.
    Qualquer comando que modifique código-fonte, configurações, artefactos ou
    o repositório é PROIBIDO. Comandos de validação (dry-run, read-only, smoke tests)
    são permitidos para permitir validações técnicas sem violar a doutrina.
```

**Explicação Atualizada:**

```yaml
explicacao: >
  O Gatekeeper pode ler qualquer ficheiro, mas apenas pode criar/editar/eliminar
  relatórios markdown e qualquer ficheiro dentro de relatorios/para_estado_maior/.
  Pode executar comandos externos APENAS para validação (dry-run, read-only),
  nunca para modificar código-fonte, configurações ou artefactos.
```

---

## Conformidade com a Ordem

### Objetivo da Ordem

✅ **CUMPRIDO**

- Ajustar doutrina para clarificar que Gatekeeper pode executar comandos externos APENAS para validação (dry-run, smoke tests), sem modificar código-fonte ou configurações.

### Constraints da Ordem

✅ **TODOS CUMPRIDOS**

1. ✅ Manter imutabilidade da doutrina — apenas clarificar, não alterar princípios
2. ✅ Garantir que comandos externos são APENAS para validação (read-only, dry-run)
3. ✅ Proibir explicitamente qualquer comando que modifique código-fonte ou configurações

### Success Criteria da Ordem

✅ **TODOS CUMPRIDOS**

1. ✅ Doutrina clarifica que Gatekeeper pode executar comandos externos APENAS para validação
2. ✅ Doutrina proíbe explicitamente comandos que modifiquem código-fonte ou configurações
3. ✅ Exemplos claros de comandos permitidos (vercel build dry-run) e proibidos (git commit)

---

## Conformidade Constitucional

### ART-04 (Verificabilidade)

✅ **CONFORME**

- Ajuste rastreável e documentado
- Doutrina atualizada com clarificações explícitas
- Exemplos de comandos permitidos e proibidos documentados

### ART-07 (Transparência)

✅ **CONFORME**

- Processo transparente e documentado
- Clarificações explícitas na doutrina
- Relatório gerado com evidências

### ART-09 (Evidência)

✅ **CONFORME**

- Artefactos citados: `core/sop/doutrina.yaml`
- Evidências de ajuste documentadas
- Decisões baseadas em artefactos

---

## Impacto das Mudanças

### Funções Habilitadas

Com este ajuste, o Gatekeeper pode agora implementar:

1. ✅ **Vercel Guard (Pré-Deploy)**
   - Executar `vercel pull` + `vercel build` (dry-run)
   - Validar `vercel.json` sem modificar código

2. ✅ **Preflight Local (Pre-Commit)**
   - Validar workflows YAML (read-only)
   - Verificar actions deprecadas (read-only)
   - Validar permissões GITHUB_TOKEN (read-only)

3. ✅ **Dependency Radar (Agendado)**
   - Executar `npm audit` (read-only)
   - Analisar dependências sem modificar `package.json`

4. ✅ **Post-Mortem (Falha)**
   - Executar comandos de análise (read-only)
   - Gerar relatórios sem modificar código

### Funções Mantidas Proibidas

O ajuste mantém a proibição de:

1. ❌ **Auto-Fix Direto**
   - Comandos que modifiquem código-fonte continuam proibidos
   - Alternativa aprovada: Gatekeeper → Ordem → Engenheiro

2. ❌ **Modificação de Artefactos**
   - `git commit`, `npm install`, `make build` continuam proibidos
   - Apenas validação (read-only) é permitida

---

## Artefactos Citados

- `core/sop/doutrina.yaml` (doutrina atualizada)
- `relatorios/para_estado_maior/decisao_estado_maior_funcoes_gatekeeper.md` (decisão do Estado-Maior)
- `relatorios/para_estado_maior/parecer_gatekeeper_funcoes_adicionais_sop.md` (parecer do SOP)

---

## Conclusão

**Status Final:** ✅ **AJUSTE CONCLUÍDO**

**Resumo:**

- Doutrina atualizada com clarificação sobre comandos externos
- Gatekeeper pode executar comandos APENAS para validação (dry-run, read-only)
- Proibição explícita de comandos que modifiquem código-fonte ou configurações
- Exemplos claros de comandos permitidos e proibidos documentados

**Próximo Passo:**

- Engenheiro pode implementar as 5 funções aprovadas (incluindo Vercel Guard)
- Gatekeeper pode executar comandos externos para validação conforme doutrina atualizada

**Conformidade Constitucional:** ✅ **CONFORME** (ART-04, ART-07, ART-09)

---

**Agente:** SOP (FÁBRICA 2.0)  
**Data/Hora:** 2025-11-02  
**Regras aplicadas:** ART-04, ART-07, ART-09, Doutrina de Acesso

---

**COMANDO A EXECUTAR:** "ESTADO-MAIOR CONFIRMAR AJUSTE DA DOUTRINA. ENGENHEIRO IMPLEMENTAR 5 FUNÇÕES APROVADAS CONFORME ORDEM EM `ordem/ordens/engineer.in.yaml`."
