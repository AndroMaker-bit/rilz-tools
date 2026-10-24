#!/usr/bin/env python3
"""
RILZ TOOLS CLI - Elite Cyber Hacking & Tactical Terminal Arsenal
Created for: RILZ
Aesthetic: 1337 Underground Cyberpunk / Kali Matrix Edition
Features:
- Centered Titles
- 100% Fixed & Visible Numbering [01-16]
- Cinematic Startup CRT Glitch Flicker
- Second Brain / Local Vault (rilz-vault)
- v2.0.0: Error Handler, Version System, Activity Logger, Quick-Launch CLI,
          Vault URL Import, Desktop Notifications, Vault Export, Stealth Mode
"""

# ── Version ────────────────────────────────────────────────────────────────────
RILZ_VERSION = "2.0.0"

import argparse
import os
import random
import sys
import time

# Ensure script directory is always in sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from rich.align import Align
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# ── Global stealth-mode flag (set before any Console is created) ───────────────
STEALTH_MODE: bool = False

# Console is lazily replaced when --stealth is parsed; defined here for module
# imports that happen before arg-parsing.
console = Console()


def _get_console() -> Console:
    """Return the module-level console (honours STEALTH_MODE)."""
    return console


# ── Import all 16 modular tools ───────────────────────────────────────────────
from tools.video import download_video
from tools.file_downloader import download_file
from tools.pdf import images_to_pdf, merge_pdfs, extract_text_from_pdf
from tools.link_bypass import display_bypass_result
from tools.hd_media import enhance_to_hd
from tools.bg_remover import remove_background
from tools.ip_intel import lookup_ip_intelligence
from tools.port_scanner import run_port_scan
from tools.crypto_suite import interactive_crypto
from tools.encoder_hub import interactive_encoder
from tools.qr_tool import interactive_qr, generate_terminal_qr
from tools.pass_gen import interactive_pass_gen
from tools.tiktok import display_tiktok_result
from tools.calc import evaluate_expression, interactive_calculator
from tools.neural_ai import run_neural_cortex
from tools.vault import run_vault

# ── New v2.0.0 modules ────────────────────────────────────────────────────────
from tools.error_handler import safe_run
from tools.logger import log_activity


# ══════════════════════════════════════════════════════════════════════════════
# UI Helpers
# ══════════════════════════════════════════════════════════════════════════════

def clear_screen():
    """Clear terminal screen completely across Windows (cmd/PowerShell) and Unix."""
    os.system("cls" if os.name == "nt" else "clear")


def run_startup_glitch():
    """Simulate a dramatic Cyberpunk / CRT monitor flicker with random timing on startup without buffer spam."""
    if STEALTH_MODE:
        return  # Skip animation in stealth mode
    clear_screen()
    dashboard = render_dashboard()
    glitch_text = Align.center(
        "[bold bright_green]0x7F...BREACH_DETECTED // SYNCHRONIZING_BUFFER...[/bold bright_green]\n"
        "[dim green]▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒[/dim green]\n"
        "[bold bright_white]───[ OVERRIDE PROTOCOL: RILZ // SYSTEM_INTEGRITY: 99.4% ]───[/bold bright_white]"
    )

    try:
        with Live(glitch_text, console=console, refresh_per_second=30, transient=True) as live:
            time.sleep(random.uniform(0.07, 0.12))
            live.update(Text(""))
            time.sleep(random.uniform(0.04, 0.08))
            live.update(dashboard)
            time.sleep(random.uniform(0.06, 0.10))
            live.update(Text(""))
            time.sleep(random.uniform(0.03, 0.06))
    except Exception:
        pass

    clear_screen()


def build_hacker_banner():
    """Render authentic Cyberpunk / Matrix hacker banner with centered layout."""
    if STEALTH_MODE:
        return Panel(
            Text("RILZ TOOLS v2.0.0 — CYBERNETIC ARSENAL", justify="center"),
            border_style="white",
            padding=(0, 2),
        )

    banner_text = (
        "[bold bright_green]██████╗ ██╗██╗     ███████╗[/bold bright_green]   [bold bright_cyan]████████╗ ██████╗  ██████╗ ██╗     ███████╗[/bold bright_cyan]\n"
        "[bold bright_green]██╔══██╗██║██║     ╚══███╔╝[/bold bright_green]   [bold bright_cyan]╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██╔════╝[/bold bright_cyan]\n"
        "[bold green]██████╔╝██║██║       ███╔╝ [/bold green]   [bold cyan]   ██║   ██║   ██║██║   ██║██║     ███████╗[/bold cyan]\n"
        "[bold green]██╔══██╗██║██║      ███╔╝  [/bold green]   [bold cyan]   ██║   ██║   ██║██║   ██║██║     ╚════██║[/bold cyan]\n"
        "[bold dim green]██║  ██║██║███████╗███████╗[/bold dim green]   [bold blue]   ██║   ╚██████╔╝╚██████╔╝███████╗███████║[/bold blue]\n"
        "[bold dim green]╚═╝  ╚═╝╚═╝╚══════╝╚══════╝[/bold dim green]   [bold blue]   ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚══════╝[/bold blue]\n\n"
        "[bold bright_white]───[ [bold bright_green]0x1337_FRAMEWORK[/bold bright_green] [dim]•[/dim] [bold bright_cyan]OPERATIVE: RILZ[/bold bright_cyan] [dim]•[/dim] [bold bright_red]SECURITY: UNRESTRICTED[/bold bright_red] ]───[/bold bright_white]"
    )
    p = Panel(
        Align.center(banner_text),
        border_style="bright_green",
        title="[bold bright_green]⚡ RILZ CYBERNETIC ARSENAL ⚡[/bold bright_green]",
        title_align="center",
        subtitle="[bold dim green]ROOT ACCESS GRANTED • ENCRYPTION: SHA-512/GCM • DEFCON-1[/bold dim green]",
        subtitle_align="center",
        padding=(0, 2),
    )
    return p


def render_dashboard() -> Table:
    """Render the dual-column cyber arsenal dashboard with perfectly visible numbers and centered titles."""

    if STEALTH_MODE:
        # Plain text menu for stealth / no-color mode
        plain = Table(box=None, expand=True, padding=(0, 1), show_header=False)
        plain.add_column("Menu", style="white", no_wrap=True)
        items = [
            "[01] Video Infiltrator (YouTube, TikTok, IG)",
            "[02] Cloud Storage Ripper (MediaFire, GDrive)",
            "[03] PDF Shadow Suite (Img2PDF, Merge, Text)",
            "[04] Redirect Link Unmasker (Trace & Bypass)",
            "[05] HD Resolution Upscaler (Lanczos 2x/4x)",
            "[06] Alpha Mask Isolator (PNG Transparency)",
            "[07] Geo-IP Reconnaissance (ISP, ASN, Map)",
            "[08] Multi-Thread Port Probe (TCP Scanner)",
            "[09] Cryptographic Hash Lab (MD5, SHA256)",
            "[10] Cyber Decoder Matrix (Base64, Hex, JWT)",
            "[11] QR Matrix Generator (Terminal & PNG)",
            "[12] Quantum Entropy Keygen (CS-PRNG Keys)",
            "[13] TikTok Profile OSINT (Account & Video)",
            "[14] Binary AST Calculator (Scientific Math)",
            "[15] RILZ Neural Cortex (AI Terminal & Core)",
            "[16] Local Vault / Second Brain (File & Notes)",
            "[00] Exit",
        ]
        for item in items:
            plain.add_row(item)
        container = Table.grid(expand=True)
        container.add_row(Panel(Text("RILZ TOOLS v2.0.0 [STEALTH MODE]", justify="center"), border_style="white"))
        container.add_row(plain)
        container.add_row(Panel(Text(f"STEALTH MODE ACTIVE | v{RILZ_VERSION}", justify="center"), border_style="white"))
        return container

    # ── 1. Left Column ────────────────────────────────────────────────────────
    left_table = Table(box=None, expand=True, padding=(0, 1), show_header=False)
    left_table.add_column("Subsystem", style="bold bright_white", no_wrap=True)

    left_table.add_row("[bold bright_green][01][/bold bright_green]  🎬 Video Infiltrator [dim](YouTube, TikTok, IG)[/dim]")
    left_table.add_row("[bold bright_green][02][/bold bright_green]  📥 Cloud Storage Ripper [dim](MediaFire, GDrive)[/dim]")
    left_table.add_row("[bold bright_green][03][/bold bright_green]  📄 PDF Shadow Suite [dim](Img2PDF, Merge, Text)[/dim]")
    left_table.add_row("[bold bright_green][04][/bold bright_green]  🔗 Redirect Link Unmasker [dim](Trace & Bypass)[/dim]")
    left_table.add_row("[bold bright_green][05][/bold bright_green]  ✨ HD Resolution Upscaler [dim](Lanczos 2x/4x)[/dim]")
    left_table.add_row("[bold bright_green][06][/bold bright_green]  ✂️  Alpha Mask Isolator [dim](PNG Transparency)[/dim]")
    left_table.add_row("[bold bright_green][07][/bold bright_green]  🌐 Geo-IP Reconnaissance [dim](ISP, ASN, Map)[/dim]")
    left_table.add_row("[bold bright_green][08][/bold bright_green]  🔍 Multi-Thread Port Probe [dim](TCP Scanner)[/dim]")
    left_table.add_row("[bold bright_red][00][/bold bright_red]  🚪 Abort & Terminate Grid [dim](Kill Session)[/dim]")

    left_panel = Panel(
        left_table,
        title="[bold bright_green]☣️ OFFENSIVE & NETWORK ARSENAL ☣️[/bold bright_green]",
        title_align="center",
        border_style="bright_green",
        padding=(1, 1),
    )

    # ── 2. Right Column ───────────────────────────────────────────────────────
    right_table = Table(box=None, expand=True, padding=(0, 1), show_header=False)
    right_table.add_column("Subsystem", style="bold bright_white", no_wrap=True)

    right_table.add_row("[bold bright_cyan][09][/bold bright_cyan]  🔐 Cryptographic Hash Lab [dim](MD5, SHA256)[/dim]")
    right_table.add_row("[bold bright_cyan][10][/bold bright_cyan]  🔤 Cyber Decoder Matrix [dim](Base64, Hex, JWT)[/dim]")
    right_table.add_row("[bold bright_cyan][11][/bold bright_cyan]  📱 QR Matrix Generator [dim](Terminal & PNG)[/dim]")
    right_table.add_row("[bold bright_cyan][12][/bold bright_cyan]  🔑 Quantum Entropy Keygen [dim](CS-PRNG Keys)[/dim]")
    right_table.add_row("[bold bright_cyan][13][/bold bright_cyan]  🎵 TikTok Profile OSINT [dim](Account & Video)[/dim]")
    right_table.add_row("[bold bright_cyan][14][/bold bright_cyan]  🧮 Binary AST Calculator [dim](Scientific Math)[/dim]")
    right_table.add_row("[bold bright_cyan][15][/bold bright_cyan]  🧠 RILZ Neural Cortex [dim](AI Terminal & Core)[/dim]")
    right_table.add_row("[bold bright_yellow][16][/bold bright_yellow]  📦 Local Vault / Second Brain [dim](File & Notes)[/dim]")
    right_table.add_row("[bold bright_red][00][/bold bright_red]  🚪 Abort & Terminate Grid [dim](Kill Session)[/dim]")

    right_panel = Panel(
        right_table,
        title="[bold bright_cyan]⚡ CRYPTO, NEURAL & VAULT MATRIX ⚡[/bold bright_cyan]",
        title_align="center",
        border_style="bright_cyan",
        padding=(1, 1),
    )

    # ── Main Grid ─────────────────────────────────────────────────────────────
    main_grid = Table.grid(expand=True)
    main_grid.add_column(ratio=1)
    main_grid.add_column(ratio=1)
    main_grid.add_row(left_panel, right_panel)

    # ── Status Bar (now shows version) ───────────────────────────────────────
    status_text = (
        "[bold green]● NETWORK: ONLINE[/bold green] [dim]│[/dim] "
        "[bold bright_cyan]CIPHER: AES-256-GCM[/bold bright_cyan] [dim]│[/dim] "
        "[bold bright_magenta]NEURAL CORTEX: SYNCHRONIZED[/bold bright_magenta] [dim]│[/dim] "
        "[bold bright_yellow]VAULT: ACTIVE[/bold bright_yellow] [dim]│[/dim] "
        "[bold bright_red]CLEARANCE: ROOT (1337)[/bold bright_red] [dim]│[/dim] "
        f"[bold dim green]v{RILZ_VERSION}[/bold dim green]"
    )
    status_ribbon = Panel(
        Text.from_markup(status_text, justify="center"),
        border_style="dim green",
        padding=(0, 1),
    )

    # ── Outer Container ───────────────────────────────────────────────────────
    container = Table.grid(expand=True)
    container.add_row(build_hacker_banner())
    container.add_row(main_grid)
    container.add_row(status_ribbon)

    return container


# ══════════════════════════════════════════════════════════════════════════════
# Tool dispatcher — called directly from quick-launch AND the interactive menu
# ══════════════════════════════════════════════════════════════════════════════

def _dispatch_tool(clean_choice: str, interactive: bool = True) -> bool:
    """
    Execute the tool identified by clean_choice.
    Returns True if a valid tool was selected, False otherwise.
    When interactive=True the function will prompt for input; when False it
    still runs but without the "press Enter to return" gate at the end.
    """

    def _pause():
        if interactive:
            console.input("\n[dim green]Tekan Enter untuk kembali ke grid...[/dim green]")

    if clean_choice in ("0", "00"):
        return False  # Signal caller to exit

    elif clean_choice == "1":
        clear_screen()
        console.print("\n[bold bright_green]=== [ 🎬 VIDEO INFILTRATOR & EXTRACTOR ] ===[/bold bright_green]")
        url = console.input("[bold bright_cyan]target_url ❯ [/bold bright_cyan]").strip()
        if url:
            audio_only = console.input("[bold white]Hanya audio MP3? (y/N):[/bold white] ").strip().lower() == "y"
            log_activity("Video Infiltrator", f"url={url}")
            safe_run(download_video, url, audio_only=audio_only, context="Video Infiltrator")
        _pause()

    elif clean_choice == "2":
        clear_screen()
        console.print("\n[bold bright_green]=== [ 📥 CLOUD STORAGE INFILTRATOR & RIPPER ] ===[/bold bright_green]")
        console.print("[dim green]Bypass & Rip: MediaFire, Google Drive, TeraBox, Dropbox, Pixeldrain, Direct URL.[/dim green]\n")
        url = console.input("[bold bright_cyan]cloud_url ❯ [/bold bright_cyan]").strip()
        if url:
            out_fn = console.input("[bold white]Nama file khusus (opsional, kosongkan jika auto):[/bold white] ").strip()
            log_activity("Cloud Storage Ripper", f"url={url}")
            safe_run(download_file, url, custom_filename=out_fn or None, context="Cloud Storage Ripper")
        _pause()

    elif clean_choice == "3":
        clear_screen()
        console.print("\n[bold bright_green]=== [ 📄 PDF SHADOW SUITE ] ===[/bold bright_green]")
        console.print("[bold bright_white]1.[/bold bright_white] Gambar ke PDF\n[bold bright_white]2.[/bold bright_white] Gabungkan Beberapa PDF\n[bold bright_white]3.[/bold bright_white] Ekstrak Teks dari PDF")
        sub = console.input("[bold bright_cyan]payload_mode [1-3] ❯ [/bold bright_cyan]").strip()
        if sub == "1":
            files_raw = console.input("[bold white]Path file gambar (pisahkan koma):[/bold white] ").strip()
            files = [f.strip(' "\'') for f in files_raw.split(",") if f.strip()]
            out_name = console.input("[bold white]Output PDF (default: output.pdf):[/bold white] ").strip() or "output.pdf"
            log_activity("PDF Suite", f"mode=img2pdf out={out_name}")
            safe_run(images_to_pdf, files, out_name, context="PDF Suite")
        elif sub == "2":
            files_raw = console.input("[bold white]Path file PDF (pisahkan koma):[/bold white] ").strip()
            files = [f.strip(' "\'') for f in files_raw.split(",") if f.strip()]
            out_name = console.input("[bold white]Output PDF gabungan (default: merged.pdf):[/bold white] ").strip() or "merged.pdf"
            log_activity("PDF Suite", f"mode=merge out={out_name}")
            safe_run(merge_pdfs, files, out_name, context="PDF Suite")
        elif sub == "3":
            pdf_in = console.input("[bold white]Path file PDF:[/bold white] ").strip(' "\'')
            out_txt = console.input("[bold white]Simpan ke file TXT? (kosongkan jika print ke terminal):[/bold white] ").strip(' "\'')
            log_activity("PDF Suite", f"mode=extract src={pdf_in}")
            text = safe_run(extract_text_from_pdf, pdf_in, out_txt or None, context="PDF Suite")
            if not out_txt and text:
                console.print(Panel(text[:1500] + ("..." if len(text) > 1500 else ""), title="Isi PDF"))
        _pause()

    elif clean_choice == "4":
        clear_screen()
        console.print("\n[bold bright_green]=== [ 🔗 REDIRECT LINK UNMASKER & BYPASS ] ===[/bold bright_green]")
        url = console.input("[bold bright_cyan]masked_url ❯ [/bold bright_cyan]").strip()
        if url:
            log_activity("Link Bypass", f"url={url}")
            safe_run(display_bypass_result, url, context="Link Bypass")
        _pause()

    elif clean_choice == "5":
        clear_screen()
        console.print("\n[bold bright_green]=== [ ✨ HD RESOLUTION ENHANCER ] ===[/bold bright_green]")
        img_path = console.input("[bold bright_cyan]image_path ❯ [/bold bright_cyan]").strip(' "\'')
        if img_path:
            scale_raw = console.input("[bold white]Skala perbesaran (2 atau 4, default 2):[/bold white] ").strip()
            scale = 4 if scale_raw == "4" else 2
            log_activity("HD Upscaler", f"path={img_path} scale={scale}")
            safe_run(enhance_to_hd, img_path, scale_factor=scale, context="HD Upscaler")
        _pause()

    elif clean_choice == "6":
        clear_screen()
        console.print("\n[bold bright_green]=== [ ✂️ ALPHA MASK BACKGROUND ISOLATOR ] ===[/bold bright_green]")
        img_path = console.input("[bold bright_cyan]image_path ❯ [/bold bright_cyan]").strip(' "\'')
        if img_path:
            tol_raw = console.input("[bold white]Toleransi background [10-80, default 40]:[/bold white] ").strip()
            tol = int(tol_raw) if tol_raw.isdigit() else 40
            log_activity("BG Remover", f"path={img_path} tol={tol}")
            safe_run(remove_background, img_path, tolerance=tol, context="BG Remover")
        _pause()

    elif clean_choice == "7":
        clear_screen()
        console.print("\n[bold bright_green]=== [ 🌐 GEO-IP & ASN RECONNAISSANCE ] ===[/bold bright_green]")
        target = console.input("[bold bright_cyan]target_ip_or_domain ❯ [/bold bright_cyan]").strip()
        log_activity("IP Intelligence", f"target={target or 'self'}")
        safe_run(lookup_ip_intelligence, target or None, context="IP Intelligence")
        _pause()

    elif clean_choice == "8":
        clear_screen()
        console.print("\n[bold bright_green]=== [ 🔍 MULTI-THREAD TCP PORT PROBE ] ===[/bold bright_green]")
        host = console.input("[bold bright_cyan]target_host ❯ [/bold bright_cyan]").strip()
        if host:
            log_activity("Port Scanner", f"host={host}")
            safe_run(run_port_scan, host, context="Port Scanner")
        _pause()

    elif clean_choice == "9":
        clear_screen()
        log_activity("Crypto Suite")
        safe_run(interactive_crypto, context="Crypto Suite")
        _pause()

    elif clean_choice == "10":
        clear_screen()
        log_activity("Encoder Hub")
        safe_run(interactive_encoder, context="Encoder Hub")
        _pause()

    elif clean_choice == "11":
        clear_screen()
        log_activity("QR Generator")
        safe_run(interactive_qr, context="QR Generator")
        _pause()

    elif clean_choice == "12":
        clear_screen()
        log_activity("Password Generator")
        safe_run(interactive_pass_gen, context="Password Generator")
        _pause()

    elif clean_choice == "13":
        clear_screen()
        console.print("\n[bold bright_green]=== [ 🎵 TIKTOK PROFILE & VIDEO OSINT ] ===[/bold bright_green]")
        query = console.input("[bold bright_cyan]username_or_url ❯ [/bold bright_cyan]").strip()
        if query:
            log_activity("TikTok OSINT", f"query={query}")
            safe_run(display_tiktok_result, query, context="TikTok OSINT")
        _pause()

    elif clean_choice == "14":
        clear_screen()
        log_activity("Calculator")
        safe_run(interactive_calculator, context="Calculator")
        _pause()

    elif clean_choice == "15":
        clear_screen()
        log_activity("Neural Cortex")
        safe_run(run_neural_cortex, context="Neural Cortex")
        _pause()

    elif clean_choice == "16":
        clear_screen()
        log_activity("Vault")
        run_vault()

    else:
        console.print("[yellow]⚠ Pilihan tidak valid. Masukkan nomor 00–16.[/yellow]")
        _pause()

    return True  # Valid selection processed


# ══════════════════════════════════════════════════════════════════════════════
# Interactive Menu Loop
# ══════════════════════════════════════════════════════════════════════════════

def interactive_menu():
    """Run interactive terminal menu loop with startup CRT glitch and Kali zsh hacker prompt."""
    run_startup_glitch()

    while True:
        clear_screen()
        console.print(render_dashboard())

        # Iconic Kali Linux zsh hacker prompt style
        console.print(
            "[bold bright_green]┌──([/bold bright_green]"
            "[bold white]root㉿rilz[/bold white]"
            "[bold bright_green])-[/bold bright_green]"
            "[bold bright_cyan][~/cyber-arsenal][/bold bright_cyan]"
        )

        try:
            choice = console.input("[bold bright_green]└─#[/bold bright_green] [bold bright_white]").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[bold bright_red][SYSTEM HALTED][/bold bright_red] [dim green]Session terminated safely. Goodbye, Operative Rilz.[/dim green]\n")
            break

        clean_choice = choice.lstrip("0") or "0"

        if clean_choice in ("0", "00"):
            console.print("\n[bold bright_red][SYSTEM HALTED][/bold bright_red] [dim green]Session terminated safely. Goodbye, Operative Rilz.[/dim green]\n")
            break

        _dispatch_tool(clean_choice, interactive=True)


# ══════════════════════════════════════════════════════════════════════════════
# Main / argparse entry-point
# ══════════════════════════════════════════════════════════════════════════════

def main():
    global STEALTH_MODE, console  # noqa: PLW0603

    parser = argparse.ArgumentParser(
        description="RILZ TOOLS v2.0.0 - 1337 Cybernetic Hacker Arsenal for Terminal",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # ── Global flags ─────────────────────────────────────────────────────────
    parser.add_argument(
        "--version", "-v",
        action="version",
        version=f"RILZ TOOLS v{RILZ_VERSION} — PHANTOM MATRIX",
    )
    parser.add_argument(
        "--stealth",
        action="store_true",
        default=False,
        help="Disable colors, emoji, and animations (screen-recording / plain terminal mode)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Direct tactical execution")

    # ── Quick-launch by number (e.g. rilz 7) ─────────────────────────────────
    for num in range(1, 17):
        subparsers.add_parser(str(num), help=f"Quick-launch tool [{num:02d}] directly")

    # ── Vault sub-commands ────────────────────────────────────────────────────
    p_vault = subparsers.add_parser("vault", help="Open vault menu or run vault sub-commands")
    vault_subs = p_vault.add_subparsers(dest="vault_cmd", help="Vault actions")

    p_vsearch = vault_subs.add_parser("search", help="Search vault non-interactively")
    p_vsearch.add_argument("keyword", help="Keyword to search")

    p_vnote = vault_subs.add_parser("note", help="Save a quick note non-interactively")
    p_vnote.add_argument("text", help="Note text content")
    p_vnote.add_argument("--tag", "-t", default="", help="Comma-separated tags")

    # ── Web sub-command ──────────────────────────────────────────────────────
    subparsers.add_parser("web", help="Launch RILZ WEB Liquid Glass Server")

    # ── Existing sub-commands ────────────────────────────────────────────────
    subparsers.add_parser("ai", help="Launch RILZ Neural Cortex Dramatic AI Terminal")

    p_ip = subparsers.add_parser("ip", help="Lookup IP Geolocation & ASN intelligence")
    p_ip.add_argument("target", nargs="?", help="IP or domain to lookup")

    p_scan = subparsers.add_parser("scan", help="Scan open TCP ports on target host")
    p_scan.add_argument("host", help="Target host / IP")

    p_qr = subparsers.add_parser("qr", help="Generate scannable QR code in terminal")
    p_qr.add_argument("text", help="Text/URL for QR code")
    p_qr.add_argument("--save", "-s", default=None, help="Save PNG image path")

    p_pass = subparsers.add_parser("pass", help="Generate CS-PRNG cryptographically secure password")
    p_pass.add_argument("--len", "-l", type=int, default=18, help="Password length")

    p_video = subparsers.add_parser("video", help="Rip video/audio from URL (YouTube, TikTok, etc)")
    p_video.add_argument("url", help="Target video URL")
    p_video.add_argument("--audio", "-a", action="store_true", help="Extract audio only (MP3)")
    p_video.add_argument("--out", "-o", default="downloads", help="Output directory")

    p_file = subparsers.add_parser("file", help="Infiltrate and rip files from MediaFire, GDrive, TeraBox, etc.")
    p_file.add_argument("url", help="Target file download URL")
    p_file.add_argument("--out", "-o", default="downloads", help="Output directory")
    p_file.add_argument("--name", "-n", default=None, help="Custom filename")

    p_pdf = subparsers.add_parser("pdf", help="Manipulate PDF payloads")
    p_pdf.add_argument("images", nargs="+", help="Image files to convert")
    p_pdf.add_argument("--out", "-o", default="output.pdf", help="Output PDF filename")

    p_bypass = subparsers.add_parser("bypass", help="Unmask and bypass redirected / short links")
    p_bypass.add_argument("url", help="URL to unshorten/bypass")

    p_hd = subparsers.add_parser("hd", help="Enhance image to HD resolution")
    p_hd.add_argument("image", help="Target image path")
    p_hd.add_argument("--scale", "-s", type=int, choices=[2, 4], default=2, help="Upscale factor (2 or 4)")

    p_rmbg = subparsers.add_parser("rmbg", help="Isolate image background")
    p_rmbg.add_argument("image", help="Target image path")
    p_rmbg.add_argument("--tol", "-t", type=int, default=40, help="Tolerance (10-80)")

    p_tiktok = subparsers.add_parser("tiktok", help="Perform OSINT on TikTok user or video")
    p_tiktok.add_argument("query", help="Username (@name) or video URL")

    p_calc = subparsers.add_parser("calc", help="Evaluate mathematical AST expression")
    p_calc.add_argument("expr", nargs="?", help="Expression to evaluate, e.g. 'sqrt(144) + 2^5'")

    args = parser.parse_args()

    # ── Apply stealth mode ────────────────────────────────────────────────────
    if args.stealth:
        STEALTH_MODE = True
        console = Console(no_color=True)

    # ── Dispatch ──────────────────────────────────────────────────────────────
    if not args.command:
        interactive_menu()

    # Quick-launch by number (1-16)
    elif args.command.isdigit() and 1 <= int(args.command) <= 16:
        run_startup_glitch()
        _dispatch_tool(args.command, interactive=True)

    # Vault commands
    elif args.command == "vault":
        if not hasattr(args, "vault_cmd") or not args.vault_cmd:
            # Open full vault menu interactively
            log_activity("Vault", "direct-launch")
            run_vault()
        elif args.vault_cmd == "search":
            # Non-interactive vault search
            from tools.vault import feature_search_keyword
            log_activity("Vault Search", f"keyword={args.keyword}")
            feature_search_keyword(args.keyword)
        elif args.vault_cmd == "note":
            # Non-interactive quick note
            from tools.vault import feature_quick_note_cli
            log_activity("Vault Note", f"tags={args.tag}")
            feature_quick_note_cli(args.text, args.tag)

    # Web server
    elif args.command == "web":
        from web.server import get_local_ip
        local_ip = get_local_ip()
        console.print(f"\n[bold bright_green]⚡ RILZ WEB LIQUID GLASS SERVER STARTED[/bold bright_green]")
        console.print(f"👉 Localhost : [bold bright_cyan]http://localhost:8000[/bold bright_cyan]")
        console.print(f"👉 WiFi / Temen: [bold bright_yellow]http://{local_ip}:8000[/bold bright_yellow]\n")
        import uvicorn
        log_activity("Web Server", f"ip={local_ip}")
        uvicorn.run("web.server:app", host="0.0.0.0", port=8000, reload=True)

    # Existing named commands
    elif args.command == "ai":
        log_activity("Neural Cortex", "cli-launch")
        run_neural_cortex()
    elif args.command == "ip":
        log_activity("IP Intelligence", f"target={args.target}")
        lookup_ip_intelligence(args.target)
    elif args.command == "scan":
        log_activity("Port Scanner", f"host={args.host}")
        run_port_scan(args.host)
    elif args.command == "qr":
        log_activity("QR Generator", f"text={args.text}")
        generate_terminal_qr(args.text, save_png=args.save)
    elif args.command == "pass":
        from tools.pass_gen import generate_password, calculate_entropy
        p = generate_password(length=args.len)
        log_activity("Password Generator", f"len={args.len}")
        console.print(f"[bold bright_green]Generated Cipher Key:[/bold bright_green] [bold white on blue] {p} [/bold white on blue] ({calculate_entropy(p):.1f} bits entropy)")
    elif args.command == "video":
        log_activity("Video Infiltrator", f"url={args.url}")
        download_video(args.url, output_dir=args.out, audio_only=args.audio)
    elif args.command == "file":
        log_activity("Cloud Ripper", f"url={args.url}")
        download_file(args.url, output_dir=args.out, custom_filename=args.name)
    elif args.command == "pdf":
        log_activity("PDF Suite", f"images={args.images}")
        images_to_pdf(args.images, args.out)
    elif args.command == "bypass":
        log_activity("Link Bypass", f"url={args.url}")
        display_bypass_result(args.url)
    elif args.command == "hd":
        log_activity("HD Upscaler", f"image={args.image} scale={args.scale}")
        enhance_to_hd(args.image, scale_factor=args.scale)
    elif args.command == "rmbg":
        log_activity("BG Remover", f"image={args.image} tol={args.tol}")
        remove_background(args.image, tolerance=args.tol)
    elif args.command == "tiktok":
        log_activity("TikTok OSINT", f"query={args.query}")
        display_tiktok_result(args.query)
    elif args.command == "calc":
        if args.expr:
            res = evaluate_expression(args.expr)
            console.print(f"[bold bright_green]= {res}[/bold bright_green]")
        else:
            interactive_calculator()


if __name__ == "__main__":
    main()
