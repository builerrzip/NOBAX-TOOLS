#!/usr/bin/env python3
"""
NOBAX TOOLS - All-in-One Termux Toolkit, AI Assistant & Browser Launcher
Developer: NOEL
"""

import argparse
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def run_health_check() -> int:
    """Memverifikasi seluruh modul inti dapat di-import tanpa error."""
    modules = [
        "core.ui",
        "core.config",
        "core.browser",
        "core.commands",
        "core.engine",
        "ai.provider",
        "ai.history",
        "ai.memory",
        "ai.assistant",
        "tools.generator",
        "tools.encoder",
        "tools.decoder",
        "tools.qr",
        "tools.json_tool",
        "tools.hash_tool",
        "tools.network",
        "tools.system",
        "tools.center",
        "browser.launcher",
        "manager.file_manager",
    ]
    failed = []
    for mod in modules:
        try:
            __import__(mod)
        except Exception as exc:
            failed.append((mod, str(exc)))

    if failed:
        print("[ERROR] Gagal memuat modul berikut:")
        for mod, err in failed:
            print(f"  - {mod}: {err}")
        return 1

    print("[OK] Seluruh 20 modul NOBAX TOOLS terverifikasi dan siap digunakan.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="nobax",
        description="NOBAX TOOLS — All-in-One Termux Toolkit & AI Assistant by NOEL",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Jalankan pemeriksaan integritas modul dan keluar.",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Tampilkan versi NOBAX TOOLS.",
    )
    args = parser.parse_args()

    if args.version:
        print("NOBAX TOOLS v1.0.0 — NOBAX DEX @ TERMUX (Dev: NOEL)")
        return 0

    if args.check:
        return run_health_check()

    from core.engine import NobaxEngine

    engine = NobaxEngine()
    try:
        engine.run()
    except KeyboardInterrupt:
        print("\n\033[38;5;135m[◈] Sesi NOBAX TOOLS dihentikan oleh pengguna. Sampai jumpa!\033[0m")
    return 0


if __name__ == "__main__":
    sys.exit(main())
