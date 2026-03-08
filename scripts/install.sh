#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════
#   DeepRoulette  --  First Time Setup  (Linux / macOS)
#   Run once before starting the program.
#   Usage:  bash scripts/setup.sh
# ══════════════════════════════════════════════════════

# Always run from the project root
cd "$(dirname "$0")/.." || exit 1

set -e   # Exit immediately on any error

echo ""
echo " ====================================================="
echo "   DeepRoulette  --  First Time Setup"
echo " ====================================================="
echo ""
echo " This will install all required Python packages."
echo " This only needs to be done ONCE."
echo ""
read -rp " Press Enter to continue (Ctrl+C to cancel)..."

# ── Step 1: Check Python ───────────────────────────────────
echo ""
echo " [Step 1/4] Checking Python installation..."

if command -v python3 &>/dev/null; then
    PYTHON=python3
    PIP=pip3
elif command -v python &>/dev/null; then
    PYTHON=python
    PIP=pip
else
    echo ""
    echo " [ERROR] Python was not found on your system!"
    echo ""
    echo " Please install Python 3 first:"
    echo "   Ubuntu/Debian : sudo apt install python3 python3-pip"
    echo "   macOS         : brew install python  (or download from python.org)"
    echo ""
    exit 1
fi

$PYTHON --version
echo " Python found!"

# ── Step 2: Install packages ───────────────────────────────
echo ""
echo " [Step 2/4] Installing required packages..."
$PIP install -r requirements.txt

# ── Step 3: Create required folders ───────────────────────
echo ""
echo " [Step 3/4] Creating required folders..."
mkdir -p saved_models logs data_store

# ── Step 4: Verify installation ────────────────────────────
echo ""
echo " [Step 4/4] Verifying installation..."
$PYTHON -c "import tensorflow, websockets, numpy, rich; print('  All packages verified!')"

echo ""
echo " ====================================================="
echo "   Setup Complete!"
echo ""
echo "   To start the program, run:  bash start.sh"
echo " ====================================================="
echo ""
