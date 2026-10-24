import urllib.parse
import webbrowser
from typing import Dict, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

AI_SERVICES: Dict[str, Dict[str, str]] = {
    "1": {
        "name": "ChatGPT",
        "url": "https://chatgpt.com",
        "search_url": "https://chatgpt.com/?q={query}",
        "desc": "OpenAI Flagship Chat Assistant",
    },
    "2": {
        "name": "Claude",
        "url": "https://claude.ai",
        "search_url": "https://claude.ai/new",
        "desc": "Anthropic AI for coding, writing & reasoning",
    },
    "3": {
        "name": "DeepSeek",
        "url": "https://chat.deepseek.com",
        "search_url": "https://chat.deepseek.com",
        "desc": "DeepSeek-V3 & R1 reasoning models",
    },
    "4": {
        "name": "Google Gemini",
        "url": "https://gemini.google.com",
        "search_url": "https://gemini.google.com/app",
        "desc": "Google Multimodal Gemini Assistant",
    },
    "5": {
        "name": "Perplexity AI",
        "url": "https://www.perplexity.ai",
        "search_url": "https://www.perplexity.ai/search?q={query}",
        "desc": "AI Search Engine with real-time sources",
    },
    "6": {
        "name": "HuggingChat",
        "url": "https://huggingface.co/chat",
        "search_url": "https://huggingface.co/chat",
        "desc": "Open-Source Models Hub (Llama, Mistral, Qwen)",
    },
    "7": {
        "name": "Grok",
        "url": "https://x.com/i/grok",
        "search_url": "https://x.com/i/grok",
        "desc": "xAI real-time information assistant",
    },
    "8": {
        "name": "v0 by Vercel",
        "url": "https://v0.dev",
        "search_url": "https://v0.dev",
        "desc": "Generative UI & Full-stack React Component Builder",
    },
    "9": {
        "name": "Mistral Le Chat",
        "url": "https://chat.mistral.ai",
        "search_url": "https://chat.mistral.ai",
        "desc": "Mistral AI Frontier Models",
    },
}


def open_ai_service(key_or_name: str, query: Optional[str] = None) -> bool:
    """Open specified AI web service in user's default browser."""
    target_key = None
    key_lower = key_or_name.lower().strip()

    if key_lower in AI_SERVICES:
        target_key = key_lower
    else:
        for k, v in AI_SERVICES.items():
            if key_lower in v["name"].lower():
                target_key = k
                break

    if not target_key:
        console.print(f"[bold red]AI Service '{key_or_name}' tidak ditemukan.[/bold red]")
        return False

    service = AI_SERVICES[target_key]
    if query:
        encoded_query = urllib.parse.quote(query)
        url = service["search_url"].format(query=encoded_query)
    else:
        url = service["url"]

    console.print(f"[bold green]🚀 Membuka {service['name']} di browser:[/bold green] {url}")
    webbrowser.open(url)
    return True


def interactive_ai_launcher():
    """Display interactive AI menu and allow launching by numbers or name."""
    table = Table(title="🤖 AI Web Shortcuts Launcher", expand=True)
    table.add_column("No", style="bold cyan", width=4, justify="center")
    table.add_column("AI Service", style="bold white", width=18)
    table.add_column("Deskripsi", style="dim", ratio=1)
    table.add_column("Web URL", style="blue")

    for k, v in AI_SERVICES.items():
        table.add_row(k, v["name"], v["desc"], v["url"])

    console.print(table)
    console.print(
        "\n[dim]Pilih nomor layanan (misal: [bold white]1[/bold white] atau [bold white]1,3,4[/bold white] atau ketik nama seperti [bold white]deepseek[/bold white]).[/dim]"
    )
    console.print("[dim]Ketik [bold cyan]'all'[/bold cyan] untuk buka semua, atau [bold cyan]'q'[/bold cyan] untuk batal.[/dim]\n")

    choice = console.input("[bold cyan]Pilihanmu>[/bold cyan] ").strip()
    if not choice or choice.lower() in ("q", "exit", "cancel"):
        return

    if choice.lower() == "all":
        for k in AI_SERVICES:
            open_ai_service(k)
        return

    # Check for prompt query option
    ask_query = console.input("[bold yellow]Ingin buka dengan query pencarian langsung? (Enter untuk lewati):[/bold yellow] ").strip()
    query = ask_query if ask_query else None

    # Handle comma separated
    items = [x.strip() for x in choice.split(",") if x.strip()]
    for item in items:
        open_ai_service(item, query=query)
