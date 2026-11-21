"""
Tool #11: File Information
Tool #12: System Information
"""

import json
import mimetypes
import os
import platform
import shutil
import socket
import stat
import subprocess
from datetime import datetime
from pathlib import Path

from core.ui import Theme, ask, clear_screen, error, panel, pause, print_banner
from tools.hash_tool import hash_file


def format_bytes(num_bytes: int | float) -> str:
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"


def get_file_info(raw_path: str) -> dict:
    target = Path(raw_path).expanduser()
    if not target.exists():
        return {"exists": False, "error": f"Path tidak ditemukan: {target}"}

    st = target.stat()
    perms = stat.filemode(st.st_mode)
    mime_type, _ = mimetypes.guess_type(str(target))
    info_dict = {
        "exists": True,
        "name": target.name,
        "path": str(target.resolve()),
        "type": "Direktori" if target.is_dir() else "File",
        "size_bytes": st.st_size,
        "size_human": format_bytes(st.st_size),
        "permissions": perms,
        "modified": datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
        "created": datetime.fromtimestamp(st.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
        "mime_type": mime_type or ("inode/directory" if target.is_dir() else "application/octet-stream"),
        "sha256": hash_file(target, "sha256") if target.is_file() else "N/A",
    }
    return info_dict


def _run_getprop(prop_name: str) -> str:
    if shutil.which("getprop") is None:
        return "N/A"
    try:
        proc = subprocess.run(
            ["getprop", prop_name],
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )
        val = proc.stdout.strip()
        return val if val else "N/A"
    except Exception:
        return "N/A"


def _get_battery_status() -> str:
    if shutil.which("termux-battery-status") is not None:
        try:
            proc = subprocess.run(
                ["termux-battery-status"],
                capture_output=True,
                text=True,
                timeout=4,
                check=False,
            )
            if proc.returncode == 0 and proc.stdout.strip():
                data = json.loads(proc.stdout)
                pct = data.get("percentage")
                status = data.get("status", "")
                if pct is not None:
                    return f"{pct}% ({status})" if status else f"{pct}%"
        except Exception:
            pass

    cap_path = Path("/sys/class/power_supply/battery/capacity")
    stat_path = Path("/sys/class/power_supply/battery/status")
    try:
        if cap_path.exists():
            cap = cap_path.read_text(encoding="utf-8").strip()
            st = stat_path.read_text(encoding="utf-8").strip() if stat_path.exists() else ""
            return f"{cap}% ({st})" if st else f"{cap}%"
    except OSError:
        pass

    return "N/A"


def _get_ram_info() -> str:
    meminfo = Path("/proc/meminfo")
    if meminfo.exists():
        try:
            values: dict[str, int] = {}
            for line in meminfo.read_text(encoding="utf-8").splitlines():
                parts = line.split()
                if len(parts) >= 2 and parts[0].rstrip(":") in ("MemTotal", "MemAvailable"):
                    values[parts[0].rstrip(":")] = int(parts[1]) * 1024
            if "MemTotal" in values and "MemAvailable" in values:
                total = values["MemTotal"]
                avail = values["MemAvailable"]
                used = max(0, total - avail)
                return f"{format_bytes(used)} / {format_bytes(total)} (Tersedia: {format_bytes(avail)})"
        except Exception:
            pass
    return "N/A"


def _get_storage_info() -> str:
    try:
        usage = shutil.disk_usage(Path.home())
        return f"{format_bytes(usage.used)} / {format_bytes(usage.total)} (Bebas: {format_bytes(usage.free)})"
    except OSError:
        return "N/A"


def _check_internet() -> str:
    try:
        with socket.create_connection(("1.1.1.1", 53), timeout=3):
            return "Terhubung (Online)"
    except OSError:
        return "Offline / Tidak Terjangkau"


def get_system_info() -> dict[str, str]:
    manufacturer = _run_getprop("ro.product.manufacturer")
    model = _run_getprop("ro.product.model")
    if manufacturer != "N/A" and model != "N/A":
        device = f"{manufacturer} {model}"
    elif model != "N/A":
        device = model
    else:
        device = platform.node() or "N/A"

    android_ver = _run_getprop("ro.build.version.release")
    android_sdk = _run_getprop("ro.build.version.sdk")
    if android_ver != "N/A" and android_sdk != "N/A":
        android_str = f"Android {android_ver} (SDK {android_sdk})"
    elif android_ver != "N/A":
        android_str = f"Android {android_ver}"
    else:
        android_str = "N/A"

    termux_ver = os.getenv("TERMUX_VERSION", "").strip()
    termux_prefix = os.getenv("PREFIX", "").strip()
    if termux_ver:
        termux_str = f"Termux {termux_ver}"
    elif "com.termux" in termux_prefix:
        termux_str = f"Aktif ({termux_prefix})"
    else:
        termux_str = "N/A"

    return {
        "device": device,
        "os_kernel": f"{platform.system()} {platform.release()} ({platform.machine()})",
        "android_version": android_str,
        "python_version": f"{platform.python_version()} ({platform.python_implementation()})",
        "battery": _get_battery_status(),
        "ram": _get_ram_info(),
        "storage": _get_storage_info(),
        "termux": termux_str,
        "internet": _check_internet(),
    }


def render_system_info() -> None:
    info_data = get_system_info()
    lines = [
        f"{Theme.ELECTRIC_BLUE}Perangkat       :{Theme.RESET} {Theme.WHITE}{info_data['device']}{Theme.RESET}",
        f"{Theme.ELECTRIC_BLUE}OS / Kernel     :{Theme.RESET} {Theme.SILVER}{info_data['os_kernel']}{Theme.RESET}",
        f"{Theme.ELECTRIC_BLUE}Versi Android   :{Theme.RESET} {Theme.WHITE}{info_data['android_version']}{Theme.RESET}",
        f"{Theme.ELECTRIC_BLUE}Versi Python    :{Theme.RESET} {Theme.GREEN}{info_data['python_version']}{Theme.RESET}",
        f"{Theme.ELECTRIC_BLUE}Status Baterai  :{Theme.RESET} {Theme.WHITE}{info_data['battery']}{Theme.RESET}",
        f"{Theme.ELECTRIC_BLUE}Memori (RAM)    :{Theme.RESET} {Theme.WHITE}{info_data['ram']}{Theme.RESET}",
        f"{Theme.ELECTRIC_BLUE}Penyimpanan     :{Theme.RESET} {Theme.WHITE}{info_data['storage']}{Theme.RESET}",
        f"{Theme.ELECTRIC_BLUE}Info Termux     :{Theme.RESET} {Theme.NEON_PURPLE}{info_data['termux']}{Theme.RESET}",
        f"{Theme.ELECTRIC_BLUE}Koneksi Internet:{Theme.RESET} {Theme.WHITE}{info_data['internet']}{Theme.RESET}",
    ]
    panel("SYSTEM INFORMATION — NOBAX DEX", lines, accent="purple")


def run_file_info_ui() -> None:
    clear_screen()
    print_banner()
    raw_path = ask("Masukkan path file atau folder")
    if not raw_path:
        error("Path tidak boleh kosong.")
        pause()
        return

    res = get_file_info(raw_path)
    if not res["exists"]:
        error(res["error"])
        pause()
        return

    lines = [
        f"{Theme.ELECTRIC_BLUE}Nama        :{Theme.RESET} {Theme.WHITE}{res['name']}{Theme.RESET}",
        f"{Theme.ELECTRIC_BLUE}Path        :{Theme.RESET} {res['path']}",
        f"{Theme.ELECTRIC_BLUE}Tipe        :{Theme.RESET} {res['type']} ({res['mime_type']})",
        f"{Theme.ELECTRIC_BLUE}Ukuran      :{Theme.RESET} {res['size_human']} ({res['size_bytes']} bytes)",
        f"{Theme.ELECTRIC_BLUE}Permission  :{Theme.RESET} {res['permissions']}",
        f"{Theme.ELECTRIC_BLUE}Diubah      :{Theme.RESET} {res['modified']}",
        f"{Theme.ELECTRIC_BLUE}SHA-256     :{Theme.RESET} {Theme.GREEN}{res['sha256']}{Theme.RESET}",
    ]
    panel("FILE INFORMATION", lines, accent="blue")
    pause()
