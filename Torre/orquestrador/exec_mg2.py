#!/usr/bin/env python3
"""
Execução MG2 - RAG Externo Filtrado (read-only)
Order ID: mg2-2025-11-01T16-21-00
Objetivo: Implementar cliente RAG externo com deny-lists e filtro constitucional
"""

import json
import hashlib
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import re

REPO_ROOT = Path(__file__).resolve().parents[2]
TORRE_ROOT = REPO_ROOT / "torre"
RELATORIOS_DIR = REPO_ROOT / "relatorios"
RAG_QUERIES_FILE = RELATORIOS_DIR / "rag_queries.json"
RAG_SMOKE_FILE = RELATORIOS_DIR / "rag_smoke.md"

# Deny-lists para filtragem
DENY_PATTERNS = [
    r'\.env$',
    r'\.env\..*',
    r'.*credentials.*',
    r'.*secret.*',
    r'.*password.*',
    r'.*api[_-]?key.*',
    r'.*token.*',
    r'.*\.pem$',
    r'.*\.key$',
    r'.*\.p12$',
    r'.*\.pfx$',
    r'node_modules/',
    r'__pycache__/',
    r'\.git/',
    r'\.venv/',
    r'venv/',
]

# Padrões constitucionais para filtragem
CONSTITUTIONAL_PATTERNS = [
    r'ART-\d+',
    r'ARTIGO\s+\d+',
    r'Constituição',
    r'Tríade',
    r'SOP',
    r'Gatekeeper',
]

print("OWNER: ENGENHEIRO-TORRE — Próxima ação: implementar RAG externo filtrado (read-only)")
print()

order_id = "mg2-2025-11-01T16-21-00"
started_at = datetime.now()

print(f"[ENGINEER-TORRE] [{order_id[:8]}] Iniciando MG2: RAG Externo Filtrado")
print()

# Step 1: Implementar cliente RAG externo com deny-lists e filtro constitucional
print("🔍 Step 1: Implementando cliente RAG externo filtrado...")

class RAGExternalClient:
    """Cliente RAG externo read-only com deny-lists e filtro constitucional"""
    
    def __init__(self, repo_root: Path, deny_patterns: List[str], constitutional_patterns: List[str]):
        self.repo_root = repo_root
        self.deny_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in deny_patterns]
        self.constitutional_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in constitutional_patterns]
        self.queries_log = []
    
    def is_allowed(self, file_path: Path) -> bool:
        """Verifica se arquivo está permitido (não está em deny-list)"""
        rel_path = str(file_path.relative_to(self.repo_root))
        for pattern in self.deny_patterns:
            if pattern.search(rel_path):
                return False
        return True
    
    def is_constitutional(self, content: str) -> bool:
        """Verifica se conteúdo tem referências constitucionais"""
        for pattern in self.constitutional_patterns:
            if pattern.search(content):
                return True
        return False
    
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Busca read-only com filtragem"""
        results = []
        
        # Buscar em arquivos permitidos
        for ext in ['.py', '.md', '.yaml', '.yml', '.json', '.ts', '.tsx', '.js']:
            for file_path in self.repo_root.rglob(f'*{ext}'):
                if not self.is_allowed(file_path):
                    continue
                
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    
                    # Buscar query no conteúdo
                    if query.lower() in content.lower():
                        # Verificar relevância constitucional
                        constitutional_relevance = self.is_constitutional(content)
                        
                        # Extrair contexto ao redor da query
                        lines = content.split('\n')
                        matches = []
                        for i, line in enumerate(lines):
                            if query.lower() in line.lower():
                                context_start = max(0, i - 2)
                                context_end = min(len(lines), i + 3)
                                context = '\n'.join(lines[context_start:context_end])
                                matches.append({
                                    'line': i + 1,
                                    'context': context
                                })
                        
                        if matches:
                            results.append({
                                'file': str(file_path.relative_to(self.repo_root)),
                                'matches': matches,
                                'constitutional_relevance': constitutional_relevance,
                                'score': len(matches) + (10 if constitutional_relevance else 0)
                            })
                
                except Exception as e:
                    continue
                
                if len(results) >= max_results:
                    break
            
            if len(results) >= max_results:
                break
        
        # Ordenar por score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:max_results]
    
    def query(self, query_text: str) -> Dict[str, Any]:
        """Executa query e registra resultado"""
        query_hash = hashlib.sha256(query_text.encode()).hexdigest()[:16]
        
        results = self.search(query_text)
        
        query_record = {
            'query_id': query_hash,
            'query': query_text,
            'timestamp': datetime.now().isoformat() + 'Z',
            'results_count': len(results),
            'results': results,
            'sources': [r['file'] for r in results]
        }
        
        self.queries_log.append(query_record)
        return query_record

# Criar cliente RAG
rag_client = RAGExternalClient(REPO_ROOT, DENY_PATTERNS, CONSTITUTIONAL_PATTERNS)
print(f"  ✅ Cliente RAG criado com {len(DENY_PATTERNS)} deny-patterns e filtro constitucional")
print()

# Step 2: Registrar cada query em relatorios/rag_queries.json
print("📝 Step 2: Preparando sistema de registro de queries...")
RELATORIOS_DIR.mkdir(parents=True, exist_ok=True)
print(f"  ✅ Sistema de registro preparado: {RAG_QUERIES_FILE.relative_to(REPO_ROOT)}")
print()

# Step 3: Testar 5 consultas e citar fontes
print("🧪 Step 3: Testando 5 consultas...")

test_queries = [
    "ART-01",
    "Constituição da FÁBRICA",
    "Gatekeeper",
    "SOP validação",
    "Tríade White Paper"
]

query_results = []
for i, query in enumerate(test_queries, 1):
    print(f"  🔍 Query {i}/5: '{query}'...")
    result = rag_client.query(query)
    query_results.append(result)
    print(f"    ✅ {result['results_count']} resultados encontrados")
    if result['sources']:
        print(f"    📄 Fontes: {', '.join(result['sources'][:3])}")

print()

# Salvar queries em JSON
queries_data = {
    'order_id': order_id,
    'created_at': started_at.isoformat() + 'Z',
    'total_queries': len(query_results),
    'queries': query_results
}
RAG_QUERIES_FILE.write_text(
    json.dumps(queries_data, indent=2, ensure_ascii=False),
    encoding='utf-8'
)
print(f"  ✅ Queries registradas: {RAG_QUERIES_FILE.relative_to(REPO_ROOT)}")
print()

# Gerar relatório rag_smoke.md com citações
print("📊 Step 4: Gerando relatório rag_smoke.md com citações...")

smoke_report = f"""# RAG Externo Filtrado - Smoke Test

**Order ID**: {order_id}  
**Gate**: MG2  
**Data**: {started_at.isoformat()}Z  
**Status**: ✅ CONCLUÍDO

## Resumo Executivo

Cliente RAG externo read-only implementado com:
- ✅ Deny-lists para arquivos sensíveis (.env, credenciais, etc.)
- ✅ Filtro constitucional para relevância
- ✅ Registro de queries em JSON
- ✅ {len(test_queries)} consultas testadas

## Consultas Testadas

"""
for i, query_record in enumerate(query_results, 1):
    smoke_report += f"""### Consulta {i}: "{query_record['query']}"

**Query ID**: `{query_record['query_id']}`  
**Timestamp**: {query_record['timestamp']}  
**Resultados**: {query_record['results_count']}

**Fontes encontradas**:
"""
    for result in query_record['results']:
        smoke_report += f"- `{result['file']}` (score: {result['score']}, relevância constitucional: {'sim' if result['constitutional_relevance'] else 'não'})\n"
        if result['matches']:
            match = result['matches'][0]
            smoke_report += f"  - Linha {match['line']}: ```\n{match['context'][:200]}...\n```\n"
    smoke_report += "\n"

smoke_report += f"""## Métricas

- **Total de queries**: {len(query_results)}
- **Queries com resultados**: {len([q for q in query_results if q['results_count'] > 0])}
- **Total de fontes únicas**: {len(set(sum([q['sources'] for q in query_results], [])))}
- **Filtragem ativa**: Deny-lists e filtro constitucional

## Filtros Aplicados

### Deny-lists
- Arquivos `.env*`
- Arquivos com credenciais/secrets/passwords
- Diretórios: `node_modules/`, `__pycache__/`, `.git/`, `.venv/`

### Filtro Constitucional
- Padrões: ART-*, ARTIGO *, Constituição, Tríade, SOP, Gatekeeper
- Relevância constitucional aumenta score dos resultados

## Artefactos Gerados

- `relatorios/rag_queries.json` - Log completo de queries
- `relatorios/rag_smoke.md` - Este relatório

---
*Gerado automaticamente pelo Engenheiro da TORRE*
"""

RAG_SMOKE_FILE.write_text(smoke_report, encoding='utf-8')
print(f"  ✅ Relatório gerado: {RAG_SMOKE_FILE.relative_to(REPO_ROOT)}")
print()

# Resumo final
finished_at = datetime.now()
duration_seconds = (finished_at - started_at).total_seconds()

consultas_testadas = len(query_results)
citacoes_ok = all(q['results_count'] > 0 for q in query_results)

print("=" * 60)
print("📊 RESUMO DA EXECUÇÃO MG2")
print("=" * 60)
print(f"Order ID: {order_id}")
print(f"Gate: MG2")
print(f"Duração: {duration_seconds:.2f}s")
print()
print(f"✅ Consultas testadas: {consultas_testadas} (>=5: {consultas_testadas >= 5})")
print(f"✅ Citações OK: {citacoes_ok}")
print(f"✅ Queries registradas: {RAG_QUERIES_FILE.relative_to(REPO_ROOT)}")
print(f"✅ Relatório gerado: {RAG_SMOKE_FILE.relative_to(REPO_ROOT)}")
print()

if consultas_testadas >= 5 and citacoes_ok:
    print("✅ CRITÉRIOS DE SUCESSO ATENDIDOS")
    print("   - Consultas_testadas: >=5")
    print("   - Citacoes_ok: true")
    sys.exit(0)
else:
    print("⚠️  CRITÉRIOS PARCIALMENTE ATENDIDOS")
    if consultas_testadas < 5:
        print(f"   - Consultas_testadas: {consultas_testadas} (< 5)")
    if not citacoes_ok:
        print(f"   - Citacoes_ok: false")
    sys.exit(1)

