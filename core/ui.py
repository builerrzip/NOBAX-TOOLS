"""
Terminal UI Engine untuk NOBAX TOOLS.
Tema: Hitam Pekat, Ungu Neon, dan Biru Elektrik dengan layout responsif layar HP Termux.
"""

import os
import re
import shutil
import sys
import time
from pathlib import Path

try:
    import colorama
    colorama.init(autoreset=True)
except ImportError:
    pass


class Theme:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    BG_DARK = "\033[48;5;232m"
    PURPLE = "\033[38;5;135m"
    NEON_PURPLE = "\033[38;5;165m"
    DEEP_PURPLE = "\033[38;5;93m"
    BLUE = "\033[38;5;39m"
    ELECTRIC_BLUE = "\033[38;5;45m"
    WHITE = "\033[38;5;255m"
    SILVER = "\033[38;5;250m"
    MUTED = "\033[38;5;242m"
    GREEN = "\033[38;5;48m"
    YELLOW = "\033[38;5;220m"
    RED = "\033[38;5;197m"


ANSI_ESCAPE_RE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


def strip_ansi(text: str) -> str:
    return ANSI_ESCAPE_RE.sub("", text)


def term_width() -> int:
    """Mendapatkan lebar terminal secara dinamis dan responsif untuk layar HP."""
    cols = shutil.get_terminal_size((64, 24)).columns
    return max(44, min(96, cols))


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def divider(char: str = "─", accent: str = "purple") -> None:
    color = Theme.NEON_PURPLE if accent == "purple" else Theme.ELECTRIC_BLUE
    print(f"{color}{char * term_width()}{Theme.RESET}")


def print_banner() -> None:
    """Menampilkan ASCII banner NOBAX dengan gradien ungu neon & biru elektrik."""
    width = term_width()
    logo_path = Path(__file__).resolve().parent.parent / "assets" / "logo.txt"
    gradient = [
        Theme.NEON_PURPLE,
        Theme.PURPLE,
        Theme.DEEP_PURPLE,
        Theme.BLUE,
        Theme.ELECTRIC_BLUE,
        Theme.NEON_PURPLE,
    ]

    print()
    if logo_path.exists() and width >= 48:
        lines = logo_path.read_text(encoding="utf-8").splitlines()
        for idx, line in enumerate(lines):
            color = gradient[idx % len(gradient)]
            trimmed = line[:width]
            print(f"{Theme.BOLD}{color}{trimmed}{Theme.RESET}")
    else:
        title = "◈ NOBAX TOOLS ◈"
        print(f"{Theme.BOLD}{Theme.NEON_PURPLE}{title.center(width)}{Theme.RESET}")

    subtitle = "NOBAX DEX @ TERMUX  •  ALL-IN-ONE TOOLKIT"
    dev_tag = "Developer: NOEL  |  Mode: Termux / CLI"
    print(f"{Theme.BOLD}{Theme.ELECTRIC_BLUE}{subtitle[:width].center(width)}{Theme.RESET}")
    print(f"{Theme.MUTED}{dev_tag[:width].center(width)}{Theme.RESET}")
    divider("━", "purple")


def wrap_line(text: str, max_width: int) -> list[str]:
    """Membungkus baris teks panjang sambil mempertahankan ANSI escape codes."""
    plain = strip_ansi(text)
    if len(plain) <= max_width:
        return [text]

    words = plain.split(" ")
    wrapped = []
    current = ""
    for word in words:
        while len(word) > max_width:
            if current:
                wrapped.append(current)
                current = ""
            wrapped.append(word[:max_width])
            word = word[max_width:]
        if not current:
            current = word
        elif len(current) + 1 + len(word) <= max_width:
            current += " " + word
        else:
            wrapped.append(current)
            current = word
    if current:
        wrapped.append(current)
    return wrapped or [""]


def panel(title: str, lines: list[str], accent: str = "purple") -> None:
    """Merender panel informasi berbingkai melengkung yang responsif."""
    width = term_width()
    inner_w = width - 4
    border_color = Theme.NEON_PURPLE if accent == "purple" else Theme.ELECTRIC_BLUE
    title_color = Theme.ELECTRIC_BLUE if accent == "purple" else Theme.NEON_PURPLE

    clean_title = f" {title} "
    if len(clean_title) > width - 4:
        clean_title = clean_title[: width - 7] + "... "

    top_fill = max(0, width - 3 - len(clean_title))
    print(
        f"{border_color}╭─{Theme.BOLD}{title_color}{clean_title}"
        f"{Theme.RESET}{border_color}{'─' * top_fill}╮{Theme.RESET}"
    )

    for raw_line in lines:
        for seg in wrap_line(raw_line, inner_w):
            pad = max(0, inner_w - len(strip_ansi(seg)))
            print(
                f"{border_color}│{Theme.RESET} "
                f"{seg}{' ' * pad} "
                f"{border_color}│{Theme.RESET}"
            )

    print(f"{border_color}╰{'─' * (width - 2)}╯{Theme.RESET}")


def spinner(message: str, duration: float = 0.45) -> None:
    """Animasi loading ringkas di terminal."""
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    end_time = time.time() + duration
    idx = 0
    while time.time() < end_time:
        frame = frames[idx % len(frames)]
        sys.stdout.write(
            f"\r{Theme.NEON_PURPLE}{frame}{Theme.RESET} "
            f"{Theme.SILVER}{message}{Theme.RESET}"
        )
        sys.stdout.flush()
        time.sleep(0.06)
        idx += 1
    sys.stdout.write("\r" + " " * (len(message) + 6) + "\r")
    sys.stdout.flush()


def progress_bar(label: str, steps: int = 20, delay: float = 0.015) -> None:
    """Indikator progres bertema ungu neon & biru elektrik."""
    width = min(24, max(12, term_width() - len(label) - 14))
    for i in range(steps + 1):
        pct = int((i / steps) * 100)
        filled = int((i / steps) * width)
        bar = (
            f"{Theme.NEON_PURPLE}{'█' * filled}"
            f"{Theme.MUTED}{'░' * (width - filled)}{Theme.RESET}"
        )
        sys.stdout.write(
            f"\r{Theme.ELECTRIC_BLUE}▸{Theme.RESET} {label} [{bar}] "
            f"{Theme.BOLD}{Theme.WHITE}{pct:3d}%{Theme.RESET}"
        )
        sys.stdout.flush()
        time.sleep(delay)
    print()


def success(msg: str) -> None:
    print(f"{Theme.BOLD}{Theme.GREEN}[✔]{Theme.RESET} {Theme.WHITE}{msg}{Theme.RESET}")


def info(msg: str) -> None:
    print(f"{Theme.BOLD}{Theme.ELECTRIC_BLUE}[◈]{Theme.RESET} {Theme.SILVER}{msg}{Theme.RESET}")


def warn(msg: str) -> None:
    print(f"{Theme.BOLD}{Theme.YELLOW}[!]{Theme.RESET} {Theme.YELLOW}{msg}{Theme.RESET}")


def error(msg: str) -> None:
    print(f"{Theme.BOLD}{Theme.RED}[✘]{Theme.RESET} {Theme.RED}{msg}{Theme.RESET}")


def ask(prompt_label: str = "nobax@termux:~") -> str:
    return input(
        f"{Theme.BOLD}{Theme.NEON_PURPLE}{prompt_label}"
        f"{Theme.ELECTRIC_BLUE}▸ {Theme.WHITE}"
    ).strip()


def pause(msg: str = "Tekan [Enter] untuk kembali...") -> None:
    input(f"\n{Theme.MUTED}{msg}{Theme.RESET}")
