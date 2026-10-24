#!/usr/bin/env python3
"""
RILZ TOOLS - WhatsApp Sticker & Animated GIF Engine
Converts videos, GIFs, and images to:
1. WhatsApp Animated Sticker (.webp, 512x512, <= 500KB, <= 6s)
2. High-Quality Looping GIF (Palette-optimized)
3. WhatsApp Static Sticker (.webp, 512x512)
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FFMPEG_BIN = PROJECT_ROOT / "bin" / "ffmpeg.exe"

def get_ffmpeg_path() -> str:
    if FFMPEG_BIN.exists():
        return str(FFMPEG_BIN)
    sys_ffmpeg = shutil.which("ffmpeg")
    if sys_ffmpeg:
        return sys_ffmpeg
    return "ffmpeg"


def video_to_wa_sticker(input_path: str, output_path: str, duration: float = 6.0, fps: int = 15) -> Dict[str, Any]:
    """
    Converts video/gif to an official WhatsApp Animated Sticker:
    - Max 512x512 (aspect ratio preserved, centered with transparent padding)
    - Max 6.0 seconds duration
    - 15 fps
    - WebP format (libwebp), loop 0
    - File size target: <= 500 KB
    """
    ffmpeg = get_ffmpeg_path()
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    # WhatsApp requirements: scale to fit 512x512, transparent background padding
    vf_filter = (
        f"fps={fps},"
        f"scale=512:512:force_original_aspect_ratio=decrease,"
        f"pad=512:512:(ow-iw)/2:(oh-ih)/2:color=0x00000000"
    )

    cmd = [
        ffmpeg,
        "-y",
        "-t", str(min(duration, 6.0)),
        "-i", input_path,
        "-vf", vf_filter,
        "-vcodec", "libwebp",
        "-lossless", "0",
        "-compression_level", "4",
        "-q:v", "55",
        "-loop", "0",
        "-an",
        "-vsync", "0",
        output_path
    ]

    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60)
        if proc.returncode != 0 or not os.path.exists(output_path):
            return {"success": False, "error": f"FFmpeg error: {proc.stderr[-300:] if proc.stderr else 'Unknown'}"}

        size_bytes = os.path.getsize(output_path)
        # If size exceeds 500KB (WhatsApp limit), do a fast pass with lower quality
        if size_bytes > 500 * 1024:
            cmd_smaller = [
                ffmpeg,
                "-y",
                "-t", str(min(duration, 5.0)),
                "-i", input_path,
                "-vf", f"fps=12,scale=400:400:force_original_aspect_ratio=decrease,pad=512:512:(ow-iw)/2:(oh-ih)/2:color=0x00000000",
                "-vcodec", "libwebp",
                "-lossless", "0",
                "-q:v", "35",
                "-loop", "0",
                "-an",
                output_path
            ]
            subprocess.run(cmd_smaller, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=40)
            size_bytes = os.path.getsize(output_path)

        size_kb = round(size_bytes / 1024, 1)
        return {
            "success": True,
            "filepath": output_path,
            "filename": os.path.basename(output_path),
            "size_kb": size_kb,
            "size_str": f"{size_kb} KB",
            "format": "webp_animated",
            "wa_compliant": size_bytes <= 500 * 1024
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def video_to_gif(input_path: str, output_path: str, duration: float = 8.0, fps: int = 15, width: int = 480) -> Dict[str, Any]:
    """
    Converts video to high quality palette-optimized looping GIF.
    """
    ffmpeg = get_ffmpeg_path()
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    # 2-pass palette generation for ultra-clean GIF colors
    vf_filter = f"fps={fps},scale={width}:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer"

    cmd = [
        ffmpeg,
        "-y",
        "-t", str(duration),
        "-i", input_path,
        "-vf", vf_filter,
        "-loop", "0",
        output_path
    ]

    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60)
        if proc.returncode != 0 or not os.path.exists(output_path):
            return {"success": False, "error": f"FFmpeg error: {proc.stderr[-300:] if proc.stderr else 'Unknown'}"}

        size_bytes = os.path.getsize(output_path)
        size_kb = round(size_bytes / 1024, 1)
        return {
            "success": True,
            "filepath": output_path,
            "filename": os.path.basename(output_path),
            "size_kb": size_kb,
            "size_str": f"{size_kb} KB" if size_kb < 1024 else f"{round(size_kb/1024, 2)} MB",
            "format": "gif"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def image_to_wa_sticker(input_path: str, output_path: str) -> Dict[str, Any]:
    """
    Converts static image (PNG/JPG) to a 512x512 transparent static WhatsApp Sticker (.webp).
    """
    ffmpeg = get_ffmpeg_path()
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    vf_filter = "scale=512:512:force_original_aspect_ratio=decrease,pad=512:512:(ow-iw)/2:(oh-ih)/2:color=0x00000000"

    cmd = [
        ffmpeg,
        "-y",
        "-i", input_path,
        "-vf", vf_filter,
        "-vcodec", "libwebp",
        "-lossless", "0",
        "-q:v", "80",
        output_path
    ]

    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)
        if proc.returncode != 0 or not os.path.exists(output_path):
            return {"success": False, "error": f"FFmpeg error: {proc.stderr[-300:] if proc.stderr else 'Unknown'}"}

        size_bytes = os.path.getsize(output_path)
        size_kb = round(size_bytes / 1024, 1)
        return {
            "success": True,
            "filepath": output_path,
            "filename": os.path.basename(output_path),
            "size_kb": size_kb,
            "size_str": f"{size_kb} KB",
            "format": "webp_static",
            "wa_compliant": size_bytes <= 100 * 1024
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
