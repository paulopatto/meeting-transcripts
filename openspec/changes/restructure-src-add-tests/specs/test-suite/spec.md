## ADDED Requirements

### Requirement: Suite de testes com PyTest

O projeto DEVE ter testes automatizados usando PyTest, organizados no diretório `tests/`.

#### Scenario: pytest é executado sem erros

- **WHEN** `uv run pytest tests/` é executado
- **THEN** todos os testes DEVEM passar (exit code 0)

### Requirement: Testes para teams_check.py

O arquivo `tests/test_teams_check.py` DEVE conter testes unitários que mockam as chamadas HTTP à Microsoft Graph API.

#### Scenario: authenticate com CLIENT_ID faltando

- **WHEN** `TEAMS_CLIENT_ID` não está configurado
- **THEN** `authenticate()` DEVE exibir mensagem de erro e sair com sys.exit(1)

#### Scenario: authenticate com Device Code Flow

- **WHEN** `TEAMS_CLIENT_ID` está configurado e não há token em cache
- **THEN** `authenticate()` DEVE iniciar Device Code Flow e retornar access_token

#### Scenario: graph_get sucesso

- **WHEN** Graph API retorna HTTP 200
- **THEN** `graph_get()` DEVE retornar dict com status e body

#### Scenario: graph_get erro 403

- **WHEN** Graph API retorna HTTP 403
- **THEN** `graph_get()` DEVE retornar dict com status 403

#### Scenario: list_my_meetings com resposta vazia

- **WHEN** Graph API retorna lista vazia de reuniões
- **THEN** `list_my_meetings()` DEVE exibir mensagem "Nenhuma reunião encontrada"

### Requirement: Testes para tldv_check.py

O arquivo `tests/test_tldv_check.py` DEVE conter testes unitários que mockam as chamadas HTTP à API do tl;dv.

#### Scenario: TldvClient.get com sucesso

- **WHEN** API do tl;dv retorna HTTP 200
- **THEN** `TldvClient.get()` DEVE retornar dict com status e body

#### Scenario: check_api_access com API key inválida

- **WHEN** API retorna HTTP 401
- **THEN** `check_api_access()` DEVE retornar False

#### Scenario: list_meetings retorna lista

- **WHEN** API retorna lista de reuniões
- **THEN** `list_meetings()` DEVE exibir tabela com os resultados

#### Scenario: get_transcript com transcrição disponível

- **WHEN** API retorna HTTP 200 com conteúdo de transcrição
- **THEN** `get_transcript()` DEVE exibir preview e salvar arquivo

### Requirement: Dependências de teste no pyproject.toml

O `pyproject.toml` DEVE incluir `pytest` e `pytest-mock` como dependências opcionais de teste.

#### Scenario: pytest está instalável

- **WHEN** `uv sync --group test` é executado
- **THEN** pytest DEVE estar disponível como comando
