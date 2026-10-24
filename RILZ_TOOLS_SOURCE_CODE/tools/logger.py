#!/usr/bin/env python3
"""
RILZ TOOLS — Session Activity Logger
Logs every tool invocation (and errors) to rilz-vault/logs/activity.log.
"""

import os
from datetime import datetime
from pathlib import Path

# Vault directory is one level up from this file's parent (tools/)
_VAULT_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / "rilz-vault"
_LOG_DIR   = _VAULT_DIR / "logs"
_LOG_FILE  = _LOG_DIR / "activity.log"


def _ensure_log_dir():
    """Create the logs directory if it does not exist."""
    _LOG_DIR.mkdir(parents=True, exist_ok=True)


def log_activity(tool_name: str, detail: str = "") -> None:
    """
    Append one log line to activity.log.

    Format:
        [2026-10-22 17:30:45] [TOOL: Video Infiltrator] url=https://...
    """
    _ensure_log_dir()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    detail_part = f"  {detail}" if detail else ""
    line = f"[{timestamp}] [TOOL: {tool_name}]{detail_part}\n"
    try:
        with open(_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        pass  # Never crash the caller because of a logging failure


def get_recent_logs(n: int = 50) -> list[str]:
    """Return the last n lines from the activity log."""
    _ensure_log_dir()
    if not _LOG_FILE.exists():
        return []
    try:
        lines = _LOG_FILE.read_text(encoding="utf-8", errors="ignore").splitlines()
        return lines[-n:]
    except Exception:
        return []
