# RAG Constitucional — Memória Viva

Sistema de busca e citação de informação normativa, histórico e decisões da FÁBRICA.

## Uso

```bash
python3 core/rag_constitucional/buscar.py "ART-04" constituicao
```

## Documentos Indexados

- Constituição (`core/sop/constituição.yaml`)
- Leis (`core/sop/leis.yaml`)
- Exceções (`core/sop/exceptions.yaml`)
- Doutrina (`core/sop/doutrina.yaml`)

## Próximos Passos

- [ ] Implementar embeddings vetoriais
- [ ] Adicionar busca semântica
- [ ] Indexar relatórios históricos
- [ ] Integrar com LLM para raciocínio contextualizado
