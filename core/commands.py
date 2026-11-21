"""
Command System & Natural Language Browser Intent Detector untuk NOBAX TOOLS.
"""

import re
from typing import Optional


NLP_OPEN_PATTERNS = [
    re.compile(
        r"^(?:tolong\s+|please\s+|coba\s+)?(?:buka|bukakan|open|launch|akses)\s+"
        r"(?:website\s+|situs\s+|web\s+)?(?P<target>.+?)"
        r"(?:\s+(?:di|in|on|via|menggunakan|pakai)\s+(?:google\s+)?(?:chrome|browser))?[.!?]*$",
        re.IGNORECASE,
    ),
]


def detect_browser_intent(text: str) -> Optional[str]:
    """
    Mendeteksi apakah kalimat pengguna merupakan permintaan membuka website di browser.
    Contoh: 'Tolong buka GitHub di Chrome.' -> 'GitHub'
    """
    cleaned = text.strip()
    if not cleaned:
        return None

    for pattern in NLP_OPEN_PATTERNS:
        match = pattern.match(cleaned)
        if match:
            target = match.group("target").strip(" \"'.,!?")
            if target:
                return target
    return None


def parse_slash_command(text: str) -> Optional[tuple[str, str]]:
    """
    Memisahkan slash command menjadi (command, argument).
    Mengembalikan None jika input bukan slash command.
    """
    cleaned = text.strip()
    if not cleaned.startswith("/"):
        return None
    parts = cleaned.split(maxsplit=1)
    cmd = parts[0].lower()
    arg = parts[1].strip() if len(parts) > 1 else ""
    return cmd, arg
