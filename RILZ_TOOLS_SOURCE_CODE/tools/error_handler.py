#!/usr/bin/env python3
"""
RILZ TOOLS — Global Error Handler
Provides a safe_run() wrapper that catches ALL exceptions and renders a
beautiful cyber-styled error panel, then logs the event via logger.
"""

import traceback
from functools import wraps

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

# Map common exception types to helpful user hints
_HINTS = {
    "ConnectionError": "Check your network connection and try again.",
    "TimeoutError": "Request timed out. Verify target is reachable.",
    "FileNotFoundError": "Verify the file path exists and is accessible.",
    "PermissionError": "Run with elevated privileges or check file permissions.",
    "ImportError": "Install missing dependency: pip install <package>",
    "ModuleNotFoundError": "Install missing dependency: pip install <package>",
    "ValueError": "Invalid input value — double-check what you entered.",
    "KeyboardInterrupt": "Operation cancelled by user.",
    "JSONDecodeError": "Invalid JSON received — server may be down.",
    "requests.exceptions.ConnectionError": "Check your internet connection.",
    "requests.exceptions.Timeout": "Request timed out. Try again later.",
    "sqlite3.OperationalError": "Database error — vault may be corrupted.",
}


def _get_hint(exc: Exception) -> str:
    """Return a helpful tip based on exception class name."""
    name = type(exc).__name__
    for key, hint in _HINTS.items():
        if key in name or name == key:
            return hint
    return "Try again, or check logs for more details."


def _render_error_panel(exc: Exception, context: str = "") -> Panel:
    """Render a cyber-aesthetic error panel for the given exception."""
    exc_type = type(exc).__name__
    exc_msg  = str(exc) or "(no message)"
    hint     = _get_hint(exc)

    content = Text()
    content.append("  ⚠  SYSTEM FAULT DETECTED\n", style="bold bright_red")
    if context:
        content.append(f"  Context   : {context}\n", style="dim yellow")
    content.append(f"  Error     : ", style="bold white")
    content.append(f"{exc_type}", style="bold bright_red")
    content.append(f" — {exc_msg}\n", style="red")
    content.append(f"  → Hint    : {hint}\n", style="bright_yellow")
    content.append("  → Type 00 to exit or select another option.\n", style="dim green")

    return Panel(
        content,
        title="[bold bright_red]⚡ RILZ ERROR MATRIX ⚡[/bold bright_red]",
        title_align="center",
        border_style="bright_red",
        padding=(0, 2),
    )


def safe_run(fn, *args, context: str = "", log: bool = True, **kwargs):
    """
    Execute fn(*args, **kwargs) safely.
    On any exception: display a cyber error panel and optionally log it.
    Returns None on failure, or the function's return value on success.
    """
    try:
        return fn(*args, **kwargs)
    except (KeyboardInterrupt, EOFError):
        console.print("\n[dim bright_red]Operation cancelled by user.[/dim bright_red]")
        return None
    except Exception as exc:
        console.print()
        console.print(_render_error_panel(exc, context=context or fn.__name__))
        if log:
            try:
                from tools.logger import log_activity
                log_activity(
                    tool_name=context or fn.__name__,
                    detail=f"ERROR {type(exc).__name__}: {exc}",
                )
            except Exception:
                pass  # Never let the logger crash the error handler
        return None


def safe_tool(context: str = ""):
    """
    Decorator version of safe_run for use on tool functions.
    Usage:
        @safe_tool("IP Intelligence")
        def my_tool():
            ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            return safe_run(fn, *args, context=context or fn.__name__, **kwargs)
        return wrapper
    return decorator
