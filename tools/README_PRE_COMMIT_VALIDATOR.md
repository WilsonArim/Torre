# Validador Pré-Commit FÁBRICA 2.0

Validador local que imita 100% os workflows GitHub Actions e bloqueia commit/push se algum check falhar.

## Objetivo

Eliminar ciclos de erro após push: validar localmente antes de commitar, poupando tempo e mantendo histórico limpo.

## Uso

### Execução Automática (Git Hook)

O hook `pre-commit` é instalado automaticamente e executa antes de cada commit:

```bash
git commit -m "mensagem"
# Validador executa automaticamente
# Se falhar, commit é bloqueado
```

### Execução Manual

Para testar antes de commitar:

```bash
# Via Makefile
make -C core/orquestrador validate

# Ou diretamente
python3 tools/pre_commit_validator.py --skip-staged-check
```

### Pular Validação (Apenas em Emergências)

```bash
git commit --no-verify -m "mensagem"
```

⚠️ **AVISO:** Usar `--no-verify` apenas em emergências. Sempre valide antes de push.

## Validações Executadas

O validador replica **exatamente** os mesmos passos dos workflows GitHub:

1. **Validar imutabilidade da Constituição**
   - Bloqueia modificações em `core/sop/constituição.yaml`

2. **Bloquear scripts legados de pipeline**
   - Bloqueia modificações em `ordem/` e `deprecated/ordem/`

3. **Executar pre-commit hooks**
   - Formatação, linting, etc.

4. **Gerar security reports e SBOM**
   - Bandit, Semgrep, npm audit, Trivy
   - SBOM (Software Bill of Materials)

5. **Validar SOP**
   - Executa `core/scripts/validator.py`
   - Valida conformidade constitucional

6. **Executar Gatekeeper**
   - Validação ética e técnica
   - Gera parecer do Gatekeeper

7. **Preparar Gatekeeper e validar pipeline**
   - Gatekeeper prep
   - Validação de pipeline

8. **Validação completa**
   - Todos os checks passaram

## Estrutura

```
tools/
  pre_commit_validator.py    # Script principal
  README_PRE_COMMIT_VALIDATOR.md  # Esta documentação

.git/hooks/
  pre-commit                 # Git hook instalado
```

## Saída

### Sucesso

```
✅ Todas as validações passaram!
Commit/Push autorizado.
```

### Falha

```
❌ Validação falhou no passo X
Commit/Push bloqueado. Corrija os erros acima antes de tentar novamente.
```

## Dependências

O validador tenta instalar automaticamente as dependências necessárias:

- `pre-commit` (hooks de formatação)
- `bandit` (análise de segurança Python)
- `coverage` (cobertura de testes)
- `cyclonedx-bom` (geração de SBOM)

## Troubleshooting

### "Validador pré-commit não encontrado"

O hook não encontrou o script. Verificar se `tools/pre_commit_validator.py` existe e está executável.

### "SBOM não foi gerado"

Instalar `cyclonedx-bom`:

```bash
npm install -g @cyclonedx/cyclonedx-npm
```

### "SOP validation falhou"

Verificar logs em `relatorios/relatorio_sop.md` e `relatorios/sop_status.json`.

### "Gatekeeper falhou"

Verificar logs em `relatorios/parecer_gatekeeper.md`.

## Conformidade Constitucional

- **ART-04 (Verificabilidade):** Validações são rastreáveis e documentadas
- **ART-07 (Transparência):** Processo claro e reportado
- **ART-09 (Evidência):** Artefactos gerados antes de commit/push

## Referências

- Workflows GitHub: `.github/workflows/ci.yml`, `.github/workflows/fabrica-ci.yml`
- Makefile: `core/orquestrador/Makefile`
- Validador SOP: `core/scripts/validator.py`
