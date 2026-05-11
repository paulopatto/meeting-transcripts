# meeting-transcripts

Scripts Python para verificar acesso a transcrições de reuniões via API do **Microsoft Teams** e **tl;dv**.

## Estrutura

```
meeting-transcripts/
├── src/
│   ├── teams/
│   │   └── teams_check.py   # Verifica transcrições via Microsoft Graph API
│   └── tldv/
│       └── tldv_check.py    # Verifica transcrições via API do tl;dv
├── .env.example             # Template de variáveis de ambiente
├── pyproject.toml
└── README.md
```

## Setup

```bash
# 1. Copiar e preencher variáveis de ambiente
cp .env.example .env

# 2. Instalar dependências (uv resolve tudo automaticamente)
uv sync
```

---

## Teams (`teams_check.py`)

### Pré-requisitos

Crie um **App Registration** no Azure AD:

1. Acesse [portal.azure.com](https://portal.azure.com)
2. Azure Active Directory → App registrations → **New registration**
3. Dê um nome (ex: `transcript-checker`) e registre
4. Em **API permissions** adicione (Microsoft Graph, Delegated):
   - `OnlineMeetings.Read`
   - `OnlineMeetingTranscript.Read.All`
5. Em **Authentication** → Add platform → Mobile/Desktop → URI: `http://localhost:8080`
6. Copie o **Application (client) ID** e o **Directory (tenant) ID** para o `.env`

> **Nota:** Não é necessário ser admin para criar o App Registration, mas o admin do tenant pode precisar conceder consent às permissões.

### Uso

```bash
# Ver se você tem reuniões registradas no Graph (as que você criou)
uv run src/teams/teams_check.py --list-meetings

# Verificar transcrições de uma reunião específica
uv run src/teams/teams_check.py --meeting-id <MEETING_ID>

# Rodar diagnóstico completo (se TEAMS_MEETING_ID estiver no .env)
uv run src/teams/teams_check.py
```

### Limitação importante

A Microsoft Graph API (`/me/onlineMeetings`) só retorna reuniões **criadas pelo próprio usuário autenticado**. Se você não é o organizador, o endpoint retorna 403 ou lista vazia. Nesse caso:

- Peça ao organizador o Meeting ID interno (≠ link de convite)
- O organizador pode fazer a chamada de API e te passar a transcrição
- Considere usar o **canal de gravação** no Teams, que fica acessível a todos os participantes

---

## tl;dv (`tldv_check.py`)

### Pré-requisitos

1. Acesse [app.tldv.io/settings/api](https://app.tldv.io/settings/api)
2. Gere ou copie sua API Key
3. Cole no `.env` como `TLDV_API_KEY`

> **Plano FREE:** A disponibilidade da API varia. O script detecta automaticamente o que está acessível e informa o diagnóstico.

### Uso

```bash
# Verificar acesso + listar reuniões
uv run src/tldv/tldv_check.py --list

# Buscar reuniões por título
uv run src/tldv/tldv_check.py --search "reunião de segurança"

# Baixar transcrição de reunião específica
uv run src/tldv/tldv_check.py --meeting-id <ID>

# Ver o que está disponível no plano FREE
uv run src/tldv/tldv_check.py --plan-info

# Diagnóstico completo (lista + primeira transcrição)
uv run src/tldv/tldv_check.py
```

### Saída

Se a transcrição for acessível, ela é salva automaticamente em `transcript_<ID>.txt`.

---

## Variáveis de ambiente

| Variável | Descrição |
|---|---|
| `TEAMS_CLIENT_ID` | Client ID do App Registration no Azure |
| `TEAMS_TENANT_ID` | Tenant ID da sua organização |
| `TEAMS_MEETING_ID` | (Opcional) Meeting ID padrão para testar |
| `TLDV_API_KEY` | API Key do tl;dv |
| `TLDV_MEETING_ID` | (Opcional) Meeting ID padrão do tl;dv |
