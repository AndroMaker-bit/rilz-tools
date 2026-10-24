import os
from typing import Optional
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
from rich.console import Console

console = Console()


def enhance_to_hd(
    image_path: str,
    output_path: Optional[str] = None,
    scale_factor: int = 2,
    sharpness: float = 1.4,
    contrast: float = 1.1,
    color_boost: float = 1.05,
) -> Optional[str]:
    """
    Upscale image to HD resolution and apply perceptual sharpening & contrast enhancement.
    Returns the output file path string on success, or None on failure.
    """
    if not os.path.exists(image_path):
        console.print(f"[bold red]File {image_path} tidak ditemukan![/bold red]")
        return None

    try:
        raw_img = Image.open(image_path)
        # Correct mobile phone orientation from EXIF
        img = ImageOps.exif_transpose(raw_img) or raw_img
        orig_w, orig_h = img.size

        # Clamp scale factor to a safe range (2 to 4)
        scale = max(1, min(int(scale_factor), 8))

        # Check alpha channel
        has_alpha = img.mode in ("RGBA", "LA", "P")
        working_img = img if has_alpha else img.convert("RGB")

        # 1. Upscale using high-fidelity Lanczos resampling
        new_w = int(orig_w * scale)
        new_h = int(orig_h * scale)
        upscaled = working_img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        # 2. Unsharp mask filter for crisp micro-details
        enhanced = upscaled.filter(ImageFilter.UnsharpMask(radius=2, percent=140, threshold=3))

        # 3. Dynamic enhancements
        if sharpness != 1.0:
            enhancer = ImageEnhance.Sharpness(enhanced)
            enhanced = enhancer.enhance(sharpness)

        if contrast != 1.0:
            enhancer = ImageEnhance.Contrast(enhanced)
            enhanced = enhancer.enhance(contrast)

        if color_boost != 1.0 and not has_alpha:
            enhancer = ImageEnhance.Color(enhanced)
            enhanced = enhancer.enhance(color_boost)

        # Output path handling
        if not output_path:
            dir_name, base_name = os.path.split(image_path)
            name, ext = os.path.splitext(base_name)
            output_path = os.path.join(dir_name or ".", f"{name}_HD_{scale}x{ext or '.png'}")

        abs_out = os.path.abspath(output_path)
        os.makedirs(os.path.dirname(abs_out), exist_ok=True)

        ext_lower = os.path.splitext(abs_out)[1].lower()
        if ext_lower in (".jpg", ".jpeg"):
            if enhanced.mode in ("RGBA", "LA", "P"):
                # Composite onto clean white background for JPEG
                bg = Image.new("RGB", enhanced.size, (255, 255, 255))
                if enhanced.mode == "RGBA":
                    bg.paste(enhanced, mask=enhanced.split()[3])
                else:
                    bg.paste(enhanced.convert("RGBA"))
                enhanced = bg
            enhanced.save(abs_out, format="JPEG", quality=95, optimize=True)
        elif ext_lower == ".webp":
            enhanced.save(abs_out, format="WEBP", quality=95)
        else:
            # Default to PNG
            enhanced.save(abs_out, format="PNG", optimize=True)

        console.print(f"\n[bold green]✅ Gambar berhasil di-upgrade ke HD![/bold green]")
        console.print(f"📐 Resolusi Asli : [bold cyan]{orig_w}x{orig_h}[/bold cyan]")
        console.print(f"🚀 Resolusi HD   : [bold bright_green]{new_w}x{new_h}[/bold bright_green] ({scale}x Scale)")
        console.print(f"💾 File Output   : [bold white]{abs_out}[/bold white]\n")
        return abs_out

    except Exception as e:
        console.print(f"[bold red]Gagal memproses gambar ke HD:[/bold red] {e}")
        return None
