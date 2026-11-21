"""
NOBAX TOOLS Core Engine.
"""

from ai.assistant import AIAssistant
from core.browser import BrowserBridge
from core.commands import detect_browser_intent, parse_slash_command
from core.config import PROVIDER_PRESETS, ConfigManager, mask_secret
from core.ui import (
    Theme,
    ask,
    clear_screen,
    divider,
    error,
    info,
    panel,
    pause,
    print_banner,
    progress_bar,
    spinner,
    success,
    warn,
)
from manager.file_manager import FileManager
from tools.center import ToolsCenter
from tools.system import render_system_info


class NobaxEngine:
    def __init__(self) -> None:
        self.config = ConfigManager()
        self.browser = BrowserBridge(self.config)
        self.assistant = AIAssistant(self.config, self.browser)
        self.tools = ToolsCenter()
        self.file_manager = FileManager()

    def render_dashboard(self) -> None:
        clear_screen()
        print_banner()

        provider_key = self.config.get("provider", "openai")
        provider_name = PROVIDER_PRESETS.get(provider_key, {}).get("name", provider_key)
        ai_status = (
            f"{Theme.GREEN}READY ({provider_name}){Theme.RESET}"
            if self.config.has_api_key()
            else f"{Theme.YELLOW}API KEY BELUM DIATUR (/settings){Theme.RESET}"
        )

        status_lines = [
            f"{Theme.ELECTRIC_BLUE}AI Engine :{Theme.RESET} {ai_status}",
            f"{Theme.ELECTRIC_BLUE}Model     :{Theme.RESET} {Theme.WHITE}{self.config.get('model')}{Theme.RESET}",
            f"{Theme.ELECTRIC_BLUE}Browser   :{Theme.RESET} {Theme.WHITE}{'Google Chrome (Android Intent)' if self.config.get('prefer_chrome') else 'Default Browser'}{Theme.RESET}",
        ]
        panel("SYSTEM & AI STATUS", status_lines, accent="blue")
        print()

        menu_lines = [
            f"{Theme.BOLD}{Theme.NEON_PURPLE}[01]{Theme.RESET} {Theme.WHITE}AI ASSISTANT{Theme.RESET}      {Theme.MUTED}• Chat AI, Streaming & Riwayat{Theme.RESET}",
            f"{Theme.BOLD}{Theme.NEON_PURPLE}[02]{Theme.RESET} {Theme.WHITE}TOOLS CENTER{Theme.RESET}      {Theme.MUTED}• 15 Utility Developer & Network{Theme.RESET}",
            f"{Theme.BOLD}{Theme.NEON_PURPLE}[03]{Theme.RESET} {Theme.WHITE}BROWSER CENTER{Theme.RESET}    {Theme.MUTED}• Buka Website via Chrome Android{Theme.RESET}",
            f"{Theme.BOLD}{Theme.NEON_PURPLE}[04]{Theme.RESET} {Theme.WHITE}FILE MANAGER{Theme.RESET}      {Theme.MUTED}• Kelola File & Folder Aman{Theme.RESET}",
            f"{Theme.BOLD}{Theme.NEON_PURPLE}[05]{Theme.RESET} {Theme.WHITE}SYSTEM INFO{Theme.RESET}       {Theme.MUTED}• Perangkat, Android, RAM & Termux{Theme.RESET}",
            f"{Theme.BOLD}{Theme.NEON_PURPLE}[06]{Theme.RESET} {Theme.WHITE}SETTINGS{Theme.RESET}          {Theme.MUTED}• Konfigurasi API Key & Provider{Theme.RESET}",
            f"{Theme.BOLD}{Theme.RED}[00]{Theme.RESET} {Theme.SILVER}EXIT{Theme.RESET}              {Theme.MUTED}• Keluar dari NOBAX TOOLS{Theme.RESET}",
        ]
        panel("MAIN MENU — NOBAX DEX @ TERMUX", menu_lines, accent="purple")
        print(
            f"{Theme.MUTED}Tips: Ketik angka menu (01-06), perintah (/help, /open, /new, /past, /settings), "
            f"atau langsung tulis pertanyaan untuk AI.{Theme.RESET}"
        )
        divider("─", "blue")

    def show_help(self) -> None:
        help_lines = [
            f"{Theme.BOLD}{Theme.ELECTRIC_BLUE}Navigasi Menu:{Theme.RESET}",
            "  01 / 1   -> Masuk ke mode interaktif AI Assistant",
            "  02 / 2   -> Buka 15 Tools Center (Generator, Encoder, Network, dll)",
            "  03 / 3   -> Buka Browser Center (Google Chrome Android Intent)",
            "  04 / 4   -> Buka File Manager",
            "  05 / 5   -> Lihat System Information",
            "  06 / 6   -> Buka Pengaturan API & Browser",
            "  00 / 0   -> Keluar dari aplikasi",
            "",
            f"{Theme.BOLD}{Theme.ELECTRIC_BLUE}Slash Commands (Bisa dipakai kapan saja):{Theme.RESET}",
            "  /new          -> Mulai percakapan AI baru",
            "  /past         -> Lihat & muat riwayat percakapan",
            "  /open <web>   -> Buka website di Chrome (cth: /open github)",
            "  /settings     -> Atur API Key, Provider, & Model AI",
            "  /clear        -> Bersihkan & muat ulang tampilan terminal",
            "  /help         -> Tampilkan panduan bantuan ini",
            "",
            f"{Theme.BOLD}{Theme.ELECTRIC_BLUE}Prompt Langsung:{Theme.RESET}",
            "  Ketik pertanyaan apa saja langsung di nobax@termux:~ untuk bertanya ke AI,",
            "  atau tulis: 'Tolong buka GitHub di Chrome.'",
        ]
        panel("PANDUAN NOBAX TOOLS", help_lines, accent="blue")

    def open_settings(self) -> None:
        while True:
            clear_screen()
            print_banner()
            prov_key = self.config.get("provider", "openai")
            prov_name = PROVIDER_PRESETS.get(prov_key, {}).get("name", prov_key)
            lines = [
                f"{Theme.ELECTRIC_BLUE}[1] Provider AI   :{Theme.RESET} {Theme.WHITE}{prov_name} ({prov_key}){Theme.RESET}",
                f"{Theme.ELECTRIC_BLUE}[2] API Key       :{Theme.RESET} {Theme.WHITE}{mask_secret(self.config.get('api_key', ''))}{Theme.RESET}",
                f"{Theme.ELECTRIC_BLUE}[3] Model AI      :{Theme.RESET} {Theme.WHITE}{self.config.get('model')}{Theme.RESET}",
                f"{Theme.ELECTRIC_BLUE}[4] Base URL      :{Theme.RESET} {Theme.WHITE}{self.config.get('base_url')}{Theme.RESET}",
                f"{Theme.ELECTRIC_BLUE}[5] Streaming     :{Theme.RESET} {Theme.WHITE}{'Aktif' if self.config.get('stream') else 'Nonaktif'}{Theme.RESET}",
                f"{Theme.ELECTRIC_BLUE}[6] Chrome Intent :{Theme.RESET} {Theme.WHITE}{'Utamakan Chrome' if self.config.get('prefer_chrome') else 'Browser Default'}{Theme.RESET}",
                f"{Theme.ELECTRIC_BLUE}[7] Hapus API Key :{Theme.RESET} {Theme.MUTED}Hapus key tersimpan dari data/config.json{Theme.RESET}",
                f"{Theme.RED}[0] Kembali{Theme.RESET}",
            ]
            panel("SETTINGS — KONFIGURASI AI & BROWSER", lines, accent="purple")
            choice = ask("nobax@settings:~")

            if choice == "0":
                break
            elif choice == "1":
                print(f"\n{Theme.ELECTRIC_BLUE}Pilih Provider AI:{Theme.RESET}")
                keys = list(PROVIDER_PRESETS.keys())
                for idx, k in enumerate(keys, 1):
                    print(f"  [{idx}] {PROVIDER_PRESETS[k]['name']} ({k}) — Default: {PROVIDER_PRESETS[k]['default_model']}")
                sel = ask("Pilih nomor provider")
                if sel.isdigit() and 1 <= int(sel) <= len(keys):
                    chosen = keys[int(sel) - 1]
                    self.config.set_provider(chosen)
                    success(f"Provider diubah ke {PROVIDER_PRESETS[chosen]['name']}.")
                else:
                    warn("Pilihan tidak valid.")
                pause()
            elif choice == "2":
                info("API Key disimpan secara lokal di data/config.json (tidak di-commit ke Git).")
                new_key = ask("Masukkan API Key baru (kosongkan untuk batal)")
                if new_key:
                    self.config.set("api_key", new_key)
                    success("API Key berhasil disimpan!")
                else:
                    warn("Perubahan API Key dibatalkan.")
                pause()
            elif choice == "3":
                new_model = ask(f"Masukkan nama model [{self.config.get('model')}]")
                if new_model:
                    self.config.set("model", new_model)
                    success(f"Model diubah menjadi: {new_model}")
                pause()
            elif choice == "4":
                new_url = ask(f"Masukkan Base URL endpoint [{self.config.get('base_url')}]")
                if new_url:
                    self.config.set("base_url", new_url)
                    success("Base URL diperbarui.")
                pause()
            elif choice == "5":
                curr = bool(self.config.get("stream", True))
                self.config.set("stream", not curr)
                success(f"Streaming response: {'Aktif' if not curr else 'Nonaktif'}")
                pause()
            elif choice == "6":
                curr = bool(self.config.get("prefer_chrome", True))
                self.config.set("prefer_chrome", not curr)
                success(f"Prioritas Google Chrome: {'Aktif' if not curr else 'Nonaktif'}")
                pause()
            elif choice == "7":
                self.config.set("api_key", "")
                success("API Key lokal telah dihapus.")
                pause()
            else:
                warn("Menu pengaturan tidak dikenal.")
                pause()

    def handle_command(self, cmd: str, arg: str) -> bool:
        if cmd == "/help":
            self.show_help()
            return True
        if cmd == "/clear":
            self.render_dashboard()
            return True
        if cmd == "/settings":
            self.open_settings()
            self.render_dashboard()
            return True
        if cmd == "/new":
            self.assistant.start_new_chat()
            return True
        if cmd == "/past":
            self.assistant.show_and_load_history()
            return True
        if cmd == "/open":
            if not arg:
                warn("Gunakan format: /open <nama_situs_atau_url> (contoh: /open github)")
                return True
            result = self.browser.launch(arg)
            if result["success"]:
                success(result["message"])
            else:
                error(result["message"])
            return True
        return False

    def run(self) -> None:
        progress_bar("Memuat NOBAX TOOLS Engine", steps=18, delay=0.012)
        self.render_dashboard()

        while True:
            try:
                user_input = ask("nobax@termux:~")
            except EOFError:
                break

            if not user_input:
                continue

            low = user_input.lower()

            if low in ("00", "0", "exit", "quit"):
                spinner("Menutup sesi NOBAX TOOLS...", duration=0.35)
                success("Terima kasih telah menggunakan NOBAX TOOLS!")
                break
            elif low in ("01", "1"):
                self.assistant.interactive_loop(on_open_settings=self.open_settings)
                self.render_dashboard()
            elif low in ("02", "2"):
                self.tools.interactive_menu()
                self.render_dashboard()
            elif low in ("03", "3"):
                self.browser.open_menu()
                self.render_dashboard()
            elif low in ("04", "4"):
                self.file_manager.interactive_menu()
                self.render_dashboard()
            elif low in ("05", "5"):
                clear_screen()
                print_banner()
                render_system_info()
                pause()
                self.render_dashboard()
            elif low in ("06", "6"):
                self.open_settings()
                self.render_dashboard()
            else:
                parsed = parse_slash_command(user_input)
                if parsed is not None:
                    cmd, arg = parsed
                    if not self.handle_command(cmd, arg):
                        warn(f"Command tidak dikenal: {cmd}. Ketik /help untuk daftar perintah.")
                    continue

                browser_target = detect_browser_intent(user_input)
                if browser_target:
                    spinner(f"Membuka {browser_target}...", duration=0.3)
                    result = self.browser.launch(browser_target)
                    if result["success"]:
                        success(result["message"])
                    else:
                        error(result["message"])
                    continue

                self.assistant.ask_once(user_input)
