# Diário de Bordo da Fábrica

## Ordem Inicial

ID: 2025-09-29-001
PRIORIDADE: Alta
CONTEXTO: O módulo GAMA precisa da base de autenticação mínima
AÇÃO: Implementar autenticação JWT
DETALHES:

- Criar endpoint /token
- Validar email + password
- Gerar JWT com expiração curta e jti
- Middleware para proteger endpoints
- Decorador @role('admin') para RBAC
  CRITÉRIOS:
- Login devolve token válido
- Endpoint protegido falha sem token
- RBAC funciona com papéis
- Testes pytest passam
  CHECKLIST:
- [x] PATCH aplicado
- [x] Testes a verde
- [x] Gatekeeper a 100%
      PRAZO: Até fechar a Fase 1 da pipeline

## Ordem Concluída

- [x] ORDEM 2025-09-29-001 — Micro-GAMA: JWT
  - PATCH aplicado | Testes 100% | Gatekeeper 7/7 PASSOU
  - Aula: /treino_torre/2025-09-29-001-micro-gama-jwt.md
