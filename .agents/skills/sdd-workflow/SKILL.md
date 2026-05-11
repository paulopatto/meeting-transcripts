---
name: sdd-workflow
description: Gerencia o ciclo de vida de features com OpenSpec e git-worktrees.
---

# Fluxo de Trabalho SDD

Sempre que uma nova funcionalidade for solicitada, siga esta sequência:

## Passo 1: Leitura do Plano

- O agente deve ler obrigatoriamente `openspec/changes/active/<feature_name>/tasks.md`.
- Se o plano não existir, use `openspec propose` para criá-lo antes de codar.

## Passo 2: Isolamento com Worktree

Para cada tarefa ou feature, execute:

```bash
# Cria uma branch e um worktree isolado dentro de .opencode/worktrees
git worktree add -b feature/<nome-da-feature> .opencode/worktrees/<nome-da-feature> main
```

## Passo 3: Execução

- Mude o diretório de trabalho para o worktree: `cd .opencode/worktrees/<nome-da-feature>`.
- Realize as tarefas descritas no `tasks.md` do OpenSpec.
- Após concluir, faça o commit seguindo o padrão conventional commits
- Se abra um pull request para a `main` no github do projeto.
- Descreve o que o pull request faz com base na spec.

## Passo 4: Limpeza

```bash
git worktree remove .opencode/worktrees/<nome-da-feature>
git branch -d feature/<nome-da-feature>
openspec archive <nome-da-feature>
```
