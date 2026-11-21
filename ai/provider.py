"""
Multi-Provider AI Client (OpenAI, OpenRouter, Groq, Gemini, Ollama/Custom).
"""

import json
import urllib.error
import urllib.request
from typing import Generator

try:
    import requests
except ImportError:
    requests = None

from core.config import ConfigManager


class AIProviderError(Exception):
    """Error terstruktur saat komunikasi dengan API AI gagal."""


class AIProviderClient:
    def __init__(self, config: ConfigManager) -> None:
        self.config = config

    def _build_headers(self) -> dict[str, str]:
        api_key = str(self.config.get("api_key", "")).strip()
        headers = {
            "Content-Type": "application/json",
            "Accept": "text/event-stream, application/json",
            "User-Agent": "NOBAX-TOOLS/1.0 (Termux-Android)",
        }
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        if self.config.get("provider") == "openrouter":
            headers["HTTP-Referer"] = "https://github.com/NOEL/NOBAX-TOOLS"
            headers["X-Title"] = "NOBAX TOOLS"
        return headers

    def _build_payload(self, messages: list[dict[str, str]], stream: bool) -> dict:
        return {
            "model": self.config.get("model", "gpt-4o-mini"),
            "messages": messages,
            "temperature": float(self.config.get("temperature", 0.7)),
            "max_tokens": int(self.config.get("max_tokens", 1024)),
            "stream": stream,
        }

    def _format_http_error(self, status_code: int, detail: str = "") -> str:
        clean_detail = detail[:220].replace("\n", " ").strip()
        if status_code == 401:
            return "API Key tidak valid atau ditolak (HTTP 401). Periksa kembali key Anda di /settings."
        if status_code == 403:
            return "Akses ditolak oleh provider AI (HTTP 403). Periksa izin akun atau region Anda."
        if status_code == 404:
            return "Endpoint atau Model AI tidak ditemukan (HTTP 404). Cek nama model di /settings."
        if status_code == 429:
            return "Batas kuota / rate limit tercapai (HTTP 429). Coba lagi beberapa saat lagi."
        if status_code >= 500:
            return f"Server provider AI sedang bermasalah (HTTP {status_code})."
        return f"Permintaan AI gagal (HTTP {status_code}): {clean_detail}"

    def stream_chat(self, messages: list[dict[str, str]]) -> Generator[str, None, None]:
        """Menghasilkan potongan teks jawaban AI secara real-time."""
        if not self.config.has_api_key():
            raise AIProviderError(
                "API Key AI belum dikonfigurasi! Ketik /settings atau menu [06] untuk memasukkan API Key Anda."
            )

        base_url = str(self.config.get("base_url", "")).strip()
        if not base_url:
            raise AIProviderError("Base URL provider AI kosong. Atur melalui /settings.")

        use_stream = bool(self.config.get("stream", True))
        headers = self._build_headers()
        payload = self._build_payload(messages, stream=use_stream)

        if requests is not None:
            yield from self._request_via_requests(base_url, headers, payload, use_stream)
        else:
            yield from self._request_via_urllib(base_url, headers, payload, use_stream)

    def _request_via_requests(
        self, url: str, headers: dict[str, str], payload: dict, use_stream: bool
    ) -> Generator[str, None, None]:
        try:
            resp = requests.post(
                url,
                headers=headers,
                json=payload,
                stream=use_stream,
                timeout=(10, 60),
            )
        except requests.exceptions.Timeout as exc:
            raise AIProviderError("Koneksi ke server AI timeout. Periksa jaringan internet Anda.") from exc
        except requests.exceptions.ConnectionError as exc:
            raise AIProviderError("Tidak dapat terhubung ke server AI. Pastikan internet aktif.") from exc
        except requests.exceptions.RequestException as exc:
            raise AIProviderError(f"Error jaringan saat menghubungi AI: {exc}") from exc

        if resp.status_code >= 400:
            try:
                err_body = resp.text
            except Exception:
                err_body = ""
            raise AIProviderError(self._format_http_error(resp.status_code, err_body))

        if not use_stream:
            try:
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                if content:
                    yield content
                return
            except Exception as exc:
                raise AIProviderError(f"Format respons AI tidak valid: {exc}") from exc

        emitted = False
        for raw_line in resp.iter_lines(decode_unicode=True):
            if not raw_line:
                continue
            line = raw_line.strip()
            if line.startswith("data:"):
                data_str = line[5:].strip()
                if data_str == "[DONE]":
                    break
                try:
                    chunk = json.loads(data_str)
                    choices = chunk.get("choices", [])
                    if choices:
                        delta = choices[0].get("delta", {})
                        token = delta.get("content")
                        if token:
                            emitted = True
                            yield token
                except json.JSONDecodeError:
                    continue

        if not emitted:
            try:
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                if content:
                    yield content
            except Exception:
                pass

    def _request_via_urllib(
        self, url: str, headers: dict[str, str], payload: dict, use_stream: bool
    ) -> Generator[str, None, None]:
        body_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=body_bytes, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                if not use_stream:
                    data = json.loads(resp.read().decode("utf-8"))
                    yield data["choices"][0]["message"]["content"]
                    return

                for raw_line in resp:
                    line = raw_line.decode("utf-8", errors="replace").strip()
                    if line.startswith("data:"):
                        data_str = line[5:].strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data_str)
                            choices = chunk.get("choices", [])
                            if choices:
                                token = choices[0].get("delta", {}).get("content")
                                if token:
                                    yield token
                        except json.JSONDecodeError:
                            continue
        except urllib.error.HTTPError as exc:
            err_detail = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
            raise AIProviderError(self._format_http_error(exc.code, err_detail)) from exc
        except urllib.error.URLError as exc:
            raise AIProviderError(f"Gagal terhubung ke server AI: {exc.reason}") from exc
