import os
import re
import shutil
import tempfile
import time
from pathlib import Path
from typing import Dict, Optional, Tuple
import requests
from rich.console import Console

console = Console()


def get_ffmpeg_path() -> Optional[str]:
    """Find FFmpeg executable from imageio_ffmpeg, PATH, or local directories."""
    try:
        import imageio_ffmpeg
        exe = imageio_ffmpeg.get_ffmpeg_exe()
        if exe and os.path.exists(exe):
            return exe
    except Exception:
        pass

    which_ffmpeg = shutil.which("ffmpeg")
    if which_ffmpeg and os.path.exists(which_ffmpeg):
        return which_ffmpeg

    # Common local Windows paths
    candidates = [
        r"C:\ffmpeg\bin\ffmpeg.exe",
        os.path.expanduser(r"~\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-*\bin\ffmpeg.exe"),
    ]
    for c in candidates:
        matches = list(Path(os.path.dirname(c)).glob(os.path.basename(c))) if "*" in c else ([Path(c)] if Path(c).exists() else [])
        if matches and matches[0].exists():
            return str(matches[0])

    return None


def sanitize_filename(title: str, max_len: int = 60) -> str:
    """Sanitize title to be a valid Windows & Android filename."""
    if not title:
        return "media"
    cleaned = re.sub(r'[\\/*?:"<>|]', '_', title)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    cleaned = cleaned[:max_len].rstrip('. ')
    return cleaned or "media"


def is_tiktok_url(url: str) -> bool:
    """Check if the URL is from TikTok."""
    low = url.lower()
    return "tiktok.com" in low or "vt.tiktok.com" in low or "vm.tiktok.com" in low


def fetch_tiktok_direct(url: str, output_dir: str, audio_only: bool = False) -> Optional[Dict]:
    """
    Directly fetch TikTok video (No Watermark MP4) or audio (MP3) using TikWM.
    Lightning fast and guarantees pure MP4 without needing ffmpeg re-encode.
    """
    try:
        api_url = "https://www.tikwm.com/api/"
        resp = requests.get(api_url, params={"url": url, "hd": 1}, timeout=10)
        if resp.status_code != 200:
            return None

        data = resp.json()
        if data.get("code") != 0 or "data" not in data:
            return None

        d = data["data"]
        title = d.get("title") or "TikTok_Video"
        clean_name = sanitize_filename(title)
        stamp = int(time.time())

        os.makedirs(output_dir, exist_ok=True)

        if audio_only:
            media_url = d.get("music") or d.get("music_info", {}).get("play")
            if not media_url:
                return None
            filename = f"{clean_name}_{stamp}.mp3"
            filepath = os.path.join(output_dir, filename)
            r = requests.get(media_url, stream=True, timeout=20)
            if r.status_code == 200:
                with open(filepath, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1024 * 64):
                        if chunk:
                            f.write(chunk)
                size = os.path.getsize(filepath)
                return {
                    "success": True,
                    "filepath": filepath,
                    "filename": filename,
                    "ext": ".mp3",
                    "title": title,
                    "thumbnail": d.get("cover", ""),
                    "duration": d.get("duration", 0),
                    "size_bytes": size,
                    "size_mb": round(size / (1024 * 1024), 2),
                    "media_type": "audio/mpeg",
                    "source": "TikTok (TikWM Direct)",
                }
        else:
            # Video: try HD play first, then standard play
            media_url = d.get("hdplay") or d.get("play")
            if not media_url:
                return None
            filename = f"{clean_name}_{stamp}.mp4"
            filepath = os.path.join(output_dir, filename)
            r = requests.get(media_url, stream=True, timeout=30)
            if r.status_code == 200:
                with open(filepath, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1024 * 128):
                        if chunk:
                            f.write(chunk)
                size = os.path.getsize(filepath)
                return {
                    "success": True,
                    "filepath": filepath,
                    "filename": filename,
                    "ext": ".mp4",
                    "title": title,
                    "thumbnail": d.get("cover", ""),
                    "duration": d.get("duration", 0),
                    "size_bytes": size,
                    "size_mb": round(size / (1024 * 1024), 2),
                    "media_type": "video/mp4",
                    "source": "TikTok No-Watermark HD",
                }
    except Exception as e:
        console.print(f"[dim yellow]TikWM direct bypass skipped ({e}), falling back to yt-dlp...[/dim yellow]")
        return None


def get_video_info(url: str) -> Dict:
    """Fetch video metadata quickly without downloading."""
    try:
        import yt_dlp
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                "success": True,
                "title": info.get("title", "Video"),
                "thumbnail": info.get("thumbnail", ""),
                "duration": info.get("duration", 0),
                "uploader": info.get("uploader", "Unknown"),
                "view_count": info.get("view_count", 0),
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


def process_video_download(url: str, output_dir: str, audio_only: bool = False) -> Dict:
    """
    Download video or audio ensuring standard MP4 (video) or MP3 (audio) output.
    Uses FFmpeg integration so streams are properly merged and playable anywhere.
    """
    os.makedirs(output_dir, exist_ok=True)

    # 1. Try TikTok ultra-fast direct no-watermark path
    if is_tiktok_url(url):
        tiktok_res = fetch_tiktok_direct(url, output_dir, audio_only=audio_only)
        if tiktok_res and tiktok_res.get("success"):
            return tiktok_res

    # 2. General yt-dlp path with FFmpeg integration
    try:
        import yt_dlp
    except ImportError:
        return {"success": False, "error": "yt-dlp belum terpasang di sistem."}

    ffmpeg_bin = get_ffmpeg_path()
    stamp = int(time.time())
    out_id = f"media_{stamp}_{os.getpid()}"
    out_template = os.path.join(output_dir, f"{out_id}.%(ext)s")

    if audio_only:
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": out_template,
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
        }
        if ffmpeg_bin:
            ydl_opts["ffmpeg_location"] = ffmpeg_bin
            ydl_opts["postprocessors"] = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ]
    else:
        # Standard video: Ensure MP4 container with merged audio & video
        ydl_opts = {
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best[ext=mp4]/best",
            "outtmpl": out_template,
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
        }
        if ffmpeg_bin:
            ydl_opts["ffmpeg_location"] = ffmpeg_bin
            ydl_opts["merge_output_format"] = "mp4"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            candidate_fn = ydl.prepare_filename(info)

        # Locate final file on disk
        final_path = None
        if os.path.exists(candidate_fn):
            final_path = candidate_fn
        else:
            # Check files matching out_id in output_dir
            for p in Path(output_dir).glob(f"{out_id}.*"):
                final_path = str(p)
                break

        if not final_path or not os.path.exists(final_path):
            return {"success": False, "error": "File hasil unduhan tidak ditemukan di server."}

        # Check extension
        raw_ext = os.path.splitext(final_path)[1].lower()
        title = info.get("title") or "Video"
        clean_name = sanitize_filename(title)
        target_ext = ".mp3" if audio_only else ".mp4"

        # Rename to clean target name if needed or ensure safe filename
        target_filename = f"{clean_name}{target_ext}"
        target_path = os.path.join(output_dir, f"{clean_name}_{stamp}{target_ext}")

        # If extension matches target, rename to readable filename
        if raw_ext == target_ext:
            os.rename(final_path, target_path)
            final_path = target_path
        else:
            # If not matching but ffmpeg is available and video isn't mp4, rewrap to mp4
            if not audio_only and ffmpeg_bin and raw_ext in [".webm", ".mkv"]:
                try:
                    import subprocess
                    subprocess.run(
                        [ffmpeg_bin, "-y", "-i", final_path, "-c", "copy", target_path],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        check=True,
                    )
                    os.remove(final_path)
                    final_path = target_path
                    raw_ext = target_ext
                except Exception:
                    pass

        file_ext = os.path.splitext(final_path)[1].lower()
        size = os.path.getsize(final_path)

        return {
            "success": True,
            "filepath": final_path,
            "filename": f"{clean_name}{file_ext}",
            "ext": file_ext,
            "title": title,
            "thumbnail": info.get("thumbnail", ""),
            "duration": info.get("duration", 0),
            "size_bytes": size,
            "size_mb": round(size / (1024 * 1024), 2),
            "media_type": "audio/mpeg" if file_ext == ".mp3" else "video/mp4",
            "source": info.get("extractor_key", "yt-dlp"),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def download_video(url: str, output_dir: str = "downloads", audio_only: bool = False) -> bool:
    """CLI wrapper for terminal commands."""
    res = process_video_download(url, output_dir, audio_only=audio_only)
    if res.get("success"):
        console.print(f"\n[bold green]✅ Berhasil mengunduh:[/bold green] [bold white]{res.get('title')}[/bold white]")
        console.print(f"[dim]Tersimpan di: {res.get('filepath')} ({res.get('size_mb')} MB)[/dim]\n")
        try:
            from tools.notifier import notify
            notify("RILZ TOOLS — Video Downloader", f"Berhasil mengunduh: {res.get('title', '')[:40]}")
        except Exception:
            pass
        return True
    else:
        console.print(f"\n[bold red]❌ Gagal mengunduh video:[/bold red] {res.get('error')}\n")
        return False
