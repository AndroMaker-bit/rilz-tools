"""
Authentic Kali Linux Dragon ASCII Art for RILZ TOOLS
"""

# Animated breathing / pulsing dragon frames (Cyber Blue -> Neon Cyan -> Ember Glint -> Electric Aura)
# By modulating color styles smoothly rather than redrawing character positions,
# the animation runs at 60 FPS buttery smooth without any screen jitter or tearing!

COLOR_SCHEMES = [
    # 0. Deep Cyber Blue
    {"head": "bold cyan", "body": "cyan", "tail": "blue", "eye": "bold bright_red", "ember": "dim cyan"},
    # 1. Electric Cyan Glint
    {"head": "bold bright_cyan", "body": "cyan", "tail": "bright_blue", "eye": "bold bright_yellow", "ember": "bold cyan"},
    # 2. Plasma Burst
    {"head": "bold bright_white", "body": "bold bright_cyan", "tail": "cyan", "eye": "bold bright_red", "ember": "bold bright_cyan"},
    # 3. Neon Kali Blue
    {"head": "bold bright_cyan", "body": "bold cyan", "tail": "blue", "eye": "bold red", "ember": "blue"},
]

def get_kali_dragon(frame_idx: int) -> str:
    scheme = COLOR_SCHEMES[frame_idx % len(COLOR_SCHEMES)]
    h = scheme["head"]
    b = scheme["body"]
    t = scheme["tail"]
    e = scheme["eye"]
    emb = scheme["ember"]

    # Embers floating near the dragon's breath
    embers = ["  ", " .", "° ", "·~", " *", "~°", "  ", "· "]
    em1 = embers[frame_idx % len(embers)]
    em2 = embers[(frame_idx + 3) % len(embers)]

    lines = [
        f"               [{h}]_[/{h}]",
        f"              [{h}]/ \\      _-'[/{h}]",
        f"            [{h}]_/|  \\-''- _ /[/{h}]",
        f"       [{b}]__-' {{ |          \\[/{b}]",
        f"           [{b}]/             \\[/{b}]",
        f"           [{b}]/       [{e}]\"o.[/{e}]  [{e}]|o[/{e}] }}[/{b}]  [{emb}]{em1}[/{emb}]",
        f"           [{b}]|            \\ ;[/{b}]    [{emb}]{em2}[/{emb}]",
        f"                     [{b}',[/{b}]",
        f"              [{t}]\\_         __\\[/{t}]",
        f"                [{t}]''-_    \\.//[/{t}]",
        f"                    [{t}]/   _-'[/{t}]",
        f"                   [{t}]/  _/[/{t}]",
        f"                  [{t}]/ _/[/{t}]",
        f"                 [{t}]/ /[/{t}]",
        f"                [{t}]/ /[/{t}]",
        f"               [{t}]( ([/{t}]",
        f"                [{t}'-_[/{t}]",
        f"                   [{t}'[/{t}]",
    ]
    return "\n".join(lines)
