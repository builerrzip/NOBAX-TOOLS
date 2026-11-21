"""
Automated Unit Tests untuk seluruh komponen NOBAX TOOLS.
"""

import tempfile
import unittest
from pathlib import Path

from ai.history import HistoryManager
from ai.memory import ConversationMemory
from browser.launcher import BrowserLauncher
from core.commands import detect_browser_intent, parse_slash_command
from core.config import ConfigManager, mask_secret
from manager.file_manager import FileManager
from tools.decoder import decode_text
from tools.encoder import convert_text, encode_text
from tools.generator import (
    generate_ascii_banner,
    generate_password,
    generate_random_data,
)
from tools.hash_tool import hash_text
from tools.json_tool import format_json
from tools.network import parse_url_details
from tools.qr import build_qr_ascii, qrcode as qr_lib
from tools.system import get_system_info


class TestNobaxTools(unittest.TestCase):
    def test_config_and_secret_masking(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cfg = ConfigManager(base_dir=Path(tmp))
            cfg.set_provider("groq")
            self.assertEqual(cfg.get("provider"), "groq")
            cfg.set("api_key", "gsk_1234567890abcdef")
            masked = mask_secret(cfg.get("api_key"))
            self.assertTrue(masked.startswith("gsk_"))
            self.assertTrue(masked.endswith("cdef"))
            self.assertNotIn("567890ab", masked)

    def test_commands_and_nlp_browser_intent(self) -> None:
        self.assertEqual(parse_slash_command("/open github"), ("/open", "github"))
        self.assertEqual(parse_slash_command("/new"), ("/new", ""))
        self.assertIsNone(parse_slash_command("Halo apa kabar?"))

        self.assertEqual(detect_browser_intent("Tolong buka GitHub di Chrome."), "GitHub")
        self.assertEqual(detect_browser_intent("buka YouTube"), "YouTube")
        self.assertIsNone(detect_browser_intent("Jelaskan cara kerja DNS"))

    def test_browser_launcher_validation_and_intents(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            launcher = BrowserLauncher(bookmarks_path=Path(tmp) / "websites.json")
            ok, url, _ = launcher.validate_url("github")
            self.assertTrue(ok)
            self.assertEqual(url, "https://github.com")

            ok2, url2, _ = launcher.validate_url("example.org/docs")
            self.assertTrue(ok2)
            self.assertEqual(url2, "https://example.org/docs")

            bad, _, _ = launcher.validate_url("javascript:alert(1)")
            self.assertFalse(bad)

            bad_inj, _, _ = launcher.validate_url("https://evil.com; rm -rf /")
            self.assertFalse(bad_inj)

            intents = launcher.build_android_intents("https://github.com", prefer_chrome=True)
            self.assertIn("com.android.chrome", " ".join(intents[0][1]))

    def test_ai_history_and_memory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            hist = HistoryManager(history_dir=Path(tmp))
            sid = hist.new_session()
            hist.add_message("user", "Apa itu Termux?")
            hist.add_message("assistant", "Termux adalah terminal emulator Linux untuk Android.")

            sessions = hist.list_sessions()
            self.assertEqual(len(sessions), 1)
            self.assertEqual(sessions[0]["session_id"], sid)

            mem = ConversationMemory(max_turns=10)
            ctx = mem.build_context("System prompt", hist.messages)
            self.assertEqual(ctx[0]["role"], "system")
            self.assertEqual(len(ctx), 3)

    def test_generators_and_qr(self) -> None:
        pwd = generate_password(length=20, use_symbols=True)
        self.assertEqual(len(pwd["password"]), 20)
        self.assertGreater(pwd["entropy_bits"], 80)

        banner = generate_ascii_banner("NOBAX")
        self.assertEqual(len(banner.splitlines()), 5)

        uuids = generate_random_data("uuid", count=3)
        self.assertEqual(len(uuids), 3)

        if qr_lib is not None:
            qr_art = build_qr_ascii("https://github.com")
            self.assertIn("█", qr_art)

    def test_encoder_decoder_and_converter(self) -> None:
        sample = "NOBAX TOOLS @ Termux 2026!"
        for method in ("base64", "base32", "url", "hex", "binary", "rot13", "html"):
            enc = encode_text(sample, method)
            dec = decode_text(enc, method)
            self.assertEqual(dec, sample)

        self.assertEqual(convert_text("nobax tools cli", "snake"), "nobax_tools_cli")
        self.assertEqual(convert_text("nobax tools cli", "camel"), "nobaxToolsCli")

    def test_json_hash_url_and_system_tools(self) -> None:
        j_ok = format_json('{"b":1,"a":2}', sort_keys=True)
        self.assertTrue(j_ok["valid"])
        self.assertIn('"a": 2', j_ok["output"])

        j_bad = format_json('{"broken": }')
        self.assertFalse(j_bad["valid"])

        self.assertEqual(hash_text("nobax", "sha256"), "3605ba615f61ede293a92396e6ea491fc0d5cca883515b3cdc318f46b261a6f5")

        parsed = parse_url_details("https://github.com/NOEL/NOBAX-TOOLS?tab=readme#install")
        self.assertTrue(parsed["valid"])
        self.assertEqual(parsed["hostname"], "github.com")
        self.assertEqual(parsed["query_params"]["tab"], ["readme"])

        sys_info = get_system_info()
        self.assertIn("python_version", sys_info)
        self.assertIn("internet", sys_info)

    def test_file_manager_crud_and_security(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fm = FileManager(start_dir=Path(tmp))
            self.assertFalse(fm.is_accessible_path(Path("/system/build.prop")))

            ok_dir, _ = fm.create_folder("notes")
            self.assertTrue(ok_dir)

            ok_file, _ = fm.create_file("hello.txt", "Halo NOBAX")
            self.assertTrue(ok_file)

            ok_read, content = fm.read_text_file("hello.txt")
            self.assertTrue(ok_read)
            self.assertEqual(content, "Halo NOBAX")

            ok_ren, _ = fm.rename_item("hello.txt", "renamed.txt")
            self.assertTrue(ok_ren)

            ok_del, _ = fm.delete_item("renamed.txt")
            self.assertTrue(ok_del)


if __name__ == "__main__":
    unittest.main()
