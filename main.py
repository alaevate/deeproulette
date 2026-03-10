#!/usr/bin/env python3
"""
DeepRoulette
============
Professional AI-powered roulette prediction system.

How to run
----------
  Windows  ->  Double-click  START.bat
  Terminal ->  python main.py

First time?  Run  SETUP.bat  first to install all dependencies.
"""

import sys
import os

# Suppress TensorFlow's verbose CPU/GPU info messages before any TF import
os.environ["TF_CPP_MIN_LOG_LEVEL"]      = "3"   # 0=all, 1=info, 2=warning, 3=error only
os.environ["TF_ENABLE_ONEDNN_OPTS"]     = "0"   # silence oneDNN optimizer notices
os.environ["CUDA_VISIBLE_DEVICES"]      = ""    # suppress GPU detection noise if no GPU

# Ensure the project root is always on the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# -- Dependency check (friendly error for non-tech users) ---------------------
try:
    from rich.console import Console
except ImportError:
    print()
    print("  ERROR: Required packages are not installed.")
    print()
    print("  Please run  SETUP.bat  first (Windows)")
    print("  or run:  pip install -r requirements.txt")
    print()
    input("  Press Enter to exit...")
    sys.exit(1)

import asyncio

from ui.menu    import run_menu, console
from ui.display import (
    render_spin,
    render_waiting,
    render_session_header,
    render_balance_empty,
    render_session_summary,
    render_bet_advice,
    render_milestone_summary,
)
from core.engine     import PredictionEngine
from config.settings import SAVED_MODELS_DIR, OFFLINE_MODELS_DIR, ONLINE_MODELS_DIR, LOGS_DIR, DATA_STORE_DIR
from utils.updater   import check_for_updates


# -- Folder setup --------------------------------------------------------------

def ensure_directories():
    """Create required directories if they don't exist yet."""
    for directory in [SAVED_MODELS_DIR, OFFLINE_MODELS_DIR, ONLINE_MODELS_DIR, LOGS_DIR, DATA_STORE_DIR]:
        os.makedirs(directory, exist_ok=True)


# -- Session runner ------------------------------------------------------------

async def run_session(config: dict):
    """Initialise the engine and run until Ctrl+C or balance depleted."""
    strategy = config["strategy_cls"]()
    balance  = config["balance"]

    engine = PredictionEngine(
        strategy        = strategy,
        initial_balance = balance,
        auto_train      = config["auto_train"],
        use_live        = config["use_live"],
        spin_interval   = config.get("spin_interval", 5.0),
        manual_mode     = config.get("manual_mode", False),
    )

    # Wire up UI callbacks
    engine.on_spin_complete = render_spin
    engine.on_waiting       = render_waiting
    engine.on_balance_empty = render_balance_empty
    engine.on_advice        = render_bet_advice

    # Checkpoint mode: pause at every milestone and show full stats.
    async def _on_milestone(spin_count: int):
        await asyncio.to_thread(
            render_milestone_summary, spin_count, engine.tracker, strategy, balance
        )

    engine.on_milestone = _on_milestone

    # Print session header
    render_session_header(strategy, balance, config["use_live"], config["auto_train"], config.get("manual_mode", False))

    try:
        await engine.run()
    except (asyncio.CancelledError, KeyboardInterrupt):
        pass
    finally:
        # Skip the final summary if checkpoint mode already printed it at the 1000-spin milestone
        if not engine.checkpoint_mode_complete:
            render_session_summary(engine.tracker, strategy, balance)


# -- Entry point ---------------------------------------------------------------

def main():
    ensure_directories()

    # Check GitHub for a newer release
    check_for_updates()

    # Run the interactive menu
    try:
        config = run_menu()
    except KeyboardInterrupt:
        console.print("\n[bold yellow]  Goodbye! [/bold yellow]\n")
        return

    # Run the prediction session
    try:
        asyncio.run(run_session(config))
    except KeyboardInterrupt:
        pass   # summary already printed inside run_session's finally block

    console.print("[bold yellow]  Thanks for using DeepRoulette![/bold yellow]\n")


if __name__ == "__main__":
    main()
