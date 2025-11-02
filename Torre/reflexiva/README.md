# Torre Reflexiva (2C)

Módulo de auto-avaliação e pesquisa externa da FÁBRICA.

## Especificações

- ✅ Opera apenas como medidor estatístico
- ✅ Pesquisa na internet sobre temas novos, ideias novas
- ❌ **NÃO tem autonomia para criar**
- ✅ Pode criar apenas ficheiros YAML e Markdown na sua pasta
- ✅ SOP dará parecer sobre segurança
- ✅ Estado-Maior dará parecer se vale a pena incluir

## Uso

```bash
python3 Torre/reflexiva/pesquisar.py "tema de pesquisa" fonte1 fonte2
```

## Estrutura

- `pesquisas/` — Pesquisas salvas em YAML
- `sinteses/` — Sínteses salvas em Markdown

## Conformidade Constitucional

- ART-05: Não-Autonomia Absoluta — apenas medidor estatístico
- ART-07: Transparência — metadados obrigatórios em todos os ficheiros
- ART-09: Evidência — todas as pesquisas são rastreáveis

## Próximos Passos

- [ ] Integrar pesquisa externa real (web scraping controlado)
- [ ] Adicionar filtros de segurança
- [ ] Integrar com APIs de pesquisa
- [ ] Adicionar validação SOP automática
