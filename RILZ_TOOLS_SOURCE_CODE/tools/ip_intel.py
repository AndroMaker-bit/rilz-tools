"""
IP & Geolocation Intelligence Tool for RILZ TOOLS
Lookup any IP address or domain for Country, City, ISP, ASN, and Coordinates.
"""

from typing import Optional
import requests
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def lookup_ip_intelligence(target: Optional[str] = None):
    """Query IP geolocation, ISP, ASN, and network metadata."""
    query = (target or "").strip().replace("http://", "").replace("https://", "").split("/")[0]

    api_url = f"http://ip-api.com/json/{query}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,query"
    console.print(f"\n[bold cyan]🔍 Mengambil intelijen jaringan untuk:[/bold cyan] {query or 'IP Publik Anda'}")

    try:
        r = requests.get(api_url, timeout=8)
        data = r.json()

        if data.get("status") != "success":
            console.print(f"[bold red]❌ Gagal mendapatkan informasi IP:[/bold red] {data.get('message', 'Unknown error')}\n")
            return

        table = Table(title=f"🌐 IP Intelligence: {data.get('query')}", expand=True)
        table.add_column("Property", style="bold cyan", width=18)
        table.add_column("Details", style="bold white")

        table.add_row("IP Address", data.get("query", "N/A"))
        table.add_row("Country", f"{data.get('country')} ({data.get('countryCode')})")
        table.add_row("Region / City", f"{data.get('city')}, {data.get('regionName')} ({data.get('zip', '')})")
        table.add_row("Timezone", data.get("timezone", "N/A"))
        table.add_row("ISP Provider", data.get("isp", "N/A"))
        table.add_row("Organization", data.get("org", "N/A"))
        table.add_row("Autonomous System", data.get("as", "N/A"))
        table.add_row("Coordinates", f"Lat: {data.get('lat')}, Lon: {data.get('lon')}")
        table.add_row("Maps Link", f"https://www.google.com/maps?q={data.get('lat')},{data.get('lon')}")

        console.print(table)
        console.print()

    except Exception as e:
        console.print(f"[bold red]❌ Terjadi error saat menghubungi server IP:[/bold red] {e}\n")
