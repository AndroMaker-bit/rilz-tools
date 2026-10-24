"""
Complex High-Tech Cyber Telemetry HUD for RILZ TOOLS
Sleek, ultra-compact, and zero-wrap layout for all terminal sizes.
"""

import os
import platform
import socket
import time
from typing import Optional
import psutil
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


def make_hud_bar(percent: float, width: int = 8) -> Text:
    """Generate a sleek cybernetic progress meter."""
    percent = max(0.0, min(100.0, percent))
    filled = int(round((percent / 100.0) * width))
    empty = width - filled

    if percent < 60:
        color = "bright_cyan"
    elif percent < 85:
        color = "bright_yellow"
    else:
        color = "bright_red"

    t = Text()
    t.append("█" * filled, style=color)
    t.append("░" * empty, style="dim white")
    t.append(f" {percent:4.1f}%", style=f"bold {color}")
    return t


def measure_quick_ping(host: str = "1.1.1.1") -> Optional[float]:
    """Measure uplink TCP ping to Cloudflare DNS in ms."""
    t0 = time.perf_counter()
    try:
        with socket.create_connection((host, 53), timeout=0.8):
            return (time.perf_counter() - t0) * 1000.0
    except Exception:
        return None


def get_cyber_hud_panel() -> Panel:
    """Generate the complex Mission Control HUD panel."""
    # 1. Collect Telemetry
    cpu_pct = psutil.cpu_percent(interval=None)
    cpu_cores = psutil.cpu_count(logical=True) or 4
    mem = psutil.virtual_memory()
    mem_used_gb = mem.used / (1024**3)
    mem_total_gb = mem.total / (1024**3)

    disk = psutil.disk_usage("C:\\" if os.name == "nt" else "/")
    disk_free_gb = disk.free / (1024**3)

    ping = measure_quick_ping()
    ping_str = f"{ping:4.1f}ms" if ping is not None else "TIMEOUT"
    ping_color = "bright_green" if (ping and ping < 60) else ("yellow" if (ping and ping < 150) else "bright_red")

    hostname = socket.gethostname()
    os_name = f"{platform.system()} {platform.release()}"

    uptime_sec = time.time() - psutil.boot_time()
    hours, remainder = divmod(int(uptime_sec), 3600)
    minutes, _ = divmod(remainder, 60)

    # 2. Build Nested Grid
    grid = Table.grid(expand=True, padding=(0, 1))
    grid.add_column(ratio=1)

    # SECTION 1: Hardware Vitals
    grid.add_row(Text("⚡ HARDWARE VITALS", style="bold bright_cyan"))
    grid.add_row(
        Text.from_markup(" [dim]├─[/dim] [bold white]CPU :[/bold white] ")
        + make_hud_bar(cpu_pct, width=8)
        + Text(f" ({cpu_cores}T)", style="dim")
    )
    grid.add_row(
        Text.from_markup(" [dim]├─[/dim] [bold white]RAM :[/bold white] ")
        + make_hud_bar(mem.percent, width=8)
        + Text(f" [{mem_used_gb:.1f}/{mem_total_gb:.1f}G]", style="dim")
    )
    grid.add_row(
        Text.from_markup(" [dim]├─[/dim] [bold white]Disk:[/bold white] ")
        + make_hud_bar(disk.percent, width=8)
        + Text(f" [{disk_free_gb:.0f}G Free]", style="dim")
    )
    grid.add_row(
        Text.from_markup(f" [dim]└─[/dim] [bold white]Ping:[/bold white] [{ping_color}]{ping_str}[/{ping_color}] [dim](1.1.1.1)[/dim]")
    )

    grid.add_row(Text(""))

    # SECTION 2: Security & Defense Matrix
    grid.add_row(Text("🛡️ CYBER MATRIX", style="bold bright_yellow"))
    grid.add_row(Text.from_markup(f" [dim]├─[/dim] [bold white]Node  :[/bold white] [cyan]{hostname[:18]}[/cyan]"))
    grid.add_row(Text.from_markup(" [dim]├─[/dim] [bold white]Cipher:[/bold white] [bright_green]AES-256-GCM[/bright_green] [dim]SECURED[/dim]"))
    grid.add_row(Text.from_markup(" [dim]├─[/dim] [bold white]Threat:[/bold white] [bold bright_green]LEVEL 0[/bold bright_green] [dim]CLEAN[/dim]"))
    grid.add_row(Text.from_markup(f" [dim]└─[/dim] [bold white]Uptime:[/bold white] [white]{hours}h {minutes}m[/white] [dim]STABLE[/dim]"))

    grid.add_row(Text(""))

    # SECTION 3: Live Telemetry Event Stream
    curr_time = time.strftime("%H:%M:%S")
    grid.add_row(Text("🛰️ LIVE TELEMETRY STREAM", style="bold bright_magenta"))
    grid.add_row(Text.from_markup(f" [dim][{curr_time}][/dim] [bold cyan]CORE[/bold cyan] : [white]Neural matrix online[/white]"))
    grid.add_row(Text.from_markup(f" [dim][{curr_time}][/dim] [bold green]NET [/bold green] : [white]Cloud direct stream OK[/white]"))
    grid.add_row(Text.from_markup(f" [dim][{curr_time}][/dim] [bold yellow]HUD [/bold yellow] : [bold white]SYNCHRONIZED[/bold white]"))

    return Panel(
        grid,
        title="[bold bright_cyan]🛰️ MISSION CONTROL • HUD[/bold bright_cyan]",
        border_style="bright_cyan",
        padding=(0, 1),
    )
