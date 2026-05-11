## Context

`.agents/sdd-agent.md` define as regras de comportamento do agente SDD. Atualmente tem 4 passos (ler specs, verificar changes, usar sdd-workflow, validar CLI). `openspec/config.yaml` já declara "We always use TDD", mas o agente não tem instrução explícita para seguir TDD.

## Goals / Non-Goals

**Goals:**
- Adicionar passo 5: seguir ciclo TDD (Red-Green-Refactor)
- Adicionar passo 6: executar `uv run pytest tests/` antes de considerar tarefa concluída
- Referenciar PyTest como framework padrão

**Non-Goals:**
- Não alterar a estrutura do arquivo além dos novos passos
- Não modificar `openspec/config.yaml`
- Não alterar outros arquivos de agente

## Decisions

| Decisão | Escolha | Alternativa | Razão |
|---------|---------|-------------|-------|
| Posição dos novos passos | Após passo 4 | Antes ou misturado | Preserva a sequência lógica existente |
| Framework citado | PyTest | unittest | Já definido no config.yaml |

## Risks / Trade-offs

- [Risco] Agentes antigos podem ignorar os novos passos → Treinamento/documentação cobre
- Nenhum risco técnico — mudança puramente documental/instrutiva
