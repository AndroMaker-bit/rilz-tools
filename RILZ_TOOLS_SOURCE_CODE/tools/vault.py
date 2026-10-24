#!/usr/bin/env python3
"""
RILZ TOOLS - Local Vault / Second Brain Module
Utility CLI untuk menyimpan, mengelola, dan mencari file/snippet/catatan lokal.

Fitur:
  1. Quick Note / Memo              - Catat ide/teks singkat dari terminal
  2. Simpan Script / File           - Drop file ke vault dengan auto-kategori & tag
                                      (mendukung URL http/https untuk auto-download)
  3. Instant Search & Full-Text     - Cari keyword dari nama file ATAU isi kode
  4. Copy Snippet to Clipboard      - Salin isi file vault langsung ke clipboard
  5. Jelajah & Buka Vault           - Lihat semua isi vault, buka file/folder
  6. Hapus Item dari Vault          - Hapus item vault
  7. Backup / Sync ke Flashdisk     - Mirror vault ke path eksternal
  8. Lihat Activity Log             - Tampilkan 50 baris log terakhir
  9. Export Vault (MD / HTML)       - Ekspor semua vault ke satu file

Storage: SQLite (.vault.db) + folder terstruktur di VAULT_DIR
"""

import json
import os
import platform
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
import urllib.parse
from datetime import datetime
from pathlib import Path

from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.rule import Rule
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

console = Console()

# ─── Vault Config ─────────────────────────────────────────────────────────────
# Letakkan vault di samping folder rilz-tools, bukan di dalam
VAULT_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / "rilz-vault"
DB_PATH   = VAULT_DIR / ".vault.db"

# Kategori folder bawaan
CATEGORIES = {
    "scripts":    "🐍 Script & Program",
    "snippets":   "⚡ Code Snippet",
    "notes":      "📝 Catatan & Memo",
    "cheatsheets":"📖 Cheatsheet",
    "configs":    "⚙️  Config & Settings",
    "research":   "🔬 Riset & Referensi",
    "misc":       "📦 Misc / Lainnya",
}

# Ekstensi auto-kategori
EXT_MAP = {
    ".py": "scripts", ".sh": "scripts", ".bash": "scripts", ".ps1": "scripts",
    ".js": "snippets", ".ts": "snippets", ".rb": "snippets", ".go": "snippets",
    ".c": "snippets", ".cpp": "snippets", ".java": "snippets", ".rs": "snippets",
    ".md": "notes", ".txt": "notes",
    ".json": "configs", ".yaml": "configs", ".yml": "configs", ".toml": "configs",
    ".ini": "configs", ".env": "configs",
    ".pdf": "research", ".html": "research",
}

# Ekstensi yang bisa ditampilkan syntax highlight
CODE_EXTS = {
    ".py": "python", ".js": "javascript", ".ts": "typescript", ".sh": "bash",
    ".ps1": "powershell", ".json": "json", ".yaml": "yaml", ".yml": "yaml",
    ".md": "markdown", ".txt": "text", ".toml": "toml", ".go": "go", ".rs": "rust",
    ".c": "c", ".cpp": "cpp", ".java": "java", ".rb": "ruby", ".html": "html",
    ".css": "css", ".sql": "sql",
}


# ─── Inisialisasi Vault ───────────────────────────────────────────────────────
def _init_vault():
    """Buat struktur folder dan database vault kalau belum ada."""
    VAULT_DIR.mkdir(parents=True, exist_ok=True)
    for cat in CATEGORIES:
        (VAULT_DIR / cat).mkdir(exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS vault_items (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT NOT NULL,
            category    TEXT NOT NULL,
            filepath    TEXT NOT NULL,
            tags        TEXT DEFAULT '',
            description TEXT DEFAULT '',
            created_at  TEXT NOT NULL,
            size_bytes  INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


def _db():
    """Buka koneksi DB (pastikan vault sudah di-init)."""
    _init_vault()
    return sqlite3.connect(DB_PATH)


# ─── Helpers ──────────────────────────────────────────────────────────────────
def _cyber_header(title: str, subtitle: str = ""):
    console.print(Rule(f"[bold bright_cyan]{title}[/bold bright_cyan]", style="bright_cyan"))
    if subtitle:
        console.print(f"  [dim green]{subtitle}[/dim green]\n")


def _format_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def _detect_category(filepath: str) -> str:
    ext = Path(filepath).suffix.lower()
    return EXT_MAP.get(ext, "misc")


def _copy_to_clipboard(text: str) -> bool:
    """Cross-platform clipboard copy. Returns True jika berhasil."""
    try:
        if platform.system() == "Windows":
            subprocess.run(["clip"], input=text.encode("utf-8"), check=True)
            return True
        elif platform.system() == "Darwin":
            subprocess.run(["pbcopy"], input=text.encode("utf-8"), check=True)
            return True
        else:
            subprocess.run(["xclip", "-selection", "clipboard"],
                           input=text.encode("utf-8"), check=True)
            return True
    except Exception:
        return False


def _render_vault_item_row(row, idx: int) -> str:
    item_id, title, cat, fpath, tags, desc, created, size = row
    cat_icon = CATEGORIES.get(cat, "📦 Misc").split()[0]
    tag_str  = f"[dim cyan][{tags}][/dim cyan]" if tags else ""
    size_str = f"[dim]{_format_size(size)}[/dim]"
    date_str = created[:10] if created else "—"
    return (
        f"[bold bright_cyan]\\[{idx:02d}][/bold bright_cyan]  "
        f"{cat_icon} [bold white]{title}[/bold white] "
        f"[dim]({cat})[/dim]  {tag_str}  {size_str}  [dim]{date_str}[/dim]"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# FITUR 1 — Quick Note / Memo
# ═══════════════════════════════════════════════════════════════════════════════
def feature_quick_note():
    """Catat ide/teks singkat dari terminal, simpan ke vault."""
    _cyber_header("📝 QUICK NOTE — SECURE MEMO CAPTURE", "Catat apa saja tanpa ribet buka Notepad.")

    title = console.input("[bold bright_cyan]Judul memo ❯ [/bold bright_cyan]").strip()
    if not title:
        console.print("[yellow]⚠ Judul tidak boleh kosong.[/yellow]")
        return

    console.print("[dim]Ketik isi catatan di bawah. Ketik [bold]SELESAI[/bold] di baris baru untuk menyimpan:[/dim]")
    lines = []
    while True:
        try:
            line = input("  │ ")
            if line.strip().upper() == "SELESAI":
                break
            lines.append(line)
        except (KeyboardInterrupt, EOFError):
            break

    if not lines:
        console.print("[yellow]⚠ Isi catatan kosong, dibatalkan.[/yellow]")
        return

    tags_raw = console.input("[bold bright_cyan]Tag (pisah koma, opsional) ❯ [/bold bright_cyan]").strip()
    desc     = console.input("[bold bright_cyan]Deskripsi singkat (opsional) ❯ [/bold bright_cyan]").strip()

    content  = "\n".join(lines)
    safe_fn  = "".join(c if c.isalnum() or c in "._- " else "_" for c in title).replace(" ", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename  = f"{safe_fn}_{timestamp}.txt"
    dest_path = VAULT_DIR / "notes" / filename

    _init_vault()
    dest_path.write_text(content, encoding="utf-8")
    size = dest_path.stat().st_size

    conn = _db()
    conn.execute(
        "INSERT INTO vault_items (title, category, filepath, tags, description, created_at, size_bytes) VALUES (?,?,?,?,?,?,?)",
        (title, "notes", str(dest_path), tags_raw, desc, datetime.now().isoformat(), size)
    )
    conn.commit()
    conn.close()

    console.print(f"\n[bold bright_green]✅ MEMO TERSIMPAN![/bold bright_green]")
    console.print(f"   Path   : [dim]{dest_path}[/dim]")
    console.print(f"   Tags   : [cyan]{tags_raw or '—'}[/cyan]")
    console.print(f"   Ukuran : [dim]{_format_size(size)}[/dim]")


# ═══════════════════════════════════════════════════════════════════════════════
# FITUR 2 — Simpan Script / File
# ═══════════════════════════════════════════════════════════════════════════════
def feature_add_file():
    """Salin file dari path mana saja ke dalam vault dengan auto-kategori dan tag.
    Jika input diawali http:// atau https://, file akan didownload terlebih dahulu.
    """
    _cyber_header("💾 SIMPAN FILE KE VAULT", "Drop script/config/apapun ke dalam Second Brain.\nUntuk URL (http/https) file akan didownload otomatis.")

    src_raw = console.input("[bold bright_cyan]Path file / URL ❯ [/bold bright_cyan]").strip().strip('"\'')

    # ── URL Download branch ───────────────────────────────────────────────────
    if src_raw.startswith("http://") or src_raw.startswith("https://"):
        src = _download_url_to_temp(src_raw)
        if src is None:
            return  # Error already printed inside helper
    else:
        src = Path(src_raw)
        if not src.exists() or not src.is_file():
            console.print(f"[bold red]✗ File tidak ditemukan:[/bold red] [dim]{src_raw}[/dim]")
            return

    auto_cat = _detect_category(str(src))
    console.print(f"[dim]Kategori otomatis terdeteksi: [bold cyan]{auto_cat}[/bold cyan][/dim]")
    cat_display = "\n".join(f"  [bold cyan]{k}[/bold cyan] — {v}" for k, v in CATEGORIES.items())
    console.print(f"\nPilihan kategori:\n{cat_display}")
    cat_input = console.input(f"[bold bright_cyan]Kategori (Enter = {auto_cat}) ❯ [/bold bright_cyan]").strip().lower()
    category  = cat_input if cat_input in CATEGORIES else auto_cat

    title    = console.input(f"[bold bright_cyan]Nama/judul file (Enter = '{src.name}') ❯ [/bold bright_cyan]").strip() or src.name
    tags_raw = console.input("[bold bright_cyan]Tag (pisah koma, opsional) ❯ [/bold bright_cyan]").strip()
    desc     = console.input("[bold bright_cyan]Deskripsi singkat (opsional) ❯ [/bold bright_cyan]").strip()

    _init_vault()
    dest_dir  = VAULT_DIR / category
    dest_path = dest_dir / src.name

    # Handle nama duplikat
    counter = 1
    while dest_path.exists():
        stem    = src.stem
        suffix  = src.suffix
        dest_path = dest_dir / f"{stem}_{counter}{suffix}"
        counter += 1

    shutil.copy2(str(src), str(dest_path))
    size = dest_path.stat().st_size

    conn = _db()
    conn.execute(
        "INSERT INTO vault_items (title, category, filepath, tags, description, created_at, size_bytes) VALUES (?,?,?,?,?,?,?)",
        (title, category, str(dest_path), tags_raw, desc, datetime.now().isoformat(), size)
    )
    conn.commit()
    conn.close()

    console.print(f"\n[bold bright_green]✅ FILE BERHASIL DISIMPAN KE VAULT![/bold bright_green]")
    console.print(f"   Sumber  : [dim]{src_raw}[/dim]")
    console.print(f"   Vault   : [cyan]{dest_path}[/cyan]")
    console.print(f"   Kategori: [bold cyan]{category}[/bold cyan]  Tags: [cyan]{tags_raw or '—'}[/cyan]")
    console.print(f"   Ukuran  : [dim]{_format_size(size)}[/dim]")


def _download_url_to_temp(url: str) -> "Path | None":
    """Download a URL to a temp file. Returns the Path on success, None on failure."""
    try:
        import requests
        from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn
    except ImportError:
        console.print("[bold red]✗ `requests` tidak terinstall. Jalankan: pip install requests[/bold red]")
        return None

    console.print(f"[bold cyan]⬇  Mendeteksi URL — mengunduh file...[/bold cyan] [dim]{url}[/dim]")

    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            )
        }
        resp = requests.get(url, headers=headers, stream=True, timeout=30)
        resp.raise_for_status()

        # ── Detect filename ───────────────────────────────────────────────────
        import re, urllib.parse as _up
        filename = None
        cd = resp.headers.get("Content-Disposition", "")
        if cd:
            m = re.search(r"filename\*=UTF-8''([^;'\"]+)", cd, re.IGNORECASE)
            if m:
                filename = _up.unquote(m.group(1))
            else:
                m = re.search(r'filename=["\'"]?([^;"\']+)["\'"]?', cd, re.IGNORECASE)
                if m:
                    filename = m.group(1).strip()
        if not filename:
            parsed = _up.urlparse(url)
            basename = os.path.basename(parsed.path)
            filename = _up.unquote(basename) if basename and "." in basename else "downloaded_file.bin"

        # Sanitise
        safe_name = re.sub(r'[\\/*?:"<>|]', "_", filename)

        import tempfile as _tf
        tmp_dir  = Path(_tf.mkdtemp(prefix="rilz_vault_"))
        tmp_path = tmp_dir / safe_name
        total    = int(resp.headers.get("content-length", 0))

        console.print(f"[dim]Nama file terdeteksi: [bold white]{safe_name}[/bold white][/dim]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[bold cyan]{task.fields[fn]}", justify="left"),
            BarColumn(bar_width=None),
            "[progress.percentage]{task.percentage:>3.1f}%",
            "•", DownloadColumn(), "•", TransferSpeedColumn(), "•", TimeRemainingColumn(),
            console=console, expand=True,
        ) as prog:
            task = prog.add_task("dl", fn=safe_name[:25], total=total or None)
            with open(tmp_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=65536):
                    if chunk:
                        f.write(chunk)
                        prog.update(task, advance=len(chunk))

        console.print(f"[bold bright_green]✅ Download selesai:[/bold bright_green] [cyan]{tmp_path}[/cyan]")
        return tmp_path

    except Exception as e:
        console.print(f"[bold red]✗ Gagal mendownload URL:[/bold red] {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# FITUR 3 — Instant Search & Full-Text Preview
# ═══════════════════════════════════════════════════════════════════════════════
def feature_search():
    """Cari keyword dari nama, tag, atau isi konten file di dalam vault."""
    _cyber_header("🔍 INSTANT VAULT SEARCH", "Cari dari nama file, tag, maupun isi kode/catatan.")

    keyword = console.input("[bold bright_cyan]Keyword pencarian ❯ [/bold bright_cyan]").strip()
    if not keyword:
        return

    _init_vault()
    conn  = _db()
    klike = f"%{keyword}%"
    rows  = conn.execute(
        "SELECT id, title, category, filepath, tags, description, created_at, size_bytes "
        "FROM vault_items "
        "WHERE title LIKE ? OR tags LIKE ? OR description LIKE ? "
        "ORDER BY created_at DESC",
        (klike, klike, klike)
    ).fetchall()
    conn.close()

    # Full-text search di isi file
    fulltext_hits = []
    if (VAULT_DIR).exists():
        for fpath in VAULT_DIR.rglob("*"):
            if fpath.is_file() and fpath.suffix.lower() in CODE_EXTS:
                try:
                    content = fpath.read_text(encoding="utf-8", errors="ignore")
                    if keyword.lower() in content.lower():
                        # Cek apakah sudah masuk dari DB
                        already = any(Path(r[3]) == fpath for r in rows)
                        if not already:
                            fulltext_hits.append(str(fpath))
                except Exception:
                    pass

    total = len(rows) + len(fulltext_hits)
    if total == 0:
        console.print(f"\n[yellow]Tidak ada hasil untuk keyword '[bold]{keyword}[/bold]'[/yellow]")
        return

    console.print(f"\n[bold bright_green]✅ Ditemukan {total} hasil untuk '[bold cyan]{keyword}[/bold cyan]':[/bold bright_green]\n")

    tbl = Table(box=None, padding=(0, 2), show_header=False, expand=True)
    tbl.add_column("Info", style="white")

    for idx, row in enumerate(rows, 1):
        tbl.add_row(_render_vault_item_row(row, idx))

    for i, fp in enumerate(fulltext_hits, len(rows) + 1):
        tbl.add_row(
            f"[bold bright_cyan]\\[{i:02d}][/bold bright_cyan]  "
            f"📄 [bold white]{Path(fp).name}[/bold white]  "
            f"[dim yellow](full-text match)[/dim yellow]  [dim]{fp}[/dim]"
        )

    console.print(tbl)

    # Tawarin preview
    pick = console.input(
        "\n[bold bright_cyan]Preview isi file? Masukkan nomor (Enter = skip) ❯ [/bold bright_cyan]"
    ).strip()
    if pick.isdigit():
        pidx = int(pick)
        all_paths = [r[3] for r in rows] + fulltext_hits
        if 1 <= pidx <= len(all_paths):
            _preview_file(all_paths[pidx - 1], keyword)


def _preview_file(fpath: str, highlight_kw: str = ""):
    """Tampilkan preview isi file dengan syntax highlight."""
    fp = Path(fpath)
    if not fp.exists():
        console.print(f"[red]File tidak ditemukan:[/red] {fpath}")
        return

    ext     = fp.suffix.lower()
    lang    = CODE_EXTS.get(ext, "text")
    size    = fp.stat().st_size

    if size > 100_000:  # Jangan load file > 100KB penuh
        console.print(f"[yellow]File terlalu besar ({_format_size(size)}), tampil 80 baris pertama.[/yellow]")

    try:
        content = fp.read_text(encoding="utf-8", errors="ignore")
        lines   = content.splitlines()
        preview = "\n".join(lines[:80]) if len(lines) > 80 else content
    except Exception as e:
        console.print(f"[red]Gagal membaca file: {e}[/red]")
        return

    console.print(f"\n[bold dim]📄 {fp.name}[/bold dim]  [dim]{_format_size(size)}[/dim]")
    try:
        syntax = Syntax(preview, lang, theme="monokai", line_numbers=True, word_wrap=False)
        console.print(Panel(syntax, border_style="dim cyan", padding=(0, 1)))
    except Exception:
        console.print(Panel(preview, border_style="dim cyan"))


# ═══════════════════════════════════════════════════════════════════════════════
# FITUR 4 — Copy Snippet to Clipboard
# ═══════════════════════════════════════════════════════════════════════════════
def feature_copy_to_clipboard():
    """Tampilkan daftar vault, pilih satu item, salin isinya ke clipboard."""
    _cyber_header("📋 COPY SNIPPET KE CLIPBOARD", "Pilih file dari vault, langsung copy ke clipboard.")

    _init_vault()
    conn = _db()
    rows = conn.execute(
        "SELECT id, title, category, filepath, tags, description, created_at, size_bytes "
        "FROM vault_items ORDER BY created_at DESC LIMIT 30"
    ).fetchall()
    conn.close()

    if not rows:
        console.print("[yellow]Vault masih kosong. Tambahkan file/note dulu![/yellow]")
        return

    tbl = Table(box=None, padding=(0, 2), show_header=False, expand=True)
    tbl.add_column("Item", style="white")
    for idx, row in enumerate(rows, 1):
        tbl.add_row(_render_vault_item_row(row, idx))
    console.print(tbl)

    pick = console.input("\n[bold bright_cyan]Pilih nomor item ❯ [/bold bright_cyan]").strip()
    if not pick.isdigit() or not (1 <= int(pick) <= len(rows)):
        console.print("[yellow]Nomor tidak valid.[/yellow]")
        return

    row   = rows[int(pick) - 1]
    fpath = Path(row[3])

    if not fpath.exists():
        console.print(f"[red]File tidak ditemukan di vault: {fpath}[/red]")
        return

    try:
        content = fpath.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        console.print(f"[red]Gagal membaca file: {e}[/red]")
        return

    _preview_file(str(fpath))

    if _copy_to_clipboard(content):
        console.print(f"\n[bold bright_green]✅ Konten '[cyan]{row[1]}[/cyan]' berhasil disalin ke clipboard![/bold bright_green]")
        console.print("[dim]Langsung Ctrl+V di mana saja untuk paste. 🚀[/dim]")
    else:
        console.print("[yellow]⚠ Clipboard tidak tersedia di sistem ini. Konten ditampilkan di atas.[/yellow]")


# ═══════════════════════════════════════════════════════════════════════════════
# FITUR 5 — Jelajah & Buka Vault
# ═══════════════════════════════════════════════════════════════════════════════
def feature_browse_vault():
    """Tampilkan semua isi vault dikelompokkan per kategori, pilih untuk dipreview/buka."""
    _cyber_header("🗂️  JELAJAH VAULT — SECOND BRAIN EXPLORER", f"Vault: {VAULT_DIR}")

    _init_vault()
    conn = _db()
    rows = conn.execute(
        "SELECT id, title, category, filepath, tags, description, created_at, size_bytes "
        "FROM vault_items ORDER BY category, created_at DESC"
    ).fetchall()
    conn.close()

    if not rows:
        console.print("[yellow]Vault masih kosong. Tambahkan file/note dulu![/yellow]")
        _show_vault_stats()
        return

    # Kelompokkan per kategori
    by_cat: dict[str, list] = {}
    for row in rows:
        by_cat.setdefault(row[2], []).append(row)

    all_rows_ordered = []
    for cat, items in by_cat.items():
        icon = CATEGORIES.get(cat, "📦 Misc").split()[0]
        label = CATEGORIES.get(cat, cat)
        console.print(f"\n[bold bright_green]{icon} {label.upper()}[/bold bright_green] [dim]({len(items)} items)[/dim]")
        for item in items:
            idx = len(all_rows_ordered) + 1
            all_rows_ordered.append(item)
            console.print(f"  {_render_vault_item_row(item, idx)}")

    _show_vault_stats()

    pick = console.input(
        "\n[bold bright_cyan]Nomor untuk preview / buka (Enter = skip) ❯ [/bold bright_cyan]"
    ).strip()
    if pick.isdigit() and 1 <= int(pick) <= len(all_rows_ordered):
        row   = all_rows_ordered[int(pick) - 1]
        fpath = row[3]

        action = console.input(
            "[bold bright_cyan]Aksi: [P]review / [O]pen di editor / [C]opy ke clipboard ❯ [/bold bright_cyan]"
        ).strip().upper()

        if action == "P" or action == "":
            _preview_file(fpath)
        elif action == "O":
            _open_in_editor(fpath)
        elif action == "C":
            try:
                content = Path(fpath).read_text(encoding="utf-8", errors="ignore")
                if _copy_to_clipboard(content):
                    console.print("[bold bright_green]✅ Disalin ke clipboard![/bold bright_green]")
                else:
                    console.print("[yellow]⚠ Clipboard tidak tersedia.[/yellow]")
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")


def _open_in_editor(fpath: str):
    """Buka file di editor default sistem."""
    try:
        if platform.system() == "Windows":
            os.startfile(fpath)
        elif platform.system() == "Darwin":
            subprocess.run(["open", fpath])
        else:
            subprocess.run(["xdg-open", fpath])
        console.print(f"[dim green]📂 Membuka {Path(fpath).name} di editor default...[/dim green]")
    except Exception as e:
        console.print(f"[red]Gagal membuka file: {e}[/red]")


def _show_vault_stats():
    """Tampilkan statistik vault."""
    conn = _db()
    total_items = conn.execute("SELECT COUNT(*) FROM vault_items").fetchone()[0]
    total_size  = conn.execute("SELECT SUM(size_bytes) FROM vault_items").fetchone()[0] or 0
    conn.close()
    console.print(
        f"\n[dim]Vault: [bold]{total_items}[/bold] item • "
        f"Total: [bold]{_format_size(total_size)}[/bold] • "
        f"Lokasi: [cyan]{VAULT_DIR}[/cyan][/dim]"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# FITUR 6 — Backup / Sync ke Flashdisk atau Folder Lain
# ═══════════════════════════════════════════════════════════════════════════════
def feature_backup_sync():
    """Mirror seluruh vault ke flashdisk atau path eksternal manapun."""
    _cyber_header("🔄 BACKUP & SYNC VAULT", "Mirror vault ke flashdisk / folder eksternal.")

    console.print(f"[dim]Vault sumber: [bold cyan]{VAULT_DIR}[/bold cyan][/dim]\n")
    dest_raw = console.input("[bold bright_cyan]Path tujuan backup (contoh: E:\\RILZ_BACKUP) ❯ [/bold bright_cyan]").strip().strip('"\'')

    if not dest_raw:
        console.print("[yellow]⚠ Path tujuan tidak boleh kosong.[/yellow]")
        return

    dest = Path(dest_raw)
    try:
        dest.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        console.print(f"[red]✗ Tidak punya akses tulis ke: {dest}[/red]")
        return
    except Exception as e:
        console.print(f"[red]✗ Gagal membuat folder tujuan: {e}[/red]")
        return

    backup_folder = dest / f"rilz-vault-backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    console.print(f"\n[bold]Memulai sync ke[/bold] [cyan]{backup_folder}[/cyan]...")
    start = time.time()

    try:
        copied = 0
        skipped = 0
        total_bytes = 0

        for src_file in VAULT_DIR.rglob("*"):
            if src_file.is_file():
                rel = src_file.relative_to(VAULT_DIR)
                dst_file = backup_folder / rel
                dst_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(str(src_file), str(dst_file))
                total_bytes += src_file.stat().st_size
                copied += 1
                console.print(f"  [dim green]✓[/dim green] [dim]{rel}[/dim]")

        elapsed = time.time() - start
        console.print(f"\n[bold bright_green]✅ BACKUP SELESAI![/bold bright_green]")
        console.print(f"   File tersalin : [bold]{copied}[/bold]")
        console.print(f"   Total ukuran  : [bold]{_format_size(total_bytes)}[/bold]")
        console.print(f"   Durasi        : [dim]{elapsed:.2f}s[/dim]")
        console.print(f"   Lokasi backup : [cyan]{backup_folder}[/cyan]")

    except Exception as e:
        console.print(f"\n[bold red]✗ Backup gagal: {e}[/bold red]")


# ═══════════════════════════════════════════════════════════════════════════════
# HAPUS ITEM DARI VAULT
# ═══════════════════════════════════════════════════════════════════════════════
def feature_delete_item():
    """Hapus item dari vault (DB + file fisik)."""
    _cyber_header("🗑️  HAPUS ITEM DARI VAULT", "Pilih item yang mau dihapus permanen dari vault.")

    _init_vault()
    conn = _db()
    rows = conn.execute(
        "SELECT id, title, category, filepath, tags, description, created_at, size_bytes "
        "FROM vault_items ORDER BY created_at DESC LIMIT 30"
    ).fetchall()
    conn.close()

    if not rows:
        console.print("[yellow]Vault masih kosong.[/yellow]")
        return

    tbl = Table(box=None, padding=(0, 2), show_header=False, expand=True)
    tbl.add_column("Item", style="white")
    for idx, row in enumerate(rows, 1):
        tbl.add_row(_render_vault_item_row(row, idx))
    console.print(tbl)

    pick = console.input("\n[bold bright_red]Nomor item yang mau dihapus (Enter = batal) ❯ [/bold bright_red]").strip()
    if not pick.isdigit() or not (1 <= int(pick) <= len(rows)):
        console.print("[dim]Dibatalkan.[/dim]")
        return

    row   = rows[int(pick) - 1]
    item_id, title, _, fpath = row[0], row[1], row[2], row[3]

    confirm = console.input(
        f"[bold bright_red]Yakin hapus '[/bold bright_red][bold white]{title}[/bold white][bold bright_red]'? (y/N) ❯ [/bold bright_red]"
    ).strip().lower()

    if confirm != "y":
        console.print("[dim]Dibatalkan.[/dim]")
        return

    # Hapus file fisik
    try:
        fp = Path(fpath)
        if fp.exists():
            fp.unlink()
    except Exception as e:
        console.print(f"[yellow]⚠ File fisik tidak bisa dihapus: {e}[/yellow]")

    # Hapus dari DB
    conn = _db()
    conn.execute("DELETE FROM vault_items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

    console.print(f"[bold bright_green]✅ '[cyan]{title}[/cyan]' berhasil dihapus dari vault.[/bold bright_green]")


# ═══════════════════════════════════════════════════════════════════════════════
# FITUR 8 — View Activity Log
# ═══════════════════════════════════════════════════════════════════════════════
def feature_view_activity_log():
    """Tampilkan 50 baris terakhir dari activity log."""
    _cyber_header("📜 ACTIVITY LOG — SESSION HISTORY", "50 aktivitas terakhir RILZ TOOLS.")
    try:
        from tools.logger import get_recent_logs
    except ImportError:
        console.print("[red]Logger module tidak tersedia.[/red]")
        return

    lines = get_recent_logs(50)
    if not lines:
        console.print("[yellow]Log masih kosong — belum ada aktivitas tercatat.[/yellow]")
        return

    log_text = "\n".join(lines)
    try:
        syn = Syntax(log_text, "text", theme="monokai", line_numbers=True, word_wrap=False)
        console.print(Panel(syn, title="[bold bright_cyan]📜 RILZ ACTIVITY LOG[/bold bright_cyan]",
                            border_style="bright_cyan", padding=(0, 1)))
    except Exception:
        console.print(Panel(log_text, border_style="bright_cyan"))


# ═══════════════════════════════════════════════════════════════════════════════
# FITUR 9 — Export Vault (Markdown & HTML)
# ═══════════════════════════════════════════════════════════════════════════════
def feature_export_vault():
    """Ekspor semua isi vault ke satu file Markdown ATAU HTML standalone."""
    _cyber_header("📤 EXPORT VAULT", "Ekspor semua isi vault ke Markdown atau HTML.")

    fmt = console.input("[bold bright_cyan]Format export [md/html] (default: md) ❯ [/bold bright_cyan]").strip().lower()
    if fmt not in ("md", "html", ""):
        console.print("[yellow]Format tidak dikenal. Gunakan 'md' atau 'html'.[/yellow]")
        return
    fmt = fmt or "md"

    _init_vault()
    conn = _db()
    rows = conn.execute(
        "SELECT id, title, category, filepath, tags, description, created_at, size_bytes "
        "FROM vault_items ORDER BY category, created_at DESC"
    ).fetchall()
    conn.close()

    if not rows:
        console.print("[yellow]Vault masih kosong.[/yellow]")
        return

    export_dir = VAULT_DIR / "exports"
    export_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if fmt == "md":
        _export_markdown(rows, export_dir, timestamp)
    else:
        _export_html(rows, export_dir, timestamp)


def _export_markdown(rows, export_dir: Path, timestamp: str):
    """Generate a single Markdown file with all vault items."""
    out_path = export_dir / f"vault_export_{timestamp}.md"
    lines = [
        f"# RILZ Vault Export\n",
        f"> Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        f"> Total items: {len(rows)}\n\n",
        "---\n\n",
    ]

    for row in rows:
        item_id, title, cat, fpath, tags, desc, created, size = row
        fp = Path(fpath)
        ext = fp.suffix.lower().lstrip(".")
        lang = CODE_EXTS.get(fp.suffix.lower(), ext or "text")

        lines.append(f"## {title}\n\n")
        lines.append(f"| Field    | Value |\n")
        lines.append(f"|----------|-------|\n")
        lines.append(f"| Category | `{cat}` |\n")
        lines.append(f"| Tags     | `{tags or '—'}` |\n")
        lines.append(f"| Date     | {created[:10]} |\n")
        lines.append(f"| Size     | {_format_size(size)} |\n")
        if desc:
            lines.append(f"| Desc     | {desc} |\n")
        lines.append("\n")

        if fp.exists():
            try:
                content = fp.read_text(encoding="utf-8", errors="ignore")
                lines.append(f"```{lang}\n{content}\n```\n\n")
            except Exception:
                lines.append(f"_[Could not read file: {fpath}]_\n\n")
        else:
            lines.append(f"_[File not found: {fpath}]_\n\n")
        lines.append("---\n\n")

    out_path.write_text("".join(lines), encoding="utf-8")
    console.print(f"\n[bold bright_green]✅ EXPORT SELESAI![/bold bright_green]")
    console.print(f"   Format  : [bold cyan]Markdown[/bold cyan]")
    console.print(f"   File    : [cyan]{out_path}[/cyan]")
    console.print(f"   Items   : [bold]{len(rows)}[/bold]")
    _open_in_editor(str(out_path))


def _export_html(rows, export_dir: Path, timestamp: str):
    """Generate a dark-themed standalone HTML file with highlight.js."""
    out_path = export_dir / f"vault_export_{timestamp}.html"

    sections = []
    for row in rows:
        item_id, title, cat, fpath, tags, desc, created, size = row
        fp = Path(fpath)
        ext = fp.suffix.lower().lstrip(".") or "text"

        file_content = ""
        if fp.exists():
            try:
                file_content = fp.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                file_content = f"[Could not read file: {fpath}]"
        else:
            file_content = f"[File not found: {fpath}]"

        # HTML-escape
        import html as _html
        esc_content = _html.escape(file_content)
        esc_title   = _html.escape(title)
        esc_tags    = _html.escape(tags or "—")
        esc_desc    = _html.escape(desc or "")

        sections.append(f"""
  <section class="item">
    <h2>📄 {esc_title}</h2>
    <div class="meta">
      <span class="badge">{cat}</span>
      <span class="badge tag">{esc_tags}</span>
      <span class="date">{created[:10]}</span>
      <span class="size">{_format_size(size)}</span>
    </div>
    {f'<p class="desc">{esc_desc}</p>' if esc_desc else ""}
    <pre><code class="language-{ext}">{esc_content}</code></pre>
  </section>
""")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>RILZ Vault Export — {timestamp}</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
  <script>hljs.highlightAll();</script>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ background: #0d1117; color: #c9d1d9; font-family: 'Segoe UI', Consolas, monospace; padding: 2rem; }}
    h1 {{ color: #39ff14; border-bottom: 2px solid #39ff14; padding-bottom: .5rem; margin-bottom: 1.5rem; }}
    .subtitle {{ color: #8b949e; margin-bottom: 2rem; font-size: .9rem; }}
    .item {{ background: #161b22; border: 1px solid #30363d; border-radius: 8px; margin-bottom: 2rem; padding: 1.5rem; }}
    h2 {{ color: #58a6ff; margin-bottom: .75rem; }}
    .meta {{ display: flex; gap: .5rem; flex-wrap: wrap; margin-bottom: .75rem; align-items: center; }}
    .badge {{ background: #21262d; border: 1px solid #30363d; border-radius: 4px; padding: 2px 8px; font-size: .8rem; color: #79c0ff; }}
    .badge.tag {{ color: #a5d6ff; }}
    .date, .size {{ color: #8b949e; font-size: .8rem; }}
    .desc {{ color: #8b949e; font-style: italic; margin-bottom: .5rem; }}
    pre {{ border-radius: 6px; overflow-x: auto; max-height: 500px; }}
    code {{ font-size: .85rem; }}
  </style>
</head>
<body>
  <h1>⚡ RILZ Vault Export</h1>
  <p class="subtitle">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {len(rows)} items</p>
{"".join(sections)}
</body>
</html>"""

    out_path.write_text(html, encoding="utf-8")
    console.print(f"\n[bold bright_green]✅ EXPORT SELESAI![/bold bright_green]")
    console.print(f"   Format  : [bold cyan]HTML[/bold cyan]")
    console.print(f"   File    : [cyan]{out_path}[/cyan]")
    console.print(f"   Items   : [bold]{len(rows)}[/bold]")
    _open_in_editor(str(out_path))


# ═══════════════════════════════════════════════════════════════════════════════
# CLI helper functions (for non-interactive quick-launch from main.py)
# ═══════════════════════════════════════════════════════════════════════════════
def feature_search_keyword(keyword: str):
    """Non-interactive vault search — prints results and exits."""
    _init_vault()
    conn  = _db()
    klike = f"%{keyword}%"
    rows  = conn.execute(
        "SELECT id, title, category, filepath, tags, description, created_at, size_bytes "
        "FROM vault_items "
        "WHERE title LIKE ? OR tags LIKE ? OR description LIKE ? "
        "ORDER BY created_at DESC",
        (klike, klike, klike)
    ).fetchall()
    conn.close()

    # Full-text scan in files
    fulltext_hits = []
    if VAULT_DIR.exists():
        for fpath in VAULT_DIR.rglob("*"):
            if fpath.is_file() and fpath.suffix.lower() in CODE_EXTS:
                try:
                    content = fpath.read_text(encoding="utf-8", errors="ignore")
                    if keyword.lower() in content.lower():
                        already = any(Path(r[3]) == fpath for r in rows)
                        if not already:
                            fulltext_hits.append(str(fpath))
                except Exception:
                    pass

    total = len(rows) + len(fulltext_hits)
    if total == 0:
        console.print(f"[yellow]Tidak ada hasil untuk keyword '[bold]{keyword}[/bold]'[/yellow]")
        return

    console.print(f"\n[bold bright_green]✅ Ditemukan {total} hasil untuk '[cyan]{keyword}[/cyan]':[/bold bright_green]\n")
    for idx, row in enumerate(rows, 1):
        console.print(f"  {_render_vault_item_row(row, idx)}")

    for i, fp in enumerate(fulltext_hits, len(rows) + 1):
        console.print(
            f"  [bold bright_cyan]\\[{i:02d}][/bold bright_cyan]  "
            f"📄 [bold white]{Path(fp).name}[/bold white]  "
            f"[dim yellow](full-text match)[/dim yellow]  [dim]{fp}[/dim]"
        )


def feature_quick_note_cli(text: str, tags: str = ""):
    """Non-interactive quick note — saves text directly and exits."""
    if not text.strip():
        console.print("[yellow]⚠ Teks catatan tidak boleh kosong.[/yellow]")
        return

    title = f"QuickNote_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename  = f"quicknote_{timestamp}.txt"
    dest_path = VAULT_DIR / "notes" / filename
    desc      = text[:120].replace("\n", " ")

    _init_vault()
    dest_path.write_text(text, encoding="utf-8")
    size = dest_path.stat().st_size

    conn = _db()
    conn.execute(
        "INSERT INTO vault_items (title, category, filepath, tags, description, created_at, size_bytes) VALUES (?,?,?,?,?,?,?)",
        (title, "notes", str(dest_path), tags, desc, datetime.now().isoformat(), size)
    )
    conn.commit()
    conn.close()

    console.print(f"[bold bright_green]✅ Quick note tersimpan:[/bold bright_green] [cyan]{dest_path}[/cyan]")
    if tags:
        console.print(f"   Tags: [cyan]{tags}[/cyan]")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN INTERACTIVE VAULT MENU
# ═══════════════════════════════════════════════════════════════════════════════
def run_vault():
    """Entry point untuk menu Second Brain / Local Vault di RILZ TOOLS."""
    _init_vault()

    while True:
        console.print()
        console.print(Panel(
            "[bold bright_green]01[/bold bright_green]  📝 Quick Note / Capture Memo Kilat\n"
            "[bold bright_green]02[/bold bright_green]  💾 Simpan Script / File ke Vault (Path / URL)\n"
            "[bold bright_green]03[/bold bright_green]  🔍 Instant Search & Full-Text Preview\n"
            "[bold bright_green]04[/bold bright_green]  📋 Copy Snippet ke Clipboard\n"
            "[bold bright_green]05[/bold bright_green]  🗂️  Jelajah & Buka File Vault\n"
            "[bold bright_green]06[/bold bright_green]  🗑️  Hapus Item dari Vault\n"
            "[bold bright_green]07[/bold bright_green]  🔄 Backup / Sync ke Flashdisk\n"
            "[bold bright_green]08[/bold bright_green]  📜 Session Activity Log\n"
            "[bold bright_green]09[/bold bright_green]  📤 Export Vault (Markdown & HTML)\n"
            "[bold bright_red]00[/bold bright_red]  ← Kembali ke Main Grid",
            title="[bold bright_yellow]📦 RILZ LOCAL VAULT — SECOND BRAIN[/bold bright_yellow]",
            title_align="center",
            border_style="bright_yellow",
            padding=(1, 3),
        ))

        try:
            pick = console.input("[bold bright_yellow]vault ❯ [/bold bright_yellow]").strip().lstrip("0") or "0"
        except (KeyboardInterrupt, EOFError):
            break

        console.print()

        if pick == "0":
            break
        elif pick == "1":
            feature_quick_note()
        elif pick == "2":
            feature_add_file()
        elif pick == "3":
            feature_search()
        elif pick == "4":
            feature_copy_to_clipboard()
        elif pick == "5":
            feature_browse_vault()
        elif pick == "6":
            feature_delete_item()
        elif pick == "7":
            feature_backup_sync()
        elif pick == "8":
            feature_view_activity_log()
        elif pick == "9":
            feature_export_vault()
        else:
            console.print("[yellow]⚠ Pilihan tidak valid.[/yellow]")

        console.input("\n[dim green]Tekan Enter untuk kembali ke Vault Menu...[/dim green]")
