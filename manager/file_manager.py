"""
File Manager untuk NOBAX TOOLS.
"""

import shutil
from pathlib import Path

from core.ui import (
    Theme,
    ask,
    clear_screen,
    error,
    panel,
    pause,
    print_banner,
    success,
    warn,
)
from tools.system import format_bytes

RESTRICTED_ROOTS = ("/system", "/proc", "/sys", "/dev", "/root", "/boot", "/sbin")


class FileManager:
    def __init__(self, start_dir: Path | None = None) -> None:
        self.current_dir = (start_dir or Path.cwd()).resolve()

    def is_accessible_path(self, target: Path) -> bool:
        resolved = str(target.resolve())
        for restricted in RESTRICTED_ROOTS:
            if resolved == restricted or resolved.startswith(restricted + "/"):
                return False
        return True

    def list_entries(self) -> list[Path]:
        if not self.is_accessible_path(self.current_dir):
            raise PermissionError("Akses ke direktori sistem dibatasi.")
        entries = list(self.current_dir.iterdir())
        entries.sort(key=lambda p: (not p.is_dir(), p.name.lower()))
        return entries

    def change_dir(self, target_str: str) -> tuple[bool, str]:
        if target_str == "..":
            candidate = self.current_dir.parent
        else:
            raw = Path(target_str).expanduser()
            candidate = raw if raw.is_absolute() else (self.current_dir / raw)

        try:
            resolved = candidate.resolve()
        except OSError as exc:
            return False, f"Path tidak valid: {exc}"

        if not self.is_accessible_path(resolved):
            return False, "Akses ditolak: Direktori sistem berada di luar izin pengguna."
        if not resolved.exists() or not resolved.is_dir():
            return False, f"Direktori tidak ditemukan: {resolved}"

        try:
            list(resolved.iterdir())
        except PermissionError:
            return False, "Permission denied oleh sistem Android/OS."

        self.current_dir = resolved
        return True, f"Berpindah ke: {self.current_dir}"

    def create_folder(self, folder_name: str) -> tuple[bool, str]:
        clean = folder_name.strip()
        if not clean or "/" in clean or "\\" in clean:
            return False, "Nama folder tidak valid."
        target = (self.current_dir / clean).resolve()
        if not self.is_accessible_path(target):
            return False, "Akses ditolak."
        try:
            target.mkdir(parents=False, exist_ok=False)
            return True, f"Folder '{clean}' berhasil dibuat."
        except FileExistsError:
            return False, f"Folder '{clean}' sudah ada."
        except PermissionError:
            return False, "Tidak memiliki izin menulis di direktori ini."

    def create_file(self, file_name: str, content: str = "") -> tuple[bool, str]:
        clean = file_name.strip()
        if not clean or "/" in clean or "\\" in clean:
            return False, "Nama file tidak valid."
        target = (self.current_dir / clean).resolve()
        if not self.is_accessible_path(target):
            return False, "Akses ditolak."
        if target.exists():
            return False, f"File '{clean}' sudah ada."
        try:
            target.write_text(content, encoding="utf-8")
            return True, f"File '{clean}' berhasil dibuat ({len(content)} karakter)."
        except PermissionError:
            return False, "Tidak memiliki izin menulis di direktori ini."

    def read_text_file(self, file_name: str, max_chars: int = 4000) -> tuple[bool, str]:
        target = (self.current_dir / file_name.strip()).resolve()
        if not self.is_accessible_path(target):
            return False, "Akses ditolak."
        if not target.is_file():
            return False, "File tidak ditemukan."
        try:
            raw_bytes = target.read_bytes()
            if b"\x00" in raw_bytes[:512]:
                return False, "File terdeteksi sebagai file biner, bukan file teks."
            text = raw_bytes.decode("utf-8", errors="replace")
            if len(text) > max_chars:
                text = text[:max_chars] + f"\n\n... [Terpotong, total {len(text)} karakter]"
            return True, text
        except PermissionError:
            return False, "Permission denied saat membaca file."

    def rename_item(self, old_name: str, new_name: str) -> tuple[bool, str]:
        src = (self.current_dir / old_name.strip()).resolve()
        clean_new = new_name.strip()
        if not clean_new or "/" in clean_new or "\\" in clean_new:
            return False, "Nama baru tidak valid."
        dst = (self.current_dir / clean_new).resolve()
        if not (self.is_accessible_path(src) and self.is_accessible_path(dst)):
            return False, "Akses ditolak."
        if not src.exists():
            return False, f"Item '{old_name}' tidak ditemukan."
        if dst.exists():
            return False, f"Target '{clean_new}' sudah ada."
        try:
            src.rename(dst)
            return True, f"Berhasil mengganti nama '{old_name}' -> '{clean_new}'."
        except PermissionError:
            return False, "Permission denied saat mengganti nama."

    def delete_item(self, item_name: str) -> tuple[bool, str]:
        target = (self.current_dir / item_name.strip()).resolve()
        if not self.is_accessible_path(target) or target == self.current_dir:
            return False, "Akses ditolak atau target tidak valid."
        if not target.exists():
            return False, f"Item '{item_name}' tidak ditemukan."
        try:
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()
            return True, f"'{item_name}' telah dihapus permanen."
        except PermissionError:
            return False, "Permission denied saat menghapus item."

    def interactive_menu(self) -> None:
        while True:
            clear_screen()
            print_banner()
            try:
                entries = self.list_entries()
            except PermissionError as exc:
                error(str(exc))
                self.current_dir = Path.home().resolve()
                entries = self.list_entries()

            lines = [
                f"{Theme.ELECTRIC_BLUE}Direktori :{Theme.RESET} {Theme.WHITE}{self.current_dir}{Theme.RESET}",
                "",
            ]
            if not entries:
                lines.append(f"{Theme.MUTED}(Direktori kosong){Theme.RESET}")
            else:
                for idx, entry in enumerate(entries[:25], 1):
                    if entry.is_dir():
                        lines.append(
                            f"{Theme.NEON_PURPLE}[{idx:02d}]{Theme.RESET} "
                            f"{Theme.BOLD}{Theme.ELECTRIC_BLUE}[DIR]  {entry.name}/{Theme.RESET}"
                        )
                    else:
                        try:
                            sz = format_bytes(entry.stat().st_size)
                        except OSError:
                            sz = "?"
                        lines.append(
                            f"{Theme.NEON_PURPLE}[{idx:02d}]{Theme.RESET} "
                            f"{Theme.WHITE}[FILE] {entry.name}{Theme.RESET} "
                            f"{Theme.MUTED}({sz}){Theme.RESET}"
                        )
                if len(entries) > 25:
                    lines.append(f"{Theme.MUTED}... dan {len(entries) - 25} item lainnya{Theme.RESET}")

            lines.extend(
                [
                    "",
                    f"{Theme.NEON_PURPLE}[..]{Theme.RESET} Naik Folder   "
                    f"{Theme.NEON_PURPLE}[CD]{Theme.RESET} Pindah Path   "
                    f"{Theme.NEON_PURPLE}[MD]{Theme.RESET} Buat Folder",
                    f"{Theme.NEON_PURPLE}[NF]{Theme.RESET} Buat File     "
                    f"{Theme.NEON_PURPLE}[RD]{Theme.RESET} Baca File     "
                    f"{Theme.NEON_PURPLE}[RN]{Theme.RESET} Rename",
                    f"{Theme.RED}[RM]{Theme.RESET} Hapus Item    "
                    f"{Theme.RED}[00]{Theme.RESET} Kembali ke Menu Utama",
                ]
            )
            panel("FILE MANAGER — USER SANDBOXED", lines, accent="blue")
            cmd = ask("nobax@files:~")
            low = cmd.lower()

            if low in ("0", "00"):
                break
            elif cmd == "..":
                ok, msg = self.change_dir("..")
                if not ok:
                    error(msg)
                    pause()
            elif cmd.isdigit() and 1 <= int(cmd) <= min(25, len(entries)):
                chosen = entries[int(cmd) - 1]
                if chosen.is_dir():
                    ok, msg = self.change_dir(chosen.name)
                    if not ok:
                        error(msg)
                        pause()
                else:
                    ok, content = self.read_text_file(chosen.name)
                    if ok:
                        panel(f"ISI FILE: {chosen.name}", content.splitlines() or ["(Kosong)"], accent="purple")
                    else:
                        error(content)
                    pause()
            elif low == "cd":
                dest = ask("Masukkan nama subfolder atau path tujuan")
                ok, msg = self.change_dir(dest)
                success(msg) if ok else error(msg)
                pause()
            elif low == "md":
                fname = ask("Nama folder baru")
                ok, msg = self.create_folder(fname)
                success(msg) if ok else error(msg)
                pause()
            elif low == "nf":
                fname = ask("Nama file baru (cth: catatan.txt)")
                body = ask("Isi teks awal file")
                ok, msg = self.create_file(fname, body + "\n" if body else "")
                success(msg) if ok else error(msg)
                pause()
            elif low == "rd":
                fname = ask("Nama file teks yang akan dibaca")
                ok, content = self.read_text_file(fname)
                if ok:
                    panel(f"ISI FILE: {fname}", content.splitlines() or ["(Kosong)"], accent="purple")
                else:
                    error(content)
                pause()
            elif low == "rn":
                old_n = ask("Nama file/folder lama")
                new_n = ask("Nama baru")
                ok, msg = self.rename_item(old_n, new_n)
                success(msg) if ok else error(msg)
                pause()
            elif low == "rm":
                target_n = ask("Nama file/folder yang akan dihapus")
                confirm = ask(f"Yakin ingin menghapus '{target_n}' secara permanen? (y/N)").lower()
                if confirm == "y":
                    ok, msg = self.delete_item(target_n)
                    success(msg) if ok else error(msg)
                else:
                    warn("Penghapusan dibatalkan.")
                pause()
            else:
                warn("Perintah File Manager tidak dikenal.")
                pause()
