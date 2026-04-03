#!/usr/bin/env python3
"""DeepRoulette — AI-powered roulette prediction system."""

import sys
import os

# Suppress TensorFlow noise before any TF import
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["CUDA_VISIBLE_DEVICES"] = ""

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from rich.console import Console
except ImportError:
    print("\n  ERROR: Required packages are not installed.")
    print("  Run:  pip install -r requirements.txt\n")
    input("  Press Enter to exit...")
    sys.exit(1)

import asyncio

from ui.menu import run_menu, console
from ui.dashboard import LiveDashboard
from core.engine import PredictionEngine
from config.settings import (
    SAVED_MODELS_DIR, REAL_MODELS_DIR, SIMULATION_MODELS_DIR,
    LOGS_DIR, DATA_STORE_DIR, TRAINING_FILES_DIR,
)
from utils.updater import check_for_updates


def ensure_directories():
    for d in (SAVED_MODELS_DIR, REAL_MODELS_DIR, SIMULATION_MODELS_DIR,
              LOGS_DIR, DATA_STORE_DIR, TRAINING_FILES_DIR):
        os.makedirs(d, exist_ok=True)


async def run_session(config: dict):
    """Set up the dashboard + engine, run until Ctrl+C or balance gone."""
    strategy = config["strategy_cls"]()
    balance = config["balance"]
    manual = config.get("manual_mode", False)
    use_live = config["use_live"]

    if manual:
        mode_label = "[magenta]✍️ Manual[/magenta]"
    elif use_live:
        mode_label = "[cyan]🌐 Live[/cyan]"
    else:
        mode_label = "[yellow]🔄 Sim[/yellow]"

    dashboard = LiveDashboard(strategy, balance, mode_label, config["auto_train"])

    engine = PredictionEngine(
        strategy=strategy,
        initial_balance=balance,
        bet_per_number=config.get("bet_per_number", 1.00),
        auto_train=config["auto_train"],
        use_live=use_live,
        spin_interval=config.get("spin_interval", 5.0),
        manual_mode=manual,
    )

    # Manual mode needs stdin so can't use alt-screen Live — use legacy scroll display
    if manual:
        from ui.display import (
            render_spin, render_waiting, render_session_header,
            render_balance_empty, render_session_summary, render_bet_advice,
        )
        engine.on_spin_complete = render_spin
        engine.on_waiting = render_waiting
        engine.on_balance_empty = render_balance_empty
        engine.on_advice = render_bet_advice
        render_session_header(strategy, balance, use_live, config["auto_train"], True)
        try:
            await engine.run()
        except (asyncio.CancelledError, KeyboardInterrupt):
            pass
        finally:
            if not engine.checkpoint_mode_complete:
                render_session_summary(engine.tracker, strategy, balance)
        return

    # Simulation / Live: full-screen fixed-page dashboard
    engine.on_spin_complete = dashboard.on_spin_complete
    engine.on_waiting = dashboard.on_waiting
    engine.on_balance_empty = dashboard.on_balance_empty
    engine.on_advice = dashboard.on_advice
    engine.on_model_status = dashboard.on_model_status
    engine.on_milestone = dashboard.on_milestone   # checkpoint pauses at 100/250/500/1000 spins

    live_ctx = dashboard.start()
    with live_ctx:
        try:
            await engine.run()
        except (asyncio.CancelledError, KeyboardInterrupt):
            pass

    # Print final summary after Live screen closes
    if not engine.checkpoint_mode_complete:
        dashboard.print_summary(engine.tracker, strategy)


def main():
    ensure_directories()
    check_for_updates()

    try:
        config = run_menu()
    except KeyboardInterrupt:
        console.print("\n[bold yellow]  Goodbye![/bold yellow]\n")
        return

    # File-training mode runs synchronously (no live engine needed)
    if config.get("file_train"):
        from core.file_trainer import run_file_training
        strategy = config["strategy_cls"]()
        run_file_training(strategy)
        console.print("[bold yellow]  Thanks for using DeepRoulette![/bold yellow]\n")
        return

    try:
        asyncio.run(run_session(config))
    except KeyboardInterrupt:
        pass

    console.print("[bold yellow]  Thanks for using DeepRoulette![/bold yellow]\n")


if __name__ == "__main__":
    main()
