"""
Browser Launcher untuk Android Termux & Cross-Platform.
"""

import json
import os
import re
import shutil
import subprocess
import webbrowser
from pathlib import Path
from urllib.parse import urlparse

from core.ui import (
    Theme,
    ask,
    clear_screen,
    error,
    panel,
    pause,
    print_banner,
    spinner,
    success,
)

UNSAFE_CHARS_RE = re.compile(r"[\s`$;|&<>\"'\\\x00-\x1f]")


class BrowserLauncher:
    def __init__(self, bookmarks_path: Path | None = None) -> None:
        root = Path(__file__).resolve().parent.parent
        self.bookmarks_file = bookmarks_path or (root / "browser" / "websites.json")
        self.bookmarks_file.parent.mkdir(parents=True, exist_ok=True)
        self.favorites: dict[str, str] = self._load_favorites()

    def _load_favorites(self) -> dict[str, str]:
        defaults = {
            "youtube": "https://www.youtube.com",
            "google": "https://www.google.com",
            "github": "https://github.com",
            "chatgpt": "https://chatgpt.com",
            "spotify": "https://open.spotify.com",
        }
        if self.bookmarks_file.exists():
            try:
                data = json.loads(self.bookmarks_file.read_text(encoding="utf-8"))
                if isinstance(data, dict) and data:
                    return {str(k).lower(): str(v) for k, v in data.items()}
            except (json.JSONDecodeError, OSError):
                pass
        self._save_favorites(defaults)
        return defaults

    def _save_favorites(self, data: dict[str, str]) -> None:
        self.bookmarks_file.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def resolve_target(self, raw_target: str) -> str:
        cleaned = raw_target.strip()
        key = cleaned.lower()
        if key in self.favorites:
            return self.favorites[key]
        return cleaned

    def validate_url(self, raw_url: str) -> tuple[bool, str, str]:
        candidate = self.resolve_target(raw_url)
        if not candidate:
            return False, "", "URL atau nama website tidak boleh kosong."

        if UNSAFE_CHARS_RE.search(candidate):
            return False, "", "URL mengandung karakter tidak valid atau spasi."

        if not candidate.startswith(("http://", "https://")):
            if "://" in candidate:
                return False, "", "Hanya protokol http:// dan https:// yang diizinkan."
            candidate = "https://" + candidate

        parsed = urlparse(candidate)
        if parsed.scheme not in ("http", "https"):
            return False, "", "Protokol URL harus http atau https."

        hostname = parsed.hostname or ""
        if not hostname or "." not in hostname and hostname != "localhost":
            return False, "", f"Domain tidak valid: '{hostname or candidate}'."

        return True, candidate, ""

    @staticmethod
    def is_android_termux() -> bool:
        prefix = os.getenv("PREFIX", "")
        return (
            "com.termux" in prefix
            or bool(os.getenv("TERMUX_VERSION"))
            or shutil.which("am") is not None
        )

    def build_android_intents(self, url: str, prefer_chrome: bool = True) -> list[tuple[str, list[str]]]:
        intents: list[tuple[str, list[str]]] = []
        if prefer_chrome:
            intents.append(
                (
                    "Google Chrome (Android Component Intent)",
                    [
                        "am",
                        "start",
                        "-n",
                        "com.android.chrome/com.google.android.apps.chrome.Main",
                        "-a",
                        "android.intent.action.VIEW",
                        "-d",
                        url,
                    ],
                )
            )
            intents.append(
                (
                    "Google Chrome (Package Intent)",
                    [
                        "am",
                        "start",
                        "-a",
                        "android.intent.action.VIEW",
                        "-p",
                        "com.android.chrome",
                        "-d",
                        url,
                    ],
                )
            )

        intents.append(
            (
                "Android Default Browser Intent",
                [
                    "am",
                    "start",
                    "-a",
                    "android.intent.action.VIEW",
                    "-d",
                    url,
                ],
            )
        )
        return intents

    def open_url(self, target: str, prefer_chrome: bool = True) -> dict:
        valid, normalized_url, err_msg = self.validate_url(target)
        if not valid:
            return {"success": False, "url": target, "method": "none", "message": err_msg}

        if self.is_android_termux() and shutil.which("am") is not None:
            for label, cmd in self.build_android_intents(normalized_url, prefer_chrome=prefer_chrome):
                try:
                    proc = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=8,
                        check=False,
                    )
                    stderr_low = (proc.stderr or "").lower()
                    if proc.returncode == 0 and "error:" not in stderr_low and "unable to resolve" not in stderr_low:
                        return {
                            "success": True,
                            "url": normalized_url,
                            "method": label,
                            "message": f"Membuka {normalized_url} melalui {label}.",
                        }
                except Exception:
                    continue

        if shutil.which("termux-open-url") is not None:
            try:
                proc = subprocess.run(
                    ["termux-open-url", normalized_url],
                    capture_output=True,
                    text=True,
                    timeout=8,
                    check=False,
                )
                if proc.returncode == 0:
                    return {
                        "success": True,
                        "url": normalized_url,
                        "method": "termux-open-url",
                        "message": f"Membuka {normalized_url} melalui termux-open-url.",
                    }
            except Exception:
                pass

        try:
            opened = webbrowser.open(normalized_url, new=2)
            if opened:
                return {
                    "success": True,
                    "url": normalized_url,
                    "method": "Python webbrowser",
                    "message": f"Membuka {normalized_url} di browser sistem.",
                }
        except Exception as exc:
            return {
                "success": False,
                "url": normalized_url,
                "method": "none",
                "message": f"Gagal meluncurkan browser: {exc}",
            }

        return {
            "success": False,
            "url": normalized_url,
            "method": "none",
            "message": f"Tidak ditemukan browser yang tersedia untuk membuka {normalized_url}.",
        }

    def add_favorite(self, name: str, raw_url: str) -> tuple[bool, str]:
        alias = name.strip().lower()
        if not alias or len(alias) > 30:
            return False, "Nama favorit harus 1-30 karakter."
        valid, normalized_url, err_msg = self.validate_url(raw_url)
        if not valid:
            return False, err_msg
        self.favorites[alias] = normalized_url
        self._save_favorites(self.favorites)
        return True, f"Website favorit '{alias}' ({normalized_url}) disimpan."

    def remove_favorite(self, name: str) -> tuple[bool, str]:
        alias = name.strip().lower()
        if alias not in self.favorites:
            return False, f"Favorit '{alias}' tidak ditemukan."
        del self.favorites[alias]
        self._save_favorites(self.favorites)
        return True, f"Favorit '{alias}' dihapus."

    def interactive_menu(self, prefer_chrome: bool = True) -> None:
        while True:
            clear_screen()
            print_banner()

            fav_keys = list(self.favorites.keys())
            lines = [
                f"{Theme.MUTED}Catatan: Membuka URL web di Google Chrome Android via Android Intent.{Theme.RESET}",
                "",
            ]
            for idx, key in enumerate(fav_keys, 1):
                lines.append(
                    f"{Theme.NEON_PURPLE}[{idx:02d}]{Theme.RESET} "
                    f"{Theme.BOLD}{Theme.WHITE}{key.upper():<14}{Theme.RESET} "
                    f"{Theme.ELECTRIC_BLUE}{self.favorites[key]}{Theme.RESET}"
                )
            lines.extend(
                [
                    "",
                    f"{Theme.NEON_PURPLE}[A]{Theme.RESET}  {Theme.WHITE}Buka Website Custom (URL){Theme.RESET}",
                    f"{Theme.NEON_PURPLE}[B]{Theme.RESET}  {Theme.WHITE}Tambah Website Favorit{Theme.RESET}",
                    f"{Theme.NEON_PURPLE}[C]{Theme.RESET}  {Theme.WHITE}Hapus Website Favorit{Theme.RESET}",
                    f"{Theme.RED}[0]{Theme.RESET}  {Theme.SILVER}Kembali ke Menu Utama{Theme.RESET}",
                ]
            )
            panel("BROWSER CENTER — CHROME ANDROID LAUNCHER", lines, accent="blue")
            choice = ask("nobax@browser:~")

            if choice in ("0", "00"):
                break
            elif choice.isdigit() and 1 <= int(choice) <= len(fav_keys):
                target_key = fav_keys[int(choice) - 1]
                spinner(f"Meluncurkan {target_key.upper()} di Chrome...", duration=0.35)
                res = self.open_url(target_key, prefer_chrome=prefer_chrome)
                success(res["message"]) if res["success"] else error(res["message"])
                pause()
            elif choice.lower() == "a":
                custom_url = ask("Masukkan URL (cth: https://docs.python.org)")
                if custom_url:
                    spinner("Memvalidasi & membuka URL...", duration=0.3)
                    res = self.open_url(custom_url, prefer_chrome=prefer_chrome)
                    success(res["message"]) if res["success"] else error(res["message"])
                pause()
            elif choice.lower() == "b":
                alias = ask("Nama singkat favorit (cth: reddit)")
                url_val = ask("URL lengkap (cth: https://www.reddit.com)")
                ok, msg = self.add_favorite(alias, url_val)
                success(msg) if ok else error(msg)
                pause()
            elif choice.lower() == "c":
                alias = ask("Nama favorit yang ingin dihapus")
                ok, msg = self.remove_favorite(alias)
                success(msg) if ok else error(msg)
                pause()
            else:
                res = self.open_url(choice, prefer_chrome=prefer_chrome)
                success(res["message"]) if res["success"] else error(res["message"])
                pause()
