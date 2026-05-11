"""
tldv_check.py
=============
Verifica seu acesso à API do tl;dv e tenta baixar transcrições
de reuniões gravadas — incluindo diagnóstico claro do que está
disponível no plano FREE vs pago.

Documentação oficial: https://doc.tldv.io/

Uso:
    uv run src/tldv/tldv_check.py
    uv run src/tldv/tldv_check.py --meeting-id <ID>
    uv run src/tldv/tldv_check.py --list
    uv run src/tldv/tldv_check.py --search "nome da reunião"
"""

import argparse
import os
import sys

import requests
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

load_dotenv()

console = Console()

API_BASE = "https://api.tldv.io/v1a"  # endpoint público documentado


class TldvClient:
    def __init__(self, api_key: str):
        self.session = requests.Session()
        self.session.headers.update({
            "x-api-key": api_key,
            "Content-Type": "application/json",
        })

    def get(self, path: str, params: dict = None) -> dict:
        resp = self.session.get(f"{API_BASE}{path}", params=params or {})
        return {
            "status": resp.status_code,
            "body":   resp.json() if resp.content else {},
            "headers": dict(resp.headers),
        }


# ── Verificação de conectividade e plano ─────────────────────────────────────

def check_api_access(client: TldvClient) -> bool:
    """Testa autenticação e mostra info do plano/conta."""
    console.rule("[bold]1. Verificando acesso à API do tl;dv")

    result = client.get("/meetings", params={"limit": 1})
    status = result["status"]

    if status == 200:
        console.print("[green]✓ API Key válida – acesso autenticado![/green]")
        return True

    if status == 401:
        console.print(Panel(
            "[red]✗ HTTP 401 – API Key inválida ou não encontrada[/red]\n\n"
            "Verifique [bold]TLDV_API_KEY[/bold] no seu .env\n\n"
            "Para obter sua API Key:\n"
            "  1. Acesse https://app.tldv.io/settings/api\n"
            "  2. Gere ou copie sua chave\n\n"
            "[yellow]⚠ Atenção:[/yellow] O plano FREE pode não ter acesso à API. "
            "Verifique em Settings > Plan se a seção de API está disponível.",
            title="Sem acesso",
            border_style="red",
        ))
        return False

    if status == 403:
        console.print(Panel(
            "[yellow]✗ HTTP 403 – Acesso negado[/yellow]\n\n"
            "Sua conta não tem permissão para usar a API.\n\n"
            "[bold]Plano FREE do tl;dv:[/bold]\n"
            "  • A API pública estava disponível em versões anteriores, mas "
            "atualmente pode estar restrita a planos pagos (Pro/Business).\n"
            "  • Verifique em: https://tldv.io/pricing\n\n"
            "[bold]Alternativas para plano FREE:[/bold]\n"
            "  • Export manual: abra a reunião > botão Share > Export as text\n"
            "  • Webhook (se disponível no seu plano): Settings > Integrations",
            title="Plano sem acesso à API",
            border_style="yellow",
        ))
        return False

    if status == 404:
        console.print(Panel(
            f"[yellow]HTTP 404 – Endpoint não encontrado[/yellow]\n\n"
            f"URL tentada: {API_BASE}/meetings\n\n"
            "A API do tl;dv pode ter mudado. Verifique: https://doc.tldv.io/",
            title="Endpoint não encontrado",
            border_style="yellow",
        ))
        return False

    console.print(f"[red]Resposta inesperada: HTTP {status}[/red]")
    console.print(f"[dim]{result['body']}[/dim]")
    return False


# ── Listagem de reuniões ──────────────────────────────────────────────────────

def list_meetings(client: TldvClient, search: str = None) -> list:
    """Lista reuniões gravadas com tl;dv."""
    console.rule("[bold]2. Listando reuniões gravadas")

    params = {"limit": 20}
    if search:
        params["search"] = search
        console.print(f"[dim]Filtrando por: '{search}'[/dim]")

    result = client.get("/meetings", params=params)
    status = result["status"]

    if status != 200:
        console.print(f"[red]Erro {status}: {result['body']}[/red]")
        return []

    body     = result["body"]
    meetings = body.get("meetings", body.get("data", body.get("results", [])))

    if not meetings:
        console.print("[yellow]Nenhuma reunião encontrada.[/yellow]")
        console.print("[dim]Possíveis razões:[/dim]")
        console.print("  • Nenhuma gravação feita ainda com esta conta")
        console.print("  • A conta usada para a API key é diferente da que tem as gravações")
        return []

    table = Table("ID", "Título", "Data", "Duração", "Participantes", "Tem Transcrição?")
    for m in meetings:
        duration_s = m.get("duration", 0)
        duration   = f"{duration_s // 60}min" if duration_s else "N/A"

        # Campos podem variar por versão da API
        has_transcript = "✓" if m.get("transcript") or m.get("hasTranscript") else "?"

        table.add_row(
            str(m.get("id", m.get("_id", "N/A"))),
            (m.get("title") or m.get("name") or "(sem título)")[:40],
            str(m.get("startedAt") or m.get("date") or m.get("createdAt") or "N/A")[:19],
            duration,
            str(m.get("attendeesCount") or len(m.get("attendees", [])) or "N/A"),
            has_transcript,
        )

    console.print(table)
    console.print(f"\n[dim]Total retornado: {len(meetings)} reuniões[/dim]")
    return meetings


# ── Transcrição de reunião específica ────────────────────────────────────────

def get_transcript(client: TldvClient, meeting_id: str) -> None:
    """Tenta baixar a transcrição de uma reunião pelo ID."""
    console.rule(f"[bold]3. Buscando transcrição: {meeting_id}")

    # Endpoint principal de transcrição
    endpoints_to_try = [
        f"/meetings/{meeting_id}/transcript",
        f"/meetings/{meeting_id}/transcripts",
        f"/meetings/{meeting_id}",
    ]

    for path in endpoints_to_try:
        result = client.get(path)
        status = result["status"]
        body   = result["body"]

        console.print(f"\n[dim]GET {API_BASE}{path}[/dim]")
        console.print(f"Status: {_status_label(status)}")

        if status == 200:
            _display_transcript(body, meeting_id, path)
            return

        if status == 403:
            console.print("[yellow]  → Acesso negado neste endpoint[/yellow]")
        elif status == 404:
            console.print("[dim]  → Não encontrado, tentando próximo endpoint…[/dim]")
        else:
            console.print(f"[dim]  → {body}[/dim]")

    console.print(Panel(
        "[yellow]Nenhum endpoint retornou transcrição.[/yellow]\n\n"
        "Possíveis razões:\n"
        "  • ID da reunião incorreto\n"
        "  • Reunião não tem transcrição gerada\n"
        "  • Seu plano não permite acesso a transcrições via API\n\n"
        "Use [cyan]--list[/cyan] para ver IDs de reuniões válidas.",
        title="Transcrição não disponível",
        border_style="yellow",
    ))


def _display_transcript(body: dict, meeting_id: str, path: str) -> None:
    """Exibe e salva a transcrição encontrada."""
    # Tenta extrair o texto de diferentes formatos de resposta
    transcript_text = None

    if isinstance(body, str):
        transcript_text = body
    elif isinstance(body, dict):
        # Formatos possíveis da API do tl;dv
        transcript_text = (
            body.get("transcript")
            or body.get("content")
            or body.get("text")
            or body.get("vtt")
        )

        # Formato com segmentos/utterances
        if not transcript_text:
            utterances = body.get("utterances") or body.get("segments") or []
            if utterances:
                lines = []
                for u in utterances:
                    speaker = u.get("speaker") or u.get("name") or "?"
                    text    = u.get("text") or u.get("content") or ""
                    start   = u.get("startTime") or u.get("start") or ""
                    lines.append(f"[{start}] {speaker}: {text}")
                transcript_text = "\n".join(lines)

    if transcript_text:
        preview = transcript_text[:500]
        console.print(Panel(
            f"[green]✓ Transcrição obtida![/green]\n\n{preview}{'…' if len(transcript_text) > 500 else ''}",
            title="Preview (500 chars)",
        ))

        # Salvar arquivo
        output_file = f"transcript_{meeting_id}.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(transcript_text)
        console.print(f"\n[green]✓ Transcrição completa salva em: [bold]{output_file}[/bold][/green]")
    else:
        # Mostra a estrutura bruta para diagnóstico
        console.print(Panel(
            f"[yellow]Resposta recebida mas sem campo de transcrição reconhecido.[/yellow]\n\n"
            f"Estrutura da resposta:\n[dim]{str(body)[:600]}[/dim]",
            title="Diagnóstico – estrutura bruta",
            border_style="yellow",
        ))


def _status_label(status: int) -> str:
    colors = {200: "green", 403: "yellow", 404: "dim", 401: "red"}
    color  = colors.get(status, "white")
    return f"[{color}]HTTP {status}[/{color}]"


# ── Diagnóstico de plano FREE ─────────────────────────────────────────────────

def show_free_plan_info() -> None:
    console.print(Panel(
        "[bold]tl;dv – Plano FREE: o que funciona via API?[/bold]\n\n"
        "✓ [green]Disponível no FREE (quando API Key existe):[/green]\n"
        "  • Listar reuniões gravadas\n"
        "  • Metadados básicos (título, data, participantes)\n"
        "  • Highlights/clipes marcados manualmente\n\n"
        "⚠ [yellow]Pode ser restrito (depende da versão/conta):[/yellow]\n"
        "  • Download completo de transcrições\n"
        "  • Export em VTT/SRT\n"
        "  • Webhooks automáticos\n\n"
        "✗ [red]Geralmente requer plano pago:[/red]\n"
        "  • Resumos automáticos via IA\n"
        "  • Integrações com Jira/Notion/Slack\n"
        "  • Transcrições em múltiplos idiomas\n\n"
        "[dim]Ref: https://tldv.io/pricing | https://doc.tldv.io/[/dim]",
        title="📋 Guia de Acesso – tl;dv FREE",
        border_style="blue",
    ))


# ── Entrypoint ────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Verifica acesso à API do tl;dv e baixa transcrições."
    )
    parser.add_argument("--meeting-id", help="ID da reunião para buscar transcrição")
    parser.add_argument("--list",       action="store_true", help="Lista reuniões gravadas")
    parser.add_argument("--search",     help="Filtra reuniões por título")
    parser.add_argument("--plan-info",  action="store_true", help="Mostra o que está disponível no plano FREE")
    args = parser.parse_args()

    console.print(Panel(
        "[bold]tl;dv Transcript Access Checker[/bold]\n"
        "Verifica acesso à API pública do tl;dv",
        border_style="blue",
    ))

    api_key = os.getenv("TLDV_API_KEY", "")
    if not api_key:
        console.print("[bold red]❌ TLDV_API_KEY não configurado no .env[/bold red]")
        console.print("Obtenha sua chave em: https://app.tldv.io/settings/api")
        if args.plan_info:
            show_free_plan_info()
        sys.exit(1)

    if args.plan_info:
        show_free_plan_info()
        return

    client = TldvClient(api_key)

    # Sempre verifica acesso primeiro
    if not check_api_access(client):
        show_free_plan_info()
        sys.exit(1)

    meeting_id = args.meeting_id or os.getenv("TLDV_MEETING_ID", "")

    if meeting_id:
        get_transcript(client, meeting_id)
    elif args.list or args.search:
        meetings = list_meetings(client, search=args.search)
        if meetings and not args.meeting_id:
            first_id = meetings[0].get("id") or meetings[0].get("_id", "")
            console.print(
                f"\n[dim]💡 Para ver a transcrição: "
                f"[cyan]uv run src/tldv/tldv_check.py --meeting-id {first_id}[/cyan][/dim]"
            )
    else:
        # Sem argumentos: verifica tudo
        meetings = list_meetings(client)
        if meetings:
            first_id = str(meetings[0].get("id") or meetings[0].get("_id", ""))
            if first_id:
                get_transcript(client, first_id)


if __name__ == "__main__":
    main()
