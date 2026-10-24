"""
Animated Rotating 360-degree Skull ASCII Art Frames for RILZ TOOLS
"""

# 8 Rotational Perspectives of a Sinister Skull (0° -> 45° -> 90° -> 135° -> 180° -> 225° -> 270° -> 315°)

FRAME_0 = """
      [bold red].--''''--.[/bold red]
     [bold white]/   [bold red]__[/bold red]  [bold red]__[/bold red]   \\
    |   [bold bright_red](●)[/bold bright_red]  [bold bright_red](●)[/bold bright_red]   |
    |      [bold red]/\\[/bold red]      |
     \\   [bold white]|====|[/bold white]   /
      '--[bold white]|WWWW|[/bold white]--'
        [dim]||||||[/dim]
"""

# 45 degrees: Turning Right
FRAME_45 = """
      [bold red].--''''--.[/bold red]
     [bold white]/   [bold red]__[/bold red]     \\
    |   [bold bright_red](●)[/bold bright_red]  [bold red](o)[/bold red]   \\
    |     [bold red]/|[/bold red]       |
     \\  [bold white]|===|[/bold white]    /
      '-[bold white]|WWW|[/bold white]----'
        [dim]|||||[/dim]
"""

# 90 degrees: Pure Right Profile
FRAME_90 = """
      [bold red].-''''-.[/bold red]
     [bold white]/  [bold red]____[/bold red]   \\
    |  [bold bright_red](●)[/bold bright_red]     |
    |   [bold red]--.[/bold red]   /
     \\  [bold white]|=[/bold white]   /
      '-[bold white]|W|[/bold white]--'
        [dim]|||[/dim]
"""

# 135 degrees: Back-Right
FRAME_135 = """
       [bold red].-''''-.[/bold red]
      [bold white]/        \\
     |    ___   |
     |   /   \\  |
      \\        /
       '------'
         [dim]|||[/dim]
"""

# 180 degrees: Back of Skull
FRAME_180 = """
      [bold red].--''''--.[/bold red]
     [bold white]/          \\
    |     _      |
    |    / \\     |
     \\          /
      '--------'
        [dim]||||||[/dim]
"""

# 225 degrees: Back-Left
FRAME_225 = """
      [bold red].-''''-.[/bold red]
     [bold white]/        \\
    |   ___    |
    |  /   \\   |
     \\        /
      '------'
        [dim]|||[/dim]
"""

# 270 degrees: Pure Left Profile
FRAME_270 = """
       [bold red].-''''-.[/bold red]
      [bold white]/   [bold red]____[/bold red]  \\
     |     [bold bright_red](●)[/bold bright_red]  |
      \\   [bold red].--[/bold red]   |
       \\   [bold white]=|[/bold white]  /
       '-[bold white]|W|[/bold white]-'
         [dim]|||[/dim]
"""

# 315 degrees: Turning Front-Left
FRAME_315 = """
      [bold red].--''''--.[/bold red]
     [bold white]/     [bold red]__[/bold red]   \\
    /   [bold red](o)[/bold red]  [bold bright_red](●)[/bold bright_red]   |
    |       [bold red]|\\[/bold red]     |
     \\    [bold white]|===|[/bold white]  /
      '----[bold white]|WWW|[/bold white]-'
         [dim]|||||[/dim]
"""

# Detailed 12-line Sinister Skull Models for maximum visual impact
DETAILED_FRAMES = [
    # 0° Front
    """
       [bold bright_red]_,.-------.,_[/bold bright_red]
     [bold white],;~'             '~;,
   ,;                   ;,
  ;                       ;
 ;   [bold bright_red],---.         ,---.[/bold bright_red]   ;
 |  [bold bright_red]/ [bold white]#[/bold white] [bold red]O[/bold red] \\       / [bold red]O[/bold red] [bold white]#[/bold white] \\[/bold bright_red]  |
 |  [bold bright_red]\\___/   [bold white],_[/bold white]   \\___/[/bold bright_red]  |
  ;        [bold red]/|_\\[/bold red]        ;
   \\      [bold white]|_|_|[/bold white]       /
    '--.,_______,.--'
       [bold white]|_|_|_|_|[/bold white]
       [dim]| | | | |[/dim]
    """,
    # 30° Front-Right
    """
       [bold bright_red]_,.-------.,_[/bold bright_red]
     [bold white],;~'            '~;,
   ,;                  ;,
  ;                      ;
 ;  [bold bright_red],---.        ,-.[/bold bright_red]    ;
 | [bold bright_red]/ [bold white]#[/bold white] [bold red]O[/bold red] \\      / [bold red]O[/bold red] \\[/bold bright_red]   |
 | [bold bright_red]\\___/   [bold white],_[/bold white]   \\_/[/bold bright_red]   |
  ;       [bold red]/|_/[/bold red]         ;
   \\     [bold white]|_|_|[/bold white]        /
    '--.,______,.--'
       [bold white]|_|_|_|[/bold white]
       [dim]| | | |[/dim]
    """,
    # 60° Quarter-Right
    """
        [bold bright_red],.-------.,[/bold bright_red]
     [bold white],;~'          '~;,
   ,;                ;,
  ;                    ;
 ;  [bold bright_red],---.       ,-.[/bold bright_red]   ;
 | [bold bright_red]/ [bold white]#[/bold white] [bold red]O[/bold red] \\     /   \\[/bold bright_red]  |
 | [bold bright_red]\\___/   [bold white],_[/bold white]  '---'[/bold bright_red]  ;
  ;      [bold red]/|_/[/bold red]         /
   \\    [bold white]|_|_|[/bold white]        /
    '--.,_____,.--'
        [bold white]|_|_|[/bold white]
        [dim]| | |[/dim]
    """,
    # 90° Side-Right
    """
         [bold bright_red],.-----.,[/bold bright_red]
      [bold white],;~'       '~;,
    ,;               ;,
   ;                   ;
  ;  [bold bright_red],---.[/bold bright_red]            ;
  | [bold bright_red]/ [bold white]#[/bold white] [bold red]O[/bold red] \\[/bold bright_red]            |
  | [bold bright_red]\\___/    [bold white],-[/bold white][/bold bright_red]        ;
   ;        [bold red]/ /[/bold red]        /
    \\      [bold white]|_|[/bold white]        /
     '--.,___,.--'
         [bold white]|_|[/bold white]
         [dim]| |[/dim]
    """,
    # 120° Back-Right
    """
         [bold bright_red],.-----.,[/bold bright_red]
      [bold white],;~'       '~;,
    ,;               ;,
   ;                   ;
  ;                     ;
  |                     |
  |          [dim]__[/dim]         ;
   ;        [dim]/  \\[/dim]       /
    \\                   /
     '--.,_______,.--'
           [dim]|||[/dim]
    """,
    # 150° Back-Quarter
    """
       [bold bright_red]_,.-------.,_[/bold bright_red]
     [bold white],;~'             '~;,
   ,;                   ;,
  ;                       ;
 ;                         ;
 |                         |
 |           [dim]___[/dim]           |
  ;         [dim]/   \\[/dim]         ;
   \\                     /
    '--.,_______,.--'
          [dim]|||||[/dim]
    """,
    # 180° Full Back
    """
       [bold bright_red]_,.-------.,_[/bold bright_red]
     [bold white],;~'             '~;,
   ,;                   ;,
  ;                       ;
 ;                         ;
 |            [dim].[/dim]            |
 |           [dim]/ \\[/dim]           |
  ;         [dim]|   |[/dim]         ;
   \\         [dim]'-'[/dim]         /
    '--.,_______,.--'
         [dim]|||||||[/dim]
    """,
    # 210° Back-Left
    """
       [bold bright_red]_,.-------.,_[/bold bright_red]
     [bold white],;~'             '~;,
   ,;                   ;,
  ;                       ;
 ;                         ;
 |                         |
 |           [dim]___[/dim]           |
  ;         [dim]/   \\[/dim]         ;
   \\                     /
    '--.,_______,.--'
          [dim]|||||[/dim]
    """,
    # 240° Back-Quarter-Left
    """
         [bold bright_red],.-----.,[/bold bright_red]
      [bold white],;~'       '~;,
    ,;               ;,
   ;                   ;
  ;                     ;
  |                     |
  ;         [dim]__[/dim]          |
   \\       [dim]/  \\[/dim]        ;
    \\                   /
     '--.,_______,.--'
           [dim]|||[/dim]
    """,
    # 270° Side-Left
    """
         [bold bright_red],.-----.,[/bold bright_red]
      [bold white],;~'       '~;,
    ,;               ;,
   ;                   ;
  ;            [bold bright_red],---.[/bold bright_red]  ;
  |            [bold bright_red]/ [bold red]O[/bold red] [bold white]#[/bold white] \\[/bold bright_red] |
  ;        [bold white]-,[/bold white]    [bold bright_red]\\___/[/bold bright_red] |
   \\        [bold red]\\ \\[/bold red]        ;
    \\        [bold white]|_|[/bold white]      /
     '--.,___,.--'
         [bold white]|_|[/bold white]
         [dim]| |[/dim]
    """,
    # 300° Quarter-Left
    """
        [bold bright_red],.-------.,[/bold bright_red]
     [bold white],;~'          '~;,
   ,;                ;,
  ;                    ;
 ;   [bold bright_red],-.       ,---.[/bold bright_red]  ;
 |  [bold bright_red]/   \\     / [bold red]O[/bold red] [bold white]#[/bold white] \\[/bold bright_red] |
 ;  [bold bright_red]'---'  [bold white]_,[/bold white]   \\___/[/bold bright_red] |
  \\         [bold red]\\_|/[/bold red]      ;
   \\        [bold white]|_|_|[/bold white]    /
    '--.,_____,.--'
        [bold white]|_|_|[/bold white]
        [dim]| | |[/dim]
    """,
    # 330° Front-Left
    """
       [bold bright_red]_,.-------.,_[/bold bright_red]
     [bold white],;~'            '~;,
   ,;                  ;,
  ;                      ;
 ;    [bold bright_red],-.        ,---.[/bold bright_red]  ;
 |   [bold bright_red]/ [bold red]O[/bold red] \\      / [bold red]O[/bold red] [bold white]#[/bold white] \\[/bold bright_red] |
 |   [bold bright_red]\\_/   [bold white]_,[/bold white]   \\___/[/bold bright_red] |
  ;         [bold red]\\_|/[/bold red]       ;
   \\        [bold white]|_|_|[/bold white]     /
    '--.,______,.--'
       [bold white]|_|_|_|[/bold white]
       [dim]| | | |[/dim]
    """,
]


def get_skull_frame(index: int) -> str:
    """Return skull frame by rotational index (0 to 11)."""
    return DETAILED_FRAMES[index % len(DETAILED_FRAMES)]
