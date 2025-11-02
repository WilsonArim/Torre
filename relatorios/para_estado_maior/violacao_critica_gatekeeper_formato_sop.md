# Violação Crítica SOP — Gatekeeper Não Segue Formato Obrigatório

**PIPELINE/FORA_PIPELINE:** FORA_PIPELINE

**OWNER: SOP — Próxima ação:** Reportar violação crítica do formato obrigatório pelo Gatekeeper

**Data:** 2025-11-02  
**Agente:** SOP v3.0  
**Objetivo:** Reportar violação crítica: Gatekeeper não seguiu formato obrigatório de interações

---

## 🚨 VIOLAÇÃO CRÍTICA IDENTIFICADA

**Problema:** Gatekeeper emitiu resposta que **NÃO segue o formato obrigatório** de interações conforme doutrina.

**Severidade:** 🔴 **CRÍTICO** — Violação direta da doutrina de formato_interacoes

**Evidência:** Resposta do Gatekeeper ao comando "executar Gatekeeper" não contém:
- ❌ Início: `**PIPELINE/FORA_PIPELINE:**`
- ❌ Fim: `**COMANDO A EXECUTAR:**`

---

## 📋 RESPOSTA DO GATEKEEPER (VIOLANDO FORMATO)

### Resposta Recebida (INCORRETA):

```
Comando reconhecido: **executar Gatekeeper**.

Vou proceder à auditoria conforme o protocolo:

1. Ler e validar todos os artefatos obrigatórios...
2. Verificar se todas as constraints...
3. Emitir os relatórios de decisão...

Para avançar com a execução "Gatekeeper", é necessário que o arquivo obrigatório `relatorios/coverage.xml` exista no workspace.

Neste momento, **não foi possível encontrar `coverage.xml`**, portanto a decisão protocolar é:

---

**DECISÃO:**  
⛔ BLOQUEADO

**Motivo:**  
Faltando artefato obrigatório: `relatorios/coverage.xml`.

---

**Próximos passos sugeridos**:
1. Gere o arquivo de cobertura...
2. Solicite novamente a execução "Gatekeeper"...
```

### Problemas Identificados:

1. ❌ **Não começa com `**PIPELINE/FORA_PIPELINE:**`**
2. ❌ **Não inclui `**OWNER: GATEKEEPER — Próxima ação:**`**
3. ❌ **Não termina com `**COMANDO A EXECUTAR:**`**
4. ❌ **Não segue formato obrigatório conforme doutrina**

---

## ✅ FORMATO CORRETO ESPERADO

### Resposta Correta (conforme doutrina):

```markdown
**PIPELINE/FORA_PIPELINE:** FORA_PIPELINE

**OWNER: GATEKEEPER — Próxima ação:** Auditoria de gate bloqueada por artefato faltante

Para avançar com a execução "Gatekeeper", é necessário que o arquivo obrigatório `relatorios/coverage.xml` exista no workspace.

Neste momento, **não foi possível encontrar `coverage.xml`**, portanto a decisão protocolar é:

---

**DECISÃO:**  
⛔ BLOQUEADO

**Motivo:**  
Faltando artefato obrigatório: `relatorios/coverage.xml`.

---

**Próximos passos sugeridos**:
1. Gere o arquivo de cobertura (`coverage.xml`) — normalmente via:
   ```bash
   coverage run -m pytest
   coverage xml -o relatorios/coverage.xml
   ```
2. Solicite novamente a execução "Gatekeeper" para reprocessar e emitir o parecer PASS assim que todos os artefatos estiverem presentes.

---

**COMANDO A EXECUTAR:** "ENGENHEIRO GERAR coverage.xml E SOLICITAR NOVA EXECUÇÃO DO GATEKEEPER"
```

---

## 🔍 ANÁLISE DA CAUSA

### Problema Identificado:

**Gatekeeper não possui código Python automatizado** que implemente o formato obrigatório.

**Evidência:**
- ✅ PIN do Gatekeeper especifica formato obrigatório (`factory/pins/gatekeeper.yaml`, linhas 13-21)
- ❌ Não existe `gatekeeper_cli.py` ou código Python equivalente
- ❌ Gatekeeper está sendo executado diretamente pelo LLM (Composer)
- ❌ LLM não está aplicando formato obrigatório automaticamente

### Comparação com Outros Agentes:

| Agente | Código Python | Formato Automático | Status |
|--------|---------------|-------------------|--------|
| ENGENHEIRO | ✅ `engineer_cli.py` | ✅ Implementado | ✅ CONFORME |
| SOP | ✅ `sop_cli.py` | ✅ Implementado | ✅ CONFORME |
| GATEKEEPER | ❌ Não existe | ❌ Não implementado | ❌ **VIOLANDO** |

---

## ⚖️ VIOLAÇÕES CONSTITUCIONAIS

### ART-04 (Verificabilidade)
❌ **VIOLAÇÃO:** Resposta do Gatekeeper não segue formato obrigatório, reduzindo verificabilidade

### ART-09 (Evidência)
❌ **VIOLAÇÃO:** Resposta do Gatekeeper não inclui comando a executar, reduzindo rastreabilidade

### Doutrina (formato_interacoes)
❌ **VIOLAÇÃO CRÍTICA:** Gatekeeper não segue formato obrigatório conforme `core/sop/doutrina.yaml`

---

## 🛡️ CORREÇÕES NECESSÁRIAS

### Prioridade CRÍTICA

#### 1. Implementar Código Python do Gatekeeper

**Arquivo:** `core/orquestrador/gatekeeper_cli.py` (a criar)

**Requisitos:**
- Implementar função `formatar_resposta_agente()` ou importar de `file_access_guard.py`
- Garantir que todas as respostas sigam formato obrigatório
- Implementar fallback que garanta formato mesmo sem importação

**Base de Referência:**
- `core/orquestrador/engineer_cli.py` (implementação completa)
- `core/orquestrador/sop_cli.py` (implementação completa)

---

#### 2. Garantir que LLM Use Formato Obrigatório

**Problema:** Se Gatekeeper continuar sendo executado diretamente pelo LLM, o LLM deve ser instruído a sempre usar formato obrigatório.

**Solução:**
- Adicionar instrução explícita no contexto do LLM
- Garantir que PIN do Gatekeeper seja sempre lido antes da execução
- Implementar validação automática de formato antes de enviar resposta

---

## 📋 RECOMENDAÇÕES

### Curto Prazo (Imediato)

1. **Criar `gatekeeper_cli.py`** seguindo padrão de `engineer_cli.py` e `sop_cli.py`
2. **Implementar formato obrigatório** em todas as funções do Gatekeeper
3. **Adicionar fallback** que garanta formato mesmo sem importação

### Médio Prazo

4. **Integrar Gatekeeper com sistema de ordens** (`ordem/ordens/gatekeeper.in.yaml`)
5. **Garantir que pareceres markdown** também sigam formato obrigatório
6. **Implementar validação automática** de formato antes de salvar pareceres

---

## 📋 CONCLUSÃO

**Violação Crítica:** Gatekeeper não segue formato obrigatório de interações conforme doutrina.

**Causa Raiz:** Gatekeeper não possui código Python automatizado que implemente formato obrigatório.

**Impacto:** Todas as respostas do Gatekeeper violam doutrina de formato_interacoes.

**Correção Necessária:** Implementar código Python do Gatekeeper seguindo padrão dos outros agentes.

**Status:** 🔴 **BLOQUEADO** — Violação crítica da doutrina

---

**Artefactos Citados:**
- `factory/pins/gatekeeper.yaml` (linhas 13-21) ⚠️ Especifica formato, mas não há código que implemente
- `core/sop/doutrina.yaml` (formato_interacoes) ⚠️ Violado
- `core/orquestrador/engineer_cli.py` ✅ Referência de implementação correta
- `core/orquestrador/sop_cli.py` ✅ Referência de implementação correta
- `core/orquestrador/file_access_guard.py` ✅ Função helper disponível

---

**Agente:** SOP (FÁBRICA 2.0)  
**Data/Hora:** 2025-11-02  
**Regras aplicadas:** ART-04, ART-09, Doutrina de Acesso a Ficheiros (formato_interacoes)

---

**COMANDO A EXECUTAR:** "ENGENHEIRO CRIAR gatekeeper_cli.py IMPLEMENTANDO FORMATO OBRIGATÓRIO EM TODAS AS RESPOSTAS DO GATEKEEPER, SEGUINDO PADRÃO DE engineer_cli.py E sop_cli.py"

