"""
ui/menu.py
==========
Interactive startup menu — fully guided, no command-line knowledge needed.

Walks the user through:
  1. Welcome screen
  2. Strategy selection
  3. Starting balance
  4. Data mode (live / simulation)
  5. Auto-train toggle
  6. Confirmation & launch
"""

from rich.console  import Console
from rich.panel    import Panel
from rich.table    import Table
from rich.prompt   import Prompt, Confirm, FloatPrompt
from rich.text     import Text
from rich.align    import Align
from rich.columns  import Columns
from rich          import box

from strategies    import ALL_STRATEGIES
from config.settings  import DEFAULT_BALANCE
from utils.constants  import SPEED_PRESETS

console = Console()

_RISK_COLOUR = {
    "Extreme":  "red",
    "High":     "orange1",
    "Medium":   "yellow",
    "Low":      "green",
    "Variable": "cyan",
}


# ── Welcome screen ────────────────────────────────────────────────────────────

# "DEEP" block — 32 chars wide
_LOGO_DEEP = [
    ("██████╗ ███████╗███████╗██████╗ ", "bold cyan"),
    ("██╔══██╗██╔════╝██╔════╝██╔══██╗", "bold cyan"),
    ("██║  ██║█████╗  █████╗  ██████╔╝", "bold bright_cyan"),
    ("██║  ██║██╔══╝  ██╔══╝  ██╔═══╝ ", "bold bright_cyan"),
    ("██████╔╝███████╗███████╗██║     ", "bold cyan"),
    ("╚═════╝ ╚══════╝╚══════╝╚═╝     ", "cyan"),
]

# "ROULETTE" block — 68 chars wide
_LOGO_ROULETTE = [
    ("██████╗  ██████╗ ██╗   ██╗██╗     ███████╗████████╗████████╗███████╗",  "bold bright_cyan"),
    ("██╔══██╗██╔═══██╗██║   ██║██║     ██╔════╝╚══██╔══╝╚══██╔══╝██╔════╝",  "bold bright_cyan"),
    ("██████╔╝██║   ██║██║   ██║██║     █████╗     ██║      ██║   █████╗  ",   "bold cyan"),
    ("██╔══██╗██║   ██║██║   ██║██║     ██╔══╝     ██║      ██║   ██╔══╝  ",   "bold cyan"),
    ("██║  ██║╚██████╔╝╚██████╔╝███████╗███████╗   ██║      ██║   ███████╗",   "bold bright_cyan"),
    ("╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚══════╝╚══════╝   ╚═╝      ╚═╝   ╚══════╝",  "cyan"),
]

def show_welcome():
    console.clear()

    ROULETTE_W = 68   # width of ROULETTE block (the wider part)
    DEEP_W     = 32   # width of DEEP block

    term_w   = console.width or 120
    base_pad = max(2, (term_w - ROULETTE_W) // 2)
    indent_r = " " * base_pad                                       # ROULETTE left edge
    indent_d = " " * (base_pad + (ROULETTE_W - DEEP_W) // 2)       # DEEP centred above ROULETTE

    # Build logo text block
    logo = Text()
    logo.append("\n")
    for line, colour in _LOGO_DEEP:
        logo.append(indent_d + line + "\n", style=colour)
    for line, colour in _LOGO_ROULETTE:
        logo.append(indent_r + line + "\n", style=colour)

    # Subtitle — each line individually centred under the ROULETTE block
    def _centre(text: str) -> str:
        """Return indent that centres `text` within the ROULETTE block."""
        pad = base_pad + max(0, (ROULETTE_W - len(text)) // 2)
        return " " * pad

    logo.append("\n")

    line1 = "Deep LSTM Neural Network   •    Real-Time Prediction"
    line2 = "━" * 52
    line3 = "v2.0.0  •  github.com/alaevate/deeproulette  •  2026"

    logo.append(_centre(line1) + line1 + "\n", style="dim cyan")
    logo.append(_centre(line2) + line2 + "\n", style="cyan")
    logo.append(_centre(line3) + line3 + "\n", style="dim")
    # logo.append("\n")

    console.print(Panel(
        logo,
        border_style="cyan",
        padding=(0, 2),
        expand=True,
    ))
    console.print()


# ── Step 1 — Strategy selection ───────────────────────────────────────────────

def ask_strategy() -> type:
    """Show strategy table and return the chosen strategy class."""
    table = Table(
        title="[bold]Step 1 of 4  —  Choose Your Strategy[/bold]",
        box=box.ROUNDED,
        border_style="cyan",
        show_header=True,
        header_style="bold cyan",
        padding=(0, 1),
    )
    table.add_column("#",            width=1,  justify="center")
    table.add_column("Strategy",     width=22)
    table.add_column("Risk Level",   width=12, justify="center")
    table.add_column("Numbers Bet",  width=12, justify="center")
    table.add_column("Win Chance",   width=12, justify="center")
    table.add_column("Description",  min_width=40)

    for i, cls in enumerate(ALL_STRATEGIES, 1):
        s          = cls()
        risk_color = _RISK_COLOUR.get(s.RISK_LEVEL, "white")
        nums       = str(s.NUMBERS_TO_BET) if s.NUMBERS_TO_BET > 0 else "1–18"
        chance     = f"{s.TARGET_WIN_RATE:.1f}%" if s.TARGET_WIN_RATE > 0 else "Varies"

        table.add_row(
            str(i),
            s.STRATEGY_NAME,
            f"[{risk_color}]{s.RISK_LEVEL}[/{risk_color}]",
            nums,
            chance,
            s.DESCRIPTION,
        )

    console.print(table)
    console.print()
    console.print(
        "  [dim]Not sure which to pick?  "
        "[bold]3 (Balanced)[/bold] is a great starting point.[/dim]"
    )
    console.print()

    choice = Prompt.ask(
        "[bold]Enter the number of your strategy[/bold]",
        choices=[str(i) for i in range(1, len(ALL_STRATEGIES) + 1)],
        default="3",
    )
    selected = ALL_STRATEGIES[int(choice) - 1]
    console.print(
        f"\n  ✅ Strategy selected: [bold cyan]{selected.STRATEGY_NAME}[/bold cyan]\n"
    )
    return selected


# ── Step 2 — Starting balance ─────────────────────────────────────────────────

def ask_balance() -> float:
    """Prompt for the starting virtual wallet size."""
    console.print(Panel(
        "[bold]Step 2 of 4  —  Starting Balance[/bold]\n\n"
        "  This is your virtual wallet for this session.\n"
        "  [dim]No real money is used — this is a simulation of betting.[/dim]\n\n"
        "  💡 Recommended: [bold]$50 – $500[/bold] to get meaningful statistics.",
        border_style="dim",
        padding=(0, 2),
    ))
    console.print()

    balance = FloatPrompt.ask(
        "[bold]Enter starting balance ($)[/bold]",
        default=DEFAULT_BALANCE,
    )
    balance = max(1.0, float(balance))
    console.print(f"\n  ✅ Balance set to: [bold yellow]${balance:.2f}[/bold yellow]\n")
    return balance


# ── Step 3 — Data source ──────────────────────────────────────────────────────

def ask_mode() -> tuple:
    """Ask whether to use live casino, simulation, or manual entry."""
    console.print(Panel(
        "[bold]Step 3 of 4  —  Data Source[/bold]\n\n"
        "  [bold cyan][1] Live Mode[/bold cyan]\n"
        "      Connects to a real Pragmatic Play casino WebSocket.\n"
        "      [dim]Real spins, real-time. Requires internet connection.[/dim]\n\n"
        "  [bold yellow][2] Simulation Mode[/bold yellow]\n"
        "      Generates random spins locally on your computer.\n"
        "      [dim]No internet needed. Great for collecting training data.[/dim]\n\n"
        "  [bold magenta][3] Manual Entry  ← Use AI advice at a real casino[/bold magenta]\n"
        "      You type each spin result — AI shows where to bet before each spin.\n"
        "      [dim]Perfect for using the AI at a live or online casino.[/dim]",
        border_style="dim",
        padding=(0, 2),
    ))
    console.print()

    choice = Prompt.ask(
        "[bold]Choose mode[/bold]",
        choices=["1", "2", "3"],
        default="3",
    )
    use_live    = (choice == "1")
    manual_mode = (choice == "3")
    labels = {"1": "[cyan]Live Casino[/cyan]", "2": "[yellow]Simulation[/yellow]", "3": "[magenta]Manual Entry[/magenta]"}
    console.print(f"\n  ✅ Mode set to: {labels[choice]}\n")
    return use_live, manual_mode


# ── Step 4 — Simulation speed (only in simulation mode) ──────────────────────

def ask_sim_speed() -> float:
    """Let the user pick how fast the simulator generates spins."""
    table = Table(
        title="[bold]Step 4 of 5  —  Simulation Speed[/bold]",
        box=box.ROUNDED,
        border_style="cyan",
        show_header=True,
        header_style="bold cyan",
        padding=(0, 1),
    )
    table.add_column("#",           width=3,  justify="center")
    table.add_column("Speed",       width=10)
    table.add_column("Description", min_width=42)

    for i, (label, desc, _) in enumerate(SPEED_PRESETS, 1):
        colour = ["white", "yellow", "orange1", "red"][i - 1]
        table.add_row(str(i), f"[{colour}]{label}[/{colour}]", desc)

    console.print(table)
    console.print()
    console.print(
        "  [dim]Tip: use [bold]Turbo[/bold] or [bold]Max[/bold] to collect training data quickly.[/dim]"
    )
    console.print()

    choice = Prompt.ask(
        "[bold]Choose speed[/bold]",
        choices=[str(i) for i in range(1, len(SPEED_PRESETS) + 1)],
        default="1",
    )
    label, _, interval = SPEED_PRESETS[int(choice) - 1]
    console.print(f"\n  ✅ Speed set to: [bold cyan]{label}[/bold cyan]\n")
    return interval


# ── Step 5 — Auto-train ───────────────────────────────────────────────────────

def ask_auto_train() -> bool:
    """Ask whether to enable online model updates during the session."""
    console.print(Panel(
        "[bold]Step 4 of 4  —  AI Auto-Training[/bold]\n\n"
        "  When enabled, the AI will learn from each new spin in real time,\n"
        "  gradually improving its predictions as the session continues.\n\n"
        "  [dim]This uses slightly more CPU but produces a smarter model over time.\n"
        "  The updated model is saved to disk and reused in future sessions.[/dim]",
        border_style="dim",
        padding=(0, 2),
    ))
    console.print()

    enabled = Confirm.ask(
        "🤖 Enable [bold]AI auto-training[/bold]?",
        default=False,
    )
    label = "[green]Enabled[/green]" if enabled else "[dim]Disabled[/dim]"
    console.print(f"\n  ✅ Auto-training: {label}\n")
    return enabled


# ── Confirmation screen ───────────────────────────────────────────────────────

def show_confirmation(strategy_cls, balance: float, use_live: bool, auto_train: bool, spin_interval: float = 5.0, manual_mode: bool = False):
    """Display a summary of all chosen settings before launching."""
    s          = strategy_cls()
    risk_color = _RISK_COLOUR.get(s.RISK_LEVEL, "white")
    if manual_mode:
        mode_label = "[magenta]Manual Entry[/magenta]"
    elif use_live:
        mode_label = "[cyan]Live Casino[/cyan]"
    else:
        mode_label = "[yellow]Simulation[/yellow]"
    train_label = "[green]On[/green]" if auto_train else "[dim]Off[/dim]"

    # Find matching speed label
    speed_label = next(
        (lbl for lbl, _, iv in SPEED_PRESETS if iv == spin_interval),
        f"{spin_interval}s"
    )
    speed_line = "" if (use_live or manual_mode) else f"\n  Sim Speed  :  [bold cyan]{speed_label}[/bold cyan]"

    console.print(Panel(
        f"  [bold green]All set! Here's your configuration:[/bold green]\n\n"
        f"  Strategy   :  [bold]{s.STRATEGY_NAME}[/bold]\n"
        f"  Risk Level :  [{risk_color}]{s.RISK_LEVEL}[/{risk_color}]\n"
        f"  Balance    :  [bold yellow]${balance:.2f}[/bold yellow]\n"
        f"  Mode       :  {mode_label}{speed_line}\n"
        f"  Auto-Train :  {train_label}",
        title="[bold cyan]Ready to Start[/bold cyan]",
        border_style="green",
        padding=(0, 2),
    ))
    console.print()
    Confirm.ask("[bold]Press Enter to launch[/bold]", default=True)


# ── Full menu flow ────────────────────────────────────────────────────────────

def run_menu() -> dict:
    """
    Run all menu steps and return a configuration dict.

    Returns:
        {
          "strategy_cls": <class>,
          "balance":      float,
          "use_live":     bool,
          "auto_train":   bool,
        }
    """
    show_welcome()

    strategy_cls          = ask_strategy()
    balance               = ask_balance()
    use_live, manual_mode = ask_mode()
    spin_interval         = 5.0 if (use_live or manual_mode) else ask_sim_speed()
    auto_train            = ask_auto_train()

    show_confirmation(strategy_cls, balance, use_live, auto_train, spin_interval, manual_mode)

    return {
        "strategy_cls":  strategy_cls,
        "balance":       balance,
        "use_live":      use_live,
        "manual_mode":   manual_mode,
        "auto_train":    auto_train,
        "spin_interval": spin_interval,
    }
