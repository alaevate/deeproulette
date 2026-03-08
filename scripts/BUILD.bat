@echo off
cd /d "%~dp0.."
title DeepRoulette — Build EXE
color 0B
cls

echo.
echo  ╔══════════════════════════════════════════════════════╗
echo  ║           DeepRoulette  —  Build Executable          ║
echo  ║    Packages everything into a single  .exe  file      ║
echo  ╚══════════════════════════════════════════════════════╝
echo.
echo  This will create:
echo    dist\DeepRoulette.exe
echo.
echo  ⚠  The EXE will be ~400-700 MB (TensorFlow is large)
echo  ⚠  Build time: 5–15 minutes depending on your PC
echo.
pause

REM ── Check Python ──────────────────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo  ERROR: Python not found.
    echo  Please install Python 3.8+ from https://python.org
    echo.
    pause
    exit /b 1
)

REM ── Activate venv if it exists ────────────────────────────────────────────
if exist "venv\Scripts\activate.bat" (
    echo  [1/4] Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo  [1/4] No venv found — using system Python
)

REM ── Install / upgrade PyInstaller ─────────────────────────────────────────
echo.
echo  [2/4] Installing PyInstaller...
pip install pyinstaller --upgrade --quiet
if errorlevel 1 (
    echo  ERROR: Could not install PyInstaller.
    pause
    exit /b 1
)

REM ── Clean previous build ──────────────────────────────────────────────────
echo.
echo  [3/4] Cleaning previous build output...
if exist "build"  rmdir /s /q "build"
if exist "dist"   rmdir /s /q "dist"

REM ── Run PyInstaller ───────────────────────────────────────────────────────
echo.
echo  [4/4] Building EXE — this may take several minutes...
echo        (You will see lots of output — this is normal)
echo.
pyinstaller DeepRoulette.spec

if errorlevel 1 (
    echo.
    echo  ════════════════════════════════════════
    echo  ERROR: Build failed. See output above.
    echo  ════════════════════════════════════════
    pause
    exit /b 1
)

echo.
echo  ════════════════════════════════════════════════════════
echo   ✓  Build complete!
echo.
echo   Your executable is at:
echo     dist\DeepRoulette.exe
echo.
echo   Share just that ONE file — no Python needed!
echo  ════════════════════════════════════════════════════════
echo.
pause
