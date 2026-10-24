#!/usr/bin/env python3
"""
RILZ TOOLS — Desktop Notifier
Sends a desktop notification using plyer if available, with a PowerShell
fallback on Windows. Always falls back gracefully to a styled terminal panel.
"""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


def notify(title: str, message: str) -> None:
    """
    Send a desktop notification.

    Priority order:
      1. plyer  (cross-platform, best option)
      2. PowerShell BurntToast (Windows only)
      3. PowerShell MessageBox fallback (Windows only)
      4. Styled terminal panel (always works)
    """
    # --- Attempt 1: plyer ---
    try:
        from plyer import notification  # type: ignore
        notification.notify(
            title=title,
            message=message,
            app_name="RILZ TOOLS",
            timeout=5,
        )
        _print_terminal_notify(title, message, via="plyer")
        return
    except ImportError:
        pass
    except Exception:
        pass

    # --- Attempt 2: PowerShell BurntToast ---
    if _try_powershell_toast(title, message):
        _print_terminal_notify(title, message, via="PowerShell BurntToast")
        return

    # --- Attempt 3: PowerShell MessageBox (silent, non-blocking) ---
    if _try_powershell_msgbox(title, message):
        _print_terminal_notify(title, message, via="PowerShell")
        return

    # --- Fallback 4: Terminal panel only ---
    _print_terminal_notify(title, message, via="terminal")


def _try_powershell_toast(title: str, message: str) -> bool:
    """Try Windows BurntToast PowerShell module."""
    import subprocess
    try:
        script = (
            f"Import-Module BurntToast -ErrorAction Stop; "
            f"New-BurntToastNotification -Text '{title}', '{message}'"
        )
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", script],
            capture_output=True, timeout=8,
        )
        return result.returncode == 0
    except Exception:
        return False


def _try_powershell_msgbox(title: str, message: str) -> bool:
    """Fallback: Windows Forms non-blocking balloon."""
    import subprocess
    try:
        # Use a non-blocking approach via Start-Job so terminal is not frozen
        script = (
            "Add-Type -AssemblyName System.Windows.Forms; "
            "$n = New-Object System.Windows.Forms.NotifyIcon; "
            "$n.Icon = [System.Drawing.SystemIcons]::Information; "
            "$n.Visible = $true; "
            f"$n.ShowBalloonTip(4000, '{title}', '{message}', "
            "[System.Windows.Forms.ToolTipIcon]::Info); "
            "Start-Sleep 5; $n.Dispose()"
        )
        subprocess.Popen(
            ["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", script],
            creationflags=0x08000000,  # CREATE_NO_WINDOW
        )
        return True
    except Exception:
        return False


def _print_terminal_notify(title: str, message: str, via: str = "terminal") -> None:
    """Always print a styled notification panel to the terminal."""
    content = Text()
    content.append(f"  🔔  {title}\n", style="bold bright_yellow")
    content.append(f"  {message}\n", style="bright_white")
    content.append(f"  [via {via}]", style="dim green")
    console.print(
        Panel(
            content,
            title="[bold bright_yellow]RILZ NOTIFICATION[/bold bright_yellow]",
            border_style="bright_yellow",
            padding=(0, 2),
        )
    )
