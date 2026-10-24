"""
QR Code Generator & Terminal Display for RILZ TOOLS
Generates scannable QR codes directly in terminal and saves as PNG.
"""

import os
from typing import Optional
from rich.console import Console

console = Console()


def generate_terminal_qr(text: str, save_png: Optional[str] = None):
    """Generate QR code and render directly in terminal using ASCII blocks."""
    try:
        import qrcode
    except ImportError:
        console.print("[bold red]Modul qrcode belum terinstall. Jalankan 'pip install qrcode'[/bold red]")
        return

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=1,
        border=2,
    )
    qr.add_data(text)
    qr.make(fit=True)

    matrix = qr.get_matrix()

    console.print(f"\n[bold cyan]📱 QR Code Ter-generate untuk:[/bold cyan] [bold white]{text}[/bold white]\n")

    # Render scannable QR code directly in terminal
    for row in matrix:
        line = "".join("  " if col else "██" for col in row)
        console.print(f"[bold white]{line}[/bold white]")

    console.print("\n[dim]Arahkan kamera smartphone untuk langsung memindai QR code di atas![/dim]")

    if save_png:
        try:
            img = qr.make_image(fill_color="black", back_color="white")
            os.makedirs(os.path.dirname(os.path.abspath(save_png)) or ".", exist_ok=True)
            img.save(save_png)
            console.print(f"[bold green]✔ Tersimpan sebagai file gambar:[/bold green] {save_png}\n")
        except Exception as e:
            console.print(f"[bold red]Gagal menyimpan file gambar:[/bold red] {e}\n")


def interactive_qr():
    """Run interactive QR code generator session."""
    console.print("\n[bold cyan]--- 📱 QR Code Generator ---[/bold cyan]")
    content = console.input("[bold white]Masukkan teks / URL untuk dibuatkan QR code:[/bold white] ").strip()
    if not content:
        return
    save = console.input("[bold white]Simpan ke file PNG? (cth: qrcode.png, kosongkan jika tidak):[/bold white] ").strip()
    generate_terminal_qr(content, save_png=save or None)
