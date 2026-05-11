## Context

O repositório tem 2 scripts Python na raiz (`teams_check.py`, `tldv_check.py`) mas o pyproject.toml e README já assumem estrutura `src/teams/` e `src/tldv/`. Não existe diretório `tests/`.

## Goals / Non-Goals

**Goals:**
- Mover scripts para `src/teams/` e `src/tldv/` com `git mv`
- Criar `tests/` com suíte de testes unitários usando PyTest + mocks
- Adicionar `pytest` e `pytest-mock` como dependências opcionais de teste

**Non-Goals:**
- Não alterar lógica de negócio dos scripts
- Não adicionar testes de integração (API real)
- Não modificar README (já está consistente com `src/`)

## Decisions

| Decisão | Opção escolhida | Alternativa | Razão |
|---------|----------------|-------------|-------|
| Movimentação | `git mv` | `mv` simples | Preserva histórico git |
| Framework de teste | PyTest + pytest-mock | unittest | PyTest é mais conciso, já consta no config.yaml |
| Mock de requests | `unittest.mock.patch` | `responses` library | Sem dependência extra, já vem com Python |
| Estrutura de testes | `tests/` raiz | `src/tests/` | Padrão PyProject |

## Risks / Trade-offs

- [Risco] Scripts externos que importem caminho absoluto da raiz quebram → Probabilidade baixa, projeto é isolado
- [Risco] TOKEN_CACHE_FILE usa `Path(".token_cache.json")` — caminho relativo ao CWD, não ao arquivo → Não é afetado pela movimentação
