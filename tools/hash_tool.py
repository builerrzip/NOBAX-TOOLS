"""
Tool #6: Hash Generator
"""

import hashlib
from pathlib import Path

from core.ui import Theme, ask, clear_screen, error, panel, pause, print_banner

SUPPORTED_ALGOS = ["md5", "sha1", "sha224", "sha256", "sha384", "sha512", "blake2b"]


def hash_text(text: str, algo: str = "sha256") -> str:
    key = algo.strip().lower()
    if key not in SUPPORTED_ALGOS:
        raise ValueError(f"Algoritma hash tidak didukung: {algo}")
    h = hashlib.new(key)
    h.update(text.encode("utf-8"))
    return h.hexdigest()


def hash_all_text(text: str) -> dict[str, str]:
    return {algo.upper(): hash_text(text, algo) for algo in SUPPORTED_ALGOS}


def hash_file(file_path: Path, algo: str = "sha256") -> str:
    key = algo.strip().lower()
    if key not in SUPPORTED_ALGOS:
        raise ValueError(f"Algoritma hash tidak didukung: {algo}")
    h = hashlib.new(key)
    with file_path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def run_hash_generator_ui() -> None:
    clear_screen()
    print_banner()
    panel(
        "HASH GENERATOR",
        [
            "[1] Hash Teks (Semua Algoritma: MD5, SHA-1, SHA-256, SHA-512, BLAKE2b)",
            "[2] Hash File (SHA-256 & MD5)",
        ],
        accent="purple",
    )
    choice = ask("Pilih sumber input [1-2]")
    if choice == "2":
        raw_path = ask("Masukkan path file")
        target = Path(raw_path).expanduser()
        if not target.is_file():
            error("File tidak ditemukan.")
            pause()
            return
        try:
            lines = [
                f"{Theme.ELECTRIC_BLUE}File   :{Theme.RESET} {target.name}",
                f"{Theme.ELECTRIC_BLUE}MD5    :{Theme.RESET} {Theme.GREEN}{hash_file(target, 'md5')}{Theme.RESET}",
                f"{Theme.ELECTRIC_BLUE}SHA256 :{Theme.RESET} {Theme.GREEN}{hash_file(target, 'sha256')}{Theme.RESET}",
            ]
            panel("FILE CHECKSUM RESULT", lines, accent="blue")
        except OSError as exc:
            error(f"Gagal membaca file: {exc}")
    else:
        txt = ask("Masukkan teks yang akan di-hash")
        if not txt:
            error("Teks tidak boleh kosong.")
            pause()
            return
        hashes = hash_all_text(txt)
        lines = [
            f"{Theme.ELECTRIC_BLUE}{k:<8}:{Theme.RESET} {Theme.GREEN}{v}{Theme.RESET}"
            for k, v in hashes.items()
        ]
        panel("CRYPTOGRAPHIC HASH RESULT", lines, accent="blue")
    pause()
