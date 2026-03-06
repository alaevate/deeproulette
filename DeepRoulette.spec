# -*- mode: python ; coding: utf-8 -*-
# DeepRoulette.spec
# ==================
# PyInstaller build spec for DeepRoulette
# Run via:  BUILD.bat  or  pyinstaller DeepRoulette.spec

import sys
from PyInstaller.utils.hooks import collect_all, collect_data_files

# ── Collect TensorFlow / Keras (they have dynamic imports) ───────────────────
tf_datas,    tf_binaries,    tf_hiddenimports    = collect_all("tensorflow")
keras_datas, keras_binaries, keras_hiddenimports = collect_all("keras")

a = Analysis(
    ["main.py"],
    pathex=["."],
    binaries=tf_binaries + keras_binaries,
    datas=[
        # Project config / assets
        ("config",     "config"),
        ("assets",     "assets"),
        # TensorFlow & Keras bundled data
        *tf_datas,
        *keras_datas,
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
        "strategies.conservative",
        "strategies.adaptive",
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

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="DeepRoulette",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,          # compress with UPX if available (reduces size ~30%)
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,      # keep console window — needed for Rich terminal UI
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="assets/icon.ico" if __import__("os").path.exists("assets/icon.ico") else None,
)
