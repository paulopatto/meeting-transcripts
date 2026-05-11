---

name: github-pr
description: Verifica dependências, instala a CLI do GitHub se necessário e cria PRs seguindo o padrão OpenSpec.

---

# Skill: GitHub PR Manager (Multi-OS & Auto-Setup)

## 1. Verificação de Dependências (Pre-flight)

Antes de qualquer ação, o agente deve verificar se o comando `gh` está disponível.
Se não estiver, tente instalar usando o gerenciador de pacotes adequado ao sistema:

- **Se comando `gh` falhar:**
  - **macOS:** `brew install gh`
  - **Linux (Ubuntu/Debian):** `sudo apt update && sudo apt install gh -y`
  - **Windows (PowerShell):** `winget install --id GitHub.cli`
  - **Via NPM (Fallback/Node Wrapper):** `npm install -g @github/gh-cli` (Atenção: verifique se o binário é compatível).

## 2. Verificação de Autenticação

- Execute `gh auth status`.
- Se não estiver autenticado, peça ao usuário: "Por favor, execute `gh auth login` no seu terminal e me avise quando terminar."

## 3. Fluxo de Criação de Pull Request

Uma vez validado, siga os passos abaixo dentro da pasta do worktree (`.opencode/worktrees/<feature-name>`):

```bash
# 1. Garante que as specs foram movidas/arquivadas se necessário
# 2. Envia a branch do worktree para o remoto
git push origin HEAD

# 3. Extrai contexto do OpenSpec para o corpo do PR
export FEATURE_NAME=$(basename $(pwd))
export SPEC_PATH="../../../openspec/changes/active/$FEATURE_NAME/tasks.md"

# 4. Cria o PR
gh pr create \
  --title "<type>($FEATURE_NAME): <Titulo da tarefa>" \
  --body "## 🎯 Objetivo
Baseado na especificação OpenSpec.

## ✅ Checklist de Tarefas (OpenSpec)
$(cat $SPEC_PATH | grep '\[x\]' || echo 'Verificar tasks.md')

---
*Gerado automaticamente pelo Agente via OpenCode.*" \
  --assignee "@me"
```

## 4. Tratamento de Erros por Plataforma

- **Windows:** Utilize `powershell.exe` para comandos `gh` se o agente estiver em ambiente CMD.
- **Linux/Mac:** Utilize `bash`.
