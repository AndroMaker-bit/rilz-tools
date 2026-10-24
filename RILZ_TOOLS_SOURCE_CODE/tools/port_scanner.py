"""
Multithreaded Port Scanner for RILZ TOOLS
Scan host ports with service identification and response latency.
"""

import concurrent.futures
import socket
import time
from typing import List, Tuple
from rich.console import Console
from rich.table import Table

console = Console()

COMMON_PORTS = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    445: "SMB",
    1433: "MS-SQL",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    6379: "Redis",
    8000: "HTTP-Dev",
    8080: "HTTP-Proxy",
    8443: "HTTPS-Alt",
    9000: "SonarQube/Portainer",
    27017: "MongoDB",
}


def scan_single_port(host: str, port: int, timeout: float = 1.0) -> Tuple[int, bool, float, str]:
    """Test connection to single TCP port."""
    t0 = time.perf_counter()
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            res = s.connect_ex((host, port))
            latency = (time.perf_counter() - t0) * 1000.0
            is_open = (res == 0)
            service = COMMON_PORTS.get(port, "Unknown")
            return port, is_open, latency, service
    except Exception:
        return port, False, 0.0, COMMON_PORTS.get(port, "Unknown")


def run_port_scan(target: str, custom_ports: List[int] = None):
    """Scan target host using ThreadPoolExecutor."""
    clean_host = target.replace("http://", "").replace("https://", "").split("/")[0].split(":")[0]
    ports = custom_ports or list(COMMON_PORTS.keys())

    console.print(f"\n[bold cyan]🔍 Memindai {len(ports)} port pada target:[/bold cyan] [bold white]{clean_host}[/bold white]")

    try:
        ip = socket.gethostbyname(clean_host)
        console.print(f"[dim]IP Terdeteksi: {ip}[/dim]\n")
    except socket.gaierror:
        console.print(f"[bold red]❌ Gagal menyelesaikan nama host: {clean_host}[/bold red]\n")
        return

    open_ports = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
        futures = [executor.submit(scan_single_port, ip, p) for p in ports]
        for f in concurrent.futures.as_completed(futures):
            p, is_open, lat, srv = f.result()
            if is_open:
                open_ports.append((p, lat, srv))

    open_ports.sort(key=lambda x: x[0])

    if open_ports:
        table = Table(title=f"🛡️ Hasil Scan Port Terbuka ({clean_host})", expand=True)
        table.add_column("Port", style="bold cyan", width=8)
        table.add_column("Status", style="bold bright_green", width=10)
        table.add_column("Service", style="bold white", width=18)
        table.add_column("Latency (ms)", style="yellow", justify="right")

        for p, lat, srv in open_ports:
            table.add_row(str(p), "OPEN", srv, f"{lat:5.1f} ms")

        console.print(table)
    else:
        console.print(f"[bold yellow]⚠️ Tidak ada port umum yang terbuka terdeteksi pada {clean_host}.[/bold yellow]")

    console.print()
