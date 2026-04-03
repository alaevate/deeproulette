# -*- mode: python ; coding: utf-8 -*-
# DeepRoulette.spec
# ==================
# PyInstaller build spec for DeepRoulette
# Run via:  scripts/build.bat  or  pyinstaller DeepRoulette.spec

import sys
from PyInstaller.utils.hooks import collect_all, collect_data_files

# ── Version & Platform ───────────────────────────────────────────────────────
APP_VERSION = "2.0.0"

if sys.platform.startswith("win"):
    APP_OS = "windows"
elif sys.platform.startswith("darwin"):
    APP_OS = "macos"
else:
    APP_OS = "linux"

APP_NAME = f"DeepRoulette-v{APP_VERSION}-{APP_OS}"

# ── Collect TensorFlow / Keras (they have dynamic imports) ───────────────────
tf_datas,    tf_binaries,    tf_hiddenimports    = collect_all("tensorflow")
keras_datas, keras_binaries, keras_hiddenimports = collect_all("keras")

# ── Collect charset_normalizer + requests (fixes RequestsDependencyWarning) ──
csn_datas,  csn_binaries,  csn_hiddenimports  = collect_all("charset_normalizer")
req_datas,  req_binaries,  req_hiddenimports  = collect_all("requests")

a = Analysis(
    ["main.py"],
    pathex=["."],
    binaries=tf_binaries + keras_binaries + csn_binaries + req_binaries,
    datas=[
        # Project config / assets
        ("config",     "config"),
        ("assets",     "assets"),
        # TensorFlow & Keras bundled data
        *tf_datas,
        *keras_datas,
        # charset_normalizer & requests bundled data
        *csn_datas,
        *req_datas,
    ],
    hiddenimports=[
        # TensorFlow / Keras
        *tf_hiddenimports,
        *keras_hiddenimports,
        # Project modules
        "config.settings",
        "core.engine",
        "core.trainer",
        "data.live_feed",
        "data.simulator",
        "models.neural_network",
        "strategies.base",
        "strategies.sniper",
        "strategies.aggressive",
        "strategies.balanced",
        "strategies.adaptive",
        "strategies.outside_bets",
        "strategies.fusion",
        "strategies.hybrid",
        "ui.menu",
        "ui.display",
        "utils.logger",
        "utils.tracker",
        # Third-party
        "rich",
        "rich.console",
        "rich.table",
        "rich.panel",
        "rich.progress",
        "colorama",
        "websockets",
        "numpy",
        "asyncio",
        # Fix requests charset detection warning in EXE
        *csn_hiddenimports,
        *req_hiddenimports,
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude heavy unused packages to shrink size
        "matplotlib",
        "PIL",
        "tkinter",
        "PyQt5",
        "jupyter",
        "IPython",
        "notebook",
        "scipy",
        "pandas",
        "sklearn",
        "cv2",
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

# ── onefile mode — single portable EXE ───────────────────────────────────────
# UPX is disabled: it corrupts python3xx.dll and causes
# 'Failed to load Python DLL' at runtime on Windows.
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,             # ← must stay False — UPX breaks python DLL loading
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,          # keep console window — needed for Rich terminal UI
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="assets/logo.ico",
)
