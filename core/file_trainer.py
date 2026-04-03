"""Batch file-trainer — trains and evaluates the AI on each .txt data file."""

import os
import logging

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn
from rich import box

from models.neural_network import RouletteNeuralNetwork
from core.trainer import ModelTrainer
from data.file_feed import FileFeed
from strategies.base import BaseStrategy
from utils.tracker import StatsTracker
from config.settings import (
    SEQUENCE_LENGTH, REAL_MODELS_DIR, TRAINING_FILES_DIR,
    TRAINING_EPOCHS, BATCH_SIZE,
)

console = Console()
_log = logging.getLogger("FileTrainer")


def run_file_training(strategy: BaseStrategy, auto_train: bool = True):
    """
    Main entry-point for file-based training mode.

    For each .txt file in TRAINING_FILES_DIR:
      1. Parse the spin history
      2. Train the model (full offline pass)
      3. Replay every spin through the strategy and collect stats
      4. Print per-file results
    """
    feed = FileFeed()
    files = feed.load_all()

    if not files:
        console.print(Panel(
            f"[bold red]No .txt files found![/bold red]\n\n"
            f"  Put your casino data files in:\n"
            f"  [bold cyan]{os.path.abspath(TRAINING_FILES_DIR)}[/bold cyan]\n\n"
            f"  Format: one number per line, or comma/space separated (0-36).\n"
            f"  Lines starting with # are ignored.",
            title="[bold]File Training[/bold]",
            border_style="red",
        ))
        return

    console.print(Panel(
        f"  Found [bold cyan]{len(files)}[/bold cyan] training file(s) in "
        f"[bold]{os.path.abspath(TRAINING_FILES_DIR)}[/bold]\n"
        f"  Strategy: [bold]{strategy.STRATEGY_NAME}[/bold]\n"
        f"  Model will be saved to: [bold]{os.path.abspath(REAL_MODELS_DIR)}[/bold]",
        title="[bold cyan]📂 File Training Mode[/bold cyan]",
        border_style="cyan",
    ))
    console.print()

    # Load or create the model (shared real model for this strategy)
    nn = RouletteNeuralNetwork(
        model_name=strategy.model_filename,
        save_dir=REAL_MODELS_DIR,
    )
    nn.load()
    trainer = ModelTrainer(nn, verbose=True, save_dir=REAL_MODELS_DIR)

    all_results = []

    for idx, fdata in enumerate(files, 1):
        name = fdata["name"]
        numbers = fdata["numbers"]
        total_spins = len(numbers)

        console.rule(f"[bold yellow]File {idx}/{len(files)}: {name}[/bold yellow]")

        if total_spins < SEQUENCE_LENGTH + 1:
            console.print(
                f"  [red]⚠ Skipped — only {total_spins} spins "
                f"(need at least {SEQUENCE_LENGTH + 1})[/red]\n"
            )
            all_results.append({
                "file": name, "spins": total_spins, "status": "SKIPPED",
                "wins": 0, "losses": 0, "win_rate": 0, "roi": 0,
            })
            continue

        # ── Phase 1: Train on this file's data ──
        console.print(f"  📚 Training on [bold]{total_spins}[/bold] spins...")
        success = trainer.train_offline(numbers)
        if success:
            console.print(f"  [green]✅ Training complete — model saved.[/green]")
        else:
            console.print(f"  [yellow]⚠ Training failed (not enough usable samples).[/yellow]")

        # ── Phase 2: Replay spins and evaluate strategy ──
        console.print(f"  🎲 Evaluating strategy replay...")
        tracker = StatsTracker()
        history_buf = []

        with Progress(
            TextColumn("[dim]{task.description}[/dim]"),
            BarColumn(bar_width=30),
            TextColumn("[bold]{task.completed}/{task.total}[/bold]"),
            TimeElapsedColumn(),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task("Replaying", total=total_spins)

            for spin_idx, number in enumerate(numbers):
                history_buf.append(number)
                progress.advance(task)

                # Need SEQUENCE_LENGTH spins before prediction
                if len(history_buf) < SEQUENCE_LENGTH:
                    continue

                # Predict
                inp = RouletteNeuralNetwork.build_prediction_input(history_buf)
                probs = nn.model.predict(inp, verbose=0)[0]
                predicted = strategy.select_numbers(probs)
                bets = strategy.calculate_bets(predicted, balance=1000.0, bet_per_number=1.00)

                # Evaluate
                is_win, net, _ = strategy.evaluate_result(number, predicted, bets, 1000.0)
                tracker.record(number, predicted, bets, is_win, net, 1000.0 + tracker.total_profit + net)

        # Print per-file result
        _print_file_result(name, total_spins, tracker)

        all_results.append({
            "file": name,
            "spins": total_spins,
            "status": "OK",
            "wins": tracker.total_wins,
            "losses": tracker.total_losses,
            "win_rate": tracker.win_rate,
            "roi": tracker.roi,
        })
        console.print()

    # ── Final summary table ──
    _print_overall_summary(all_results, strategy)


def _print_file_result(name: str, total_spins: int, tracker: StatsTracker):
    """Print a compact stats block for one file."""
    wr = tracker.win_rate
    roi = tracker.roi
    wr_c = "green" if wr > 10 else "yellow" if wr > 5 else "red"
    roi_c = "green" if roi >= 0 else "red"

    console.print(
        f"\n  📊 [bold]{name}[/bold]  ({total_spins} spins)\n"
        f"     Evaluated: {tracker.total_spins} predictions  │  "
        f"Wins: [green]{tracker.total_wins}[/green]  │  "
        f"Losses: [red]{tracker.total_losses}[/red]\n"
        f"     Win Rate: [{wr_c}]{wr:.2f}%[/{wr_c}]  │  "
        f"ROI: [{roi_c}]{roi:+.2f}%[/{roi_c}]  │  "
        f"Profit: [{roi_c}]${tracker.total_profit:+.2f}[/{roi_c}]"
    )


def _print_overall_summary(results: list, strategy: BaseStrategy):
    """Print the final cross-file summary table."""
    console.print()
    console.rule("[bold cyan]📊 Overall File Training Summary[/bold cyan]")
    console.print()

    table = Table(
        title=f"Strategy: {strategy.STRATEGY_NAME}",
        box=box.ROUNDED,
        border_style="cyan",
        show_header=True,
        header_style="bold cyan",
        padding=(0, 1),
    )
    table.add_column("File", min_width=25)
    table.add_column("Spins", width=8, justify="right")
    table.add_column("Status", width=8, justify="center")
    table.add_column("Wins", width=6, justify="right")
    table.add_column("Losses", width=7, justify="right")
    table.add_column("Win Rate", width=10, justify="right")
    table.add_column("ROI", width=10, justify="right")

    total_spins = 0
    total_wins = 0
    total_losses = 0

    for r in results:
        status_style = "[green]OK[/green]" if r["status"] == "OK" else "[dim]SKIP[/dim]"
        wr_c = "green" if r["win_rate"] > 10 else "yellow" if r["win_rate"] > 5 else "red"
        roi_c = "green" if r["roi"] >= 0 else "red"

        table.add_row(
            r["file"],
            str(r["spins"]),
            status_style,
            f"[green]{r['wins']}[/green]" if r["wins"] else "—",
            f"[red]{r['losses']}[/red]" if r["losses"] else "—",
            f"[{wr_c}]{r['win_rate']:.2f}%[/{wr_c}]" if r["status"] == "OK" else "—",
            f"[{roi_c}]{r['roi']:+.2f}%[/{roi_c}]" if r["status"] == "OK" else "—",
        )
        total_spins += r["spins"]
        total_wins += r["wins"]
        total_losses += r["losses"]

    # Totals row
    total_evaluated = total_wins + total_losses
    agg_wr = (total_wins / total_evaluated * 100) if total_evaluated else 0
    table.add_section()
    table.add_row(
        "[bold]TOTAL[/bold]",
        f"[bold]{total_spins}[/bold]",
        "",
        f"[bold green]{total_wins}[/bold green]",
        f"[bold red]{total_losses}[/bold red]",
        f"[bold]{agg_wr:.2f}%[/bold]",
        "",
    )

    console.print(table)
    console.print()
    console.print(Panel(
        f"[bold green]✅ Model trained and saved to:[/bold green]  "
        f"[bold]{os.path.abspath(REAL_MODELS_DIR)}[/bold]\n\n"
        f"[dim]This model is now shared by Live and Manual modes.\n"
        f"Launch a Live or Manual session to use the improved model.[/dim]",
        border_style="green",
        padding=(0, 2),
    ))
    console.print()
