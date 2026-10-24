"""
RILZ NEURAL CORTEX - Dramatic Cybernetic AI Core
Features interactive terminal reasoning, dramatic sci-fi synthesis,
and seamless multi-vector dispatch to ChatGPT, Claude, DeepSeek, and Gemini.
"""

import sys
import time
import urllib.parse
import webbrowser
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt

console = Console()

FRONTIER_MODELS = {
    "1": ("ChatGPT", "https://chatgpt.com/?q={query}", "https://chatgpt.com"),
    "2": ("Claude", "https://claude.ai", "https://claude.ai"),
    "3": ("DeepSeek", "https://chat.deepseek.com", "https://chat.deepseek.com"),
    "4": ("Google Gemini", "https://gemini.google.com/app", "https://gemini.google.com"),
    "5": ("Perplexity AI", "https://www.perplexity.ai/search?q={query}", "https://www.perplexity.ai"),
}


def dramatic_boot_sequence():
    """Play cinematic neural startup animation in terminal."""
    os.system("cls" if os.name == "nt" else "clear")
    boot_steps = [
        ("INJECTING QUANTUM KERNEL", "OK"),
        ("CALIBRATING NEURAL SYNAPSE WEIGHTS", "99.8% FIDELITY"),
        ("ENGAGING HARDWARE CIPHER SHIELD", "AES-256 ENFORCED"),
        ("CONNECTING OPERATIVE FREQUENCY TO: RILZ", "LOCKED & VERIFIED"),
        ("SYNCHRONIZING FRONTIER MODEL HEURISTICS", "READY"),
    ]

    banner = (
        "[bold bright_magenta]   ██████╗ ██╗██╗     ███████╗[/bold bright_magenta]   [bold cyan]███╗   ██╗███████╗██╗   ██╗██████╗  █████╗ ██╗     [/bold cyan]\n"
        "[bold bright_magenta]   ██╔══██╗██║██║     ╚══███╔╝[/bold bright_magenta]   [bold cyan]████╗  ██║██╔════╝██║   ██║██╔══██╗██╔══██╗██║     [/bold cyan]\n"
        "[bold magenta]   ██████╔╝██║██║       ███╔╝ [/bold magenta]   [bold bright_cyan]██╔██╗ ██║█████╗  ██║   ██║██████╔╝███████║██║     [/bold bright_cyan]\n"
        "[bold magenta]   ██╔══██╗██║██║      ███╔╝  [/bold magenta]   [bold bright_blue]██║╚██╗██║██╔══╝  ██║   ██║██╔══██╗██╔══██║██║     [/bold bright_blue]\n"
        "[bold purple]   ██║  ██║██║███████╗███████╗[/bold purple]   [bold blue]██║ ╚████║███████╗╚██████╔╝██║  ██║██║  ██║███████╗[/bold blue]\n"
        "[bold purple]   ╚═╝  ╚═╝╚═╝╚══════╝╚══════╝[/bold purple]   [bold blue]╚═╝  ╚═══╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝[/bold blue]\n\n"
        "             [bold bright_yellow]⚡ RILZ NEURAL CORTEX • ARTIFICIAL COGNITIVE MATRIX ⚡[/bold bright_yellow]"
    )
    console.print(Panel(banner, border_style="bright_magenta", padding=(0, 2)))

    for desc, status in boot_steps:
        time.sleep(0.08)
        console.print(f" [bold cyan]>>[/bold cyan] [white]{desc:<42}[/white] [bold bright_green][ {status} ][/bold bright_green]")

    time.sleep(0.12)
    console.print("\n[bold bright_yellow]⚡ NEURAL MATRIX ONLINE. OPERATIVE AUTHORITY: RILZ.[/bold bright_yellow]\n")


def dramatic_thinking_animation():
    """Simulate intense real-time neural cognitive calculation."""
    phases = [
        "Deconstructing semantic syntax...",
        "Evaluating multi-dimensional logic vectors...",
        "Formulating tactical intelligence...",
    ]
    for phase in phases:
        console.print(f"   [dim cyan]⚡ [bold white]{phase}[/bold white][/dim cyan]")
        time.sleep(0.15)


def generate_local_intelligence(query: str) -> str:
    """Generate high-IQ dramatic cybernetic responses for code, math, and system queries."""
    q_low = query.lower()

    if any(k in q_low for k in ["siapa kamu", "who are you", "kamu siapa", "identity"]):
        return (
            "Aku adalah **RILZ NEURAL CORTEX** — Entitas kecerdasan buatan otonom "
            "yang dirancang khusus sebagai co-pilot cybernetic untuk **RILZ**.\n\n"
            "Aku memegang kontrol atas seluruh subsistem: inspeksi jaringan, manipulasi media, "
            "ekstraksi cloud storage, hingga orkestrasi model AI terdepan di dunia."
        )

    if any(k in q_low for k in ["python", "coding", "code", "bikin", "buat", "script"]):
        return (
            f"**[ANALISIS KODING DITERIMA]**\n\n"
            f"Operatif RILZ, instruksi untuk: *\"{query}\"* telah dipetakan ke dalam arsitektur logika optimal.\n\n"
            f"```python\n"
            f"# RILZ Cybernetic Script Implementation\n"
            f"import sys, os, time\n\n"
            f"def execute_task():\n"
            f"    print('[RILZ-AI] Initiating directive: {query}')\n"
            f"    # Core routine executed successfully\n"
            f"    return True\n\n"
            f"if __name__ == '__main__':\n"
            f"    execute_task()\n"
            f"```\n\n"
            f"💡 *Ingin aku teruskan blueprint ini ke DeepSeek R1 atau Claude untuk penulisan kode tingkat advance? "
            f"Cukup ketik `/deepseek` atau `/claude`!*"
        )

    if any(k in q_low for k in ["hack", "kali", "pentest", "security", "keamanan"]):
        return (
            "**[SECURITY DIRECTIVE ACCESSED]**\n\n"
            "Protokol pertahanan cyber aktif. Ingat doktrin utama Kali:\n"
            "> *\"The quieter you become, the more you are able to hear.\"*\n\n"
            "Pastikan setiap audit dan analisis keamanan selalu dilakukan dalam batas otoritas legal dan riset etis."
        )

    # General Synthesis
    return (
        f"**[NEURAL SYNTHESIS RESOLVED]**\n\n"
        f"Query: *\"{query}\"*\n\n"
        f"Berdasarkan kalkulasi matriks kognitif RILZ:\n"
        f"1. **Strategi**: Pecah masalah menjadi komponen atomik dan eliminasi titik hambatan.\n"
        f"2. **Eksekusi**: Terapkan otomatisasi langsung melalui command line untuk efisiensi maksimum.\n"
        f"3. **Tindakan Lanjut**: Jika membutuhkan analisis literatur luas, gunakan shortcut multi-model di bawah."
    )


def open_frontier(name: str, query: str = None):
    """Open frontier AI model in browser with preloaded query if available."""
    for key, (m_name, q_url, base_url) in FRONTIER_MODELS.items():
        if name.lower() in m_name.lower() or name == key:
            target = q_url.format(query=urllib.parse.quote(query)) if query and "{query}" in q_url else base_url
            console.print(f"[bold bright_green]🚀 Membuka {m_name} di browser:[/bold bright_green] {target}")
            webbrowser.open(target)
            return True
    return False


def run_neural_cortex():
    """Interactive Dramatic AI Terminal Session."""
    dramatic_boot_sequence()

    help_panel = Panel(
        "[bold bright_white]Perintah Instan AI:[/bold bright_white]\n"
        " • [bold cyan]Tanya apa saja[/bold cyan] : AI akan langsung menjawab dengan mode sci-fi analitis.\n"
        " • [bold yellow]/deepseek <tanya>[/bold yellow] : Lempar query langsung ke DeepSeek R1.\n"
        " • [bold yellow]/chatgpt <tanya>[/bold yellow]  : Lempar query langsung ke ChatGPT.\n"
        " • [bold yellow]/claude <tanya>[/bold yellow]   : Buka Claude Anthropic.\n"
        " • [bold yellow]/gemini <tanya>[/bold yellow]   : Buka Google Gemini.\n"
        " • [bold bright_red]/all <tanya>[/bold bright_red]      : Buka SEMUA 4 AI frontier sekaligus di browser!\n"
        " • [bold green]web[/bold green]                 : Buka tabel menu launcher web AI.\n"
        " • [bold white]exit / q[/bold white]            : Kembali ke menu utama RILZ TOOLS.",
        title="[bold bright_yellow]⚡ PROTOKOL OPERASIONAL AI ⚡[/bold bright_yellow]",
        border_style="yellow",
        padding=(0, 2),
    )
    console.print(help_panel)

    while True:
        try:
            prompt = console.input("\n[bold magenta]RILZ-AI[/bold magenta][bold cyan] ❯ [/bold cyan]").strip()
            if not prompt:
                continue

            if prompt.lower() in ("exit", "quit", "q"):
                console.print("\n[bold yellow]Menonaktifkan Neural Cortex. Standby mode.[/bold yellow]\n")
                break

            if prompt.lower() == "web":
                console.print("\n[bold cyan]Meluncurkan Menu Web AI Shortcuts...[/bold cyan]")
                from .ai_shortcuts import interactive_ai_launcher
                interactive_ai_launcher()
                continue

            # Command dispatches
            if prompt.startswith("/all"):
                q = prompt[4:].strip()
                console.print(f"[bold bright_red]🔥 Menembakkan query ke 4 Frontier Models sekaligus![/bold bright_red]")
                for k in ["1", "2", "3", "4"]:
                    open_frontier(k, q)
                continue

            if prompt.startswith("/"):
                parts = prompt[1:].split(" ", 1)
                target_ai = parts[0]
                q = parts[1] if len(parts) > 1 else None
                if open_frontier(target_ai, q):
                    continue

            # Local neural processing
            console.print()
            dramatic_thinking_animation()
            console.print()

            response = generate_local_intelligence(prompt)
            console.print(
                Panel(
                    response,
                    title="[bold bright_cyan]🧠 RILZ NEURAL CORTEX RESPONSE[/bold bright_cyan]",
                    border_style="bright_cyan",
                    padding=(1, 2),
                )
            )

        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Sesi AI dihentikan.[/dim]\n")
            break
