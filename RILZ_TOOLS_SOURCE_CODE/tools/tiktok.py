import re
from typing import Dict, Optional
import requests
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def check_tiktok_video(url: str) -> Optional[Dict]:
    """Check metadata of a TikTok video."""
    try:
        import yt_dlp
    except ImportError:
        console.print("[bold red]yt-dlp belum terinstall.[/bold red]")
        return None

    console.print(f"\n[bold cyan]🔍 Memeriksa detail video TikTok...[/bold cyan]")
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                return None

            details = {
                "id": info.get("id"),
                "title": info.get("title") or info.get("description", "No title"),
                "uploader": info.get("uploader"),
                "uploader_id": info.get("uploader_id"),
                "duration": info.get("duration"),
                "view_count": info.get("view_count"),
                "like_count": info.get("like_count"),
                "comment_count": info.get("comment_count"),
                "repost_count": info.get("repost_count"),
                "upload_date": info.get("upload_date"),
                "webpage_url": info.get("webpage_url", url),
            }
            return details
    except Exception as e:
        console.print(f"[bold red]Gagal mengambil data video:[/bold red] {e}")
        return None


def check_tiktok_user(username: str) -> Optional[Dict]:
    """Check existence and status of a TikTok username."""
    clean_username = username.lstrip("@").strip()
    profile_url = f"https://www.tiktok.com/@{clean_username}"

    console.print(f"\n[bold cyan]🔍 Memeriksa akun TikTok @{clean_username}...[/bold cyan]")

    try:
        import yt_dlp
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "ignoreerrors": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(profile_url, download=False, process=False)
            if info and info.get("id"):
                return {
                    "username": clean_username,
                    "exists": True,
                    "sec_uid": info.get("id"),
                    "url": profile_url,
                    "status": "Active / Registered",
                }
            else:
                return {
                    "username": clean_username,
                    "exists": False,
                    "sec_uid": None,
                    "url": profile_url,
                    "status": "Not Found / Available or Private",
                }
    except Exception as e:
        return {
            "username": clean_username,
            "exists": False,
            "error": str(e),
            "url": profile_url,
            "status": "Check failed",
        }


def display_tiktok_result(query: str):
    """Detect whether query is a video URL or username and display structured results."""
    if "tiktok.com" in query and ("/video/" in query or "/v/" in query):
        data = check_tiktok_video(query)
        if not data:
            console.print("[bold red]❌ Video tidak ditemukan atau link tidak valid.[/bold red]\n")
            return

        table = Table(title="🎵 Detail Video TikTok", expand=True)
        table.add_column("Property", style="bold cyan", width=18)
        table.add_column("Value", style="bold white")

        table.add_row("Title/Caption", str(data.get("title", ""))[:60])
        table.add_row("Creator", f"@{data.get('uploader_id')} ({data.get('uploader')})")
        table.add_row("Duration", f"{data.get('duration', 0)} detik")
        table.add_row("Views", f"{data.get('view_count', 0):,}" if data.get('view_count') else "N/A")
        table.add_row("Likes", f"{data.get('like_count', 0):,}" if data.get('like_count') else "N/A")
        table.add_row("Comments", f"{data.get('comment_count', 0):,}" if data.get('comment_count') else "N/A")
        table.add_row("Upload Date", str(data.get("upload_date", "N/A")))
        table.add_row("Video URL", data.get("webpage_url", query))

        console.print(table)
    else:
        # Username checker
        data = check_tiktok_user(query)
        if not data:
            console.print("[bold red]❌ Gagal memeriksa username.[/bold red]\n")
            return

        status_color = "green" if data["exists"] else "yellow"
        table = Table(title="👤 Status Akun TikTok", expand=True)
        table.add_column("Property", style="bold cyan", width=18)
        table.add_column("Value", style="bold white")

        table.add_row("Username", f"@{data['username']}")
        table.add_row("Status", f"[{status_color}]{data['status']}[/{status_color}]")
        if data.get("sec_uid"):
            table.add_row("TikTok SecUID", str(data["sec_uid"]))
        table.add_row("Profile Link", data["url"])

        console.print(table)
