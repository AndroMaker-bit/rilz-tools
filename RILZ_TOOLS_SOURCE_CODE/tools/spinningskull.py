"""
Spinning Skull Viral Fetch Experience (TikTok Meme Edition)
Reproduces the iconic terminal aesthetic:
Left: 3D spinning skull in amber/orange truecolor pixels.
Right: System Neofetch info and color blocks.
"""

import os
import platform
import socket
import sys
import time
import psutil

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.live import Live

from .skull_frames import ALL_FRAMES, render_frame_text

try:
    import msvcrt
    HAS_MSVCRT = True
except ImportError:
    HAS_MSVCRT = False

console = Console()


def get_fetch_text() -> str:
    """Generate Debian / Neofetch style system specifications for RILZ."""
    user = os.getlogin() if hasattr(os, "getlogin") else "rilz"
    hostname = socket.gethostname()

    # Hardware stats
    mem = psutil.virtual_memory()
    mem_used = mem.used / (1024**3)
    mem_total = mem.total / (1024**3)

    disk = psutil.disk_usage("C:\\" if os.name == "nt" else "/")
    disk_used = disk.used / (1024**3)
    disk_total = disk.total / (1024**3)

    cpu_name = platform.processor() or "AMD / Intel Multi-Core"
    cpu_cores = psutil.cpu_count(logical=True)

    # Uptime
    uptime_sec = time.time() - psutil.boot_time()
    hours, remainder = divmod(int(uptime_sec), 3600)
    minutes, _ = divmod(remainder, 60)
    uptime_str = f"{hours} hours, {minutes} mins" if hours > 0 else f"{minutes} mins"

    # Color palette blocks like in Neofetch
    color_blocks_1 = (
        "[rgb(0,0,0)]███[/rgb(0,0,0)]"
        "[rgb(230,50,50)]███[/rgb(230,50,50)]"
        "[rgb(60,200,60)]███[/rgb(60,200,60)]"
        "[rgb(240,200,50)]███[/rgb(240,200,50)]"
        "[rgb(50,120,250)]███[/rgb(50,120,250)]"
        "[rgb(200,60,220)]███[/rgb(200,60,220)]"
        "[rgb(60,220,220)]███[/rgb(60,220,220)]"
        "[rgb(230,230,230)]███[/rgb(230,230,230)]"
    )

    color_blocks_2 = (
        "[rgb(80,80,80)]███[/rgb(80,80,80)]"
        "[rgb(255,100,100)]███[/rgb(255,100,100)]"
        "[rgb(100,255,100)]███[/rgb(100,255,100)]"
        "[rgb(255,240,100)]███[/rgb(255,240,100)]"
        "[rgb(100,160,255)]███[/rgb(100,160,255)]"
        "[rgb(240,100,255)]███[/rgb(240,100,255)]"
        "[rgb(100,255,255)]███[/rgb(100,255,255)]"
        "[rgb(255,255,255)]███[/rgb(255,255,255)]"
    )

    fetch_lines = [
        f"[bold bright_red]{user}[/bold bright_red][bold white]@[/bold white][bold bright_red]{hostname}[/bold bright_red]",
        "[dim]--------------------------------------------[/dim]",
        f"[bold bright_red]OS:[/bold bright_red] [white]{platform.system()} {platform.release()} ({platform.machine()})[/white]",
        f"[bold bright_red]Host:[/bold bright_red] [white]{hostname}[/white]",
        f"[bold bright_red]Kernel:[/bold bright_red] [white]{platform.version()[:24]}[/white]",
        f"[bold bright_red]Uptime:[/bold bright_red] [white]{uptime_str}[/white]",
        f"[bold bright_red]Shell:[/bold bright_red] [white]python {sys.version.split()[0]}[/white]",
        f"[bold bright_red]CPU:[/bold bright_red] [white]{cpu_name[:26]} ({cpu_cores}T)[/white]",
        f"[bold bright_red]Memory:[/bold bright_red] [white]{mem_used:.2f} GiB / {mem_total:.2f} GiB ({mem.percent}%)[/white]",
        f"[bold bright_red]Disk:[/bold bright_red] [white]{disk_used:.1f} GiB / {disk_total:.1f} GiB ({disk.percent}%)[/white]",
        f"[bold bright_red]Security:[/bold bright_red] [bold green]RILZ GUARDIAN ACTIVE[/bold green]",
        "",
        color_blocks_1,
        color_blocks_2,
        "",
        "[dim]Press [bold white]Q[/bold white] or [bold white]Ctrl+C[/bold white] to return to menu[/dim]",
    ]

    return "\n".join(fetch_lines)


def build_spinning_view(frame_idx: int) -> Table:
    """Build the side-by-side view (Skull on Left, Fetch on Right) identical to video."""
    frame_matrix = ALL_FRAMES[frame_idx % len(ALL_FRAMES)]
    skull_markup = render_frame_text(frame_matrix)

    grid = Table.grid(expand=True, padding=(0, 2))
    grid.add_column(ratio=1)  # Left: Skull
    grid.add_column(ratio=1)  # Right: Fetch Info

    left_panel = Panel(
        skull_markup,
        title="[bold bright_red]💀 3D SPUN SKULL[/bold bright_red]",
        border_style="bright_red",
        padding=(0, 1),
    )

    right_panel = Panel(
        get_fetch_text(),
        title="[bold bright_yellow]⚡ SYSTEM SPECIFICATIONS[/bold bright_yellow]",
        border_style="yellow",
        padding=(0, 2),
    )

    grid.add_row(left_panel, right_panel)

    container = Table.grid(expand=True)
    container.add_row(
        Panel(
            "[bold white]pov: You spent 3 hours in Python just to make a spinning skull in the terminal.[/bold white]",
            border_style="dim",
            padding=(0, 1),
        )
    )
    container.add_row(grid)
    return container


def run_spinning_skull():
    """Run interactive 360-degree spinning skull loop in terminal."""
    console.clear()
    frame_idx = 0

    try:
        with Live(build_spinning_view(frame_idx), console=console, screen=True, auto_refresh=False) as live:
            while True:
                if HAS_MSVCRT and msvcrt.kbhit():
                    ch = msvcrt.getwch().lower()
                    if ch in ("q", "\x03", "\x1b", "\r"):
                        break
                frame_idx += 1
                live.update(build_spinning_view(frame_idx), refresh=True)
                time.sleep(0.12)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    run_spinning_skull()
