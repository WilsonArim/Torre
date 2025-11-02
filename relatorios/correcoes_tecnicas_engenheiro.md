# Correções Técnicas - ENGENHEIRO v3.0

**Data**: 2025-11-02  
**Agente**: ENGENHEIRO  
**Motivo**: Correções identificadas pelo SOP

## Bugs Corrigidos

### 1. Suporte a Caminhos com Espaços

**Problema**: Caminhos com espaços (ex: "CURSOR LOCAL") causavam falhas na execução de comandos Python.

**Solução**: 
- Garantir uso de `REPO_ROOT.absolute()` em todos os `cwd` de subprocess
- Usar aspas em comandos shell quando necessário
- Todos os caminhos agora são absolutos antes de passar para subprocess

**Ficheiros alterados**:
- `core/orquestrador/engineer_cli.py` - tipos `command`, `make`, `validation`

### 2. Tipo `validation` Melhorado

**Problema**: Tipo `validation` não estava implementado corretamente.

**Solução**:
- `validation: sop` agora usa `make sop` (já configurado com todas dependências)
- `validation: pipeline` usa `make pipeline_validate`
- Timeout aumentado para 600s (validações podem demorar)

### 3. Tipo `make` com Caminhos Absolutos

**Problema**: Comandos make com caminhos relativos falhavam com espaços.

**Solução**:
- Usar `ORQUESTRADOR_DIR.absolute()` entre aspas
- Garantir cwd absoluto

## Recomendações para Estado-Maior

### Formato Correto de Steps

**✅ BOM - Tipo make:**
```yaml
- type: make
  target: sop
  description: "Executar validação SOP"
```

**❌ EVITAR - Comando com make:**
```yaml
- type: command
  command: make sop  # Deve ser type: make
```

**✅ BOM - Tipo validation:**
```yaml
- type: validation
  validation: sop
  description: "Validar conformidade SOP"
```

**✅ BOM - Tipo command com Python:**
```yaml
- type: command
  command: "python3 core/orquestrador/sop_cli.py executa"
  description: "Executar SOP diretamente"
```

## Status

✅ Bugs corrigidos  
✅ Caminhos com espaços suportados  
✅ Tipo validation funcional  
✅ Makefile com caminhos absolutos  

## Testes

Ordem `f27b0b92-8a41-4b8b-b798-51853cb7a228` pode ser re-executada após correção dos steps pelo Estado-Maior.

---

**Conclusão**: Correções técnicas implementadas. Sistema robusto para caminhos com espaços e todos os tipos de steps funcionais.

