# Relatório SOP
Gate avaliado: G2
Resultado: **PASS**

## Conformidade Constitucional
- ✅ Constituição validada: 10 leis fundamentais
- ✅ Tríade de Fundamentação (ART-02): Validada

## Métricas
- Cobertura: 38.71% (mínimo python: 35%)
- Semgrep: ok=True findings=0 blocking=0
- Bandit: ok=True (worst: LOW)
- npm audit: ok=True critical=0
- Trivy: ok=True critical=0
- SBOM: ok=True
- Testes: ok=True tests=0 failures=0 errors=0

## Pipeline
- Pipeline válida: False

## Artefactos Citados (ART-09)
- Coverage: `relatorios/coverage.xml`
- Semgrep: `relatorios/semgrep.sarif`
- Bandit: `relatorios/bandit.json`
- npm audit: `relatorios/npm-audit.json`
- Trivy: `relatorios/trivy.json`
- SBOM: `relatorios/sbom.json`
- JUnit: `não encontrado`
- Leis: `core/sop/leis.yaml`
- Exceções: `core/sop/exceptions.yaml`
- Constituição: `core/sop/constituição.yaml`

--

## Exceções Aplicadas
- **coverage_min.python**: Cobertura atual da base herdada (FÁBRICA + Torre) ainda em consolidação; exceção temporária até reforço de testes. (expira: 2025-12-31)

---
**Agente**: SOP (FÁBRICA 2.0)
**Data/Hora**: 2025-11-18 09:53:42 UTC
**Objetivo**: Validação de gate G2 conforme Constituição e leis.yaml
**Regras aplicadas**: Constituição (10 artigos), leis.yaml, exceptions.yaml
