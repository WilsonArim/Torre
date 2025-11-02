# Análise SOP — Formato de Ordem vs Problema Real

**OWNER: SOP — Próxima ação:** Esclarecer confusão entre formato e problema real

**Data:** 2025-11-02  
**Ordem analisada:** `f27b0b92-8a41-4b8b-b798-51853cb7a228`

---

## 🔍 Análise: Formato vs Problema Real

### ❓ Pergunta do Estado-Maior
"Eu pedi alteração do formato de ordem dada ao engenheiro para ele compreender na sua máxima capacidade. É isso que está a criar problemas?"

### ✅ Resposta: NÃO, o formato não é o problema

---

## 📋 Análise Técnica

### Formato Atual na Ordem
```yaml
steps:
  - type: command
    command: make prepare_capitulo_4
```

### ✅ Este Formato É VÁLIDO para o ENGENHEIRO

**Evidência do código (`engineer_cli.py:177-192`):**
- O ENGENHEIRO aceita `type: command` com qualquer comando shell
- O comando `make prepare_capitulo_4` seria executado normalmente
- **O formato está correto e funciona**

### ❌ O Problema Real

**1. Target Não Existe no Makefile**
```bash
$ grep -E "prepare_capitulo|CAP-04" core/orquestrador/Makefile
# Resultado: Target não encontrado no Makefile
```

**2. O Que Acontece**
- O ENGENHEIRO executa: `make prepare_capitulo_4`
- O Makefile responde: `make: *** No rule to make target 'prepare_capitulo_4'. Stop.`
- **Isso não é um problema de formato, é um problema de target ausente**

---

## 📊 Comparação: Formato `command` vs `make`

### Opção A: `type: command` (Atual)
```yaml
- type: command
  command: make prepare_capitulo_4
```

**✅ Funciona se:** O target existe no Makefile  
**❌ Falha se:** O target não existe (caso atual)

### Opção B: `type: make` (Alternativa)
```yaml
- type: make
  target: prepare_capitulo_4
```

**✅ Funciona se:** O target existe no Makefile  
**❌ Falha se:** O target não existe (mesmo problema)

**Conclusão:** Ambos os formatos funcionam igualmente. O problema é a ausência do target, não o formato.

---

## 🎯 Recomendações

### Solução 1: Criar o Target no Makefile
```makefile
prepare_capitulo_4:
	@echo "Preparando capítulo 4..."
	# comandos aqui
```

**Depois disso, ambos os formatos funcionarão:**
- `type: command` com `command: make prepare_capitulo_4` ✅
- `type: make` com `target: prepare_capitulo_4` ✅

### Solução 2: Usar Comando Direto (Sem Makefile)
```yaml
- type: command
  command: "echo 'Preparar capítulo 4 manualmente'"
  description: "Preparar capítulo 4"
```

---

## ⚖️ Análise Constitucional

### ART-04 (Verificabilidade)
✅ **Conformidade:** O formato é verificável e executável  
⚠️ **Problema:** Target ausente viola verificabilidade (não pode ser executado)

### ART-09 (Evidência)
✅ **Conformidade:** Erro claramente reportado com evidência (`No rule to make target`)

---

## ✅ Conclusão

**O formato da ordem NÃO está causando problemas.**

**O problema real é:**
1. Target `prepare_capitulo_4` não existe no Makefile
2. A ordem tenta executar algo que não foi criado

**Solução:**
- Criar o target no Makefile, OU
- Usar comando direto sem Makefile, OU
- Alterar a ordem para usar um target existente

**O formato `type: command` está correto e funciona perfeitamente quando o comando é válido.**

---

**Artefactos Citados:**
- `ordem/ordens/engineer.in.yaml` (ordem f27b0b92-8a41-4b8b-b798-51853cb7a228)
- `core/orquestrador/engineer_cli.py` (linhas 177-192 - suporte a `type: command`)
- `core/orquestrador/Makefile` (target ausente)
- `relatorios/modelo_ordem_engenheiro.md` (documentação de formato)

---

**Agente:** SOP (FÁBRICA 2.0)  
**Data/Hora:** 2025-11-02  
**Regras aplicadas:** ART-04, ART-09

