## Why

Atualmente os scripts Python estão soltos na raiz do projeto, mas o README e o pyproject.toml já foram projetados assumindo uma estrutura `src/`. Isso causa inconsistência — comandos do README como `uv run src/teams/teams_check.py` não funcionam. Além disso, o projeto não possui testes automatizados, o que dificulta garantir que mudanças futuras não quebrem funcionalidades existentes.

## What Changes

- Mover `teams_check.py` para `src/teams/teams_check.py` e `tldv_check.py` para `src/tldv/tldv_check.py` usando `git mv` para preservar histórico
- Criar diretório `tests/` com estrutura de testes usando PyTest
- Adicionar `pytest` e `pytest-mock` como dependências opcionais de teste no `pyproject.toml`
- Escrever testes com mock das APIs externas (Microsoft Graph e tl;dv) para validar as funcionalidades principais

## Capabilities

### New Capabilities
- `project-structure`: Organização padronizada do projeto com código em `src/` e testes em `tests/`
- `test-suite`: Suite de testes automatizados para validar as funcionalidades dos scripts

### Modified Capabilities
- *(nenhuma — não há specs existentes)*

## Impact

- `teams_check.py` e `tldv_check.py` mudam de local — scripts que importem caminho absoluto quebram
- `pyproject.toml` ganha seção `[project.optional-dependencies] test`
- Comandos do README passam a funcionar corretamente
- Nenhuma mudança na lógica de negócio dos scripts
