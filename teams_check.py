"""
teams_check.py
==============
Verifica seu acesso a transcrições de reuniões do Microsoft Teams via
Microsoft Graph API — mesmo sem ser o organizador da reunião.

Fluxo de autenticação: Device Code Flow (delegated), que funciona com
a conta do próprio usuário, sem precisar de permissões de admin.

Uso:
    uv run src/teams/teams_check.py
    uv run src/teams/teams_check.py --meeting-id <ID>
    uv run src/teams/teams_check.py --list-meetings
"""

import argparse
import json
import sys
import time
import webbrowser
from pathlib import Path

import requests
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

load_dotenv()
import os

console = Console()

# ── Configuração ──────────────────────────────────────────────────────────────

CLIENT_ID  = os.getenv("TEAMS_CLIENT_ID", "")
TENANT_ID  = os.getenv("TEAMS_TENANT_ID", "common")
GRAPH_BASE = "https://graph.microsoft.com/v1.0"

SCOPES = [
    "OnlineMeetings.Read",
    "OnlineMeetingTranscript.Read.All",
    "offline_access",
]

TOKEN_CACHE_FILE = Path(".token_cache.json")


# ── Autenticação: Device Code Flow ────────────────────────────────────────────

def _token_endpoint(tenant: str) -> str:
    return f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"

def _device_code_endpoint(tenant: str) -> str:
    return f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/devicecode"


def load_cached_token() -> dict | None:
    if TOKEN_CACHE_FILE.exists():
        data = json.loads(TOKEN_CACHE_FILE.read_text())
        if data.get("expires_at", 0) > time.time() + 60:
            return data
        # Tenta refresh
        if data.get("refresh_token"):
            return refresh_token(data["refresh_token"])
    return None


def save_token(token_data: dict) -> None:
    token_data["expires_at"] = time.time() + int(token_data.get("expires_in", 3600))
    TOKEN_CACHE_FILE.write_text(json.dumps(token_data, indent=2))


def refresh_token(refresh_tok: str) -> dict | None:
    resp = requests.post(_token_endpoint(TENANT_ID), data={
        "client_id":    CLIENT_ID,
        "grant_type":   "refresh_token",
        "refresh_token": refresh_tok,
        "scope":        " ".join(SCOPES),
    })
    if resp.ok:
        token = resp.json()
        save_token(token)
        return token
    return None


def authenticate() -> str:
    """Retorna access_token. Usa cache ou inicia Device Code Flow."""
    if not CLIENT_ID:
        console.print("[bold red]❌ TEAMS_CLIENT_ID não configurado no .env[/bold red]")
        console.print("Siga as instruções em .env.example para criar o App Registration.")
        sys.exit(1)

    cached = load_cached_token()
    if cached:
        console.print("[dim]✓ Usando token em cache[/dim]")
        return cached["access_token"]

    # Iniciar Device Code Flow
    resp = requests.post(_device_code_endpoint(TENANT_ID), data={
        "client_id": CLIENT_ID,
        "scope":     " ".join(SCOPES),
    })
    resp.raise_for_status()
    flow = resp.json()

    console.print(Panel(
        f"[bold yellow]Autenticação necessária[/bold yellow]\n\n"
        f"1. Abra: [link]{flow['verification_uri']}[/link]\n"
        f"2. Digite o código: [bold cyan]{flow['user_code']}[/bold cyan]\n\n"
        f"(O navegador será aberto automaticamente em 3s...)",
        title="Microsoft Login",
    ))
    time.sleep(3)
    webbrowser.open(flow["verification_uri"])

    # Poll até autenticar
    interval = int(flow.get("interval", 5))
    expires  = time.time() + int(flow.get("expires_in", 900))

    with console.status("Aguardando autenticação..."):
        while time.time() < expires:
            time.sleep(interval)
            poll = requests.post(_token_endpoint(TENANT_ID), data={
                "client_id":   CLIENT_ID,
                "grant_type":  "urn:ietf:params:oauth:grant-type:device_code",
                "device_code": flow["device_code"],
            })
            data = poll.json()
            if "access_token" in data:
                save_token(data)
                console.print("[green]✓ Autenticado com sucesso![/green]")
                return data["access_token"]
            if data.get("error") not in ("authorization_pending", "slow_down"):
                console.print(f"[red]Erro de autenticação: {data}[/red]")
                sys.exit(1)

    console.print("[red]Timeout na autenticação.[/red]")
    sys.exit(1)


# ── Graph API helpers ─────────────────────────────────────────────────────────

def graph_get(token: str, path: str, params: dict = None) -> dict:
    resp = requests.get(
        f"{GRAPH_BASE}{path}",
        headers={"Authorization": f"Bearer {token}"},
        params=params or {},
    )
    return {"status": resp.status_code, "body": resp.json() if resp.content else {}}


# ── Funcionalidades ───────────────────────────────────────────────────────────

def list_my_meetings(token: str) -> None:
    """Lista reuniões online das quais você participou (criadas por você via Graph)."""
    console.rule("[bold]Suas reuniões online (criadas via Graph/Teams)")

    result = graph_get(token, "/me/onlineMeetings")

    if result["status"] == 403:
        console.print(Panel(
            "[yellow]⚠ HTTP 403 – Sem permissão para listar /me/onlineMeetings[/yellow]\n\n"
            "Isso é comum quando a permissão [bold]OnlineMeetings.Read[/bold] não foi "
            "concedida ou o admin bloqueou o acesso delegado.\n\n"
            "Alternativa: use o Meeting ID diretamente com [cyan]--meeting-id[/cyan]",
            title="Acesso negado",
        ))
        return

    if result["status"] != 200:
        console.print(f"[red]Erro {result['status']}: {result['body']}[/red]")
        return

    meetings = result["body"].get("value", [])
    if not meetings:
        console.print("[dim]Nenhuma reunião encontrada via API.[/dim]")
        return

    table = Table("ID (parcial)", "Assunto", "Início", "Organizador")
    for m in meetings:
        table.add_row(
            m.get("id", "")[:30] + "…",
            m.get("subject", "(sem assunto)"),
            m.get("startDateTime", ""),
            m.get("participants", {}).get("organizer", {}).get("upn", ""),
        )
    console.print(table)


def check_transcript_access(token: str, meeting_id: str) -> None:
    """Verifica e tenta baixar transcrições de uma reunião específica."""
    console.rule(f"[bold]Verificando transcrições: {meeting_id[:40]}…")

    # 1. Listar transcrições disponíveis
    path   = f"/me/onlineMeetings/{meeting_id}/transcripts"
    result = graph_get(token, path)

    status = result["status"]
    body   = result["body"]

    _print_access_result(status, body, path)

    if status != 200:
        _suggest_alternatives(status, body)
        return

    transcripts = body.get("value", [])
    if not transcripts:
        console.print("[yellow]⚠ A reunião existe mas não possui transcrições registradas.[/yellow]")
        console.print("[dim]Possíveis razões: transcrição não foi ativada, ou ainda está processando.[/dim]")
        return

    console.print(f"\n[green]✓ {len(transcripts)} transcrição(ões) encontrada(s)![/green]\n")

    for i, t in enumerate(transcripts, 1):
        transcript_id = t.get("id", "")
        console.print(f"[bold]Transcrição {i}:[/bold]")
        console.print(f"  ID:         {transcript_id}")
        console.print(f"  Criada em:  {t.get('createdDateTime', 'N/A')}")
        console.print(f"  Idioma:     {t.get('transcriptContentUrl', 'N/A')}")

        # 2. Tentar baixar o conteúdo
        content_path = f"/me/onlineMeetings/{meeting_id}/transcripts/{transcript_id}/content"
        content_result = graph_get(token, content_path)

        if content_result["status"] == 200:
            content = content_result["body"]
            preview = str(content)[:300]
            console.print(Panel(
                f"[green]✓ Conteúdo acessível![/green]\n\n[dim]{preview}…[/dim]",
                title="Preview da transcrição",
            ))
        else:
            console.print(f"  [yellow]⚠ Conteúdo não acessível: HTTP {content_result['status']}[/yellow]")
            console.print(f"  [dim]{content_result['body']}[/dim]")


def _print_access_result(status: int, body: dict, path: str) -> None:
    status_map = {
        200: ("[green]✓ HTTP 200 – Acesso permitido[/green]", ""),
        403: ("[red]✗ HTTP 403 – Acesso negado[/red]", "Sem permissão para este endpoint."),
        404: ("[yellow]⚠ HTTP 404 – Reunião não encontrada[/yellow]", "O Meeting ID pode estar errado ou a reunião foi deletada."),
        401: ("[red]✗ HTTP 401 – Não autenticado[/red]", "Token inválido ou expirado."),
    }
    color_msg, hint = status_map.get(status, (f"[yellow]HTTP {status}[/yellow]", ""))
    console.print(f"\nEndpoint: [dim]{path}[/dim]")
    console.print(f"Status:   {color_msg}")
    if hint:
        console.print(f"[dim]{hint}[/dim]")
    if body.get("error"):
        console.print(f"Detalhe:  [dim]{body['error'].get('message', body)}[/dim]")


def _suggest_alternatives(status: int, body: dict) -> None:
    error_code = body.get("error", {}).get("code", "")
    console.print()

    if status == 403 or error_code in ("AccessDenied", "Forbidden"):
        console.print(Panel(
            "[bold]Próximos passos para obter acesso:[/bold]\n\n"
            "1. [cyan]Se você não é o organizador[/cyan]: apenas o organizador pode acessar "
            "transcrições via /me/onlineMeetings. Peça ao organizador para compartilhar.\n\n"
            "2. [cyan]Permissão de admin[/cyan]: sua organização pode precisar conceder "
            "[bold]OnlineMeetingTranscript.Read.All[/bold] no tenant.\n\n"
            "3. [cyan]Alternativa – CallRecords API[/cyan]: se sua conta tem acesso ao "
            "recurso de gravação, tente /communications/callRecords.\n\n"
            "4. [cyan]Obter o Meeting ID correto[/cyan]: o ID interno do Graph é diferente "
            "do link de convite. Use [bold]--list-meetings[/bold] para ver IDs válidos.",
            title="💡 Diagnóstico",
            border_style="yellow",
        ))

    if status == 404:
        console.print(Panel(
            "O Meeting ID precisa ser o ID interno do Graph, não o link do Teams.\n\n"
            "Para obter IDs válidos:\n"
            "  [cyan]uv run src/teams/teams_check.py --list-meetings[/cyan]",
            title="💡 Como obter o Meeting ID",
            border_style="dim",
        ))


# ── Entrypoint ────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Verifica acesso a transcrições do Microsoft Teams via Graph API."
    )
    parser.add_argument("--meeting-id", help="Meeting ID interno do Graph para verificar transcrições")
    parser.add_argument("--list-meetings", action="store_true", help="Lista suas reuniões online")
    args = parser.parse_args()

    console.print(Panel(
        "[bold]Teams Transcript Access Checker[/bold]\n"
        "Verifica seu acesso via Microsoft Graph API",
        border_style="blue",
    ))

    token = authenticate()

    meeting_id = args.meeting_id or os.getenv("TEAMS_MEETING_ID", "")

    if args.list_meetings or not meeting_id:
        list_my_meetings(token)
        if not meeting_id:
            console.print(
                "\n[dim]💡 Passe [cyan]--meeting-id <ID>[/cyan] para verificar transcrições de uma reunião específica.[/dim]"
            )
    else:
        check_transcript_access(token, meeting_id)


if __name__ == "__main__":
    main()
