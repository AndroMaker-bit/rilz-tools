#!/usr/bin/env python3
"""
RILZ WEB SERVER - Liquid Glass Edition v1.0.0
FastAPI Backend for RILZ Cyber Tools
Accessible on Localhost, Local Network (WiFi), or Cloudflare Tunnel
"""

import hashlib
import io
import json
import os
import re
import socket
import sys
import tempfile
import time
import urllib.parse
from pathlib import Path
from typing import Optional, List

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

SERVER_START_TIME = time.time()

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

# Import existing core modules from RILZ TOOLS
from tools.bg_remover import remove_background
from tools.file_downloader import (
    resolve_mediafire_link,
    resolve_terabox_link,
    resolve_pixeldrain_link,
)
from tools.hd_media import enhance_to_hd
from tools.ip_intel import lookup_ip_intelligence
from tools.link_bypass import (
    bypass_and_unshorten_link,
    resolve_gdrive_link,
    resolve_dropbox_link,
)
from tools.vault import _db, _init_vault, VAULT_DIR

app = FastAPI(
    title="RILZ TOOLS — Web Edition",
    version="2.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

# Directories
STATIC_DIR = Path(__file__).resolve().parent / "static"
TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
TEMP_DIR = Path(__file__).resolve().parent / "temp"

STATIC_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# ── Security Shield & Gatekeeper Configuration ──────────────────────────────
SECURITY_CONFIG_FILE = PROJECT_ROOT / "rilz_security.json"
RATE_LIMIT_STORE = {}


def get_security_config() -> dict:
    default_cfg = {
        "pin_enabled": True,
        "master_pin": "1337",
        "anti_inspect": True,
        "rate_limit_rpm": 60,
        "block_ssrf": True,
        "secret_salt": "rilz_saber_alter_secure_salt_2026",
    }
    if SECURITY_CONFIG_FILE.exists():
        try:
            with open(SECURITY_CONFIG_FILE, "r", encoding="utf-8") as f:
                return {**default_cfg, **json.load(f)}
        except Exception:
            pass
    return default_cfg


def hash_pin_token(pin: str, salt: str) -> str:
    return hashlib.sha256(f"{pin}:{salt}:rilz_session".encode("utf-8")).hexdigest()


def is_private_or_loopback_ip(target: str) -> bool:
    try:
        clean = target.split("://")[-1].split("/")[0].split(":")[0]
        if clean.lower() in ("localhost", "127.0.0.1", "0.0.0.0", "::1"):
            return True
        resolved = socket.gethostbyname(clean)
        parts = [int(p) for p in resolved.split(".")]
        if parts[0] == 127 or parts[0] == 10 or parts[0] == 0:
            return True
        if parts[0] == 172 and 16 <= parts[1] <= 31:
            return True
        if parts[0] == 192 and parts[1] == 168:
            return True
        if parts[0] == 169 and parts[1] == 254:
            return True
    except Exception:
        pass
    return False


@app.middleware("http")
async def security_guard_middleware(request: Request, call_next):
    # 1. Detect Real Client IP (Cloudflare Tunnel or Local)
    client_ip = (
        request.headers.get("cf-connecting-ip")
        or request.headers.get("x-forwarded-for")
        or (request.client.host if request.client else "127.0.0.1")
    )
    if "," in client_ip:
        client_ip = client_ip.split(",")[0].strip()

    cfg = get_security_config()
    now = time.time()
    path = request.url.path

    # 2. Rate Limiting Protection (Anti-DDoS / Anti-Flood)
    if client_ip not in ("127.0.0.1", "::1"):
        max_rpm = cfg.get("rate_limit_rpm", 60)
        if any(h in path for h in ["/api/link/bypass", "/api/video/stream", "/api/video/download", "/api/security/scan-file"]):
            max_rpm = 15

        history = RATE_LIMIT_STORE.get(client_ip, [])
        history = [t for t in history if now - t < 60]
        if len(history) >= max_rpm:
            return JSONResponse(
                {
                    "success": False,
                    "error": "⚠️ Terlalu banyak permintaan! Kecepatan akses dibatasi otomatis oleh Anti-DDoS Shield. Harap tunggu sebentar.",
                    "rate_limited": True,
                },
                status_code=429,
                headers={"Retry-After": "60"},
            )
        history.append(now)
        RATE_LIMIT_STORE[client_ip] = history

    # 3. Master PIN Gatekeeper for Remote / Tunnel Access
    is_public_asset = (
        path.startswith("/static/")
        or path in ("/gatekeeper", "/api/security/login", "/api/system/info", "/edukids", "/game/edukids")
        or path.startswith("/edukids")
    )
    is_local_request = (
        request.client
        and request.client.host in ("127.0.0.1", "::1", "localhost")
        and not request.headers.get("cf-connecting-ip")
    )

    if cfg.get("pin_enabled", True) and not is_local_request and not is_public_asset:
        expected_token = hash_pin_token(cfg.get("master_pin", "1337"), cfg.get("secret_salt", "salt"))
        user_token = request.cookies.get("rilz_session")
        if user_token != expected_token:
            if path.startswith("/api/"):
                return JSONResponse(
                    {
                        "success": False,
                        "error": "🔒 Akses ditolak. Harap masukkan Master PIN di halaman gerbang keamanan.",
                        "auth_required": True,
                    },
                    status_code=401,
                )
            else:
                return RedirectResponse(url=f"/gatekeeper?next={urllib.parse.quote(path)}")

    # 4. Execute request
    response = await call_next(request)

    # 5. Inject Hardened Security Headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Server"] = "RILZ-SECURE-SHIELD/2.0"
    return response


# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_local_ip() -> str:
    """Detect local WiFi / LAN IP for sharing with friends on the same network."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


# ── Page Routes ──────────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_file = TEMPLATES_DIR / "index.html"
    if index_file.exists():
        return HTMLResponse(content=index_file.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>RILZ WEB initializing templates...</h1>")


@app.get("/tool/{tool_id}", response_class=HTMLResponse)
async def serve_tool_page(tool_id: str):
    tool_file = TEMPLATES_DIR / f"tool_{tool_id}.html"
    if tool_file.exists():
        return HTMLResponse(content=tool_file.read_text(encoding="utf-8"))
    return RedirectResponse(url="/")


@app.get("/edukids", response_class=HTMLResponse)
@app.get("/game/edukids", response_class=HTMLResponse)
async def serve_edukids():
    edu_file = TEMPLATES_DIR / "edukids.html"
    if edu_file.exists():
        return HTMLResponse(content=edu_file.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>Taman Belajar Ceria — Loading...</h1>")


@app.get("/gatekeeper", response_class=HTMLResponse)
async def serve_gatekeeper():
    gk_file = TEMPLATES_DIR / "gatekeeper.html"
    if gk_file.exists():
        return HTMLResponse(content=gk_file.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>Cyber Gateway Lockscreen</h1>")


@app.post("/api/security/login")
async def security_login(pin: str = Form(...)):
    cfg = get_security_config()
    master_pin = str(cfg.get("master_pin", "1337")).strip()
    if pin.strip() == master_pin:
        token = hash_pin_token(master_pin, cfg.get("secret_salt", "salt"))
        resp = JSONResponse({"success": True, "message": "Autentikasi Master PIN berhasil!"})
        resp.set_cookie(
            key="rilz_session",
            value=token,
            max_age=30 * 86400,
            httponly=True,
            samesite="lax",
            secure=False,
        )
        return resp
    return JSONResponse({"success": False, "error": "⚠️ PIN Keamanan Salah! Akses ditolak."}, status_code=401)


@app.get("/api/security/status")
async def security_status():
    cfg = get_security_config()
    return {
        "success": True,
        "pin_enabled": cfg.get("pin_enabled", True),
        "anti_inspect": cfg.get("anti_inspect", True),
        "rate_limit_rpm": cfg.get("rate_limit_rpm", 60),
        "block_ssrf": cfg.get("block_ssrf", True),
    }


@app.post("/api/security/update-pin")
async def security_update_pin(current_pin: str = Form(...), new_pin: str = Form(...)):
    cfg = get_security_config()
    master_pin = str(cfg.get("master_pin", "1337")).strip()
    if current_pin.strip() != master_pin:
        return JSONResponse({"success": False, "error": "PIN lama salah!"}, status_code=400)
    if len(new_pin.strip()) < 4:
        return JSONResponse({"success": False, "error": "PIN baru minimal 4 karakter!"}, status_code=400)
    cfg["master_pin"] = new_pin.strip()
    try:
        with open(SECURITY_CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
        token = hash_pin_token(cfg["master_pin"], cfg.get("secret_salt", "salt"))
        resp = JSONResponse({"success": True, "message": "Master PIN berhasil diperbarui!"})
        resp.set_cookie(key="rilz_session", value=token, max_age=30 * 86400, httponly=True, samesite="lax")
        return resp
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@app.get("/api/system/info")
async def system_info():
    local_ip = get_local_ip()
    public_started_ts = None
    public_url = None
    service_file = PROJECT_ROOT / "rilz_service.json"
    if service_file.exists():
        try:
            with open(service_file, "r", encoding="utf-8") as f:
                sdata = json.load(f)
                public_url = sdata.get("public_url")
                public_started_ts = sdata.get("started_ts")
                if not public_started_ts and "updated_at" in sdata:
                    import datetime
                    dt = datetime.datetime.strptime(sdata["updated_at"], "%Y-%m-%d %H:%M:%S")
                    public_started_ts = int(dt.timestamp())
        except Exception:
            pass

    if not public_started_ts:
        public_started_ts = int(SERVER_START_TIME)

    return {
        "app_name": "RILZ TOOLS Web Edition",
        "version": "1.0.0",
        "theme": "Liquid Glass",
        "local_ip": local_ip,
        "local_url": f"http://{local_ip}:8000",
        "localhost_url": "http://localhost:8000",
        "public_url": public_url,
        "public_started_ts": public_started_ts,
        "server_started_ts": int(SERVER_START_TIME),
        "now_ts": int(time.time()),
    }


# ── Tool 1: Video Info & Download ─────────────────────────────────────────────
@app.get("/api/video/file/{file_id}")
async def video_get_file(file_id: str, download_name: Optional[str] = None):
    """Serve downloaded video or audio file with clean attachment header."""
    safe_name = os.path.basename(file_id)
    file_path = TEMP_DIR / safe_name
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File download tidak ditemukan atau telah kedaluwarsa.")

    ext = file_path.suffix.lower()
    media_type = "audio/mpeg" if ext == ".mp3" else "video/mp4"
    serve_name = download_name or safe_name

    return FileResponse(
        str(file_path),
        media_type=media_type,
        filename=serve_name,
    )


@app.get("/api/video/stream")
async def video_stream_download(url: str, audio: bool = False):
    """Direct 1-click browser download route."""
    try:
        from tools.video import process_video_download
        res = process_video_download(url.strip(), str(TEMP_DIR), audio_only=audio)
        if not res.get("success"):
            return HTMLResponse(f"<h3>Error: {res.get('error', 'Gagal memproses video')}</h3>", status_code=400)

        return FileResponse(
            res["filepath"],
            media_type=res["media_type"],
            filename=res["filename"],
        )
    except Exception as e:
        return HTMLResponse(f"<h3>Error: {str(e)}</h3>", status_code=500)


@app.post("/api/video/info")
async def video_info(url: str = Form(...)):
    try:
        from tools.video import get_video_info
        res = get_video_info(url.strip())
        return res
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/video/download")
async def video_download(
    url: str = Form(...),
    audio_only: bool = Form(False),
    direct: bool = Form(False)
):
    try:
        from tools.video import process_video_download

        # Safely handle bool if called in tests or HTTP form
        is_direct = direct is True or str(direct).lower() in ["1", "true"]
        is_audio = audio_only is True or str(audio_only).lower() in ["1", "true"]

        res = process_video_download(url.strip(), str(TEMP_DIR), audio_only=is_audio)
        if not res.get("success"):
            return JSONResponse({"success": False, "error": res.get("error", "Gagal memproses video.")}, status_code=400)

        if is_direct:
            return FileResponse(
                res["filepath"],
                media_type=res["media_type"],
                filename=res["filename"],
            )

        file_basename = os.path.basename(res["filepath"])
        download_url = f"/api/video/file/{file_basename}?download_name={urllib.parse.quote(res['filename'])}"

        return {
            "success": True,
            "download_url": download_url,
            "filename": res["filename"],
            "title": res["title"],
            "thumbnail": res.get("thumbnail", ""),
            "duration": res.get("duration", 0),
            "size_mb": res.get("size_mb", 0),
            "media_type": res.get("media_type", "video/mp4"),
            "source": res.get("source", ""),
        }
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


# ── Tool 2: Cloud Storage Ripper ──────────────────────────────────────────────
@app.post("/api/cloud/rip")
async def cloud_rip(url: str = Form(...)):
    low = url.lower()
    try:
        direct = None
        service = "Direct URL"

        if "mediafire.com" in low:
            service = "MediaFire"
            link, _ = resolve_mediafire_link(url)
            direct = link
        elif "drive.google.com" in low:
            service = "Google Drive"
            direct = resolve_gdrive_link(url)
        elif "terabox" in low or "1024tera" in low or "terashare" in low:
            service = "TeraBox"
            link, _ = resolve_terabox_link(url)
            direct = link
        elif "dropbox.com" in low:
            service = "Dropbox"
            direct = resolve_dropbox_link(url)
        elif "pixeldrain.com" in low:
            service = "Pixeldrain"
            direct = resolve_pixeldrain_link(url)
        else:
            direct = url

        if direct:
            return {
                "success": True,
                "service": service,
                "original_url": url,
                "direct_download_url": direct,
            }
        return {"success": False, "error": "Bypass direct link tidak ditemukan."}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ── Tool 3: Link Bypass & Unshortener ────────────────────────────────────────
@app.post("/api/link/bypass")
async def link_bypass(url: str = Form(...)):
    try:
        if is_private_or_loopback_ip(url.strip()):
            return {"success": False, "error": "⚠️ Akses ke IP lokal/private diblokir demi keamanan (SSRF Shield)!"}

        from tools.link_bypass import SAFELINK_DOMAINS
        final_url, hop_tuples = bypass_and_unshorten_link(url.strip())
        hops = [h[1] for h in hop_tuples] if hop_tuples else [url]
        is_safelink = any(dom in final_url.lower() for dom in SAFELINK_DOMAINS)
        is_bypassed = len(hops) > 1 and not is_safelink

        return {
            "success": True,
            "original_url": url,
            "final_url": final_url,
            "hop_count": len(hops),
            "hops": hops,
            "is_redirected": is_bypassed,
            "is_safelink": is_safelink,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# ── Tool 4: Image Lab (HD Upscaler & Background Remover) ──────────────────────
@app.post("/api/image/rmbg")
async def image_rmbg(file: UploadFile = File(...), tolerance: int = Form(40)):
    try:
        timestamp = int(time.time())
        safe_stem = re.sub(r'[^a-zA-Z0-9_\-]', '_', Path(file.filename or "image").stem)[:30] or "image"
        ext = Path(file.filename or "image.png").suffix.lower()
        if ext not in (".png", ".jpg", ".jpeg", ".webp", ".bmp"):
            ext = ".png"

        in_path = TEMP_DIR / f"upload_{timestamp}_{safe_stem}{ext}"
        with open(in_path, "wb") as f:
            f.write(await file.read())

        out_name = f"transparent_{safe_stem}_{timestamp}.png"
        out_path = TEMP_DIR / out_name

        res_path = remove_background(str(in_path), output_path=str(out_path), tolerance=tolerance)
        if res_path and os.path.exists(str(res_path)):
            return FileResponse(
                str(res_path),
                media_type="image/png",
                filename=f"transparent_{safe_stem}.png",
            )
        return JSONResponse({"success": False, "error": "Gagal menghapus background"}, status_code=500)
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@app.post("/api/image/hd")
async def image_hd(file: UploadFile = File(...), scale: int = Form(2)):
    try:
        timestamp = int(time.time())
        safe_stem = re.sub(r'[^a-zA-Z0-9_\-]', '_', Path(file.filename or "image").stem)[:30] or "image"
        ext = Path(file.filename or "image.png").suffix.lower()
        if ext not in (".png", ".jpg", ".jpeg", ".webp", ".bmp"):
            ext = ".png"

        in_path = TEMP_DIR / f"upload_{timestamp}_{safe_stem}{ext}"
        with open(in_path, "wb") as f:
            f.write(await file.read())

        out_name = f"hd_{scale}x_{safe_stem}_{timestamp}.png"
        out_path = TEMP_DIR / out_name

        res_path = enhance_to_hd(str(in_path), output_path=str(out_path), scale_factor=scale)
        if res_path and os.path.exists(str(res_path)):
            return FileResponse(
                str(res_path),
                media_type="image/png",
                filename=f"hd_{scale}x_{safe_stem}.png",
            )
        return JSONResponse({"success": False, "error": "Gagal upscale gambar"}, status_code=500)
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


# ── Tool 5: QR Code Generator ─────────────────────────────────────────────────
@app.post("/api/qr")
async def generate_qr(text: str = Form(...), fill_color: str = Form("#00ff66"), back_color: str = Form("#0a0e14")):
    try:
        import qrcode

        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=2,
        )
        qr.add_data(text)
        qr.make(fit=True)

        img = qr.make_image(fill_color=fill_color, back_color=back_color)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        return StreamingResponse(buf, media_type="image/png")
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


# ── Tool 6: Crypto & Hash Lab ────────────────────────────────────────────────
@app.post("/api/hash")
async def compute_hashes(text: str = Form(...)):
    data = text.encode("utf-8")
    return {
        "success": True,
        "input_len": len(text),
        "md5": hashlib.md5(data).hexdigest(),
        "sha1": hashlib.sha1(data).hexdigest(),
        "sha256": hashlib.sha256(data).hexdigest(),
        "sha512": hashlib.sha512(data).hexdigest(),
    }


# ── Tool 7: IP & Domain Reconnaissance ───────────────────────────────────────
@app.get("/api/ip")
async def ip_recon(target: Optional[str] = None):
    try:
        import requests

        url = f"http://ip-api.com/json/{target.strip()}" if target else "http://ip-api.com/json/"
        r = requests.get(url, timeout=8)
        data = r.json()
        if data.get("status") == "success":
            return {
                "success": True,
                "ip": data.get("query"),
                "country": data.get("country"),
                "country_code": data.get("countryCode"),
                "region": data.get("regionName"),
                "city": data.get("city"),
                "isp": data.get("isp"),
                "org": data.get("org"),
                "asn": data.get("as"),
                "lat": data.get("lat"),
                "lon": data.get("lon"),
                "timezone": data.get("timezone"),
                "maps_url": f"https://www.google.com/maps?q={data.get('lat')},{data.get('lon')}",
            }
        return {"success": False, "error": data.get("message", "Lookup failed")}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ── Tool 8: TempMail Disposable Email Proxy (mail.tm) ────────────────────────
@app.get("/api/tempmail/generate")
async def tempmail_generate():
    try:
        import requests, uuid
        d_resp = requests.get("https://api.mail.tm/domains", timeout=8)
        domains = d_resp.json().get("hydra:member", [])
        if not domains:
            return {"success": False, "error": "Tidak ada domain aktif"}
        domain = domains[0]["domain"]
        uname = f"rilz_{uuid.uuid4().hex[:7]}"
        addr = f"{uname}@{domain}"
        pwd = f"Rilz_{uuid.uuid4().hex[:10]}!"

        acc = requests.post("https://api.mail.tm/accounts", json={"address": addr, "password": pwd}, timeout=8)
        if acc.status_code not in (200, 201):
            return {"success": False, "error": "Gagal membuat email"}

        t_resp = requests.post("https://api.mail.tm/token", json={"address": addr, "password": pwd}, timeout=8)
        token = t_resp.json().get("token")

        return {"success": True, "email": addr, "token": token}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/tempmail/messages")
async def tempmail_messages(token: str):
    try:
        import requests
        m_resp = requests.get(
            "https://api.mail.tm/messages",
            headers={"Authorization": f"Bearer {token}"},
            timeout=8
        )
        if m_resp.status_code == 200:
            msgs = m_resp.json().get("hydra:member", [])
            formatted = []
            for m in msgs:
                formatted.append({
                    "id": m.get("id"),
                    "from": m.get("from", {}).get("address", "Unknown"),
                    "subject": m.get("subject", "(Tanpa Subjek)"),
                    "date": m.get("createdAt", "")[:19].replace("T", " ")
                })
            return {"success": True, "messages": formatted}
        return {"success": True, "messages": []}
    except Exception as e:
        return {"success": False, "error": str(e), "messages": []}


@app.get("/api/tempmail/read")
async def tempmail_read(token: str, msg_id: str):
    try:
        import requests
        r = requests.get(
            f"https://api.mail.tm/messages/{msg_id}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=8
        )
        if r.status_code == 200:
            d = r.json()
            return {
                "success": True,
                "message": {
                    "subject": d.get("subject", "(Tanpa Subjek)"),
                    "from": d.get("from", {}).get("address", "Unknown"),
                    "date": d.get("createdAt", "")[:19].replace("T", " "),
                    "textBody": d.get("text") or d.get("intro") or "Isi pesan kosong"
                }
            }
        return {"success": False, "error": "Pesan tidak ditemukan"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ── Tool 8: Second Brain / Vault API ──────────────────────────────────────────
@app.get("/api/vault/search")
async def vault_search(keyword: str):
    try:
        _init_vault()
        conn = _db()
        klike = f"%{keyword}%"
        rows = conn.execute(
            "SELECT id, title, category, filepath, tags, description, created_at, size_bytes "
            "FROM vault_items "
            "WHERE title LIKE ? OR tags LIKE ? OR description LIKE ? "
            "ORDER BY created_at DESC LIMIT 20",
            (klike, klike, klike),
        ).fetchall()
        conn.close()

        results = []
        for r in rows:
            results.append({
                "id": r[0],
                "title": r[1],
                "category": r[2],
                "filepath": r[3],
                "tags": r[4],
                "description": r[5],
                "created_at": r[6],
                "size_bytes": r[7],
            })
        return {"success": True, "results": results, "count": len(results)}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/vault/note")
async def vault_save_note(title: str = Form(...), content: str = Form(...), tags: str = Form("")):
    try:
        _init_vault()
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        safe_fn = re.sub(r'[^a-zA-Z0-9_\-]', '_', title)[:30] or "note"
        filename = f"{safe_fn}_{timestamp}.txt"
        dest_path = VAULT_DIR / "notes" / filename

        dest_path.write_text(content, encoding="utf-8")
        size = dest_path.stat().st_size
        desc = content[:120].replace("\n", " ")

        conn = _db()
        conn.execute(
            "INSERT INTO vault_items (title, category, filepath, tags, description, created_at, size_bytes) VALUES (?,?,?,?,?,?,?)",
            (title, "notes", str(dest_path), tags, desc, time.strftime("%Y-%m-%dT%H:%M:%S"), size),
        )
        conn.commit()
        conn.close()

        return {"success": True, "message": "Catatan berhasil disimpan ke Vault!"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ── Security Suite: Virus, Malware, & Phishing Detection ─────────────────────
@app.post("/api/security/scan-file")
async def security_scan_file(file: UploadFile = File(...)):
    try:
        from tools.threat_scanner import scan_file_bytes
        content = await file.read()
        res = scan_file_bytes(content, file.filename or "unknown.bin")
        return {"success": True, "data": res}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/security/scan-url")
async def security_scan_url(url: str = Form(...)):
    try:
        if is_private_or_loopback_ip(url.strip()):
            return {"success": False, "error": "⚠️ Akses ke IP lokal/private diblokir demi keamanan (SSRF Shield)!"}
        from tools.threat_scanner import scan_url_malware
        res = scan_url_malware(url)
        return {"success": True, "data": res}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/security/check-phishing")
async def security_check_phishing(url: str = Form(...)):
    try:
        if is_private_or_loopback_ip(url.strip()):
            return {"success": False, "error": "⚠️ Akses ke IP lokal/private diblokir demi keamanan (SSRF Shield)!"}
        from tools.threat_scanner import analyze_phishing_url
        res = analyze_phishing_url(url)
        return {"success": True, "data": res}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ── PDF Toolkit Suite ────────────────────────────────────────────────────────
@app.post("/api/pdf/compress")
async def api_pdf_compress(file: UploadFile = File(...), quality: str = Form("medium")):
    try:
        from tools.pdf import compress_pdf_file
        ext = Path(file.filename or "doc.pdf").suffix.lower()
        if ext != ".pdf":
            return {"success": False, "error": "Hanya file berekstensi .pdf yang didukung."}

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        safe_stem = re.sub(r'[^a-zA-Z0-9_\-]', '_', Path(file.filename).stem)[:25] or "document"
        in_path = TEMP_DIR / f"raw_{safe_stem}_{timestamp}.pdf"
        out_name = f"compressed_{safe_stem}_{timestamp}.pdf"
        out_path = TEMP_DIR / out_name

        content = await file.read()
        in_path.write_bytes(content)

        res = compress_pdf_file(str(in_path), str(out_path), quality_preset=quality)
        if res.get("success"):
            res["download_url"] = f"/api/pdf/download/{out_name}"
        return res
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/pdf/merge")
async def api_pdf_merge(files: List[UploadFile] = File(...)):
    try:
        from tools.pdf import merge_pdf_files
        if not files or len(files) < 2:
            return {"success": False, "error": "Pilih minimal 2 file PDF untuk digabungkan."}

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        input_paths = []

        for i, f in enumerate(files):
            ext = Path(f.filename or "doc.pdf").suffix.lower()
            if ext != ".pdf":
                continue
            safe_name = f"merge_in_{i}_{timestamp}.pdf"
            p = TEMP_DIR / safe_name
            content = await f.read()
            p.write_bytes(content)
            input_paths.append(str(p))

        if len(input_paths) < 2:
            return {"success": False, "error": "Minimal 2 file PDF yang valid diperlukan."}

        out_name = f"merged_rilz_{timestamp}.pdf"
        out_path = TEMP_DIR / out_name

        res = merge_pdf_files(input_paths, str(out_path))
        if res.get("success"):
            res["download_url"] = f"/api/pdf/download/{out_name}"
        return res
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/pdf/images-to-pdf")
async def api_pdf_images_to_pdf(files: List[UploadFile] = File(...)):
    try:
        from tools.pdf import images_to_pdf_file
        if not files:
            return {"success": False, "error": "Pilih minimal 1 file gambar."}

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        input_paths = []

        for i, f in enumerate(files):
            ext = Path(f.filename or "img.jpg").suffix.lower()
            if ext not in (".jpg", ".jpeg", ".png", ".webp", ".bmp"):
                continue
            safe_name = f"img_in_{i}_{timestamp}{ext}"
            p = TEMP_DIR / safe_name
            content = await f.read()
            p.write_bytes(content)
            input_paths.append(str(p))

        if not input_paths:
            return {"success": False, "error": "Tidak ada gambar valid yang diunggah."}

        out_name = f"photos_rilz_{timestamp}.pdf"
        out_path = TEMP_DIR / out_name

        res = images_to_pdf_file(input_paths, str(out_path))
        if res.get("success"):
            res["download_url"] = f"/api/pdf/download/{out_name}"
        return res
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/pdf/download/{file_id}")
async def api_pdf_download(file_id: str):
    safe_name = os.path.basename(file_id)
    file_path = TEMP_DIR / safe_name
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File PDF tidak ditemukan atau telah kedaluwarsa.")
    return FileResponse(
        str(file_path),
        media_type="application/pdf",
        filename=safe_name,
    )


# ── WhatsApp Sticker & GIF Converter Suite ──────────────────────────────────
@app.post("/api/sticker/convert")
async def api_sticker_convert(
    file: UploadFile = File(...),
    mode: str = Form("wa_animated"),
    duration: float = Form(6.0),
    fps: int = Form(15)
):
    try:
        from tools.sticker_maker import video_to_wa_sticker, video_to_gif, image_to_wa_sticker

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        orig_ext = Path(file.filename or "media.mp4").suffix.lower()
        safe_stem = re.sub(r'[^a-zA-Z0-9_\-]', '_', Path(file.filename).stem)[:25] or "sticker"
        in_path = TEMP_DIR / f"raw_stk_{safe_stem}_{timestamp}{orig_ext}"

        content = await file.read()
        in_path.write_bytes(content)

        if mode == "wa_animated":
            out_name = f"wa_sticker_{safe_stem}_{timestamp}.webp"
            out_path = TEMP_DIR / out_name
            res = video_to_wa_sticker(str(in_path), str(out_path), duration=duration, fps=fps)
        elif mode == "gif":
            out_name = f"animated_{safe_stem}_{timestamp}.gif"
            out_path = TEMP_DIR / out_name
            res = video_to_gif(str(in_path), str(out_path), duration=duration, fps=fps)
        else:
            out_name = f"wa_static_{safe_stem}_{timestamp}.webp"
            out_path = TEMP_DIR / out_name
            res = image_to_wa_sticker(str(in_path), str(out_path))

        if res.get("success"):
            res["download_url"] = f"/api/sticker/download/{out_name}"
            res["preview_url"] = f"/api/sticker/download/{out_name}"
        return res
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/sticker/download/{file_id}")
async def api_sticker_download(file_id: str):
    safe_name = os.path.basename(file_id)
    file_path = TEMP_DIR / safe_name
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File media tidak ditemukan atau telah kedaluwarsa.")

    ext = file_path.suffix.lower()
    media_type = "image/webp" if ext == ".webp" else "image/gif"
    return FileResponse(
        str(file_path),
        media_type=media_type,
        filename=safe_name,
    )


if __name__ == "__main__":
    import uvicorn

    local_ip = get_local_ip()
    port = int(os.environ.get("PORT", 8000))
    print("=" * 60)
    print("⚡ RILZ TOOLS WEB SERVER — LIQUID GLASS EDITION")
    print(f"👉 Localhost: http://localhost:{port}")
    print(f"👉 WiFi / Temen: http://{local_ip}:{port}")
    print("=" * 60)
    uvicorn.run("web.server:app", host="0.0.0.0", port=port)
