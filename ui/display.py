"""
ui/display.py
=============
Rich-powered terminal display — renders every spin result and the
final session summary.

All functions accept plain Python dicts / objects so they stay decoupled
from the engine and strategy internals.
"""

from rich.console   import Console
from rich.table     import Table
from rich.panel     import Panel
from rich.text      import Text
from rich           import box

from utils.constants import get_number_color

console = Console()

# ── Colour mappings ───────────────────────────────────────────────────────────
_NUMBER_EMOJI  = {"red": "🔴", "black": "⚫", "green": "🟢"}
_RISK_COLOUR   = {
    "Extreme":  "red",
    "High":     "orange1",
    "Medium":   "yellow",
    "Low":      "green",
    "Variable": "cyan",
}


# ── Individual spin output ────────────────────────────────────────────────────

def render_spin(spin_data: dict):
    """
    Print a compact, colour-coded summary for one spin to the console.

    spin_data keys (all provided by PredictionEngine.handle_spin):
        number, predicted, bets, total_bet, is_win, net,
        balance, win_rate, roi, spin_num, streak, model_saved
    """
    n         = spin_data["number"]
    predicted = spin_data["predicted"]
    total_bet = spin_data["total_bet"]
    is_win    = spin_data["is_win"]
    net       = spin_data["net"]
    balance   = spin_data["balance"]
    win_rate  = spin_data["win_rate"]
    roi       = spin_data["roi"]
    spin_num  = spin_data["spin_num"]
    streak_k, streak_v = spin_data["streak"]
    saved     = spin_data.get("model_saved", False)

    color   = get_number_color(n)
    emoji   = _NUMBER_EMOJI[color]

    # Outcome
    outcome_color = "bold green" if is_win else "bold red"
    outcome_text  = "✨ WIN " if is_win else "❌ LOSS"
    net_str       = f"[{outcome_color}]{net:+.2f}[/{outcome_color}]"

    # Streak badge
    streak_color = "green" if streak_k == "W" else "red"
    streak_badge = f"[{streak_color}]{streak_k}×{streak_v}[/{streak_color}]"

    # ROI colour
    roi_color = "green" if roi >= 0 else "red"

    # Predicted numbers (truncate long lists)
    pred_display = ", ".join(str(p) for p in predicted[:8])
    if len(predicted) > 8:
        pred_display += f"  (+{len(predicted) - 8} more)"

    # Result separator — makes it visually clear this is the outcome
    console.rule(
        f"[dim]Spin #{spin_num}  ◄ RESULT ►[/dim]",
        style="dim",
    )

    # Main result line
    console.print(
        f"  {emoji} [bold white]{n:>2}[/bold white]  "
        f"[{outcome_color}]{outcome_text}[/{outcome_color}]  {net_str}"
        f"  │  Balance: [bold yellow]${balance:>8.2f}[/bold yellow]"
        f"  │  Win Rate: [cyan]{win_rate:>5.1f}%[/cyan]"
        f"  │  ROI: [{roi_color}]{roi:>+6.1f}%[/{roi_color}]"
        f"  │  Streak: {streak_badge}"
    )

    # Prediction hit indicator (bets were already shown before spin in render_bet_advice)
    hit     = n in predicted
    hit_str = "[bold green]✓ Hit![/bold green]" if hit else "[dim]✕ Miss[/dim]"
    saved_tag = "  [dim]💾 saved[/dim]" if saved else ""
    console.print(f"  🔮 AI predicted: [dim]{pred_display}[/dim]  │  {hit_str}{saved_tag}")
    console.print()


# ── Waiting message ───────────────────────────────────────────────────────────

def render_waiting(current: int, needed: int):
    """Display a progress message while the history buffer is filling up."""
    bar_filled = int((current / needed) * 20)
    bar        = "█" * bar_filled + "░" * (20 - bar_filled)
    console.print(
        f"  [dim]⏳ Building history  [{bar}]  {current}/{needed} spins[/dim]"
    )


# ── Manual mode bet advice ────────────────────────────────────────────────────

def render_bet_advice(advice: dict):
    """
    Print the AI bet advice table BEFORE the spin result is revealed.
    Called for ALL modes (manual, simulation, live) before each spin.
    The table stretches to fill the terminal width with a small margin.
    """
    predicted     = advice["predicted"]
    bets          = advice["bets"]
    balance       = advice["balance"]
    probabilities = advice.get("probabilities")
    spin_num      = advice.get("spin_num", "?")
    total_bet     = sum(bets.values())

    # ── Dynamic width: terminal width minus margins ───────────────────────────
    MARGIN        = 6          # columns to leave on each side
    term_width    = console.width or 120
    table_width   = max(60, term_width - MARGIN * 2)

    # Distribute column widths proportionally inside the table.
    # Fixed minimums:  Number=8  Color=14  Bet=16  Prob=12  → inner = table_width - borders/padding
    inner         = table_width - 5          # subtract box borders + column separators
    col_num       = max(8,  int(inner * 0.14))
    col_color     = max(14, int(inner * 0.28))
    col_bet       = max(16, int(inner * 0.32))
    col_prob      = max(12, inner - col_num - col_color - col_bet)

    table = Table(
        title=f"[bold cyan]🎯  AI Bet Advice  —  Spin #{spin_num}[/bold cyan]",
        box=box.ROUNDED,
        border_style="cyan",
        show_header=True,
        header_style="bold cyan",
        padding=(0, 2),
        width=table_width,
        expand=False,
    )
    table.add_column("Number",           justify="center", width=col_num,   no_wrap=True)
    table.add_column("Color",            justify="center", width=col_color, no_wrap=True)
    table.add_column("Bet Amount",       justify="center", width=col_bet,   no_wrap=True)
    table.add_column("AI Probability",   justify="center", width=col_prob,  no_wrap=True)

    for num in sorted(predicted):
        color    = get_number_color(num)
        emoji    = _NUMBER_EMOJI[color]
        bet      = bets.get(num, 0.0)
        prob_str = f"{probabilities[num] * 100:.1f}%" if probabilities is not None else "—"
        table.add_row(
            f"[bold white]{num}[/bold white]",
            f"{emoji} {color.capitalize()}",
            f"[bold yellow]${bet:.2f}[/bold yellow]",
            f"[cyan]{prob_str}[/cyan]",
        )

    # Centre the table with side padding
    pad = " " * MARGIN
    console.print()
    console.print(table, justify="center")
    console.print(
        f"{pad}💰  Total bet: [bold yellow]${total_bet:.2f}[/bold yellow]"
        f"  │  Balance after bet: [yellow]${balance - total_bet:.2f}[/yellow]"
    )


# ── Session header ────────────────────────────────────────────────────────────

def render_session_header(strategy, balance: float, use_live: bool, auto_train: bool, manual_mode: bool = False):
    """Print a header panel when the session starts."""
    if manual_mode:
        mode_label = "[magenta]✍️  Manual Entry[/magenta]"
    elif use_live:
        mode_label = "[cyan]🌐 Live Casino[/cyan]"
    else:
        mode_label = "[yellow]🔄 Simulation[/yellow]"
    train_label = "[green]On[/green]" if auto_train else "[dim]Off[/dim]"
    risk_color  = _RISK_COLOUR.get(strategy.RISK_LEVEL, "white")

    console.print(Panel(
        f"  Strategy  : [bold]{strategy.STRATEGY_NAME}[/bold]\n"
        f"  Risk      : [{risk_color}]{strategy.RISK_LEVEL}[/{risk_color}]\n"
        f"  Balance   : [bold yellow]${balance:.2f}[/bold yellow]\n"
        f"  Mode      : {mode_label}\n"
        f"  Auto-Train: {train_label}\n\n"
        f"  [dim]Press  Ctrl+C  at any time to stop.[/dim]",
        title="[bold cyan]Session Started[/bold cyan]",
        border_style="cyan",
        padding=(0, 2),
    ))
    console.print()


# ── Test-mode milestone checkpoint ───────────────────────────────────────────

_MILESTONE_LIST = [100, 250, 500, 1000]

def render_milestone_summary(spin_count: int, tracker, strategy, initial_balance: float):
    """
    Print a full checkpoint banner + session stats table at each milestone
    (100 / 250 / 500 / 1000 spins)
    After the final milestone the banner says 'All done'; otherwise it shows
    the next target and waits to press Enter before continuing.
    """
    is_final = spin_count == _MILESTONE_LIST[-1]

    console.print()
    console.rule(
        f"[bold yellow]🏁  CHECKPOINT — {spin_count} SPINS  🏁[/bold yellow]",
        style="bold yellow",
    )
    console.print()

    # Reuse the full session-summary table
    render_session_summary(tracker, strategy, initial_balance)

    if is_final:
        console.print(Panel(
            "[bold green]✅  All milestones completed  (100 → 250 → 500 → 1000)[/bold green]\n"
            "[dim]📸  Screenshot your results above before closing.[/dim]",
            border_style="green",
            padding=(0, 2),
        ))
        console.print()
    else:
        next_ms = _MILESTONE_LIST[_MILESTONE_LIST.index(spin_count) + 1]
        console.print(Panel(
            f"[dim]📸  Take your screenshot now.[/dim]\n"
            f"[dim]Next checkpoint: [/dim][bold cyan]{next_ms} spins[/bold cyan]",
            border_style="yellow",
            padding=(0, 2),
        ))
        console.input("  ▶  Press [bold]Enter[/bold] to continue to the next milestone...")
        console.print()


# ── Balance depleted ──────────────────────────────────────────────────────────

def render_balance_empty():
    console.print()
    console.print(Panel(
        "[bold red]⚠  Balance depleted — session ended automatically.[/bold red]",
        border_style="red",
    ))


# ── Session summary ───────────────────────────────────────────────────────────

def render_session_summary(tracker, strategy, initial_balance: float):
    """Print a formatted table summarising the completed session."""
    console.print()

    if tracker.total_spins == 0:
        console.print(Panel(
            "[dim]No spins were recorded this session.[/dim]",
            border_style="dim",
        ))
        return

    summary = tracker.summary()
    final   = tracker.current_balance
    profit  = final - initial_balance

    profit_color = "green" if profit >= 0 else "red"
    roi_color    = "green" if tracker.roi >= 0 else "red"

    table = Table(
        title="📊  Session Summary",
        box=box.ROUNDED,
        border_style="cyan",
        show_header=False,
        padding=(0, 2),
    )
    table.add_column("Metric", style="bold white", min_width=18)
    table.add_column("Value", justify="right", min_width=16)

    table.add_row("Strategy",       strategy.STRATEGY_NAME)
    table.add_row("Total Spins",    str(tracker.total_spins))
    table.add_row("Wins",           f"[green]{tracker.total_wins}[/green]")
    table.add_row("Losses",         f"[red]{tracker.total_losses}[/red]")
    table.add_row("Win Rate",       f"[cyan]{tracker.win_rate:.2f}%[/cyan]")
    table.add_row("Total Wagered",  f"${tracker.total_wagered:.2f}")
    table.add_row("Profit / Loss",  f"[{profit_color}]${profit:+.2f}[/{profit_color}]")
    table.add_row("ROI",            f"[{roi_color}]{tracker.roi:+.2f}%[/{roi_color}]")
    table.add_row("Starting Balance", f"${initial_balance:.2f}")
    table.add_row("Final Balance",  f"[bold yellow]${final:.2f}[/bold yellow]")
    table.add_row("Session Time",   summary["duration"])

    console.print(table)
    console.print()
