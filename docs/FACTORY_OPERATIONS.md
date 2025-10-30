## FACTORY_OPERATIONS

Este documento explica como usar a FÁBRICA para criar/sincronizar/validar projetos.

### Comandos
- `factory init <dest>`: cria um novo projeto com skeleton + workflows.
- `factory sync <proj_path>`: sincroniza leis, orquestrador e workflows.
- `factory validate <proj_path>`: executa `make sop` no projeto.
- `factory report <proj_path>`: agrega relatórios e produz sumário.

### Fluxo típico
1. `factory init meu-projeto`
2. Editar código e configurar CI
3. `factory validate .`
4. Ver relatorios em `relatorios/`


