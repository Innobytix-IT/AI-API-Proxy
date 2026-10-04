#!/usr/bin/env bash
# AI-API-Proxy — Linux / macOS Quickstart
# ─────────────────────────────────────────
# Lädt das Repo, installiert alle Dependencies und startet den Launcher.
#
# Nutzung:
#     curl -sSL https://raw.githubusercontent.com/Innobytix-IT/AI-API-Proxy/main/install.sh | bash

set -e

C_CYAN="\033[36m"; C_RED="\033[31m"; C_GREEN="\033[32m"
C_YELLOW="\033[33m"; C_DIM="\033[90m"; C_RESET="\033[0m"

echo -e "\n${C_CYAN}== AI-API-Proxy · Quickstart ==${C_RESET}\n"

# ── Prerequisites ────────────────────────────────────────────────────────
if ! command -v git >/dev/null 2>&1; then
    echo -e "${C_RED}Git nicht gefunden. Bitte zuerst installieren.${C_RESET}"
    exit 1
fi
echo -e "${C_DIM}Git gefunden.${C_RESET}"

PYTHON=""
for cmd in python3 python; do
    if command -v "$cmd" >/dev/null 2>&1; then
        PYTHON="$cmd"
        break
    fi
done
if [ -z "$PYTHON" ]; then
    echo -e "${C_RED}Python >= 3.10 nicht gefunden. Bitte installieren.${C_RESET}"
    exit 1
fi
echo -e "${C_DIM}Python gefunden: $PYTHON${C_RESET}"

# Hinweis für Linux: Tkinter braucht evtl. python3-tk
if [ "$(uname)" = "Linux" ] && ! "$PYTHON" -c "import tkinter" 2>/dev/null; then
    echo -e "${C_YELLOW}Hinweis: tkinter nicht verfügbar — auf Debian/Ubuntu:${C_RESET}"
    echo -e "${C_YELLOW}    sudo apt install python3-tk${C_RESET}"
fi

# ── Clone oder Update ────────────────────────────────────────────────────
INSTALL_DIR="$PWD/AI-API-Proxy"
if [ -d "$INSTALL_DIR" ]; then
    echo -e "\n${C_YELLOW}Verzeichnis existiert bereits — Pull laufender Version...${C_RESET}"
    (cd "$INSTALL_DIR" && git pull --ff-only)
else
    echo -e "\n${C_YELLOW}Klone Repo nach $INSTALL_DIR...${C_RESET}"
    git clone https://github.com/Innobytix-IT/AI-API-Proxy.git "$INSTALL_DIR"
fi

cd "$INSTALL_DIR"

# ── Dependencies ─────────────────────────────────────────────────────────
echo -e "\n${C_YELLOW}Installiere Dependencies...${C_RESET}"
"$PYTHON" -m pip install --upgrade pip --quiet
"$PYTHON" -m pip install -r requirements.txt --quiet

# ── Launcher starten ─────────────────────────────────────────────────────
echo -e "\n${C_GREEN}Starte Launcher — API-Key eintragen und 'Server starten' klicken.${C_RESET}\n"
"$PYTHON" app.py
