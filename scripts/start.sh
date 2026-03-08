#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════
#   DeepRoulette  --  Start  (Linux / macOS)
#   Usage:  bash scripts/start.sh
# ══════════════════════════════════════════════════════════

# Always run from the project root
cd "$(dirname "$0")/.." || exit 1

if command -v python3 &>/dev/null; then
    PYTHON=python3
else
    PYTHON=python
fi

$PYTHON main.py

if [ $? -ne 0 ]; then
    echo ""
    echo " [ERROR] The program encountered an error."
    echo ""
    echo " If this is your first time running the program,"
    echo " please run:  bash setup.sh  first."
    echo ""
    read -rp " Press Enter to exit..."
fi
