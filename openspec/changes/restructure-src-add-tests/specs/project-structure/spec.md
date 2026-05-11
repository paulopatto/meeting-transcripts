## ADDED Requirements

### Requirement: Scripts organizados em src/

O projeto DEVE ter seus scripts Python organizados dentro do diretório `src/` seguindo a hierarquia:

- `src/teams/teams_check.py` — script de verificação do Microsoft Teams
- `src/tldv/tldv_check.py` — script de verificação do tl;dv

#### Scenario: scripts existem no novo caminho

- **WHEN** o repositório é clonado
- **THEN** os arquivos `src/teams/teams_check.py` e `src/tldv/tldv_check.py` DEVEM existir

#### Scenario: scripts não existem mais na raiz

- **WHEN** o repositório é clonado
- **THEN** os arquivos `teams_check.py` e `tldv_check.py` NÃO DEVEM existir na raiz

#### Scenario: entrada do pyproject.toml funciona

- **WHEN** o comando `uv run teams-check` é executado
- **THEN** ele DEVE resolver para `src.teams.teams_check:main`

### Requirement: Histórico git preservado

A movimentação DEVE ser feita com `git mv` para preservar o histórico de commits dos arquivos.

#### Scenario: git log mostra histórico completo

- **WHEN** `git log --follow src/teams/teams_check.py` é executado
- **THEN** os commits anteriores à movimentação DEVEM aparecer no log

## ADDED Requirements

### Requirement: Scripts organizados em src/

O projeto DEVE ter seus scripts Python organizados dentro do diretório `src/` seguindo a hierarquia:

- `src/teams/teams_check.py` — script de verificação do Microsoft Teams
- `src/tldv/tldv_check.py` — script de verificação do tl;dv

#### Scenario: scripts existem no novo caminho

- **WHEN** o repositório é clonado
- **THEN** os arquivos `src/teams/teams_check.py` e `src/tldv/tldv_check.py` DEVEM existir

#### Scenario: scripts não existem mais na raiz

- **WHEN** o repositório é clonado
- **THEN** os arquivos `teams_check.py` e `tldv_check.py` NÃO DEVEM existir na raiz

#### Scenario: entrada do pyproject.toml funciona

- **WHEN** o comando `uv run teams-check` é executado
- **THEN** ele DEVE resolver para `src.teams.teams_check:main`

### Requirement: Histórico git preservado

A movimentação DEVE ser feita com `git mv` para preservar o histórico de commits dos arquivos.

#### Scenario: git log mostra histórico completo

- **WHEN** `git log --follow src/teams/teams_check.py` é executado
- **THEN** os commits anteriores à movimentação DEVEM aparecer no log
