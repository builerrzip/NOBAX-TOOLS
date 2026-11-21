#!/usr/bin/env bash
# NOBAX TOOLS - Termux & Linux Automated Installer
# Developer: NOEL

set -e

PURPLE='\033[1;35m'
BLUE='\033[1;36m'
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
RED='\033[1;31m'
NC='\033[0m'

echo -e "${PURPLE}==================================================${NC}"
echo -e "${PURPLE}        NOBAX TOOLS - TERMUX INSTALLER            ${NC}"
echo -e "${BLUE}        NOBAX DEX @ TERMUX | Dev: NOEL            ${NC}"
echo -e "${PURPLE}==================================================${NC}"

# 1. Periksa Python
echo -e "\n${BLUE}[1/6] Memeriksa instalasi Python...${NC}"
if ! command -v python3 >/dev/null 2>&1 && ! command -v python >/dev/null 2>&1; then
    echo -e "${YELLOW}[!] Python tidak ditemukan. Mencoba menginstal...${NC}"
    if command -v pkg >/dev/null 2>&1; then
        pkg update -y && pkg install python -y
    else
        echo -e "${RED}[✘] Python tidak ditemukan. Silakan instal Python 3.9+ terlebih dahulu.${NC}"
        exit 1
    fi
fi

PYTHON_BIN="python3"
if ! command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python"
fi
echo -e "${GREEN}[✔] Python terdeteksi: $($PYTHON_BIN --version)${NC}"

# 2. Periksa Git
echo -e "\n${BLUE}[2/6] Memeriksa instalasi Git...${NC}"
if ! command -v git >/dev/null 2>&1; then
    echo -e "${YELLOW}[!] Git tidak ditemukan. Mencoba menginstal...${NC}"
    if command -v pkg >/dev/null 2>&1; then
        pkg install git -y
    else
        echo -e "${YELLOW}[!] Git tidak terinstal, melanjutkan instalasi lokal.${NC}"
    fi
else
    echo -e "${GREEN}[✔] Git terdeteksi: $(git --version)${NC}"
fi

# 3. Instal Dependencies
echo -e "\n${BLUE}[3/6] Menginstal dependencies Python...${NC}"
$PYTHON_BIN -m pip install --upgrade pip >/dev/null 2>&1 || true
if [ -f "requirements.txt" ]; then
    $PYTHON_BIN -m pip install -r requirements.txt
    echo -e "${GREEN}[✔] Semua dependencies berhasil diinstal.${NC}"
else
    echo -e "${RED}[✘] File requirements.txt tidak ditemukan!${NC}"
    exit 1
fi

# 4. Membuat direktori konfigurasi & riwayat
echo -e "\n${BLUE}[4/6] Menyiapkan direktori data & konfigurasi...${NC}"
mkdir -p data/history data/exports
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    cp .env.example .env
    chmod 600 .env
    echo -e "${GREEN}[✔] File .env dibuat dari .env.example (mode aman 600).${NC}"
fi
echo -e "${GREEN}[✔] Direktori data/ dan data/history/ siap.${NC}"

# 5. Memastikan permission sesuai
echo -e "\n${BLUE}[5/6] Mengatur izin eksekusi file...${NC}"
chmod +x main.py install.sh
echo -e "${GREEN}[✔] Permission main.py dan install.sh diperbarui.${NC}"

# 6. Pemeriksaan awal & unit test
echo -e "\n${BLUE}[6/6] Menjalankan verifikasi sistem & automated tests...${NC}"
$PYTHON_BIN main.py --check
$PYTHON_BIN -m unittest discover -s tests -p "test_*.py"

echo -e "\n${PURPLE}==================================================${NC}"
echo -e "${GREEN}[✔] INSTALASI NOBAX TOOLS SELESAI!${NC}"
echo -e "${BLUE}Jalankan aplikasi dengan perintah:${NC} ${PURPLE}python main.py${NC}"
echo -e "${PURPLE}==================================================${NC}"
