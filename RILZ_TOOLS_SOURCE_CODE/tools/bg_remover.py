import os
from collections import deque
from typing import Optional, Tuple
from PIL import Image, ImageOps
from rich.console import Console

console = Console()


def color_distance(c1: Tuple[int, int, int], c2: Tuple[int, int, int]) -> float:
    """Calculate Euclidean distance between two RGB colors."""
    return ((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2 + (c1[2] - c2[2]) ** 2) ** 0.5


def remove_background(
    image_path: str,
    output_path: Optional[str] = None,
    tolerance: int = 40,
    replace_color: Optional[Tuple[int, int, int]] = None,
) -> Optional[str]:
    """
    Remove background from an image using edge-based flood fill mask and tolerance.
    If replace_color is given (e.g. (255, 255, 255)), replaces background instead of transparent.
    Returns output file path on success, None on failure.
    """
    if not os.path.exists(image_path):
        console.print(f"[bold red]File {image_path} tidak ditemukan![/bold red]")
        return None

    try:
        raw_img = Image.open(image_path)
        img = ImageOps.exif_transpose(raw_img) or raw_img
        img = img.convert("RGBA")
        width, height = img.size
        pixels = img.load()

        # Sample the background color from four corners
        corners = [
            pixels[0, 0][:3],
            pixels[width - 1, 0][:3],
            pixels[0, height - 1][:3],
            pixels[width - 1, height - 1][:3],
        ]

        # Use median/average corner color as background seed
        bg_r = sum(c[0] for c in corners) // 4
        bg_g = sum(c[1] for c in corners) // 4
        bg_b = sum(c[2] for c in corners) // 4
        bg_target = (bg_r, bg_g, bg_b)

        # Flood fill starting from all perimeter edge pixels
        visited = bytearray(width * height)
        queue = deque()

        # Add top and bottom borders
        for x in range(width):
            queue.append((x, 0))
            queue.append((x, height - 1))
        # Add left and right borders
        for y in range(height):
            queue.append((0, y))
            queue.append((width - 1, y))

        is_bg = bytearray(width * height)

        while queue:
            x, y = queue.popleft()
            idx = y * width + x
            if visited[idx]:
                continue
            visited[idx] = 1

            px = pixels[x, y][:3]
            dist = color_distance(px, bg_target)

            if dist <= tolerance:
                is_bg[idx] = 1
                # Check 4 neighbors
                if x > 0 and not visited[idx - 1]:
                    queue.append((x - 1, y))
                if x < width - 1 and not visited[idx + 1]:
                    queue.append((x + 1, y))
                if y > 0 and not visited[idx - width]:
                    queue.append((x, y - 1))
                if y < height - 1 and not visited[idx + width]:
                    queue.append((x, y + 1))

        # Apply transparency or replace color
        out_img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        out_pixels = out_img.load()

        for y in range(height):
            for x in range(width):
                idx = y * width + x
                r, g, b, a = pixels[x, y]
                if is_bg[idx]:
                    if replace_color:
                        out_pixels[x, y] = (replace_color[0], replace_color[1], replace_color[2], 255)
                    else:
                        out_pixels[x, y] = (0, 0, 0, 0)
                else:
                    out_pixels[x, y] = (r, g, b, a)

        # Output handling
        if not output_path:
            dir_name, base_name = os.path.split(image_path)
            name, _ = os.path.splitext(base_name)
            output_path = os.path.join(dir_name or ".", f"{name}_nobg.png")

        abs_out = os.path.abspath(output_path)
        os.makedirs(os.path.dirname(abs_out), exist_ok=True)

        if replace_color:
            out_img.convert("RGB").save(abs_out)
        else:
            out_img.save(abs_out, "PNG")

        console.print(f"\n[bold green]✅ Background berhasil dihapus![/bold green]")
        console.print(f"🎯 Target BG Color: RGB{bg_target} (Toleransi: {tolerance})")
        console.print(f"💾 File Output     : [bold white]{abs_out}[/bold white]\n")
        return abs_out

    except Exception as e:
        console.print(f"[bold red]Gagal menghapus background:[/bold red] {e}")
        return None
