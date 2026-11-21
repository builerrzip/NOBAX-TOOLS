"""
Tool #1: Password Generator
Tool #10: ASCII Banner Generator
Tool #15: Random Data Generator
"""

import math
import random
import secrets
import string
import uuid

from core.ui import Theme, ask, clear_screen, error, panel, pause, print_banner, success


BLOCK_FONT: dict[str, list[str]] = {
    "A": [" ███ ", "█   █", "█████", "█   █", "█   █"],
    "B": ["████ ", "█   █", "████ ", "█   █", "████ "],
    "C": [" ████", "█    ", "█    ", "█    ", " ████"],
    "D": ["████ ", "█   █", "█   █", "█   █", "████ "],
    "E": ["█████", "█    ", "████ ", "█    ", "█████"],
    "F": ["█████", "█    ", "████ ", "█    ", "█    "],
    "G": [" ████", "█    ", "█  ██", "█   █", " ████"],
    "H": ["█   █", "█   █", "█████", "█   █", "█   █"],
    "I": ["█████", "  █  ", "  █  ", "  █  ", "█████"],
    "J": ["  ███", "   █ ", "   █ ", "█  █ ", " ██  "],
    "K": ["█   █", "█  █ ", "███  ", "█  █ ", "█   █"],
    "L": ["█    ", "█    ", "█    ", "█    ", "█████"],
    "M": ["█   █", "██ ██", "█ █ █", "█   █", "█   █"],
    "N": ["█   █", "██  █", "█ █ █", "█  ██", "█   █"],
    "O": [" ███ ", "█   █", "█   █", "█   █", " ███ "],
    "P": ["████ ", "█   █", "████ ", "█    ", "█    "],
    "Q": [" ███ ", "█   █", "█ █ █", "█  ██", " ████"],
    "R": ["████ ", "█   █", "████ ", "█  █ ", "█   █"],
    "S": [" ████", "█    ", " ███ ", "    █", "████ "],
    "T": ["█████", "  █  ", "  █  ", "  █  ", "  █  "],
    "U": ["█   █", "█   █", "█   █", "█   █", " ███ "],
    "V": ["█   █", "█   █", "█   █", " █ █ ", "  █  "],
    "W": ["█   █", "█   █", "█ █ █", "██ ██", "█   █"],
    "X": ["█   █", " █ █ ", "  █  ", " █ █ ", "█   █"],
    "Y": ["█   █", " █ █ ", "  █  ", "  █  ", "  █  "],
    "Z": ["█████", "   █ ", "  █  ", " █   ", "█████"],
    "0": [" ███ ", "█  ██", "█ █ █", "██  █", " ███ "],
    "1": ["  █  ", " ██  ", "  █  ", "  █  ", "█████"],
    "2": ["████ ", "    █", " ███ ", "█    ", "█████"],
    "3": ["████ ", "    █", " ███ ", "    █", "████ "],
    "4": ["█   █", "█   █", "█████", "    █", "    █"],
    "5": ["█████", "█    ", "████ ", "    █", "████ "],
    "6": [" ████", "█    ", "████ ", "█   █", " ███ "],
    "7": ["█████", "    █", "   █ ", "  █  ", "  █  "],
    "8": [" ███ ", "█   █", " ███ ", "█   █", " ███ "],
    "9": [" ███ ", "█   █", " ████", "    █", "████ "],
    "-": ["     ", "     ", "█████", "     ", "     "],
    "_": ["     ", "     ", "     ", "     ", "█████"],
    "!": ["  █  ", "  █  ", "  █  ", "     ", "  █  "],
    ".": ["     ", "     ", "     ", "     ", "  █  "],
    " ": ["   ", "   ", "   ", "   ", "   "],
}


def generate_password(
    length: int = 16,
    use_upper: bool = True,
    use_lower: bool = True,
    use_digits: bool = True,
    use_symbols: bool = True,
) -> dict:
    length = max(6, min(128, length))
    pools: list[str] = []
    guaranteed: list[str] = []

    if use_upper:
        pools.append(string.ascii_uppercase)
        guaranteed.append(secrets.choice(string.ascii_uppercase))
    if use_lower:
        pools.append(string.ascii_lowercase)
        guaranteed.append(secrets.choice(string.ascii_lowercase))
    if use_digits:
        pools.append(string.digits)
        guaranteed.append(secrets.choice(string.digits))
    if use_symbols:
        syms = "!@#$%^&*()-_=+[]{}?"
        pools.append(syms)
        guaranteed.append(secrets.choice(syms))

    if not pools:
        pools = [string.ascii_letters + string.digits]
        guaranteed = [secrets.choice(pools[0])]

    alphabet = "".join(pools)
    remaining = max(0, length - len(guaranteed))
    chars = guaranteed + [secrets.choice(alphabet) for _ in range(remaining)]
    secrets.SystemRandom().shuffle(chars)
    password = "".join(chars[:length])

    entropy = round(length * math.log2(len(alphabet)), 1)
    if entropy >= 80:
        strength = "SANGAT KUAT"
    elif entropy >= 60:
        strength = "KUAT"
    elif entropy >= 40:
        strength = "SEDANG"
    else:
        strength = "LEMAH"

    return {
        "password": password,
        "length": length,
        "entropy_bits": entropy,
        "strength": strength,
    }


def generate_ascii_banner(text: str) -> str:
    cleaned = text.strip().upper()[:16] or "NOBAX"
    rows = ["", "", "", "", ""]
    for ch in cleaned:
        glyph = BLOCK_FONT.get(ch, [" ??? ", "   ? ", "  ?  ", "     ", "  ?  "])
        for r in range(5):
            rows[r] += glyph[r] + " "
    return "\n".join(rows)


def generate_random_data(category: str, count: int = 5) -> list[str]:
    count = max(1, min(25, count))
    first_names = ["Noel", "Alya", "Raka", "Sora", "Dante", "Kira", "Zayn", "Nadia", "Vero", "Tama"]
    last_names = ["Pratama", "Wijaya", "Kurnia", "Saputra", "Putri", "Santoso", "Mahendra", "Nugroho"]
    domains = ["example.com", "nobax.dev", "termux.id", "mailtest.org"]
    results: list[str] = []

    for _ in range(count):
        if category == "uuid":
            results.append(str(uuid.uuid4()))
        elif category == "user":
            fn = random.choice(first_names)
            ln = random.choice(last_names)
            num = random.randint(10, 999)
            email = f"{fn.lower()}.{ln.lower()}{num}@{random.choice(domains)}"
            results.append(f"{fn} {ln} | @{fn.lower()}{num} | {email}")
        elif category == "ipv4":
            octets = [str(random.randint(1, 254)) for _ in range(4)]
            results.append(".".join(octets))
        elif category == "mac":
            mac = ":".join(f"{secrets.randbelow(256):02X}" for _ in range(6))
            results.append(mac)
        elif category == "hexcolor":
            results.append(f"#{secrets.token_hex(3).upper()}")
        else:
            results.append(str(secrets.randbelow(1_000_000)))
    return results


def run_password_generator_ui() -> None:
    clear_screen()
    print_banner()
    raw_len = ask("Panjang password [default: 16]")
    length = int(raw_len) if raw_len.isdigit() else 16
    sym_in = ask("Sertakan simbol? (y/n) [default: y]").lower()
    use_symbols = sym_in != "n"

    res = generate_password(length=length, use_symbols=use_symbols)
    panel(
        "PASSWORD GENERATOR RESULT",
        [
            f"{Theme.ELECTRIC_BLUE}Password :{Theme.RESET} {Theme.BOLD}{Theme.GREEN}{res['password']}{Theme.RESET}",
            f"{Theme.ELECTRIC_BLUE}Panjang  :{Theme.RESET} {res['length']} karakter",
            f"{Theme.ELECTRIC_BLUE}Entropi  :{Theme.RESET} {res['entropy_bits']} bits ({res['strength']})",
        ],
        accent="purple",
    )
    pause()


def run_ascii_banner_ui() -> None:
    clear_screen()
    print_banner()
    txt = ask("Masukkan teks untuk banner (maks 16 karakter)")
    if not txt:
        error("Teks tidak boleh kosong.")
        pause()
        return
    banner_art = generate_ascii_banner(txt)
    print(f"\n{Theme.BOLD}{Theme.NEON_PURPLE}{banner_art}{Theme.RESET}")
    success("ASCII Banner berhasil dibuat.")
    pause()


def run_random_data_ui() -> None:
    clear_screen()
    print_banner()
    panel(
        "RANDOM DATA GENERATOR",
        [
            "[1] UUID v4",
            "[2] Profil User & Email Mock",
            "[3] Alamat IPv4 Acak",
            "[4] MAC Address Acak",
            "[5] Kode Warna HEX",
            "[6] Angka Acak (0 - 999999)",
        ],
        accent="blue",
    )
    choice = ask("Pilih jenis data [1-6]")
    mapping = {"1": "uuid", "2": "user", "3": "ipv4", "4": "mac", "5": "hexcolor", "6": "number"}
    cat = mapping.get(choice, "uuid")
    cnt_raw = ask("Jumlah item [default: 5]")
    cnt = int(cnt_raw) if cnt_raw.isdigit() else 5

    items = generate_random_data(cat, cnt)
    panel("HASIL RANDOM DATA", [f"• {item}" for item in items], accent="purple")
    pause()
