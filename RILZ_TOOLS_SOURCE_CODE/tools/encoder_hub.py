"""
Encoder & Decoder Hub for RILZ TOOLS
Base64, Hex, URL, Binary, ROT13, and JWT Inspector.
"""

import base64
import codecs
import json
import urllib.parse
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def decode_jwt(jwt_str: str):
    """Inspect and decode JWT Header & Payload without needing secret keys."""
    parts = jwt_str.strip().split(".")
    if len(parts) < 2:
        console.print("[bold red]Format JWT tidak valid (harus memiliki setidaknya 2 bagian yang dipisah titik).[/bold red]")
        return

    def b64_decode(s):
        s += "=" * (-len(s) % 4)
        return json.loads(base64.urlsafe_b64decode(s.encode()).decode("utf-8"))

    try:
        header = b64_decode(parts[0])
        payload = b64_decode(parts[1])

        console.print(Panel(json.dumps(header, indent=2), title="[bold cyan]JWT Header[/bold cyan]", border_style="cyan"))
        console.print(Panel(json.dumps(payload, indent=2), title="[bold bright_green]JWT Payload Claims[/bold bright_green]", border_style="bright_green"))
    except Exception as e:
        console.print(f"[bold red]Gagal mendecode JWT:[/bold red] {e}")


def interactive_encoder():
    """Run interactive encoder & decoder menu."""
    console.print("\n[bold cyan]--- 🔤 Encoder & Decoder Hub ---[/bold cyan]")
    table = Table(box=None)
    table.add_column("No", style="bold cyan")
    table.add_column("Operasi", style="bold white")
    table.add_row("1", "Base64 Encode")
    table.add_row("2", "Base64 Decode")
    table.add_row("3", "URL Encode / Decode")
    table.add_row("4", "Hex Encode / Decode")
    table.add_row("5", "ROT13 Cipher")
    table.add_row("6", "JWT Token Payload Inspector")
    console.print(table)

    opt = console.input("[bold cyan]Pilih mode [1-6]:[/bold cyan] ").strip()
    data = console.input("[bold white]Masukkan input data:[/bold white] ").strip()

    try:
        if opt == "1":
            res = base64.b64encode(data.encode()).decode()
            console.print(f"\n[bold green]Base64 Encoded:[/bold green] [bold white]{res}[/bold white]\n")
        elif opt == "2":
            res = base64.b64decode(data.encode()).decode("utf-8", errors="replace")
            console.print(f"\n[bold green]Base64 Decoded:[/bold green] [bold white]{res}[/bold white]\n")
        elif opt == "3":
            encoded = urllib.parse.quote(data)
            decoded = urllib.parse.unquote(data)
            console.print(f"\n[bold green]URL Encoded:[/bold green] {encoded}")
            console.print(f"[bold green]URL Decoded:[/bold green] {decoded}\n")
        elif opt == "4":
            hex_enc = data.encode().hex()
            console.print(f"\n[bold green]Hex Encoded:[/bold green] {hex_enc}")
            try:
                hex_dec = bytes.fromhex(data).decode("utf-8", errors="replace")
                console.print(f"[bold green]Hex Decoded:[/bold green] {hex_dec}\n")
            except Exception:
                pass
        elif opt == "5":
            rot = codecs.encode(data, "rot_13")
            console.print(f"\n[bold green]ROT13 Result:[/bold green] [bold white]{rot}[/bold white]\n")
        elif opt == "6":
            decode_jwt(data)
    except Exception as e:
        console.print(f"[bold red]Error saat memproses data:[/bold red] {e}\n")
