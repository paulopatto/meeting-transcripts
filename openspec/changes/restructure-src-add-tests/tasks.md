## 1. Restruturar arquivos em src/

- [ ] 1.1 Criar diretórios `src/teams/` e `src/tldv/`
- [ ] 1.2 Mover `teams_check.py` para `src/teams/teams_check.py` com `git mv`
- [ ] 1.3 Mover `tldv_check.py` para `src/tldv/tldv_check.py` com `git mv`
- [ ] 1.4 Atualizar entrypoints no `pyproject.toml` se necessário (já devem estar corretos)
- [ ] 1.5 Verificar que `uv run src/teams/teams_check.py --help` funciona

## 2. Adicionar dependências de teste

- [ ] 2.1 Adicionar `pytest>=8.0` e `pytest-mock>=3.14` como dependências opcionais de teste no `pyproject.toml`

## 3. Criar testes para teams_check.py

- [ ] 3.1 Criar `tests/conftest.py` com fixtures compartilhadas (token mockado, client mockado)
- [ ] 3.2 Criar `tests/test_teams_check.py` com testes para authenticate (CLIENT_ID faltando)
- [ ] 3.3 Criar teste para authenticate com Device Code Flow
- [ ] 3.4 Criar teste para graph_get com sucesso (HTTP 200)
- [ ] 3.5 Criar teste para graph_get com erro (HTTP 403)
- [ ] 3.6 Criar teste para list_my_meetings com lista vazia

## 4. Criar testes para tldv_check.py

- [ ] 4.1 Criar `tests/test_tldv_check.py` com testes para TldvClient.get
- [ ] 4.2 Criar teste para check_api_access com API key inválida (HTTP 401)
- [ ] 4.3 Criar teste para list_meetings retornando lista
- [ ] 4.4 Criar teste para get_transcript com transcrição disponível

## 5. Validar

- [ ] 5.1 Executar `uv run pytest tests/` e garantir que todos os testes passam
- [ ] 5.2 Verificar que `uv run src/teams/teams_check.py --help` funciona
- [ ] 5.3 Verificar que `uv run src/tldv/tldv_check.py --help` funciona
