"""
Photorealistic Menacing Skull Multi-Angle Matrix (TikTok Meme Edition)
Optimized for 16-block width (32 character cols) to fit side-by-side in any terminal window.
"""

PALETTE = {
    ' ': '  ',
    '#': '[bold rgb(255,215,130)]██[/bold rgb(255,215,130)]', # Golden highlight
    'O': '[bold rgb(255,165,55)]██[/bold rgb(255,165,55)]',   # Bright amber
    'o': '[rgb(220,95,25)]██[/rgb(220,95,25)]',               # Burning orange
    '.': '[rgb(120,30,12)]██[/rgb(120,30,12)]',               # Deep crimson shadow
    'X': '[rgb(15,4,4)]░░[/rgb(15,4,4)]',                     # Dark hollow void
}

# 0° - Front View (Direct menacing stare with deep hollow eyes)
FRAME_0 = [
    '    .oooOOooo.    ',
    '  .oOO####OOo.  ',
    ' .oOO######OOo. ',
    '.oOO########OOo.',
    '.oOO########OOo.',
    '.o.XX.####.XX.o.',
    '.oXXXX.##.XXXXo.',
    '.o.XX......XX.o.',
    ' .o....XX....o. ',
    '  .oo.XXXX.oo.  ',
    '  .oo.OOOO.oo.  ',
    '  .o.OO.OO.OO.o. ',
    '  .o..........o. ',
    '   .o.OO.OO.o.  ',
    '   .ooOOOOoo.   ',
    '     .oooo.     ',
]

# 45° - Turning Right
FRAME_45 = [
    '   .oooOOooo.   ',
    ' .oOO####OOo.  ',
    '.oOO######OOo. ',
    '.oOO########Oo.',
    '.oOO########Oo.',
    '.o.XX.####.XXo.',
    '.oXXXX.##.XXXX.',
    '.o.XX......XX.o',
    ' .o....XX...o. ',
    '  .oo.XXX.oo.  ',
    '  .oo.OOO.oo.  ',
    '  .o.OO.OO.o.  ',
    '  .o........o. ',
    '   .o.OO.OO.o. ',
    '   .ooOOOOoo.  ',
    '     .oooo.    ',
]

# 90° - Pure Right Profile
FRAME_90 = [
    '   .oooOOo.     ',
    ' .oOO###Oo.    ',
    '.oOO####OOo.   ',
    '.oOO#####OOo.  ',
    '.oOO#####OOo.  ',
    '.o.XX.###.oo.  ',
    '.oXXXX.##.o.   ',
    '.o.XX.....o.   ',
    ' .o...XX..o.   ',
    '  .oo.XX.o.    ',
    '  .oo.OO.o.    ',
    '  .o.OO.o.     ',
    '  .o....o.     ',
    '   .o.OO.o.    ',
    '   .ooOO.o.    ',
    '     .ooo.     ',
]

# 135° - Turning Rear-Right
FRAME_135 = [
    '   .oooOOo.     ',
    ' .oOOOO##Oo.   ',
    '.oOOOO###OOo.  ',
    '.oOOOO####Oo.  ',
    '.oOOOO####Oo.  ',
    '.o.OO.####.o.  ',
    '.oOOOO.##.Oo.  ',
    '.o.OO......o.  ',
    ' .o...OO..o.   ',
    '  .oo.OO.o.    ',
    '  .oo.OO.o.    ',
    '  .o.OO.o.     ',
    '  .o....o.     ',
    '   .o.OO.o.    ',
    '   .ooOO.o.    ',
    '     .ooo.     ',
]

# 180° - Back of Skull
FRAME_180 = [
    '    .oooOOooo.    ',
    '  .oOO####OOo.  ',
    ' .oOO######OOo. ',
    '.oOO########OOo.',
    '.oOO########OOo.',
    '.o.OO.####.OO.o.',
    '.oOOOO.##.OOOOo.',
    '.o.OO......OO.o.',
    ' .o....OO....o. ',
    '  .oo.OOOO.oo.  ',
    '  .oo.OOOO.oo.  ',
    '  .o.OOOOOOOO.o. ',
    '  .o..........o. ',
    '   .o.OOOOOO.o.  ',
    '   .ooOOOOoo.   ',
    '     .oooo.     ',
]

# 225° - Turning Rear-Left
FRAME_225 = [
    '     .oOOooo.   ',
    '   .oO##OOOOo. ',
    '  .oOO###OOOOo.',
    '  .oO####OOOOo.',
    '  .oO####OOOOo.',
    '  .o.####.OO.o.',
    '   .oO.##.OOOOo.',
    '  .o......OO.o.',
    '   .o..OO...o. ',
    '    .o.OO.oo.  ',
    '    .o.OO.oo.  ',
    '     .o.OO.o.  ',
    '     .o....o.  ',
    '    .o.OO.o.   ',
    '    .o.OOoo.   ',
    '     .ooo.     ',
]

# 270° - Pure Left Profile
FRAME_270 = [
    '     .oOOooo.   ',
    '    .oO###OOo. ',
    '   .oOO####OOo.',
    '  .oOO#####OOo.',
    '  .oOO#####OOo.',
    '  .oo.###.XX.o.',
    '   .o.##.XXXXo.',
    '   .o.....XX.o.',
    '   .o..XX...o. ',
    '    .o.XX.oo.  ',
    '    .o.OO.oo.  ',
    '     .o.OO.o.  ',
    '     .o....o.  ',
    '    .o.OO.o.   ',
    '    .o.OOoo.   ',
    '     .ooo.     ',
]

# 315° - Turning Front-Left
FRAME_315 = [
    '   .oooOOooo.   ',
    '  .oOO####OOo. ',
    ' .oOO######OOo.',
    '.oO########OOo.',
    '.oO########OOo.',
    '.oXX.####.XX.o.',
    '.XXXX.##.XXXXo.',
    'o.XX......XX.o.',
    ' .o...XX....o. ',
    '  .oo.XXX.oo.  ',
    '  .oo.OOO.oo.  ',
    '  .o.OO.OO.o.  ',
    ' .o........o.  ',
    ' .o.OO.OO.o.   ',
    '  .ooOOOOoo.   ',
    '    .oooo.     ',
]

ALL_FRAMES = [
    FRAME_0,
    FRAME_45,
    FRAME_90,
    FRAME_135,
    FRAME_180,
    FRAME_225,
    FRAME_270,
    FRAME_315,
]

def render_frame_text(frame_matrix) -> str:
    lines = []
    for row in frame_matrix:
        line = ''.join(PALETTE.get(ch, '  ') for ch in row)
        lines.append(line)
    return '\n'.join(lines)
