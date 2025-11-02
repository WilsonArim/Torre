# Padronização de Formatos

Sistema para garantir que todos os artefatos/relatórios seguem o formato obrigatório conforme doutrina.

## Formato Obrigatório

Todas as interações de todos os agentes devem seguir:

```markdown
**PIPELINE/FORA_PIPELINE:** PIPELINE ou FORA_PIPELINE

**OWNER: AGENTE — Próxima ação:** <frase curta>

[... conteúdo da interação ...]

---

**COMANDO A EXECUTAR:** "AGENTE AÇÃO (localização)"
```

## Uso

### Validar formato de um ficheiro:
```bash
python3 core/padronizacao_formatos/validar_formato.py relatorios/para_estado_maior/relatorio.md
```

### Validar todos os relatórios:
```bash
python3 core/padronizacao_formatos/validar_formato.py --todos
```

### Formatar interação:
```bash
python3 core/padronizacao_formatos/formatar_interacao.py ENGENHEIRO "Conteúdo da interação" PIPELINE "Aguardar validação" "ESTADO-MAIOR ANALISAR"
```

## Ferramentas

- `validar_formato.py` — Valida formato de interações e ficheiros markdown
- `formatar_interacao.py` — Formata interações conforme padrão obrigatório

## Conformidade Constitucional

- **ART-04:** Verificabilidade — formato garante rastreabilidade
- **ART-07:** Transparência — metadados obrigatórios presentes
- **ART-09:** Evidência — comando a executar sempre presente

## Integração

Este módulo integra-se com:
- `core/orquestrador/file_access_guard.py` — Função `formatar_resposta_agente()`
- `core/sop/doutrina.yaml` — Doutrina `formato_interacoes`
