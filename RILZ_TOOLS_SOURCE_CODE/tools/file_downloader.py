"""
Universal Cloud & Direct File Downloader for RILZ TOOLS
Supports: Google Drive, MediaFire, TeraBox, Dropbox, PixelDrain, and Direct URLs.
Features real-time Rich progress bar, speed tracker, and ETA.
"""

import os
import re
import urllib.parse
from typing import Optional, Tuple
import requests
from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TextColumn,
    DownloadColumn,
    TransferSpeedColumn,
    TimeRemainingColumn,
)

console = Console()

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}


def extract_filename_from_headers(response: requests.Response, fallback_url: str) -> str:
    """Extract filename from Content-Disposition header or fallback to URL path."""
    cd = response.headers.get("Content-Disposition", "")
    if cd:
        # Check for filename* (RFC 5987)
        match_star = re.search(r"filename\*=UTF-8''([^;'\"]+)", cd, re.IGNORECASE)
        if match_star:
            return urllib.parse.unquote(match_star.group(1))

        # Check for regular filename
        match = re.search(r'filename=["\']?([^;"\']+)["\']?', cd, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    # Fallback to URL path
    parsed = urllib.parse.urlparse(fallback_url)
    name = os.path.basename(parsed.path)
    if name and "." in name:
        return urllib.parse.unquote(name)

    return "downloaded_file.bin"


def resolve_mediafire_link(url: str) -> Tuple[Optional[str], Optional[str]]:
    """Extract direct download link and filename from a MediaFire page."""
    try:
        resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=12)
        if resp.status_code != 200:
            return None, None

        # Look for download button link
        match = re.search(r'href=[\'"](https?://download\d*\.mediafire\.com/[^\'"]+)[\'"]', resp.text)
        if not match:
            match = re.search(r'aria-label=[\'"]Download file[\'"]\s+href=[\'"]([^\'"]+)[\'"]', resp.text)

        if match:
            direct_url = match.group(1)
            # Try to find file name
            fn_match = re.search(r'<div class=[\'"]filename[\'"]>([^<]+)</div>', resp.text)
            filename = fn_match.group(1).strip() if fn_match else None
            return direct_url, filename

        return None, None
    except Exception:
        return None, None


def resolve_gdrive_download(url: str, session: requests.Session) -> Tuple[Optional[str], Optional[requests.Response]]:
    """Handle Google Drive direct download and confirmation tokens for large files."""
    file_id = None
    match = re.search(r"/file/d/([a-zA-Z0-9_-]+)", url)
    if match:
        file_id = match.group(1)
    else:
        match = re.search(r"id=([a-zA-Z0-9_-]+)", url)
        if match:
            file_id = match.group(1)

    if not file_id:
        return url, None

    download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
    resp = session.get(download_url, headers=DEFAULT_HEADERS, stream=True, timeout=15)

    # If small file or direct download starts
    content_type = resp.headers.get("Content-Type", "")
    if "text/html" not in content_type:
        return download_url, resp

    # Look for confirm token in warning page
    text = resp.text
    confirm_match = re.search(r'href=[\'"](/uc\?export=download&amp;confirm=[^&\'"]+&amp;id=[^\'"]+)[\'"]', text)
    if not confirm_match:
        confirm_match = re.search(r"confirm=([a-zA-Z0-9_-]+)", text)
        if confirm_match:
            confirm_token = confirm_match.group(1)
            confirm_url = f"https://drive.google.com/uc?export=download&confirm={confirm_token}&id={file_id}"
            resp2 = session.get(confirm_url, headers=DEFAULT_HEADERS, stream=True, timeout=15)
            return confirm_url, resp2

    if confirm_match:
        rel_url = confirm_match.group(1).replace("&amp;", "&")
        full_confirm_url = urllib.parse.urljoin("https://drive.google.com", rel_url)
        resp2 = session.get(full_confirm_url, headers=DEFAULT_HEADERS, stream=True, timeout=15)
        return full_confirm_url, resp2

    return download_url, resp


def resolve_terabox_link(url: str) -> Tuple[Optional[str], Optional[str]]:
    """Resolve TeraBox short links using public API resolvers."""
    try:
        # Extract shorturl parameter / key
        short_id = None
        match = re.search(r"/s/([a-zA-Z0-9_-]+)", url)
        if match:
            short_id = match.group(1)
        elif "surl=" in url:
            match = re.search(r"surl=([a-zA-Z0-9_-]+)", url)
            if match:
                short_id = match.group(1)

        if not short_id:
            return None, None

        api_url = f"https://terabox-dl.qtcloud.workers.dev/api/get-info?shorturl={short_id}"
        r = requests.get(api_url, headers=DEFAULT_HEADERS, timeout=12)
        if r.status_code == 200:
            data = r.json()
            if data.get("ok") and data.get("download_link"):
                return data["download_link"], data.get("filename")

        # Second public resolver fallback
        api_url2 = f"https://yt-api.m-s.workers.dev/terabox?url={urllib.parse.quote(url)}"
        r2 = requests.get(api_url2, headers=DEFAULT_HEADERS, timeout=12)
        if r2.status_code == 200:
            data2 = r2.json()
            if data2.get("download_link"):
                return data2["download_link"], data2.get("file_name")

    except Exception:
        pass

    return None, None


def resolve_pixeldrain_link(url: str) -> str:
    """Convert Pixeldrain view link to direct file download API link."""
    match = re.search(r"pixeldrain\.com/u/([a-zA-Z0-9]+)", url)
    if match:
        file_id = match.group(1)
        return f"https://pixeldrain.com/api/file/{file_id}"
    return url


def download_file(url: str, output_dir: str = "downloads", custom_filename: Optional[str] = None) -> bool:
    """Download any file with real-time speed, progress bar, and ETA."""
    os.makedirs(output_dir, exist_ok=True)
    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)

    direct_url = url.strip()
    detected_name = custom_filename
    initial_response = None

    console.print(f"\n[bold cyan]🔍 Menganalisis link unduhan:[/bold cyan] {url}")

    # 1. MediaFire
    if "mediafire.com" in direct_url:
        console.print("[dim]Mendeteksi link MediaFire, mengambil direct link...[/dim]")
        mf_url, mf_name = resolve_mediafire_link(direct_url)
        if mf_url:
            direct_url = mf_url
            if not detected_name and mf_name:
                detected_name = mf_name
            console.print(f"[bold green]✔ Direct MediaFire didapatkan:[/bold green] {detected_name or 'OK'}")
        else:
            console.print("[bold yellow]Peringatan: Gagal mengekstrak MediaFire direct link, mencoba langsung...[/bold yellow]")

    # 2. Google Drive
    elif "drive.google.com" in direct_url:
        console.print("[dim]Mendeteksi link Google Drive, memproses confirmation token...[/dim]")
        g_url, g_resp = resolve_gdrive_download(direct_url, session)
        direct_url = g_url
        initial_response = g_resp
        console.print("[bold green]✔ Link Google Drive siap diunduh[/bold green]")

    # 3. TeraBox
    elif any(d in direct_url for d in ["terabox.com", "1024tera.com", "teraboxapp.com", "terabox.app", "teraboxlink.com"]):
        console.print("[dim]Mendeteksi link TeraBox, menyelesaikan server proxy...[/dim]")
        tb_url, tb_name = resolve_terabox_link(direct_url)
        if tb_url:
            direct_url = tb_url
            if not detected_name and tb_name:
                detected_name = tb_name
            console.print(f"[bold green]✔ Direct TeraBox didapatkan:[/bold green] {detected_name or 'OK'}")
        else:
            console.print("[bold yellow]Peringatan: Gagal bypass TeraBox secara otomatis, mencoba link langsung...[/bold yellow]")

    # 4. Dropbox
    elif "dropbox.com" in direct_url:
        if "dl=0" in direct_url:
            direct_url = direct_url.replace("dl=0", "dl=1")
        elif "?dl=" not in direct_url:
            direct_url += "?dl=1"
        console.print("[bold green]✔ Direct Dropbox URL siap diunduh[/bold green]")

    # 5. Pixeldrain
    elif "pixeldrain.com" in direct_url:
        direct_url = resolve_pixeldrain_link(direct_url)
        console.print("[bold green]✔ Direct Pixeldrain API siap diunduh[/bold green]")

    # Start Streaming Download
    try:
        response = initial_response or session.get(direct_url, stream=True, timeout=20)
        response.raise_for_status()

        # Determine filename
        if not detected_name:
            detected_name = extract_filename_from_headers(response, direct_url)

        # Sanitize filename
        safe_name = re.sub(r'[\\/*?:"<>|]', "_", detected_name)
        out_path = os.path.join(output_dir, safe_name)

        total_size = int(response.headers.get("content-length", 0))

        console.print(f"📦 Nama File : [bold bright_white]{safe_name}[/bold bright_white]")
        console.print(f"📁 Lokasi    : [dim]{os.path.abspath(out_path)}[/dim]\n")

        with Progress(
            SpinnerColumn(),
            TextColumn("[bold cyan]{task.fields[filename]}", justify="left"),
            BarColumn(bar_width=None),
            "[progress.percentage]{task.percentage:>3.1f}%",
            "•",
            DownloadColumn(),
            "•",
            TransferSpeedColumn(),
            "•",
            TimeRemainingColumn(),
            console=console,
            expand=True,
        ) as progress:
            task_id = progress.add_task(
                "download",
                filename=safe_name[:25],
                total=total_size if total_size > 0 else None,
            )

            with open(out_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=65536):
                    if chunk:
                        f.write(chunk)
                        progress.update(task_id, advance=len(chunk))

        console.print(f"\n[bold green]✅ Unduhan Berhasil Selesai![/bold green]")
        console.print(f"Tersimpan di: [bold white]{os.path.abspath(out_path)}[/bold white]\n")
        try:
            from tools.notifier import notify
            notify("RILZ TOOLS — Cloud Ripper", f"Berhasil mengunduh: {safe_name[:40]}")
        except Exception:
            pass
        return True

    except Exception as e:
        console.print(f"\n[bold red]❌ Gagal mengunduh file:[/bold red] {e}\n")
        return False
