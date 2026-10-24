"""
Symmetrical Cyber Dragon Crest for RILZ TOOLS
Designed to match the exact vertical height of the main tools menu.
"""

from rich.text import Text


def get_symmetrical_dragon_text() -> Text:
    """Return a perfectly symmetrical Cyber Dragon Crest matching menu height."""
    t = Text(justify="center")

    t.append(r"   __     _/\_     __   " + "\n", style="bold bright_cyan")
    t.append(r"  /  \   / O  \   /  \  " + "\n", style="bold bright_cyan")
    t.append(r" / /\ \ /  VV  \ / /\ \ " + "\n", style="bold cyan")
    t.append(r"( (  \ [========] /  ) )" + "\n", style="bold cyan")
    t.append(r" \ \_/\  \    /  /\_/ / " + "\n", style="bold bright_blue")
    t.append(r"  \___/   \  /   \___/  " + "\n", style="bold blue")
    t.append(r"    /    / \/ \    \    " + "\n", style="bold dark_blue")
    t.append(r"   /____/      \____\   " + "\n", style="bold dark_blue")
    t.append("⚡ RILZ CYBER DRAGON ⚡\n", style="bold bright_yellow")
    t.append("● STATUS: ACTIVE  •  LEVEL 9", style="bold green")

    return t
