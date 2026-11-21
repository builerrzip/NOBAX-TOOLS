"""
Tool #5: JSON Formatter & Validator
"""

import json

from core.ui import Theme, ask, clear_screen, error, panel, pause, print_banner, success


def format_json(raw_json: str, indent: int = 2, sort_keys: bool = False, minify: bool = False) -> dict:
    try:
        parsed = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        return {
            "valid": False,
            "error": f"Syntax JSON tidak valid pada baris {exc.lineno}, kolom {exc.colno}: {exc.msg}",
            "output": "",
        }

    if minify:
        formatted = json.dumps(parsed, separators=(",", ":"), ensure_ascii=False, sort_keys=sort_keys)
    else:
        formatted = json.dumps(parsed, indent=indent, ensure_ascii=False, sort_keys=sort_keys)

    item_count = len(parsed) if isinstance(parsed, (dict, list)) else 1
    return {
        "valid": True,
        "type": type(parsed).__name__,
        "items": item_count,
        "output": formatted,
    }


def run_json_formatter_ui() -> None:
    clear_screen()
    print_banner()
    info_lines = [
        "Tempelkan JSON satu baris atau beberapa baris.",
        "Ketik baris kosong dua kali atau 'END' untuk memproses.",
    ]
    panel("JSON FORMATTER & VALIDATOR", info_lines, accent="blue")

    lines: list[str] = []
    while True:
        line = input(f"{Theme.MUTED}> {Theme.WHITE}")
        if line.strip().upper() == "END":
            break
        if line == "" and lines and lines[-1] == "":
            break
        lines.append(line)

    raw = "\n".join(lines).strip()
    if not raw:
        error("Input JSON kosong.")
        pause()
        return

    mode = ask("Mode: [1] Pretty Print  [2] Minify  [3] Sort Keys Pretty [default: 1]")
    res = format_json(
        raw,
        indent=2,
        sort_keys=(mode == "3"),
        minify=(mode == "2"),
    )
    if not res["valid"]:
        error(res["error"])
    else:
        success(f"JSON Valid! Tipe root: {res['type']} ({res['items']} elemen)")
        print(f"\n{Theme.GREEN}{res['output']}{Theme.RESET}")
    pause()
