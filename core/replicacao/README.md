# Replicação Instantânea

Sistema para copiar pipelines/projetos da FÁBRICA, herdando Tríade de Fundamentação e Leis.

## Requisitos

### Validação Obrigatória (ART-02)
Antes de replicar, o sistema valida que a Tríade de Fundamentação existe:
- ✅ White Paper (Estratégia)
- ✅ Arquitetura (Estrutura)
- ✅ Base Operacional (Execução)

### Herança Obrigatória (ART-06)
Projetos replicados herdam automaticamente:
- Constituição (`core/sop/constituição.yaml`)
- Leis (`core/sop/leis.yaml`)
- Exceções (`core/sop/exceptions.yaml`)
- Doutrina (`core/sop/doutrina.yaml`)

## Uso

```bash
python3 core/replicacao/replicar.py <nome_projeto> <destino>
```

### Exemplo
```bash
python3 core/replicacao/replicar.py meu_projeto ../meu_projeto
```

## Metadados (ART-07)

Cada projeto replicado inclui `replicacao_metadados.json` com:
- Nome do projeto
- Timestamp da replicação
- Agente que executou
- Tríade copiada
- Leis copiadas
- Regras aplicadas

## Conformidade Constitucional

- **ART-02:** Valida Tríade antes de replicar
- **ART-06:** Garante coerência entre projetos
- **ART-07:** Inclui metadados obrigatórios
- **ART-04:** Rastreabilidade completa

## Notas

- Executado pelo Engenheiro com ordem do Estado-Maior
- Não replica código-fonte automaticamente (apenas estrutura base)
- Requer validação SOP após replicação
