## SOP_MANUAL

As leis da SOP v2 definem gates (G0..G5), políticas e papéis RACI.

### Leis e Exceções
- `core/sop/leis.yaml`: políticas, thresholds e RACI
- `core/sop/exceptions.yaml`: exceções com owner e `expires_at`

### Decisão Automática
O validador agrega métricas (coverage, semgrep, bandit, audit, trivy, sbom) e decide PASS/BLOCK.

### Artefactos
- `relatorios/relatorio_sop.md`: leitura humana
- `relatorios/sop_status.json`: consumo por máquinas
- `relatorios/parecer_gatekeeper.md`: parecer manual


