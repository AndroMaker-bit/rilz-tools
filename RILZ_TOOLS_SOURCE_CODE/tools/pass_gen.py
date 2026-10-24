"""
Cryptographically Secure Password & Passphrase Generator for RILZ TOOLS
Uses Python's secrets module (CS-PRNG) with entropy calculation.
"""

import math
import secrets
import string
from rich.console import Console
from rich.panel import Panel

console = Console()

WORDS = [
    "quantum", "cipher", "matrix", "orbital", "shadow", "phoenix", "falcon", "vector",
    "plasma", "nebula", "titan", "stellar", "vortex", "aurora", "phantom", "sentinel",
    "cyber", "apex", "echo", "beacon", "glitch", "pulse", "cosmic", "abyss", "zenith"
]


def generate_password(length: int = 16, use_symbols: bool = True, use_digits: bool = True) -> str:
    """Generate cryptographically secure random password."""
    chars = string.ascii_letters
    if use_digits:
        chars += string.digits
    if use_symbols:
        chars += "!@#$%^&*()-_=+[]{}|;:,.<>?"

    pwd = [
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.ascii_uppercase),
    ]
    if use_digits:
        pwd.append(secrets.choice(string.digits))
    if use_symbols:
        pwd.append(secrets.choice("!@#$%^&*()-_=+"))

    while len(pwd) < length:
        pwd.append(secrets.choice(chars))

    secrets.SystemRandom().shuffle(pwd)
    return "".join(pwd)


def generate_passphrase(words_count: int = 4, separator: str = "-") -> str:
    """Generate memorable Diceware-style multi-word passphrase."""
    chosen = [secrets.choice(WORDS) for _ in range(words_count)]
    number = secrets.randbelow(90) + 10
    return separator.join(chosen) + f"{separator}{number}"


def calculate_entropy(pwd: str) -> float:
    """Calculate Shannon entropy in bits."""
    pool = 0
    if any(c in string.ascii_lowercase for c in pwd):
        pool += 26
    if any(c in string.ascii_uppercase for c in pwd):
        pool += 26
    if any(c in string.digits for c in pwd):
        pool += 10
    if any(c in string.punctuation for c in pwd):
        pool += 32

    if pool == 0:
        return 0.0
    return len(pwd) * math.log2(pool)


def interactive_pass_gen():
    """Run interactive password generation session."""
    console.print("\n[bold cyan]--- 🔑 Secure Password & Passphrase Generator ---[/bold cyan]")
    console.print("1. Password Kompleks (Acak Kriptografis)\n2. Passphrase Frasa Kata (Mudah Diingat)")
    sub = console.input("[bold cyan]Pilih mode [1-2]:[/bold cyan] ").strip()

    if sub == "2":
        passphrase = generate_passphrase(words_count=4)
        entropy = calculate_entropy(passphrase)
        console.print(f"\n[bold green]🔑 Passphrase Dihasilkan:[/bold green] [bold bright_yellow]{passphrase}[/bold bright_yellow]")
        console.print(f"[dim]Entropi Kekuatan: {entropy:.1f} bits (Sangat Kuat & Mudah Diingat)[/dim]\n")
    else:
        len_str = console.input("[bold white]Panjang karakter [default 18]:[/bold white] ").strip()
        length = int(len_str) if len_str.isdigit() else 18
        pwd = generate_password(length=length)
        entropy = calculate_entropy(pwd)
        console.print(f"\n[bold green]🔑 Password Dihasilkan:[/bold green] [bold bright_white on blue] {pwd} [/bold bright_white on blue]")
        console.print(f"[dim]Entropi: {entropy:.1f} bits • Dihasilkan dengan modul CS-PRNG OS[/dim]\n")
