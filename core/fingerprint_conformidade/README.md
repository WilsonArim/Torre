# Fingerprint de Conformidade

Sistema de hash/checksum automático de artefactos, pipelines e leis para garantir autenticidade e rastreabilidade.

## Uso

### Verificar um artefacto específico:
```bash
python3 core/fingerprint_conformidade/verificar.py core/sop/constituição.yaml
```

### Verificar todos os artefactos:
```bash
python3 core/fingerprint_conformidade/verificar.py --todos
```

## Artefactos Monitorados

- Constituição e Leis (`core/sop/`)
- Pipelines (`pipeline/`)
- PINs principais (`factory/pins/`)

## Próximos Passos

- [ ] Integrar com CI/CD para verificação automática
- [ ] Adicionar verificação em pre-commit hooks
- [ ] Alertar sobre alterações em artefactos críticos
- [ ] Integrar com sistema de versionamento
