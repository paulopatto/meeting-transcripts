## ADDED Requirements

### Requirement: Agente SDD segue TDD

O `.agents/sdd-agent.md` DEVE incluir instruções explícitas para seguir o ciclo TDD (Test-Driven Development).

#### Scenario: ciclo Red-Green-Refactor é obrigatório

- **WHEN** o agente inicia uma tarefa de implementação
- **THEN** ele DEVE primeiro escrever um teste que falha (Red)
- **THEN** ele DEVE implementar o código mínimo para passar (Green)
- **THEN** ele DEVE refatorar mantendo os testes verdes (Refactor)

### Requirement: Execução de testes antes de concluir

O `.agents/sdd-agent.md` DEVE exigir que `uv run pytest tests/` seja executado antes de considerar uma tarefa concluída.

#### Scenario: testes falham impedem conclusão

- **WHEN** `uv run pytest tests/` falha
- **THEN** a tarefa NÃO DEVE ser marcada como concluída

#### Scenario: testes passam permitem conclusão

- **WHEN** `uv run pytest tests/` passa (exit code 0)
- **THEN** a tarefa PODE ser marcada como concluída

### Requirement: PyTest como framework padrão

O `.agents/sdd-agent.md` DEVE referenciar PyTest como o framework de teste padrão do projeto.

#### Scenario: PyTest é citado nas instruções

- **WHEN** o arquivo `.agents/sdd-agent.md` é lido
- **THEN** PyTest DEVE ser mencionado como framework padrão
