## Why

O arquivo `.agents/sdd-agent.md` descreve o comportamento do agente SDD mas não menciona explicitamente TDD (Test-Driven Development). Embora o `openspec/config.yaml` já declare "We always use TDD", essa diretriz não está materializada nas instruções do agente, o que faz com que o agente não siga o ciclo Red-Green-Refactor na prática.

## What Changes

- Adicionar passo explícito de TDD no `.agents/sdd-agent.md`
- Definir o ciclo Red-Green-Refactor como obrigatório
- Exigir execução dos testes (`uv run pytest tests/`) antes de considerar uma tarefa concluída
- Referenciar PyTest como framework de teste padrão

## Capabilities

### New Capabilities
- `sdd-agent-tdd`: Diretrizes TDD incorporadas ao agente SDD

### Modified Capabilities
- *(nenhuma — não há specs existentes)*

## Impact

- Apenas `.agents/sdd-agent.md` é modificado
- Nenhum código de aplicação é alterado
- O agente passa a seguir TDD rigorosamente em todas as tarefas futuras
