"""
Tool #4: Text Decoder
"""

import base64
import binascii
import codecs
import html
from urllib.parse import unquote

from core.ui import Theme, ask, clear_screen, error, panel, pause, print_banner


def decode_text(encoded_text: str, method: str) -> str:
    m = method.strip().lower()
    cleaned = encoded_text.strip()
    try:
        if m == "base64":
            padded = cleaned + "=" * (-len(cleaned) % 4)
            return base64.b64decode(padded.encode("ascii")).decode("utf-8")
        if m == "base32":
            padded = cleaned.upper() + "=" * (-len(cleaned) % 8)
            return base64.b32decode(padded.encode("ascii")).decode("utf-8")
        if m == "url":
            return unquote(cleaned)
        if m == "hex":
            compact = cleaned.replace(" ", "")
            return bytes.fromhex(compact).decode("utf-8")
        if m == "binary":
            bits = cleaned.split()
            if len(bits) == 1 and len(bits[0]) % 8 == 0:
                bits = [bits[0][i : i + 8] for i in range(0, len(bits[0]), 8)]
            raw = bytes(int(b, 2) for b in bits)
            return raw.decode("utf-8")
        if m == "rot13":
            return codecs.decode(encoded_text, "rot_13")
        if m == "html":
            return html.unescape(encoded_text)
    except (binascii.Error, ValueError, UnicodeDecodeError) as exc:
        raise ValueError(f"Data tidak valid untuk dekode {method.upper()}: {exc}") from exc

    raise ValueError(f"Metode decoding tidak didukung: {method}")


def run_text_decoder_ui() -> None:
    clear_screen()
    print_banner()
    panel(
        "TEXT DECODER",
        [
            "[1] Base64 Decode",
            "[2] Base32 Decode",
            "[3] URL Decode",
            "[4] Hexadecimal Decode",
            "[5] Binary Decode",
            "[6] ROT13 Decode",
            "[7] HTML Entities Decode",
        ],
        accent="purple",
    )
    choice = ask("Pilih metode decoding [1-7]")
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

    raw_in = ask("Masukkan teks ter-encode")
    if not raw_in:
        error("Input tidak boleh kosong.")
        pause()
        return

    try:
        decoded = decode_text(raw_in, method)
        panel(
            f"HASIL DECODE ({method.upper()})",
            [
                f"{Theme.ELECTRIC_BLUE}Input  :{Theme.RESET} {raw_in}",
                f"{Theme.ELECTRIC_BLUE}Output :{Theme.RESET} {Theme.GREEN}{decoded}{Theme.RESET}",
            ],
            accent="blue",
        )
    except ValueError as exc:
        error(str(exc))
    pause()
