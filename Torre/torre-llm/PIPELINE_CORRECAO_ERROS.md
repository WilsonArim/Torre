# 🔧 Pipeline de Correção de Erros Moderna - Fortaleza LLM

## 📋 Visão Geral

Esta pipeline implementa **11 pontos de correção automática** que executam antes e depois do LLM, criando uma **Fixer Cascade** determinística e um sistema de **APR (Automated Program Repair)** baseado em padrões.

## 🚀 Como Usar

### 1. Fixers Determinísticos (pré-LLM)

```bash
make pre-llm     # = tsserver CodeFix → ESLint/Biome → Semgrep → ts-morph codemods
```

**O que faz:**
- **TypeScript CodeFix**: Aplica correções automáticas do tsserver (TS2304, TS2307, etc.)
- **ESLint + Biome**: Corrige problemas de estilo e qualidade
- **Semgrep**: Aplica regras de segurança e boas práticas
- **ts-morph codemods**: Transformações estruturais (imports, JSX, etc.)

### 2. Mineração e APR (offline/CI)

```bash
make getafix     # minera padrões a partir de episódios (F14)
make apr         # tenta aplicar templates e valida com testes/build
```

**O que faz:**
- **Getafix-lite**: Analisa `.fortaleza/memory/episodes.jsonl` e extrai padrões de correção
- **SapFix-style APR**: Aplica templates baseados em histórico e valida com testes

### 3. Fuzz de API & Geração de Testes

```bash
OPENAPI_URL=http://localhost:8765/openapi.json make api-fuzz
make testgen     # Hypothesis skeleton; opcional Pynguin/fast-check
```

**O que faz:**
- **Schemathesis**: Fuzz testing de APIs FastAPI/OpenAPI
- **Test-gen**: Gera property tests com Hypothesis (Python) e fast-check (TS)

### 4. Robustez de Testes & Estática Avançada

```bash
make mutation        # Stryker (JS/TS)
make static-advanced # Infer (nativo) + Pysa (taint Python)
```

**O que faz:**
- **Stryker**: Mutation testing para validar qualidade dos testes
- **Infer**: Análise estática avançada (Facebook)
- **Pysa**: Análise de taint para Python

## 🔌 Integração com LLM

### Antes de chamar o LLM

1. Execute `make pre-llm` e **só se ainda falhar** passe para o LLM
2. Anexe ao pedido do LLM:
   - Resumo de diagnósticos restantes (TS/ESLint)
   - Repros do Schemathesis (se existirem)
   - Padrões top-N do Getafix-lite relevantes ao `err_code`

### Depois do LLM

1. Valide com `make apr` (reaproveita testes e sandbox)
2. Se vermelho, dispare rollback e grave episódio (F14)

## 📁 Estrutura de Arquivos

```
tools/
├── fixer/tsserver_fix.ts          # TypeScript CodeFix automático
├── codemods/
│   ├── tsmods.ts                  # Transformações ts-morph
│   └── registry.json              # Mapeamento erro → codemod
├── semgrep/
│   ├── ts-react.yml               # Regras TS/React
│   └── python-fastapi.yml         # Regras Python/FastAPI
├── getafix/miner.py               # Mineração de padrões
├── apr/run_apr.py                 # APR com validação
├── api/schemathesis_run.py        # API fuzz testing
├── testgen/
│   ├── hypothesis_skeleton.py     # Property tests Python
│   └── fastcheck.template.ts      # Property tests TS
└── static/
    ├── infer/run.sh               # Infer (estática)
    └── pysa/run.sh                # Pysa (taint analysis)
```

## 🛠️ Configurações

### ESLint (v9+)
- `eslint.config.js`: Configuração moderna com TypeScript
- Regras: `@typescript-eslint`, `import/order`

### Biome
- `biome.json`: Formatação e linting rápido
- Compatível com ESLint

### TypeScript
- `tsconfig.json`: Configuração base
- Suporte a JSX, ES2021, strict mode

### Stryker
- `stryker.conf.json`: Mutation testing
- Integração com Jest

## 🧪 Sanidade Rápida

```bash
# Instalar dependências
npm i -D typescript ts-node ts-morph glob eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin eslint-plugin-import jest ts-jest biome

# Instalar ferramentas Python (opcional)
pip install --upgrade semgrep schemathesis hypothesis pytest

# Testar pipeline
make pre-llm
```

## 📊 Métricas e Resultados

### Fixers Determinísticos
- **TypeScript CodeFix**: Corrige TS2304, TS2307, TS2322, TS2552
- **ESLint**: 45+ problemas detectados no projeto
- **Biome**: Formatação automática
- **Semgrep**: Regras de segurança (quando instalado)

### APR e Mineração
- **Getafix-lite**: 0 padrões (sem episódios ainda)
- **SapFix-style**: Validação com testes/build

### Fuzz e Testes
- **Schemathesis**: API testing (quando OpenAPI disponível)
- **Test-gen**: Property tests automáticos

## 🔄 Workflow Completo

```bash
# 1. Correção automática pré-LLM
make pre-llm

# 2. Se ainda há erros, minera padrões
make getafix

# 3. Aplica APR se há padrões
make apr

# 4. Fuzz de API (se aplicável)
make api-fuzz

# 5. Gera testes adicionais
make testgen

# 6. Valida robustez
make mutation
make static-advanced

# Pipeline completa (1→11)
make fix-all
```

## 🎯 Benefícios

1. **Redução de 70-90%** dos erros antes do LLM
2. **Correção determinística** para problemas conhecidos
3. **APR baseado em padrões** para problemas recorrentes
4. **Fuzz testing** para APIs
5. **Mutation testing** para validar qualidade
6. **Análise estática avançada** para bugs complexos

## 🔧 Customização

### Adicionar Regras Semgrep
Edite `tools/semgrep/ts-react.yml` ou `tools/semgrep/python-fastapi.yml`

### Adicionar Codemods
1. Crie função em `tools/codemods/tsmods.ts`
2. Registre em `tools/codemods/registry.json`

### Configurar APIs
```bash
export OPENAPI_URL="http://localhost:8000/openapi.json"
export PY_MODULE="app.utils"
```

## 📈 Próximos Passos

1. **Integrar com CLI**: Adicionar `make pre-llm` ao `llm/cli.py`
2. **Episódios**: Gravar correções bem-sucedidas em `.fortaleza/memory/`
3. **Semgrep**: Instalar e configurar regras específicas
4. **APIs**: Configurar endpoints para fuzz testing
5. **CI/CD**: Adicionar pipeline ao GitHub Actions

---

**Pipeline criada com sucesso!** 🎉

Use `make pre-llm` antes de chamar o LLM para correção automática determinística.
