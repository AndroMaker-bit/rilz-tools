import asyncio
import base64
import concurrent.futures
import json
import re
import time
import urllib.parse
from typing import List, Optional, Tuple
from bs4 import BeautifulSoup
import requests
from rich.console import Console
from rich.table import Table

console = Console()

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

# Common safelink & redirect parameter keys
REDIRECT_PARAMS = [
    "url", "link", "target", "dest", "destination", "redirect", 
    "r", "u", "to", "go", "out", "c", "token", "next",
    "o", "dl", "file", "download", "landing", "click", "href"
]

# Recognizable destination file storage & sharing domains
KNOWN_DESTINATIONS = [
    "mediafire.com", "drive.google.com", "mega.nz", "mega.co.nz",
    "terabox.com", "1024tera.com", "teraboxapp.com", "terasharelink.com",
    "pixeldrain.com", "dropbox.com", "sfile.mobi", "sfile.co",
    "krakenfiles.com", "anonfiles.com", "gofile.io", "qiwi.gg",
    "send.cm", "uploadhaven.com", "racaty.net", "zippyshare"
]

SAFELINK_DOMAINS = [
    "sfl.gl", "sfl.ink", "safelinku.com", "safelinku.net", "safelinku.me",
    "linku.to", "safelinkblogger.com", "moneyblink.com", "ouo.io", "ouo.press",
    "clik.pw", "shrinkearn.com", "shrinkme.io", "exe.io", "za.gl", "khaddavi.net"
]


def multi_decode_url(val: str) -> str:
    """
    Robustly unmasks URLs encoded in URL-encode, single or multi-level Base64,
    Hexadecimal, or reversed Base64.
    """
    if not val or not isinstance(val, str):
        return ""
    val = val.strip()

    # Direct valid HTTP/HTTPS URL
    if val.startswith("http://") or val.startswith("https://"):
        return val

    # Try URL unquoting
    try:
        unquoted = urllib.parse.unquote(val).strip()
        if unquoted.startswith("http://") or unquoted.startswith("https://"):
            return unquoted
        val = unquoted
    except Exception:
        pass

    # Try recursive Base64 decoding (up to 4 layers)
    cur = val
    for _ in range(4):
        try:
            padded = cur + "=" * (-len(cur) % 4)
            dec = base64.b64decode(padded).decode("utf-8", errors="ignore").strip()
            if dec.startswith("http://") or dec.startswith("https://"):
                return dec
            if dec and len(dec) < len(cur):
                cur = dec
            else:
                break
        except Exception:
            break

    # Try Hexadecimal decoding
    try:
        hex_dec = bytes.fromhex(val).decode("utf-8", errors="ignore").strip()
        if hex_dec.startswith("http://") or hex_dec.startswith("https://"):
            return hex_dec
    except Exception:
        pass

    # Try Reversed Base64 decoding
    try:
        rev = val[::-1]
        padded = rev + "=" * (-len(rev) % 4)
        dec = base64.b64decode(padded).decode("utf-8", errors="ignore").strip()
        if dec.startswith("http://") or dec.startswith("https://"):
            return dec
    except Exception:
        pass

    return ""


def extract_safelink_from_url_params(url: str) -> str:
    """Inspects query string and URL fragment/hash for hidden target URLs."""
    try:
        parsed = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed.query)

        # Check query parameters
        for key in REDIRECT_PARAMS:
            if key in params and params[key]:
                val = params[key][0]
                decoded = multi_decode_url(val)
                if decoded and (decoded.startswith("http://") or decoded.startswith("https://")):
                    return decoded

        # Check fragment / hash (e.g. sfl.gl/xyz#aHR0c...)
        if parsed.fragment:
            frag_decoded = multi_decode_url(parsed.fragment)
            if frag_decoded and (frag_decoded.startswith("http://") or frag_decoded.startswith("https://")):
                return frag_decoded

    except Exception:
        pass
    return ""


def solve_adlinkfly_and_forms(html_text: str, current_url: str, session: requests.Session) -> Optional[str]:
    """
    Automated form solver for AdLinkFly / Safelinku / Linku.to networks.
    Extracts tokens (_csrfToken, ad_form_data, etc.) and replays the POST request to /links/go.
    """
    try:
        soup = BeautifulSoup(html_text, "html.parser")
        forms = soup.find_all("form")

        for form in forms:
            action = form.get("action") or ""
            form_id = form.get("id") or ""

            inputs = form.find_all("input")
            form_data = {}
            for inp in inputs:
                name = inp.get("name")
                val = inp.get("value", "")
                if name:
                    form_data[name] = val

            has_ad_tokens = any(
                k in form_data for k in ["_csrfToken", "ad_form_data", "_Token[fields]", "token", "alias"]
            )
            is_go_link = "go-link" in form_id or "link-view" in form_id or "links/go" in action

            if has_ad_tokens or is_go_link:
                parsed = urllib.parse.urlparse(current_url)
                base_domain = f"{parsed.scheme}://{parsed.netloc}"

                if not action or action == "#" or action == "":
                    go_url = f"{base_domain}/links/go"
                else:
                    go_url = urllib.parse.urljoin(current_url, action)
                    if not go_url.endswith("/links/go") and "links/go" not in go_url:
                        go_url = f"{base_domain}/links/go"

                headers = {
                    "User-Agent": DEFAULT_USER_AGENT,
                    "X-Requested-With": "XMLHttpRequest",
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "Referer": current_url,
                    "Origin": base_domain,
                    "Accept": "application/json, text/javascript, */*; q=0.01",
                }

                resp = session.post(go_url, data=form_data, headers=headers, timeout=10)
                if resp.status_code == 200:
                    try:
                        res_json = resp.json()
                        target = res_json.get("url") or res_json.get("message")
                        if target and (target.startswith("http://") or target.startswith("https://")):
                            return target
                    except Exception:
                        pass
    except Exception:
        pass
    return None


async def _solve_khaddavi_playwright(article_url: str, cookies: list) -> Optional[str]:
    """
    Headless Chromium solver for Khaddavi.net safelink network.
    Executes the multi-stage button timer, session validation, and captures target storage redirect.
    """
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        return None

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars"
            ]
        )
        context = await browser.new_context(
            user_agent=DEFAULT_USER_AGENT,
            viewport={"width": 1280, "height": 720}
        )
        if cookies:
            await context.add_cookies(cookies)

        page = await context.new_page()

        try:
            await page.goto(article_url, wait_until="domcontentloaded", timeout=25000)
        except Exception:
            pass

        # Wait for #verify button
        try:
            await page.wait_for_selector("#verify button", timeout=12000)
            await page.click("#verify button")
        except Exception:
            pass

        target_url = None
        # Watch timer countdown and page navigation transitions for up to 25 seconds
        for _ in range(25):
            await page.wait_for_timeout(1000)
            cur = page.url
            if any(dom in cur.lower() for dom in KNOWN_DESTINATIONS):
                target_url = cur
                break

            try:
                # Check verify button state
                btn_txt = await page.evaluate("() => document.querySelector('#verify button')?.innerText || ''")
                low_btn = btn_txt.lower()
                if "next" in low_btn:
                    await page.click("#verify button")
                elif "go to link" in low_btn or "get link" in low_btn:
                    await page.click("#verify button")

                # Check secondary placeholder button if step 1 rendered it
                h2 = await page.evaluate("() => document.getElementById('second_open_placeholder')?.innerText || ''")
                low_h2 = h2.lower()
                if "open" in low_h2 or "continue" in low_h2:
                    p_btn = await page.query_selector("#second_open_placeholder button")
                    if p_btn:
                        await p_btn.click()
            except Exception:
                pass

        await browser.close()
        return target_url


def solve_khaddavi_safelink(url: str, initial_html: str = "") -> Tuple[Optional[str], List[Tuple[int, str]]]:
    """
    Solves SFL (sfl.gl / sfl.ink) and Khaddavi.net safelink networks.
    Extracts initial ray_id & alias, fetches session cookies from redirect.php,
    and runs headless Chromium solver to bypass multi-stage timers.
    """
    history: List[Tuple[int, str]] = []
    try:
        import cloudscraper
        scraper = cloudscraper.create_scraper(browser={"browser": "chrome", "platform": "windows", "desktop": True})
    except Exception:
        scraper = requests.Session()

    scraper.headers.update({
        "User-Agent": DEFAULT_USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,id;q=0.8",
    })

    article_url = None
    cookies = []

    # If already on an app.khaddavi.net article
    if "khaddavi.net" in url.lower() and "redirect.php" not in url.lower():
        article_url = url
    else:
        # Step A: Fetch SFL page to extract ray_id and alias
        html_text = initial_html
        if not html_text:
            resp1 = scraper.get(url, timeout=12)
            html_text = resp1.text

        ray_match = re.search(r'name=["\']ray_id["\']\s+value=["\']([^"\']+)["\']', html_text)
        alias_match = re.search(r'name=["\']alias["\']\s+value=["\']([^"\']+)["\']', html_text)

        if not ray_match or not alias_match:
            return None, history

        ray_id = ray_match.group(1)
        alias = alias_match.group(1)
        history.append((302, f"SFL Ray Token: {ray_id[:8]}... (alias={alias})"))

        # Step B: Request redirect.php to obtain session cookies and article location
        redir_url = f"https://app.khaddavi.net/redirect.php?ray_id={ray_id}&alias={alias}"
        resp2 = scraper.get(redir_url, allow_redirects=False, timeout=12)
        loc = resp2.headers.get("Location")
        if not loc:
            return None, history

        article_url = urllib.parse.urljoin("https://app.khaddavi.net", loc)
        history.append((302, f"Khaddavi Interstitial Article: {article_url}"))

        for k, v in scraper.cookies.get_dict().items():
            cookies.append({
                "name": k,
                "value": v,
                "domain": ".khaddavi.net",
                "path": "/"
            })

    # Step C: Run headless Playwright solver in a thread-safe worker loop
    def _run_worker():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(_solve_khaddavi_playwright(article_url, cookies))
        finally:
            loop.close()

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
            target_url = ex.submit(_run_worker).result(timeout=40)
            if target_url:
                history.append((200, f"Bypass Khaddavi Countdown & Tokens -> {target_url}"))
                return target_url, history
    except Exception as e:
        history.append((500, f"Khaddavi Solver Timeout/Error: {e}"))

    return None, history


def extract_safelink_from_html(html_text: str, base_url: str) -> str:
    """
    Scrapes safelink HTML structures:
    1. Direct anchors to known file storage (MediaFire, Google Drive, Mega, TeraBox, Dropbox, etc.)
    2. Embedded base64 strings in variables or data attributes
    3. atob() Javascript redirect calls
    4. Dedicated getlink buttons
    """
    try:
        base_host = urllib.parse.urlparse(base_url).netloc.lower()
        soup = BeautifulSoup(html_text, "html.parser")

        # 1. Direct Anchor Tags to Known File Hosts (excluding current page host)
        anchors = soup.find_all("a", href=True)
        for a in anchors:
            href = a["href"].strip()
            if not href or href.startswith("#") or href.startswith("javascript:"):
                continue
            full_href = urllib.parse.urljoin(base_url, href)
            target_host = urllib.parse.urlparse(full_href).netloc.lower()

            if target_host != base_host and any(host in full_href.lower() for host in KNOWN_DESTINATIONS):
                return full_href

        # 2. Check data-attributes (data-url, data-href, data-link, data-target)
        for el in soup.find_all(True):
            for attr in ["data-url", "data-href", "data-link", "data-target"]:
                if el.has_attr(attr):
                    val = el[attr].strip()
                    dec = multi_decode_url(val)
                    if dec and any(host in dec.lower() for host in KNOWN_DESTINATIONS):
                        return dec
                    if dec and urllib.parse.urlparse(dec).netloc.lower() != base_host:
                        return dec

        # 3. Hidden input tags containing URLs or Base64
        for inp in soup.find_all("input", type="hidden"):
            val = inp.get("value", "").strip()
            if val:
                dec = multi_decode_url(val)
                if dec and (dec.startswith("http://") or dec.startswith("https://")):
                    if urllib.parse.urlparse(dec).netloc.lower() != base_host:
                        return dec

        # 4. Global Regex scan for Base64 encoded URLs in JS scripts (e.g. "aHR0cHM6Ly...")
        b64_matches = re.findall(r'["\'](aHR0c[a-zA-Z0-9+/=_-]{10,})["\']', html_text)
        for b64 in b64_matches:
            dec = multi_decode_url(b64)
            if dec and (dec.startswith("http://") or dec.startswith("https://")):
                if urllib.parse.urlparse(dec).netloc.lower() != base_host:
                    return dec

        # 5. Look for atob(...) JavaScript calls
        atob_matches = re.findall(r'atob\(["\']([a-zA-Z0-9+/=_-]{8,})["\']\)', html_text)
        for atob_val in atob_matches:
            dec = multi_decode_url(atob_val)
            if dec and (dec.startswith("http://") or dec.startswith("https://")):
                if urllib.parse.urlparse(dec).netloc.lower() != base_host:
                    return dec

        # 6. Specific Get-Link buttons
        for a in anchors:
            class_id = " ".join(a.get("class", [])) + " " + a.get("id", "")
            if re.search(r'(?:getlink|download|btn-link|safelink-btn|skip-ad|btn-main)', class_id, re.IGNORECASE):
                href = a["href"].strip()
                if href and not href.startswith("#") and not href.startswith("javascript:"):
                    full = urllib.parse.urljoin(base_url, href)
                    if urllib.parse.urlparse(full).netloc.lower() != base_host:
                        return full

    except Exception:
        pass

    return ""


def resolve_gdrive_link(url: str) -> str:
    """Convert Google Drive view/share URL to direct download URL."""
    match = re.search(r"/d/([a-zA-Z0-9_-]+)", url)
    if not match:
        match = re.search(r"id=([a-zA-Z0-9_-]+)", url)
    if match:
        file_id = match.group(1)
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    return url


def resolve_dropbox_link(url: str) -> str:
    """Convert Dropbox share link to direct download link."""
    if "dropbox.com" in url:
        return re.sub(r"[?&]dl=0", "?dl=1", url)
    return url


def bypass_and_unshorten_link(url: str, max_depth: int = 8) -> Tuple[str, List[Tuple[int, str]]]:
    """
    Follow redirect chains, decode hidden safelink parameters, unmask Safelinku / sfl.gl / Khaddavi / AdLinkFly,
    and convert cloud storage links directly to the real target URL.
    """
    history: List[Tuple[int, str]] = []
    current_url = url.strip()

    # Step 0: Initial query parameter / hash check before HTTP request
    param_target = extract_safelink_from_url_params(current_url)
    if param_target:
        history.append((307, f"Decoded Safelink Param -> {param_target}"))
        current_url = param_target

    # Cloud storage fast-paths
    if "drive.google.com" in current_url and "uc?export=download" not in current_url:
        return resolve_gdrive_link(current_url), history + [(200, "Google Drive Direct Download")]
    if "dropbox.com" in current_url and "dl=1" not in current_url:
        return resolve_dropbox_link(current_url), history + [(200, "Dropbox Direct Download")]

    # Specialized fast-path: SFL & Khaddavi networks
    low_url = current_url.lower()
    if any(k in low_url for k in ["sfl.gl", "sfl.ink", "khaddavi.net"]):
        khaddavi_target, khaddavi_hist = solve_khaddavi_safelink(current_url)
        if khaddavi_target:
            if "drive.google.com" in khaddavi_target:
                khaddavi_target = resolve_gdrive_link(khaddavi_target)
            elif "dropbox.com" in khaddavi_target:
                khaddavi_target = resolve_dropbox_link(khaddavi_target)
            return khaddavi_target, history + khaddavi_hist

    try:
        import cloudscraper
        session = cloudscraper.create_scraper(browser={"browser": "chrome", "platform": "windows", "desktop": True})
    except Exception:
        session = requests.Session()

    session.headers.update({
        "User-Agent": DEFAULT_USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,id;q=0.8",
    })

    depth = 0
    while depth < max_depth:
        depth += 1
        try:
            # Check URL parameter trick on current_url
            param_embedded = extract_safelink_from_url_params(current_url)
            if param_embedded and param_embedded != current_url:
                history.append((307, f"Unmasked Safelink Query -> {param_embedded}"))
                current_url = param_embedded
                continue

            # If current_url is already on a recognized storage host, stop!
            parsed_cur = urllib.parse.urlparse(current_url)
            if any(host in parsed_cur.netloc.lower() for host in KNOWN_DESTINATIONS):
                if "drive.google.com" in current_url:
                    current_url = resolve_gdrive_link(current_url)
                elif "dropbox.com" in current_url:
                    current_url = resolve_dropbox_link(current_url)
                history.append((200, f"Target Storage Reached: {current_url}"))
                return current_url, history

            response = session.get(current_url, allow_redirects=True, timeout=12)

            for resp in response.history:
                history.append((resp.status_code, resp.url))
            history.append((response.status_code, response.url))

            final_url = response.url
            html_content = response.text

            # If the response redirected us to a known destination host, stop!
            parsed_final = urllib.parse.urlparse(final_url)
            if any(host in parsed_final.netloc.lower() for host in KNOWN_DESTINATIONS):
                if "drive.google.com" in final_url:
                    final_url = resolve_gdrive_link(final_url)
                elif "dropbox.com" in final_url:
                    final_url = resolve_dropbox_link(final_url)
                return final_url, history

            # Check if page is an SFL / Khaddavi interstitial landing page
            if "khaddavi.net" in final_url.lower() or "khaddavi.net" in html_content:
                khaddavi_target, khaddavi_hist = solve_khaddavi_safelink(final_url, html_content)
                if khaddavi_target:
                    if "drive.google.com" in khaddavi_target:
                        khaddavi_target = resolve_gdrive_link(khaddavi_target)
                    elif "dropbox.com" in khaddavi_target:
                        khaddavi_target = resolve_dropbox_link(khaddavi_target)
                    return khaddavi_target, history + khaddavi_hist

            # 1. Automated Form / AdLinkFly / Safelinku solver (POST to /links/go)
            solved_adlink = solve_adlinkfly_and_forms(html_content, final_url, session)
            if solved_adlink and solved_adlink != final_url:
                history.append((308, f"Bypass Form Safelinku (/links/go) -> {solved_adlink}"))
                current_url = solved_adlink
                continue

            # 2. Check for Safelink HTML structures / atob scripts / storage links
            safelink_extracted = extract_safelink_from_html(html_content, final_url)
            if safelink_extracted and safelink_extracted != final_url:
                history.append((308, f"Safelink Unmasked Target -> {safelink_extracted}"))
                current_url = safelink_extracted
                continue

            # 3. Check for Meta-refresh redirect
            meta_match = re.search(
                r'<meta[^>]*http-equiv=["\']refresh["\'][^>]*content=["\'][^"\']*url=([^"\']+)["\']',
                html_content,
                re.IGNORECASE,
            )
            if meta_match:
                sub_url = meta_match.group(1).strip()
                sub_url = urllib.parse.urljoin(final_url, sub_url)
                if sub_url != final_url:
                    history.append((302, f"Meta-Refresh -> {sub_url}"))
                    current_url = sub_url
                    continue

            # 4. Check for JS window.location redirect
            js_match = re.search(r'window\.location(?:\.href)?\s*=\s*["\']([^"\']+)["\']', html_content, re.IGNORECASE)
            if js_match:
                sub_url = js_match.group(1).strip()
                sub_url = urllib.parse.urljoin(final_url, sub_url)
                if sub_url != final_url:
                    history.append((302, f"JS Redirect -> {sub_url}"))
                    current_url = sub_url
                    continue

            # 5. Check if final_url is Google Drive or Dropbox
            if "drive.google.com" in final_url:
                final_url = resolve_gdrive_link(final_url)
            elif "dropbox.com" in final_url:
                final_url = resolve_dropbox_link(final_url)

            return final_url, history

        except Exception as e:
            history.append((500, f"Error: {e}"))
            return current_url, history

    return current_url, history


def display_bypass_result(original_url: str):
    """Run bypass/unshorten and display formatted report in terminal."""
    console.print(f"\n[bold cyan]🔍 Memeriksa dan membypass rantai link:[/bold cyan] {original_url}\n")
    final_url, history = bypass_and_unshorten_link(original_url)

    table = Table(title="🔗 Hasil Bypass & Safelink Unmasker", expand=True)
    table.add_column("Langkah", width=10, style="dim")
    table.add_column("Status", width=10)
    table.add_column("URL / Redirect Target", ratio=1)

    for i, (status, link) in enumerate(history, 1):
        status_color = "green" if str(status).startswith("2") else ("yellow" if str(status).startswith("3") else "red")
        table.add_row(f"Hop #{i}", f"[{status_color}]{status}[/{status_color}]", link)

    console.print(table)
    console.print(f"\n[bold green]🎯 Direct Destination URL:[/bold green]")
    console.print(f"[bold bright_white on blue] {final_url} [/bold bright_white on blue]\n")
