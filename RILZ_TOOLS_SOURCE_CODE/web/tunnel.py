#!/usr/bin/env python3
"""
RILZ WEB TUNNEL LAUNCHER
Exposes local RILZ Web to the Internet with Cloudflare Tunnel (HTTPS)
Generates public URL accessible from anywhere (Mobile / Outside WiFi)
"""

import os
import re
import socket
import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CLOUDFLARED = PROJECT_ROOT / "cloudflared.exe"
DESKTOP_DIR = Path("C:/Users/TK Pertiwi Binorong/Desktop")
LINK_FILE = DESKTOP_DIR / "RILZ_ONLINE_LINK.txt"


def is_port_in_use(port: int = 8000) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


def copy_to_clipboard(text: str):
    try:
        p = subprocess.Popen("clip", stdin=subprocess.PIPE, shell=True)
        p.communicate(text.encode("utf-8"))
    except Exception:
        pass


def main():
    os.system("cls" if os.name == "nt" else "clear")
    print("=" * 68)
    print("  ⚡ RILZ WEB ONLINE - CLOUDFLARE PUBLIC TUNNEL")
    print("=" * 68)

    # 1. Ensure server is running
    server_process = None
    if not is_port_in_use(8000):
        print("[*] Menjalankan backend server RILZ WEB pada port 8000...")
        server_cmd = [sys.executable, "-m", "uvicorn", "web.server:app", "--host", "0.0.0.0", "--port", "8000"]
        server_process = subprocess.Popen(server_cmd, cwd=str(PROJECT_ROOT))
        time.sleep(2)
    else:
        print("[+] Backend server sudah aktif di port 8000.")

    if not CLOUDFLARED.exists():
        print(f"[!] cloudflared.exe tidak ditemukan di {CLOUDFLARED}")
        return

    print("[*] Menghubungkan ke Cloudflare Global Edge Network...")
    print("[*] Mengenerate link HTTPS publik untuk lo...")

    tunnel_cmd = [str(CLOUDFLARED), "tunnel", "--url", "http://127.0.0.1:8000"]
    tunnel_proc = subprocess.Popen(
        tunnel_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="ignore",
    )

    public_url = None
    url_pattern = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")

    try:
        while True:
            line = tunnel_proc.stdout.readline()
            if not line and tunnel_proc.poll() is not None:
                break
            if not public_url:
                match = url_pattern.search(line)
                if match:
                    public_url = match.group(0)
                    copy_to_clipboard(public_url)

                    # Save to Desktop text file for easy access
                    try:
                        LINK_FILE.write_text(
                            f"🌐 RILZ WEB ONLINE URL:\n{public_url}\n\n*Link ini bisa dibuka dari HP atau laptop mana pun di seluruh dunia tanpa perlu satu WiFi!\n*Link aktif selama jendela launcher tetap dibuka.\n",
                            encoding="utf-8"
                        )
                    except Exception:
                        pass

                    os.system("cls" if os.name == "nt" else "clear")
                    print("\n" + "╔" + "═" * 66 + "╗")
                    print("║" + "  🎉 WEB LO SUDAH ONLINE DAN BISA DIAKSES DARI MANA AJA!      ".center(66) + "║")
                    print("╠" + "═" * 66 + "╣")
                    print(f"║  URL PUBLIK:  {public_url}".ljust(67) + "║")
                    print("║" + " " * 66 + "║")
                    print("║  ✔ Bisa dibuka lewat HP / Kuota Data / Komputer Luar           ║")
                    print("║  ✔ Koneksi resmi HTTPS terenkripsi aman SSL Cloudflare         ║")
                    print("║  ✔ URL sudah otomatis DISALIN ke clipboard!                    ║")
                    print("║  ✔ File 'RILZ_ONLINE_LINK.txt' juga dibuat di Desktop          ║")
                    print("╚" + "═" * 66 + "╝\n")
                    print("[i] Jendela ini jangan ditutup agar website tetap bisa diakses online.")
                    print("[i] Tekan Ctrl+C untuk mematikan akses online.\n")
                    print("-" * 68)
                    print("LOG TRAFFIC MASUK:")
                    print("-" * 68)

            elif public_url and "HTTP" in line:
                # Print clean incoming traffic log
                print(line.strip())

    except KeyboardInterrupt:
        print("\n[*] Mematikan tunnel online...")
    finally:
        tunnel_proc.terminate()
        if server_process:
            server_process.terminate()
        print("[+] Tunnel dimatikan. Website kembali ke mode lokal.")


if __name__ == "__main__":
    main()
