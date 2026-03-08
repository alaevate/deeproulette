#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════
#   DeepRoulette  --  Build Executable  (Linux / macOS)
#   Packages everything into a single binary using PyInstaller.
#   Usage:  bash scripts/build.sh
# ══════════════════════════════════════════════════════

# Always run from the project root
cd "$(dirname "$0")/.." || exit 1

set -e

echo ""
echo " ╔══════════════════════════════════════════════════════╗"
echo " ║        DeepRoulette  —  Build Executable             ║"
echo " ║   Packages everything into a single binary file      ║"
echo " ╚══════════════════════════════════════════════════════╝"
echo ""
echo " This will create:  dist/DeepRoulette-v2.0.0"
echo ""
echo " ⚠  The binary will be ~400-700 MB (TensorFlow is large)"
echo " ⚠  Build time: 5–15 minutes depending on your machine"
echo ""
read -rp " Press Enter to continue (Ctrl+C to cancel)..."

# ── Check Python ───────────────────────────────────────────
echo ""
if command -v python3 &>/dev/null; then
    PYTHON=python3
    PIP=pip3
elif command -v python &>/dev/null; then
    PYTHON=python
    PIP=pip
else
    echo " ERROR: Python not found."
    echo " Please install Python 3.8+ first."
    exit 1
fi

# ── Activate venv if it exists ─────────────────────────────
if [ -f "venv/bin/activate" ]; then
    echo " [1/4] Activating virtual environment..."
    source venv/bin/activate
else
    echo " [1/4] No venv found — using system Python"
fi

# ── Install / upgrade PyInstaller ─────────────────────────
echo ""
echo " [2/4] Installing PyInstaller..."
$PIP install pyinstaller --upgrade --quiet

# ── Clean previous build ───────────────────────────────────
echo ""
echo " [3/4] Cleaning previous build output..."
rm -rf build dist

# ── Run PyInstaller ────────────────────────────────────────
echo ""
echo " [4/4] Building binary — this may take several minutes..."
echo "       (You will see lots of output — this is normal)"
echo ""
pyinstaller DeepRoulette.spec

echo ""
echo " ════════════════════════════════════════════════════════"
echo "  ✓  Build complete!"
echo ""
echo "  Your binary is at:  dist/DeepRoulette-v2.0.0"
echo ""
echo "  Share just that ONE file — no Python needed!"
echo " ════════════════════════════════════════════════════════"
echo ""
