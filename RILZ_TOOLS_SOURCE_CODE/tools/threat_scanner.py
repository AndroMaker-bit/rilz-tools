import hashlib
import math
import os
import re
import socket
import urllib.parse
from typing import Dict, Any, List
import requests

SUSPICIOUS_TLDS = {
    ".tk", ".ml", ".ga", ".cf", ".gq", ".top", ".xyz", ".click", ".surf",
    ".rest", ".fit", ".vip", ".cc", ".to", ".live", ".work", ".bar"
}

TARGET_BRANDS = [
    "bca", "bri", "bni", "mandiri", "cimb", "dana", "gopay", "ovo", "shopee", "tokopedia",
    "google", "gmail", "facebook", "instagram", "whatsapp", "telegram", "tiktok", "netflix",
    "paypal", "apple", "microsoft", "steam", "discord", "roblox", "freefire", "mobilelegends"
]

PHISHING_KEYWORDS = [
    "login", "signin", "masuk", "verifikasi", "verify", "secure", "security", "update",
    "banking", "wallet", "claim", "hadiah", "dana-kaget", "pulsa", "gratis", "airdrop",
    "account", "auth", "recover", "pin", "otp", "password", "konfirmasi", "bantuan"
]

DANGEROUS_EXTENSIONS = {
    ".exe", ".scr", ".bat", ".cmd", ".vbs", ".vbe", ".js", ".jse", ".wsf",
    ".wsh", ".ps1", ".msc", ".jar", ".apk", ".msi", ".dll", ".hta"
}

SUSPICIOUS_STRINGS = [
    b"powershell -enc", b"powershell.exe", b"cmd.exe /c", b"WScript.Shell", b"Shell.Application",
    b"rundll32", b"regsvr32", b"certutil -urlcache", b"bitsadmin /transfer", b"Auto_Open",
    b"Document_Open", b"vbaProject.bin", b"VirtualAlloc", b"WriteProcessMemory", b"CreateRemoteThread",
    b"eval(base64_decode", b"system(", b"exec(", b"passthru(", b"chmod +x", b"Invoke-Expression"
]


def calculate_shannon_entropy(data: bytes) -> float:
    if not data:
        return 0.0
    entropy = 0.0
    size = len(data)
    for x in range(256):
        p_x = float(data.count(bytes([x]))) / size
        if p_x > 0:
            entropy += - p_x * math.log2(p_x)
    return entropy


def scan_file_bytes(data: bytes, filename: str) -> Dict[str, Any]:
    md5 = hashlib.md5(data).hexdigest()
    sha1 = hashlib.sha1(data).hexdigest()
    sha256 = hashlib.sha256(data).hexdigest()
    size = len(data)
    ext = os.path.splitext(filename)[1].lower()

    flags: List[str] = []
    threat_score = 0

    # 1. Magic bytes verification (Spoofed extension check)
    is_pe = data.startswith(b"MZ")
    is_elf = data.startswith(b"\x7fELF")
    is_zip = data.startswith(b"PK\x03\x04")
    is_pdf = data.startswith(b"%PDF")
    is_png = data.startswith(b"\x89PNG")
    is_jpg = data.startswith(b"\xff\xd8\xff")

    if (is_png or is_jpg or is_pdf) and is_pe:
        threat_score += 65
        flags.append("Ekstensi dipalsukan! File gambar/dokumen memuat binary eksekusi Windows (PE header)")

    if is_pe and ext not in [".exe", ".dll", ".sys"]:
        threat_score += 55
        flags.append(f"Header executable Windows (MZ) ditemukan pada file berformat '{ext}'")

    if is_elf and ext not in [".bin", ".elf", ".so"]:
        threat_score += 50
        flags.append(f"Header executable Linux (ELF) terdeteksi pada file '{ext}'")

    if ext in DANGEROUS_EXTENSIONS:
        threat_score += 25
        flags.append(f"Ekstensi file eksekusi berisiko tinggi ({ext})")

    # 2. Shannon Entropy (Packed / Ransomware payload check)
    entropy = calculate_shannon_entropy(data)
    if entropy > 7.15 and size > 2048:
        threat_score += 30
        flags.append(f"Entropi file sangat tinggi ({entropy:.2f}/8.0) - Indikasi payload terenkripsi/dipacking (Ransomware/Crypter)")

    # 3. Suspicious code strings / payload checks
    found_signatures = []
    data_lower = data.lower()
    for s in SUSPICIOUS_STRINGS:
        if s.lower() in data_lower:
            found_signatures.append(s.decode('latin-1', errors='ignore'))

    if found_signatures:
        threat_score += min(len(found_signatures) * 15, 45)
        flags.append(f"Ditemukan signature instruksi berbahaya: {', '.join(found_signatures[:3])}")

    threat_score = min(threat_score, 100)
    if threat_score >= 60:
        verdict = "TERDETEKSI ANCAMAN MALWARE"
        level = "danger"
    elif threat_score >= 25:
        verdict = "MENCURIGAKAN (SUSPICIOUS)"
        level = "warning"
    else:
        verdict = "BERSIH (CLEAN)"
        level = "safe"

    return {
        "filename": filename,
        "size_bytes": size,
        "size_kb": round(size / 1024, 2),
        "md5": md5,
        "sha256": sha256,
        "entropy": round(entropy, 2),
        "threat_score": threat_score,
        "verdict": verdict,
        "level": level,
        "flags": flags,
    }


def scan_url_malware(url: str) -> Dict[str, Any]:
    url = url.strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    flags: List[str] = []
    threat_score = 0
    parsed = urllib.parse.urlparse(url)
    hostname = (parsed.hostname or "").lower()
    path = parsed.path.lower()
    ext = os.path.splitext(path)[1]

    # Direct dangerous file download link check
    if ext in DANGEROUS_EXTENSIONS:
        threat_score += 65
        flags.append(f"Tautan mengarah langsung ke unduhan file eksekusi berisiko tinggi ({ext})")

    # IP address host
    if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", hostname):
        threat_score += 35
        flags.append("Tautan menggunakan alamat IP langsung (pola distribusi malware C2)")

    # Test HTTP response headers
    resolved_ip = "Unknown"
    server_header = "Unknown"
    content_type = "Unknown"
    content_length = 0

    try:
        resolved_ip = socket.gethostbyname(hostname)
        resp = requests.head(url, allow_redirects=True, timeout=6, headers={"User-Agent": "Mozilla/5.0"})
        content_type = resp.headers.get("Content-Type", "Unknown")
        server_header = resp.headers.get("Server", "Unknown")
        content_length = int(resp.headers.get("Content-Length", 0))

        disposition = resp.headers.get("Content-Disposition", "")
        if any(d_ext in disposition.lower() for d_ext in DANGEROUS_EXTENSIONS):
            threat_score += 60
            flags.append("Header Content-Disposition memicu unduhan otomatis file berbahaya")

        if "application/x-dosexec" in content_type or "application/x-msdownload" in content_type:
            threat_score += 70
            flags.append(f"Tipe konten server adalah executable biner Windows ({content_type})")
    except Exception as e:
        flags.append(f"Peringatan koneksi: Server target tidak merespons HEAD request ({str(e)[:40]})")

    threat_score = min(threat_score, 100)
    if threat_score >= 60:
        verdict = "LINK DISTRIBUSI MALWARE"
        level = "danger"
    elif threat_score >= 25:
        verdict = "MENCURIGAKAN (SUSPICIOUS LINK)"
        level = "warning"
    else:
        verdict = "LINK BERSIH / TIDAK ADA MALWARE LANGSUNG"
        level = "safe"

    return {
        "url": url,
        "hostname": hostname,
        "resolved_ip": resolved_ip,
        "server": server_header,
        "content_type": content_type,
        "threat_score": threat_score,
        "verdict": verdict,
        "level": level,
        "flags": flags,
    }


def analyze_phishing_url(url: str) -> Dict[str, Any]:
    url = url.strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    parsed = urllib.parse.urlparse(url)
    hostname = (parsed.hostname or "").lower()
    path = parsed.path.lower()
    query = parsed.query.lower()

    flags: List[str] = []
    risk_score = 0

    # 1. IP Hostname Check
    is_ip = bool(re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", hostname))
    if is_ip:
        risk_score += 35
        flags.append("Domain menggunakan alamat IP langsung (Indikasi server phish/C2)")

    # 2. Protocol Check
    if parsed.scheme == "http":
        risk_score += 15
        flags.append("Koneksi tidak terenkripsi (HTTP polos, tanpa sertifikat SSL)")

    # 3. Punycode Check
    if hostname.startswith("xn--"):
        risk_score += 30
        flags.append("Menggunakan Punycode Homoglyph (Karakter palsu yang menyerupai huruf asli)")

    # 4. Suspicious TLD
    for tld in SUSPICIOUS_TLDS:
        if hostname.endswith(tld):
            risk_score += 20
            flags.append(f"Menggunakan ekstensi domain berisiko tinggi ({tld})")
            break

    # 5. Excessive Subdomains
    subdomain_parts = hostname.split(".")
    if len(subdomain_parts) > 3 and not is_ip:
        risk_score += 15
        flags.append(f"Struktur subdomain berlebihan ({len(subdomain_parts)} tingkat) untuk mengelabui mata")

    # 6. Deceptive @ symbol in URL
    if "@" in url:
        risk_score += 40
        flags.append("Menggunakan karakter '@' untuk menyamarkan domain asli")

    # 7. Brand Impersonation in Domain / Subdomain
    detected_brand = None
    for brand in TARGET_BRANDS:
        if brand in hostname:
            if not (hostname == f"{brand}.com" or hostname.endswith(f".{brand}.com") or hostname == f"{brand}.co.id" or hostname.endswith(f".{brand}.co.id")):
                risk_score += 40
                detected_brand = brand
                flags.append(f"Mencatut nama merek resmi '{brand.upper()}' pada domain tidak resmi")
                break

    # 8. Bait Keywords in Path/Query
    found_keywords = []
    for kw in PHISHING_KEYWORDS:
        if kw in path or kw in query or (kw in hostname and kw != detected_brand):
            found_keywords.append(kw)

    if found_keywords:
        risk_score += min(len(found_keywords) * 10, 30)
        flags.append(f"Memuat kata kunci jebakan phishing: {', '.join(found_keywords[:4])}")

    risk_score = min(risk_score, 100)
    if risk_score >= 65:
        verdict = "BAHAYA PHISHING TINGGI"
        level = "danger"
    elif risk_score >= 30:
        verdict = "MENCURIGAKAN (WASPADA)"
        level = "warning"
    else:
        verdict = "RELATIF AMAN"
        level = "safe"

    return {
        "url": url,
        "hostname": hostname,
        "risk_score": risk_score,
        "verdict": verdict,
        "level": level,
        "flags": flags,
        "detected_brand": detected_brand,
    }
