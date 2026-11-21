"""
Menu Interaktif Tools Center (15 Utility Lengkap & Berfungsi).
"""

from core.ui import Theme, ask, clear_screen, panel, pause, print_banner, warn
from tools.decoder import run_text_decoder_ui
from tools.encoder import run_text_converter_ui, run_text_encoder_ui
from tools.generator import (
    run_ascii_banner_ui,
    run_password_generator_ui,
    run_random_data_ui,
)
from tools.hash_tool import run_hash_generator_ui
from tools.json_tool import run_json_formatter_ui
from tools.network import (
    run_dns_lookup_ui,
    run_ip_info_ui,
    run_url_parser_ui,
    run_website_status_ui,
)
from tools.qr import run_qr_generator_ui
from tools.system import render_system_info, run_file_info_ui


class ToolsCenter:
    def interactive_menu(self) -> None:
        while True:
            clear_screen()
            print_banner()

            lines = [
                f"{Theme.NEON_PURPLE}[01]{Theme.RESET} Password Generator      {Theme.NEON_PURPLE}[09]{Theme.RESET} Website Status Checker",
                f"{Theme.NEON_PURPLE}[02]{Theme.RESET} QR Code Generator       {Theme.NEON_PURPLE}[10]{Theme.RESET} ASCII Banner Generator",
                f"{Theme.NEON_PURPLE}[03]{Theme.RESET} Text Encoder            {Theme.NEON_PURPLE}[11]{Theme.RESET} File Information",
                f"{Theme.NEON_PURPLE}[04]{Theme.RESET} Text Decoder            {Theme.NEON_PURPLE}[12]{Theme.RESET} System Information",
                f"{Theme.NEON_PURPLE}[05]{Theme.RESET} JSON Formatter          {Theme.NEON_PURPLE}[13]{Theme.RESET} URL Parser",
                f"{Theme.NEON_PURPLE}[06]{Theme.RESET} Hash Generator          {Theme.NEON_PURPLE}[14]{Theme.RESET} Text Converter",
                f"{Theme.NEON_PURPLE}[07]{Theme.RESET} IP Information          {Theme.NEON_PURPLE}[15]{Theme.RESET} Random Data Generator",
                f"{Theme.NEON_PURPLE}[08]{Theme.RESET} DNS Lookup              {Theme.RED}[00]{Theme.RESET} Kembali ke Menu Utama",
            ]
            panel("TOOLS CENTER — 15 ALL-IN-ONE UTILITIES", lines, accent="purple")
            choice = ask("nobax@tools:~")

            if choice in ("0", "00"):
                break
            elif choice in ("1", "01"):
                run_password_generator_ui()
            elif choice in ("2", "02"):
                run_qr_generator_ui()
            elif choice in ("3", "03"):
                run_text_encoder_ui()
            elif choice in ("4", "04"):
                run_text_decoder_ui()
            elif choice in ("5", "05"):
                run_json_formatter_ui()
            elif choice in ("6", "06"):
                run_hash_generator_ui()
            elif choice in ("7", "07"):
                run_ip_info_ui()
            elif choice in ("8", "08"):
                run_dns_lookup_ui()
            elif choice in ("9", "09"):
                run_website_status_ui()
            elif choice == "10":
                run_ascii_banner_ui()
            elif choice == "11":
                run_file_info_ui()
            elif choice == "12":
                clear_screen()
                print_banner()
                render_system_info()
                pause()
            elif choice == "13":
                run_url_parser_ui()
            elif choice == "14":
                run_text_converter_ui()
            elif choice == "15":
                run_random_data_ui()
            else:
                warn("Nomor tool tidak valid. Masukkan 01-15 atau 00.")
                pause()
