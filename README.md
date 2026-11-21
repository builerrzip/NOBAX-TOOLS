# NOBAX TOOLS

**NOBAX TOOLS** (`NOBAX DEX @ TERMUX`) adalah **All-in-One CLI Toolkit** open-source berbasis Python yang dirancang khusus untuk **Android Termux** (serta kompatibel dengan Linux & Desktop). Proyek ini menggabungkan **AI Assistant** dengan dukungan multi-provider & streaming, **Google Chrome Android Intent Launcher**, **15 Utility Tools**, **File Manager**, dan **System Monitor** dalam antarmuka terminal bertema **Hitam, Ungu Neon, dan Biru Elektrik**.

- **Developer:** NOEL
- **Platform Utama:** Android (Termux) & Linux/POSIX
- **Lisensi:** MIT License

---

## Preview Tampilan Terminal

```text
 ███╗   ██╗ ██████╗ ██████╗  █████╗ ██╗  ██╗
 ████╗  ██║██╔═══██╗██╔══██╗██╔══██╗╚██╗██╔╝
 ██╔██╗ ██║██║   ██║██████╔╝███████║ ╚███╔╝ 
 ██║╚██╗██║██║   ██║██╔══██╗██╔══██║ ██╔██╗ 
 ██║ ╚████║╚██████╔╝██████╔╝██║  ██║██╔╝ ██╗
 ╚═╝  ╚═══╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝
        NOBAX DEX @ TERMUX  •  ALL-IN-ONE TOOLKIT
          Developer: NOEL  |  Mode: Termux / CLI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
╭─ MAIN MENU — NOBAX DEX @ TERMUX ───────────────────╮
│ [01] AI ASSISTANT      • Chat AI, Streaming & Riwayat
│ [02] TOOLS CENTER      • 15 Utility Developer & Network
│ [03] BROWSER CENTER    • Buka Website via Chrome Android
│ [04] FILE MANAGER      • Kelola File & Folder Aman
│ [05] SYSTEM INFO       • Perangkat, Android, RAM & Termux
│ [06] SETTINGS          • Konfigurasi API Key & Provider
│ [00] EXIT              • Keluar dari NOBAX TOOLS
╰────────────────────────────────────────────────────╯
nobax@termux:~▸
```

---

## Fitur Utama

### 1. AI Assistant Terintegrasi
- **Direct Prompt:** Ketik pertanyaan langsung di prompt `nobax@termux:~▸` tanpa harus masuk ke sub-menu terlebih dahulu.
- **Multi-Provider Switchable:** Mendukung **OpenAI**, **OpenRouter**, **Groq**, **Google Gemini**, maupun endpoint **Ollama / Custom OpenAI-Compatible**.
- **Real-time Streaming & Riwayat:** Respons mengalir secara real-time dan setiap sesi tersimpan otomatis di `data/history/`.
- **Keamanan API Key:** Tidak ada API key yang ditanam di source code. API key disimpan lokal di `data/config.json` atau `.env` (keduanya diabaikan oleh `.gitignore`).

### 2. Slash Commands & Natural Language Browser
- `/new` — Memulai percakapan AI baru.
- `/past` — Melihat dan memuat riwayat percakapan terdahulu.
- `/open <website>` — Membuka website di Google Chrome Android (contoh: `/open github`).
- `/settings` — Mengatur API key, provider, model, dan streaming.
- `/clear` — Membersihkan tampilan terminal.
- `/help` — Menampilkan panduan lengkap.
- **Perintah Bahasa Alami:** Ketik `"Tolong buka GitHub di Chrome."` langsung di prompt utama atau chat AI, dan NOBAX TOOLS otomatis meluncurkan URL di Google Chrome Android.

### 3. Browser Center (Google Chrome Android Intent)
- Membuka website web (`YouTube`, `Google`, `GitHub`, `ChatGPT`, `Spotify`, atau URL custom) menggunakan **Android Intent (`am start`)** yang menargetkan `com.android.chrome`, dengan fallback otomatis ke browser Android default maupun `termux-open-url`.
- Dilengkapi validasi URL ketat serta manajemen website favorit di `browser/websites.json`.
- *Catatan:* Fitur ini meluncurkan alamat web (URL) ke aplikasi Google Chrome Android melalui Android Intent, bukan menjalankan APK native di dalam browser.

### 4. Tools Center (15 Utility Berfungsi Penuh)
1. **Password Generator** (Kriptografis aman + skor entropi)
2. **QR Code Generator** (Render blok Unicode langsung di layar Termux + ekspor teks)
3. **Text Encoder** (Base64, Base32, URL, Hex, Binary, ROT13, HTML)
4. **Text Decoder** (Base64, Base32, URL, Hex, Binary, ROT13, HTML)
5. **JSON Formatter** (Validasi sintaks, Pretty Print, Minify, Sort Keys)
6. **Hash Generator** (MD5, SHA-1, SHA-224, SHA-256, SHA-384, SHA-512, BLAKE2b)
7. **IP Information** (IP lokal & IP publik/ISP/lokasi)
8. **DNS Lookup** (IPv4 A, IPv6 AAAA, dan detail DNS)
9. **Website Status Checker** (HTTP Status Code, latensi ms, server header)
10. **ASCII Banner Generator** (Offline block-font generator)
11. **File Information** (Ukuran, permission, MIME type, waktu modifikasi, SHA-256)
12. **System Information** (Perangkat, versi Android, Python, baterai, RAM, storage, Termux, koneksi internet)
13. **URL Parser** (Scheme, hostname, port, path, fragment, dan parameter query)
14. **Text Converter** (UPPER, lower, Title, snake_case, kebab-case, camelCase, PascalCase, Reverse)
15. **Random Data Generator** (UUID v4, profil user/email mock, IPv4, MAC address, Hex color, angka acak)

### 5. File Manager & System Information
- Navigasi direktori, membuat folder, membuat & membaca file teks, mengganti nama, dan menghapus file/folder dengan konfirmasi eksplisit serta perlindungan batas akses pengguna.
- Menampilkan informasi perangkat nyata tanpa data palsu (`N/A` jika sensor/properti tidak tersedia di lingkungan saat itu).

---

## Panduan Instalasi di Android Termux

Jalankan perintah berikut secara berurutan di aplikasi **Termux**:

```bash
pkg update -y
pkg install git python -y
git clone https://github.com/USERNAME/NOBAX-TOOLS.git
cd NOBAX-TOOLS
bash install.sh
python main.py
```

*(Ganti `USERNAME` dengan username GitHub pemilik repository).*

---

## Konfigurasi API Key AI

Anda memiliki **dua cara** aman untuk mengatur API Key:

1. **Langsung dari Aplikasi (Direkomendasikan):**
   - Jalankan `python main.py`, lalu pilih menu **`[06] SETTINGS`** atau ketik **`/settings`**.
   - Pilih Provider AI (`openai`, `openrouter`, `groq`, `gemini`, atau `custom`), lalu masukkan API Key Anda.
2. **Melalui File `.env`:**
   ```bash
   cp .env.example .env
   nano .env
   ```
   Isi `NOBAX_API_KEY=sk-...` lalu simpan.

---

## Troubleshooting

- **Chrome tidak terbuka dari Termux:** Pastikan aplikasi **Google Chrome** terinstal di perangkat Android Anda. Pada Android 10+, pastikan izin *"Display over other apps"* untuk Termux diaktifkan di Pengaturan Android agar `am start` dapat meluncurkan aktivitas browser dari background terminal.
- **Status Baterai menampilkan `N/A`:** Instal paket `termux-api` (`pkg install termux-api`) beserta aplikasi pendamping **Termux:API** dari F-Droid agar pembacaan sensor baterai Android didukung penuh.
- **Error `API Key AI belum dikonfigurasi`:** Buka `/settings` dan masukkan API Key dari provider pilihan Anda, atau gunakan provider `custom` dengan endpoint Ollama lokal (`http://localhost:11434/v1/chat/completions`).

---

## Automated Testing

Untuk menjalankan pengujian otomatis seluruh modul:

```bash
python -m unittest discover -s tests -p "test_*.py"
```
