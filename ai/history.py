"""
Penyimpanan Riwayat Percakapan AI berbasis JSON di data/history/.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any


class HistoryManager:
    def __init__(self, history_dir: Path | None = None) -> None:
        root = Path(__file__).resolve().parent.parent
        self.history_dir = history_dir or (root / "data" / "history")
        self.history_dir.mkdir(parents=True, exist_ok=True)
        self.session_id: str = ""
        self.title: str = "Percakapan Baru"
        self.created_at: str = ""
        self.messages: list[dict[str, str]] = []
        self.new_session()

    def new_session(self) -> str:
        now = datetime.now()
        short_uid = uuid.uuid4().hex[:6]
        self.session_id = f"{now.strftime('%Y%m%d_%H%M%S')}_{short_uid}"
        self.created_at = now.strftime("%Y-%m-%d %H:%M:%S")
        self.title = "Percakapan Baru"
        self.messages = []
        return self.session_id

    @property
    def _session_path(self) -> Path:
        return self.history_dir / f"session_{self.session_id}.json"

    def add_message(self, role: str, content: str) -> None:
        self.messages.append(
            {
                "role": role,
                "content": content,
                "timestamp": datetime.now().strftime("%H:%M:%S"),
            }
        )
        if role == "user" and self.title == "Percakapan Baru":
            clean = " ".join(content.strip().split())
            self.title = (clean[:42] + "...") if len(clean) > 42 else clean
        self.save_session()

    def save_session(self) -> None:
        if not self.messages:
            return
        payload = {
            "session_id": self.session_id,
            "title": self.title,
            "created_at": self.created_at,
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "messages": self.messages,
        }
        self._session_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def list_sessions(self, limit: int = 15) -> list[dict[str, Any]]:
        sessions: list[dict[str, Any]] = []
        files = sorted(self.history_dir.glob("session_*.json"), reverse=True)
        for fp in files[:limit]:
            try:
                data = json.loads(fp.read_text(encoding="utf-8"))
                sessions.append(
                    {
                        "session_id": data.get("session_id", fp.stem.replace("session_", "")),
                        "title": data.get("title", "Tanpa Judul"),
                        "created_at": data.get("created_at", "-"),
                        "count": len(data.get("messages", [])),
                    }
                )
            except (json.JSONDecodeError, OSError):
                continue
        return sessions

    def load_session(self, session_id: str) -> bool:
        target = self.history_dir / f"session_{session_id}.json"
        if not target.exists():
            return False
        try:
            data = json.loads(target.read_text(encoding="utf-8"))
            self.session_id = data.get("session_id", session_id)
            self.title = data.get("title", "Percakapan Tersimpan")
            self.created_at = data.get("created_at", "")
            self.messages = data.get("messages", [])
            return True
        except (json.JSONDecodeError, OSError):
            return False
