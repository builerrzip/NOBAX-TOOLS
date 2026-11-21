"""
Manajemen Konfigurasi Aman untuk NOBAX TOOLS.
Tidak pernah menyimpan API key hardcoded di source code.
"""

import json
import os
from pathlib import Path
from typing import Any

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


PROVIDER_PRESETS: dict[str, dict[str, Any]] = {
    "openai": {
        "name": "OpenAI",
        "base_url": "https://api.openai.com/v1/chat/completions",
        "default_model": "gpt-4o-mini",
        "env_keys": ["NOBAX_API_KEY", "OPENAI_API_KEY"],
    },
    "openrouter": {
        "name": "OpenRouter",
        "base_url": "https://openrouter.ai/api/v1/chat/completions",
        "default_model": "openai/gpt-4o-mini",
        "env_keys": ["NOBAX_API_KEY", "OPENROUTER_API_KEY"],
    },
    "groq": {
        "name": "Groq Cloud",
        "base_url": "https://api.groq.com/openai/v1/chat/completions",
        "default_model": "llama-3.3-70b-versatile",
        "env_keys": ["NOBAX_API_KEY", "GROQ_API_KEY"],
    },
    "gemini": {
        "name": "Google Gemini (OpenAI-Compat)",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
        "default_model": "gemini-2.5-flash",
        "env_keys": ["NOBAX_API_KEY", "GEMINI_API_KEY"],
    },
    "custom": {
        "name": "Custom / Ollama Local",
        "base_url": "http://localhost:11434/v1/chat/completions",
        "default_model": "llama3",
        "env_keys": ["NOBAX_API_KEY"],
    },
}

DEFAULT_CONFIG: dict[str, Any] = {
    "provider": "openai",
    "api_key": "",
    "model": "gpt-4o-mini",
    "base_url": "https://api.openai.com/v1/chat/completions",
    "stream": True,
    "temperature": 0.7,
    "max_tokens": 1024,
    "prefer_chrome": True,
    "system_prompt": (
        "Kamu adalah NOBAX AI, asisten terminal cerdas di dalam NOBAX TOOLS pada Android Termux. "
        "Berikan jawaban yang akurat, ringkas, terstruktur, dan langsung ke inti permasalahan."
    ),
}


def mask_secret(secret: str) -> str:
    """Menyamarkan API key agar aman ditampilkan di terminal."""
    if not secret:
        return "(Belum diatur)"
    if len(secret) <= 8:
        return "*" * len(secret)
    return f"{secret[:4]}{'*' * (len(secret) - 8)}{secret[-4:]}"


class ConfigManager:
    def __init__(self, base_dir: Path | None = None) -> None:
        self.root_dir = base_dir or Path(__file__).resolve().parent.parent
        self.data_dir = self.root_dir / "data"
        self.history_dir = self.data_dir / "history"
        self.config_file = self.data_dir / "config.json"
        self.env_file = self.root_dir / ".env"

        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.history_dir.mkdir(parents=True, exist_ok=True)

        if load_dotenv is not None and self.env_file.exists():
            load_dotenv(dotenv_path=self.env_file, override=False)

        self.data: dict[str, Any] = dict(DEFAULT_CONFIG)
        self.load()

    def load(self) -> dict[str, Any]:
        """Memuat konfigurasi dari data/config.json lalu melapisinya dengan environment variables."""
        if self.config_file.exists():
            try:
                raw = json.loads(self.config_file.read_text(encoding="utf-8"))
                if isinstance(raw, dict):
                    self.data.update(raw)
            except (json.JSONDecodeError, OSError):
                pass

        env_provider = os.getenv("NOBAX_PROVIDER", "").strip().lower()
        if env_provider in PROVIDER_PRESETS and not self.config_file.exists():
            self.set_provider(env_provider, save=False)

        if os.getenv("NOBAX_MODEL"):
            self.data["model"] = os.getenv("NOBAX_MODEL", self.data["model"]).strip()
        if os.getenv("NOBAX_BASE_URL"):
            self.data["base_url"] = os.getenv("NOBAX_BASE_URL", self.data["base_url"]).strip()
        if os.getenv("NOBAX_STREAM"):
            self.data["stream"] = os.getenv("NOBAX_STREAM", "true").lower() in ("1", "true", "yes")

        if not self.data.get("api_key"):
            provider = self.data.get("provider", "openai")
            preset = PROVIDER_PRESETS.get(provider, PROVIDER_PRESETS["openai"])
            for env_name in preset["env_keys"]:
                val = os.getenv(env_name, "").strip()
                if val:
                    self.data["api_key"] = val
                    break

        return self.data

    def save(self) -> None:
        """Menyimpan konfigurasi lokal ke data/config.json (gitignored) dengan permission aman."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.config_file.write_text(
            json.dumps(self.data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        try:
            os.chmod(self.config_file, 0o600)
        except OSError:
            pass

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def set(self, key: str, value: Any, save: bool = True) -> None:
        self.data[key] = value
        if save:
            self.save()

    def set_provider(self, provider_key: str, save: bool = True) -> bool:
        key = provider_key.strip().lower()
        if key not in PROVIDER_PRESETS:
            return False
        preset = PROVIDER_PRESETS[key]
        self.data["provider"] = key
        self.data["base_url"] = preset["base_url"]
        self.data["model"] = preset["default_model"]

        if not self.data.get("api_key"):
            for env_name in preset["env_keys"]:
                val = os.getenv(env_name, "").strip()
                if val:
                    self.data["api_key"] = val
                    break
        if save:
            self.save()
        return True

    def has_api_key(self) -> bool:
        provider = self.data.get("provider", "openai")
        if provider == "custom" and "localhost" in self.data.get("base_url", ""):
            return True
        return bool(str(self.data.get("api_key", "")).strip())
