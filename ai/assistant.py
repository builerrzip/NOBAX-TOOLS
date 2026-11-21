"""
NOBAX AI Assistant.
"""

import sys
from typing import Callable, Optional

from ai.history import HistoryManager
from ai.memory import ConversationMemory
from ai.provider import AIProviderClient, AIProviderError
from core.browser import BrowserBridge
from core.commands import detect_browser_intent, parse_slash_command
from core.config import PROVIDER_PRESETS, ConfigManager
from core.ui import (
    Theme,
    ask,
    clear_screen,
    divider,
    error,
    panel,
    print_banner,
    spinner,
    success,
    warn,
)


class AIAssistant:
    def __init__(self, config: ConfigManager, browser: BrowserBridge) -> None:
        self.config = config
        self.browser = browser
        self.history = HistoryManager(config.history_dir)
        self.memory = ConversationMemory(max_turns=20)
        self.client = AIProviderClient(config)

    def start_new_chat(self) -> None:
        sid = self.history.new_session()
        success(f"Percakapan baru dimulai (ID: {sid}).")

    def show_and_load_history(self) -> None:
        sessions = self.history.list_sessions(limit=12)
        if not sessions:
            warn("Belum ada riwayat percakapan tersimpan.")
            return

        lines = []
        for idx, item in enumerate(sessions, 1):
            lines.append(
                f"{Theme.NEON_PURPLE}[{idx:02d}]{Theme.RESET} "
                f"{Theme.WHITE}{item['title']}{Theme.RESET} "
                f"{Theme.MUTED}({item['count']} pesan • {item['created_at']}){Theme.RESET}"
            )
        panel("RIWAYAT PERCAKAPAN AI (/past)", lines, accent="blue")
        sel = ask("Pilih nomor sesi untuk dimuat (Enter untuk batal)")
        if sel.isdigit() and 1 <= int(sel) <= len(sessions):
            chosen = sessions[int(sel) - 1]
            if self.history.load_session(chosen["session_id"]):
                success(f"Sesi '{chosen['title']}' berhasil dimuat!")
                for msg in self.history.messages[-4:]:
                    tag = "Anda" if msg["role"] == "user" else "NOBAX AI"
                    color = Theme.ELECTRIC_BLUE if msg["role"] == "user" else Theme.NEON_PURPLE
                    preview = msg["content"].replace("\n", " ")[:120]
                    print(f"  {color}{tag}:{Theme.RESET} {Theme.SILVER}{preview}{Theme.RESET}")
            else:
                error("Gagal memuat file riwayat percakapan.")

    def ask_once(self, prompt: str) -> str:
        """Memproses satu pertanyaan AI lengkap dengan streaming & penyimpanan riwayat."""
        browser_target = detect_browser_intent(prompt)
        if browser_target:
            spinner(f"Mendeteksi perintah browser -> {browser_target}...", duration=0.3)
            res = self.browser.launch(browser_target)
            if res["success"]:
                success(res["message"])
            else:
                error(res["message"])
            return res["message"]

        self.history.add_message("user", prompt)
        context = self.memory.build_context(
            system_prompt=str(self.config.get("system_prompt", "")),
            history_messages=self.history.messages,
        )

        provider_key = self.config.get("provider", "openai")
        provider_label = PROVIDER_PRESETS.get(provider_key, {}).get("name", provider_key)
        model_label = self.config.get("model", "gpt-4o-mini")

        print(
            f"\n{Theme.BOLD}{Theme.NEON_PURPLE}◈ NOBAX AI{Theme.RESET} "
            f"{Theme.MUTED}[{provider_label} • {model_label}]{Theme.RESET}"
        )
        divider("─", "purple")

        full_reply: list[str] = []
        try:
            for token in self.client.stream_chat(context):
                full_reply.append(token)
                sys.stdout.write(f"{Theme.WHITE}{token}{Theme.RESET}")
                sys.stdout.flush()
            print()
            divider("─", "blue")
        except AIProviderError as exc:
            print()
            error(str(exc))
            if self.history.messages and self.history.messages[-1]["role"] == "user":
                self.history.messages.pop()
            return ""
        except Exception as exc:
            print()
            error(f"Terjadi kesalahan tak terduga pada AI Assistant: {exc}")
            if self.history.messages and self.history.messages[-1]["role"] == "user":
                self.history.messages.pop()
            return ""

        final_text = "".join(full_reply).strip()
        if final_text:
            self.history.add_message("assistant", final_text)
        return final_text

    def interactive_loop(self, on_open_settings: Optional[Callable[[], None]] = None) -> None:
        """Mode percakapan AI berkelanjutan."""
        clear_screen()
        print_banner()
        info_lines = [
            f"{Theme.ELECTRIC_BLUE}Sesi Aktif :{Theme.RESET} {Theme.WHITE}{self.history.title}{Theme.RESET}",
            f"{Theme.ELECTRIC_BLUE}Provider   :{Theme.RESET} {Theme.WHITE}{self.config.get('provider')} ({self.config.get('model')}){Theme.RESET}",
            f"{Theme.MUTED}Commands   : /new • /past • /open <url> • /settings • /clear • /help • /back{Theme.RESET}",
        ]
        panel("NOBAX AI ASSISTANT — INTERACTIVE MODE", info_lines, accent="purple")

        while True:
            try:
                user_msg = ask("ai@nobax:~")
            except EOFError:
                break

            if not user_msg:
                continue

            if user_msg.lower() in ("/back", "/exit", "exit", "0", "00"):
                break

            parsed = parse_slash_command(user_msg)
            if parsed is not None:
                cmd, arg = parsed
                if cmd == "/new":
                    self.start_new_chat()
                elif cmd == "/past":
                    self.show_and_load_history()
                elif cmd == "/open":
                    if not arg:
                        warn("Contoh penggunaan: /open github")
                    else:
                        res = self.browser.launch(arg)
                        success(res["message"]) if res["success"] else error(res["message"])
                elif cmd == "/clear":
                    clear_screen()
                    print_banner()
                elif cmd == "/settings":
                    if on_open_settings:
                        on_open_settings()
                elif cmd == "/help":
                    panel(
                        "AI ASSISTANT COMMANDS",
                        [
                            "/new        -> Mulai sesi percakapan baru",
                            "/past       -> Buka riwayat percakapan terdahulu",
                            "/open <web> -> Buka website di Google Chrome",
                            "/settings   -> Ubah API Key, Provider, atau Model",
                            "/clear      -> Bersihkan layar terminal",
                            "/back       -> Kembali ke Menu Utama",
                        ],
                        accent="blue",
                    )
                else:
                    warn(f"Perintah tidak dikenal: {cmd}")
                continue

            self.ask_once(user_msg)
