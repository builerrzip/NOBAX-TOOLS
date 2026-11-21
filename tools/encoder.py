"""
Tool #3: Text Encoder
Tool #14: Text Converter
"""

import base64
import codecs
import html
import re
from urllib.parse import quote

from core.ui import Theme, ask, clear_screen, error, panel, pause, print_banner


def encode_text(text: str, method: str) -> str:
    m = method.strip().lower()
    raw = text.encode("utf-8")
    if m == "base64":
        return base64.b64encode(raw).decode("ascii")
    if m == "base32":
        return base64.b32encode(raw).decode("ascii")
    if m == "url":
        return quote(text, safe="")
    if m == "hex":
        return raw.hex()
    if m == "binary":
        return " ".join(f"{b:08b}" for b in raw)
    if m == "rot13":
        return codecs.encode(text, "rot_13")
    if m == "html":
        return html.escape(text, quote=True)
    raise ValueError(f"Metode encoding tidak didukung: {method}")


def convert_text(text: str, mode: str) -> str:
    m = mode.strip().lower()
    if m == "upper":
        return text.upper()
    if m == "lower":
        return text.lower()
    if m == "title":
        return text.title()
    if m == "sentence":
        return text.capitalize()
    if m == "reverse":
        return text[::-1]

    words = [w for w in re.split(r"[\s_\-]+", text.strip()) if w]
    if m == "snake":
        return "_".join(w.lower() for w in words)
    if m == "kebab":
        return "-".join(w.lower() for w in words)
    if m == "camel":
        if not words:
            return ""
        return words[0].lower() + "".join(w.capitalize() for w in words[1:])
    if m == "pascal":
        return "".join(w.capitalize() for w in words)
    raise ValueError(f"Mode konversi tidak didukung: {mode}")


def run_text_encoder_ui() -> None:
    clear_screen()
    print_banner()
    panel(
        "TEXT ENCODER",
        [
            "[1] Base64",
            "[2] Base32",
            "[3] URL Encode",
            "[4] Hexadecimal",
            "[5] Binary (8-bit)",
            "[6] ROT13",
            "[7] HTML Entities",
        ],
        accent="purple",
    )
    choice = ask("Pilih metode encoding [1-7]")
    methods = {
        "1": "base64",
        "2": "base32",
        "3": "url",
        "4": "hex",
        "5": "binary",
        "6": "rot13",
        "7": "html",
    }
    method = methods.get(choice)
    if not method:
        error("Pilihan metode tidak valid.")
        pause()
        return

    text = ask("Masukkan teks yang akan di-encode")
    if not text:
        error("Teks input tidak boleh kosong.")
        pause()
        return

    encoded = encode_text(text, method)
    panel(
        f"HASIL ENCODE ({method.upper()})",
        [
            f"{Theme.ELECTRIC_BLUE}Input  :{Theme.RESET} {text}",
            f"{Theme.ELECTRIC_BLUE}Output :{Theme.RESET} {Theme.GREEN}{encoded}{Theme.RESET}",
        ],
        accent="blue",
    )
    pause()


def run_text_converter_ui() -> None:
    clear_screen()
    print_banner()
    panel(
        "TEXT CONVERTER",
        [
            "[1] UPPERCASE",
            "[2] lowercase",
            "[3] Title Case",
            "[4] snake_case",
            "[5] kebab-case",
            "[6] camelCase",
            "[7] PascalCase",
            "[8] Reverse Text",
        ],
        accent="blue",
    )
    choice = ask("Pilih format konversi [1-8]")
    modes = {
        "1": "upper",
        "2": "lower",
        "3": "title",
        "4": "snake",
        "5": "kebab",
        "6": "camel",
        "7": "pascal",
        "8": "reverse",
    }
    mode = modes.get(choice)
    if not mode:
        error("Pilihan konversi tidak valid.")
        pause()
        return

    text = ask("Masukkan teks input")
    if not text:
        error("Teks input tidak boleh kosong.")
        pause()
        return

    converted = convert_text(text, mode)
    panel(
        f"HASIL TEXT CONVERTER ({mode.upper()})",
        [
            f"{Theme.ELECTRIC_BLUE}Hasil    :{Theme.RESET} {Theme.GREEN}{converted}{Theme.RESET}",
            f"{Theme.ELECTRIC_BLUE}Statistik:{Theme.RESET} {len(text)} karakter | {len(text.split())} kata",
        ],
        accent="purple",
    )
    pause()
