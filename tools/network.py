"""
Tool #7: IP Information
Tool #8: DNS Lookup
Tool #9: Website Status Checker
Tool #13: URL Parser
"""

import json
import shutil
import socket
import subprocess
import time
import urllib.error
import urllib.request
from urllib.parse import parse_qs, urlparse

from core.ui import Theme, ask, clear_screen, error, panel, pause, print_banner, spinner


def get_local_ip() -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except OSError:
        return "N/A"


def get_ip_info(target_ip: str = "") -> dict:
    local_ip = get_local_ip()
    query = target_ip.strip()
    endpoint = f"http://ip-api.com/json/{query}" if query else "http://ip-api.com/json/"
    try:
        req = urllib.request.Request(
            endpoint,
            headers={"User-Agent": "NOBAX-TOOLS/1.0"},
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        if data.get("status") == "success":
            return {
                "success": True,
                "local_ip": local_ip,
                "public_ip": data.get("query", "N/A"),
                "country": data.get("country", "N/A"),
                "region": data.get("regionName", "N/A"),
                "city": data.get("city", "N/A"),
                "isp": data.get("isp", "N/A"),
                "org": data.get("org", "N/A"),
                "as": data.get("as", "N/A"),
                "timezone": data.get("timezone", "N/A"),
            }
        return {
            "success": False,
            "local_ip": local_ip,
            "error": data.get("message", "Gagal mengambil info IP."),
        }
    except Exception as exc:
        return {
            "success": False,
            "local_ip": local_ip,
            "error": f"Tidak dapat mengambil info IP publik ({exc}).",
        }


def dns_lookup(domain: str) -> dict:
    clean_domain = domain.strip().lower()
    if clean_domain.startswith(("http://", "https://")):
        clean_domain = urlparse(clean_domain).hostname or clean_domain

    if not clean_domain:
        return {"success": False, "error": "Domain tidak boleh kosong."}

    ipv4: list[str] = []
    ipv6: list[str] = []
    try:
        infos = socket.getaddrinfo(clean_domain, None)
        for family, _, _, _, sockaddr in infos:
            ip_addr = sockaddr[0]
            if family == socket.AF_INET and ip_addr not in ipv4:
                ipv4.append(ip_addr)
            elif family == socket.AF_INET6 and ip_addr not in ipv6:
                ipv6.append(ip_addr)
    except socket.gaierror as exc:
        return {"success": False, "domain": clean_domain, "error": f"DNS tidak ditemukan: {exc}"}

    ns_raw = ""
    if shutil.which("nslookup"):
        try:
            proc = subprocess.run(
                ["nslookup", clean_domain],
                capture_output=True,
                text=True,
                timeout=6,
                check=False,
            )
            ns_raw = proc.stdout.strip()
        except Exception:
            ns_raw = ""

    return {
        "success": True,
        "domain": clean_domain,
        "ipv4": ipv4,
        "ipv6": ipv6,
        "raw": ns_raw,
    }


def check_website_status(raw_url: str) -> dict:
    url = raw_url.strip()
    if not url:
        return {"success": False, "error": "URL tidak boleh kosong."}
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    start = time.perf_counter()
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Linux; Android 14) NOBAX-TOOLS/1.0"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            elapsed_ms = round((time.perf_counter() - start) * 1000, 1)
            return {
                "success": True,
                "url": resp.geturl(),
                "status_code": resp.status,
                "reason": resp.reason,
                "latency_ms": elapsed_ms,
                "server": resp.headers.get("Server", "N/A"),
                "content_type": resp.headers.get("Content-Type", "N/A"),
            }
    except urllib.error.HTTPError as exc:
        elapsed_ms = round((time.perf_counter() - start) * 1000, 1)
        return {
            "success": True,
            "url": url,
            "status_code": exc.code,
            "reason": exc.reason,
            "latency_ms": elapsed_ms,
            "server": exc.headers.get("Server", "N/A") if exc.headers else "N/A",
            "content_type": exc.headers.get("Content-Type", "N/A") if exc.headers else "N/A",
        }
    except Exception as exc:
        return {"success": False, "url": url, "error": f"Website tidak dapat dijangkau: {exc}"}


def parse_url_details(raw_url: str) -> dict:
    candidate = raw_url.strip()
    if not candidate:
        return {"valid": False, "error": "URL tidak boleh kosong."}
    if "://" not in candidate:
        candidate = "https://" + candidate

    parsed = urlparse(candidate)
    if not parsed.hostname:
        return {"valid": False, "error": "Hostname tidak ditemukan pada URL."}

    query_params = {k: v for k, v in parse_qs(parsed.query).items()}
    return {
        "valid": True,
        "full_url": candidate,
        "scheme": parsed.scheme or "N/A",
        "hostname": parsed.hostname or "N/A",
        "port": str(parsed.port) if parsed.port else "Default",
        "path": parsed.path or "/",
        "query_raw": parsed.query or "N/A",
        "query_params": query_params,
        "fragment": parsed.fragment or "N/A",
    }


def run_ip_info_ui() -> None:
    clear_screen()
    print_banner()
    target = ask("Masukkan IP target (kosongkan untuk IP publik perangkat ini)")
    spinner("Mengambil informasi IP...", duration=0.4)
    res = get_ip_info(target)
    if res["success"]:
        lines = [
            f"{Theme.ELECTRIC_BLUE}IP Lokal   :{Theme.RESET} {res['local_ip']}",
            f"{Theme.ELECTRIC_BLUE}IP Publik  :{Theme.RESET} {Theme.GREEN}{res['public_ip']}{Theme.RESET}",
            f"{Theme.ELECTRIC_BLUE}Negara     :{Theme.RESET} {res['country']}",
            f"{Theme.ELECTRIC_BLUE}Wilayah    :{Theme.RESET} {res['region']} — {res['city']}",
            f"{Theme.ELECTRIC_BLUE}ISP        :{Theme.RESET} {res['isp']}",
            f"{Theme.ELECTRIC_BLUE}Organisasi :{Theme.RESET} {res['org']}",
            f"{Theme.ELECTRIC_BLUE}ASN        :{Theme.RESET} {res['as']}",
            f"{Theme.ELECTRIC_BLUE}Zona Waktu :{Theme.RESET} {res['timezone']}",
        ]
        panel("IP INFORMATION", lines, accent="blue")
    else:
        error(res["error"])
        panel("LOCAL NETWORK", [f"IP Lokal: {res['local_ip']}"], accent="purple")
    pause()


def run_dns_lookup_ui() -> None:
    clear_screen()
    print_banner()
    domain = ask("Masukkan nama domain (cth: github.com)")
    spinner(f"Melakukan DNS Lookup untuk {domain}...", duration=0.35)
    res = dns_lookup(domain)
    if res["success"]:
        lines = [
            f"{Theme.ELECTRIC_BLUE}Domain :{Theme.RESET} {Theme.WHITE}{res['domain']}{Theme.RESET}",
            f"{Theme.ELECTRIC_BLUE}IPv4   :{Theme.RESET} {Theme.GREEN}{', '.join(res['ipv4']) or 'N/A'}{Theme.RESET}",
            f"{Theme.ELECTRIC_BLUE}IPv6   :{Theme.RESET} {Theme.SILVER}{', '.join(res['ipv6']) or 'N/A'}{Theme.RESET}",
        ]
        panel("DNS LOOKUP RESULT", lines, accent="purple")
    else:
        error(res["error"])
    pause()


def run_website_status_ui() -> None:
    clear_screen()
    print_banner()
    url = ask("Masukkan URL website (cth: https://github.com)")
    spinner(f"Memeriksa status {url}...", duration=0.35)
    res = check_website_status(url)
    if res["success"]:
        code = res["status_code"]
        color = Theme.GREEN if 200 <= code < 400 else Theme.YELLOW
        lines = [
            f"{Theme.ELECTRIC_BLUE}URL Final    :{Theme.RESET} {res['url']}",
            f"{Theme.ELECTRIC_BLUE}HTTP Status  :{Theme.RESET} {color}{code} {res['reason']}{Theme.RESET}",
            f"{Theme.ELECTRIC_BLUE}Latensi      :{Theme.RESET} {res['latency_ms']} ms",
            f"{Theme.ELECTRIC_BLUE}Server       :{Theme.RESET} {res['server']}",
            f"{Theme.ELECTRIC_BLUE}Content-Type :{Theme.RESET} {res['content_type']}",
        ]
        panel("WEBSITE STATUS CHECKER", lines, accent="blue")
    else:
        error(res["error"])
    pause()


def run_url_parser_ui() -> None:
    clear_screen()
    print_banner()
    raw_url = ask("Masukkan URL lengkap untuk dianalisis")
    res = parse_url_details(raw_url)
    if not res["valid"]:
        error(res["error"])
        pause()
        return

    lines = [
        f"{Theme.ELECTRIC_BLUE}Scheme   :{Theme.RESET} {res['scheme']}",
        f"{Theme.ELECTRIC_BLUE}Hostname :{Theme.RESET} {Theme.GREEN}{res['hostname']}{Theme.RESET}",
        f"{Theme.ELECTRIC_BLUE}Port     :{Theme.RESET} {res['port']}",
        f"{Theme.ELECTRIC_BLUE}Path     :{Theme.RESET} {res['path']}",
        f"{Theme.ELECTRIC_BLUE}Fragment :{Theme.RESET} {res['fragment']}",
        f"{Theme.ELECTRIC_BLUE}Query    :{Theme.RESET} {res['query_raw']}",
    ]
    if res["query_params"]:
        lines.append(f"{Theme.NEON_PURPLE}Parameter Terurai:{Theme.RESET}")
        for k, vals in res["query_params"].items():
            lines.append(f"  • {k} = {', '.join(vals)}")
    panel("URL PARSER RESULT", lines, accent="purple")
    pause()
