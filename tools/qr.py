"""
Tool #2: QR Code Generator
"""

from datetime import datetime
from pathlib import Path

try:
    import qrcode
except ImportError:
    qrcode = None

from core.ui import Theme, ask, clear_screen, error, info, pause, print_banner, success


def build_qr_ascii(data: str) -> str:
    if qrcode is None:
        raise RuntimeError(
            "Library 'qrcode' belum terinstal. Jalankan: pip install qrcode"
        )

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=1,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)
    matrix = qr.get_matrix()

    lines: list[str] = []
    rows = len(matrix)
    for r in range(0, rows, 2):
        row_top = matrix[r]
        row_bot = matrix[r + 1] if r + 1 < rows else [False] * len(row_top)
        chars = []
        for top_dark, bot_dark in zip(row_top, row_bot):
            if top_dark and bot_dark:
                chars.append("█")
            elif top_dark and not bot_dark:
                chars.append("▀")
            elif not top_dark and bot_dark:
                chars.append("▄")
            else:
                chars.append(" ")
        lines.append("".join(chars))
    return "\n".join(lines)


def run_qr_generator_ui() -> None:
    clear_screen()
    print_banner()
    content = ask("Masukkan teks atau URL untuk QR Code")
    if not content:
        error("Konten QR Code tidak boleh kosong.")
        pause()
        return

    try:
        qr_art = build_qr_ascii(content)
        print(f"\n{Theme.WHITE}{qr_art}{Theme.RESET}\n")
        success(f"QR Code berhasil dibuat untuk: {content}")

        save_opt = ask("Simpan QR ASCII ke file di data/exports/? (y/n) [default: n]").lower()
        if save_opt == "y":
            export_dir = Path(__file__).resolve().parent.parent / "data" / "exports"
            export_dir.mkdir(parents=True, exist_ok=True)
            out_file = export_dir / f"qr_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            out_file.write_text(f"Data: {content}\n\n{qr_art}\n", encoding="utf-8")
            info(f"Tersimpan di: {out_file}")
    except Exception as exc:
        error(str(exc))
    pause()
