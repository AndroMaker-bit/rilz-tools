"""
Cryptographic Hashing & File Integrity Suite for RILZ TOOLS
Supports MD5, SHA-1, SHA-256, SHA-512, BLAKE2b, and Checksum verification.
"""

import hashlib
import os
from typing import Dict
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def hash_text(text: str) -> Dict[str, str]:
    """Calculate common cryptographic hashes for text."""
    b = text.encode("utf-8")
    return {
        "MD5": hashlib.md5(b).hexdigest(),
        "SHA-1": hashlib.sha1(b).hexdigest(),
        "SHA-256": hashlib.sha256(b).hexdigest(),
        "SHA-512": hashlib.sha512(b).hexdigest(),
        "BLAKE2b": hashlib.blake2b(b).hexdigest(),
    }


def hash_file(filepath: str) -> Dict[str, str]:
    """Calculate hashes for a file streaming in chunks."""
    h_md5 = hashlib.md5()
    h_sha1 = hashlib.sha1()
    h_sha256 = hashlib.sha256()

    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h_md5.update(chunk)
            h_sha1.update(chunk)
            h_sha256.update(chunk)

    return {
        "MD5": h_md5.hexdigest(),
        "SHA-1": h_sha1.hexdigest(),
        "SHA-256": h_sha256.hexdigest(),
    }


def interactive_crypto():
    """Run interactive crypto hashing and checksum menu."""
    console.print("\n[bold cyan]--- 🔐 Cryptographic Hashing & Checksum ---[/bold cyan]")
    console.print("1. Hash Teks String\n2. Hash File (Checksum Integrity)\n3. Verifikasi File Checksum")
    choice = console.input("[bold cyan]Pilih mode [1-3]:[/bold cyan] ").strip()

    if choice == "1":
        text = console.input("[bold white]Masukkan teks:[/bold white] ")
        res = hash_text(text)
        table = Table(title="🔑 Hasil Hash Kriptografi", expand=True)
        table.add_column("Algoritma", style="bold cyan", width=12)
        table.add_column("Hash Digest", style="bold white")
        for k, v in res.items():
            table.add_row(k, v)
        console.print(table)

    elif choice == "2":
        path = console.input("[bold white]Path file:[/bold white] ").strip(' "\'')
        if not os.path.exists(path):
            console.print("[bold red]File tidak ditemukan![/bold red]")
            return
        res = hash_file(path)
        table = Table(title=f"📦 File Checksums: {os.path.basename(path)}", expand=True)
        table.add_column("Algoritma", style="bold cyan", width=12)
        table.add_column("Checksum", style="bold white")
        for k, v in res.items():
            table.add_row(k, v)
        console.print(table)

    elif choice == "3":
        path = console.input("[bold white]Path file:[/bold white] ").strip(' "\'')
        expected = console.input("[bold white]Expected Hash Checksum:[/bold white] ").strip().lower()
        if not os.path.exists(path):
            console.print("[bold red]File tidak ditemukan![/bold red]")
            return
        res = hash_file(path)
        matched = False
        for algo, val in res.items():
            if val.lower() == expected:
                console.print(f"\n[bold bright_green]✅ CHECKSUM COCOK! ({algo})[/bold bright_green]")
                console.print(f"[dim]File 100% otentik dan tidak terkorupsi.[/dim]\n")
                matched = True
                break
        if not matched:
            console.print(f"\n[bold bright_red]❌ CHECKSUM TIDAK COCOK![/bold bright_red]")
            console.print(f"[dim]File mungkin terkorupsi atau telah dimodifikasi.[/dim]\n")
