#!/usr/bin/env python3
"""
RILZ WEB - 24/7 BACKGROUND SERVICE DAEMON & WATCHDOG
Runs completely silently with NO console window (via pythonw.exe or VBScript).
Monitors both FastAPI server and Cloudflare Public Tunnel.
Auto-restarts any crashed components and updates Desktop link file.
"""

import json
import os
import re
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Tuple

PROJECT_ROOT = Path("C:/Users/TK Pertiwi Binorong/.gemini/antigravity/scratch/rilz-tools")
CLOUDFLARED_BIN = PROJECT_ROOT / "cloudflared.exe"
DESKTOP_DIR = Path("C:/Users/TK Pertiwi Binorong/Desktop")
LINK_FILE = DESKTOP_DIR / "RILZ_ONLINE_LINK.txt"
STATE_FILE = PROJECT_ROOT / "rilz_service.json"
LOG_FILE = PROJECT_ROOT / "service_daemon.log"

CREATE_NO_WINDOW = 0x08000000 if os.name == "nt" else 0
LOCK_SOCKET = None


def log(msg: str):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}\n"
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        pass


def acquire_daemon_lock() -> bool:
    global LOCK_SOCKET
    LOCK_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        LOCK_SOCKET.bind(("127.0.0.1", 58742))
        return True
    except socket.error:
        return False


def get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def is_port_open(port: int = 8000) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


def kill_orphan_cloudflared():
    try:
        subprocess.run(
            ["taskkill", "/F", "/IM", "cloudflared.exe"],
            creationflags=CREATE_NO_WINDOW,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception:
        pass


def save_state(daemon_pid: int, uvicorn_pid: int = None, cloudflared_pid: int = None, public_url: str = None):
    started_at = None
    started_ts = None
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                prev = json.load(f)
                started_at = prev.get("started_at")
                started_ts = prev.get("started_ts")
        except Exception:
            pass

    now_ts = int(time.time())
    if not started_at:
        started_at = time.strftime("%Y-%m-%d %H:%M:%S")
        started_ts = now_ts

    data = {
        "daemon_pid": daemon_pid,
        "uvicorn_pid": uvicorn_pid,
        "cloudflared_pid": cloudflared_pid,
        "public_url": public_url,
        "local_ip": get_local_ip(),
        "local_url": f"http://{get_local_ip()}:8000",
        "localhost_url": "http://127.0.0.1:8000",
        "started_at": started_at,
        "started_ts": started_ts,
        "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "status": "RUNNING_24_7"
    }
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


def update_desktop_link(public_url: str = None):
    local_ip = get_local_ip()
    content = [
        "===========================================================",
        "  ⚡ RILZ WEB - 24/7 BACKGROUND SERVICE (SABER ALTER)",
        "===========================================================",
        f"  Status        : ONLINE 24/7 (Berjalan di latar belakang)",
        f"  Terakhir Cek  : {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "===========================================================",
        "",
        "🔥 LINK CUSTOM RESMI (Akses Publik Bebas dari HP / Mana Saja):",
        "👉 https://tools.rilzparker08.workers.dev",
        "",
        "🌐 LINK BACKEND CLOUDFLARE EDGE:",
        f"👉 {public_url if public_url else 'Sedang menghubungkan ke Cloudflare Edge...'}",
        "",
        "📶 LINK LOKAL WIFI (Akses dari perangkat dalam 1 jaringan WiFi):",
        f"👉 http://{local_ip}:8000",
        "",
        "💻 LINK KOMPUTER LOKAL (Akses dari laptop ini):",
        f"👉 http://127.0.0.1:8000",
        "",
        "===========================================================",
        "Catatan:",
        "- Service ini berjalan otomatis di latar belakang tanpa terminal.",
        "- PIN Keamanan: 1337",
        "- Untuk mematikan, klik 2x file 'STOP RILZ 24-7' di Desktop.",
        "- Untuk cek status, klik 2x file 'STATUS RILZ 24-7' di Desktop.",
        "==========================================================="
    ]
    try:
        LINK_FILE.write_text("\n".join(content), encoding="utf-8")
    except Exception as e:
        log(f"Failed to update desktop link: {e}")


def start_uvicorn() -> subprocess.Popen:
    log("Starting Uvicorn backend server on port 8000...")
    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "web.server:app",
        "--host",
        "0.0.0.0",
        "--port",
        "8000"
    ]
    proc = subprocess.Popen(
        cmd,
        cwd=str(PROJECT_ROOT),
        creationflags=CREATE_NO_WINDOW,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return proc


def start_cloudflared() -> Tuple[subprocess.Popen, str]:
    if not CLOUDFLARED_BIN.exists():
        log(f"cloudflared.exe not found at {CLOUDFLARED_BIN}")
        return None, None

    kill_orphan_cloudflared()
    time.sleep(1)

    log("Starting Cloudflare Tunnel...")
    cmd = [str(CLOUDFLARED_BIN), "tunnel", "--url", "http://127.0.0.1:8000"]
    proc = subprocess.Popen(
        cmd,
        cwd=str(PROJECT_ROOT),
        creationflags=CREATE_NO_WINDOW,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="ignore"
    )

    public_url = None
    url_pattern = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")

    # Read output non-blockingly until url is found or timeout 25s
    start_time = time.time()
    while time.time() - start_time < 25:
        line = proc.stdout.readline()
        if not line and proc.poll() is not None:
            break
        if line:
            m = url_pattern.search(line)
            if m:
                public_url = m.group(0)
                log(f"Cloudflare Tunnel active at: {public_url}")
                break

    return proc, public_url


def main():
    if not acquire_daemon_lock():
        log("Another instance of service_daemon is already running. Exiting duplicate.")
        sys.exit(0)

    daemon_pid = os.getpid()
    log(f"Service Daemon started with PID {daemon_pid}")

    uvicorn_proc = None
    cloudflared_proc = None
    public_url = None

    # Step 1: Ensure Uvicorn is running
    if not is_port_open(8000):
        uvicorn_proc = start_uvicorn()
        time.sleep(2)
    else:
        log("Port 8000 already active (existing server detected)")

    # Step 2: Start Cloudflare Tunnel
    cloudflared_proc, public_url = start_cloudflared()

    update_desktop_link(public_url)
    save_state(
        daemon_pid=daemon_pid,
        uvicorn_pid=uvicorn_proc.pid if uvicorn_proc else None,
        cloudflared_pid=cloudflared_proc.pid if cloudflared_proc else None,
        public_url=public_url
    )

    # Step 3: 24/7 Watchdog Loop
    log("Entering 24/7 watchdog loop...")
    while True:
        try:
            time.sleep(10)

            # Check backend health
            if not is_port_open(8000):
                log("Backend server on port 8000 died! Reviving...")
                if uvicorn_proc and uvicorn_proc.poll() is None:
                    try:
                        uvicorn_proc.terminate()
                    except Exception:
                        pass
                uvicorn_proc = start_uvicorn()
                time.sleep(2)

            # Check Cloudflare tunnel health
            if cloudflared_proc and cloudflared_proc.poll() is not None:
                log("Cloudflare tunnel process exited! Reconnecting...")
                cloudflared_proc, new_url = start_cloudflared()
                if new_url:
                    public_url = new_url
                    update_desktop_link(public_url)
                    save_state(
                        daemon_pid=daemon_pid,
                        uvicorn_pid=uvicorn_proc.pid if uvicorn_proc else None,
                        cloudflared_pid=cloudflared_proc.pid if cloudflared_proc else None,
                        public_url=public_url
                    )

        except Exception as e:
            log(f"Watchdog exception: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
