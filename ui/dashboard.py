## Copyright 2026 alaevate
# Licensed under the Apache License, Version 2.0
"""Fixed-page terminal dashboard — redraws the entire screen in-place every 0.5s."""

import asyncio
from datetime import datetime
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

from utils.constants import get_number_color

console = Console()

NUMBER_EMOJI = {"red": "🔴", "black": "⚫", "green": "🟢"}
RISK_COLOR = {
    "Extreme": "red", "High": "orange1", "Medium": "yellow",
    "Low": "green", "Very Low": "bright_green", "Variable": "cyan",
}


class LiveDashboard:
    """Holds all session state and renders a single-page Rich Layout on each refresh."""

    def __init__(self, strategy, balance: float, mode_label: str, auto_train: bool):
        self.strategy = strategy
        self.initial_balance = balance
        self.mode_label = mode_label
        self.auto_train = auto_train

        # State updated by the engine via callbacks
        self.balance = balance
        self.spin_num = 0
        self.win_rate = 0.0
        self.roi = 0.0
        self.total_wins = 0
        self.total_losses = 0
        self.streak_str = "—"
        self.session_start = datetime.now()

        # Last spin result (None until first spin completes)
        self.last_spin = None      # dict from engine
        # Current advice (None until first prediction)
        self.current_advice = None  # dict from engine
        # Recent history for the spin log (last N spins)
        self.recent_spins = []
        self.max_recent = 8

        # Status messages (model load, save, etc.)
        self.status_msg = ""
        # Waiting state
        self.waiting_current = 0
        self.waiting_needed = 0
        self.is_waiting = False

        # Milestone/checkpoint message (if any)
        self.milestone_msg = ""

        # Session finished flag
        self.session_over = False
        self.session_over_reason = ""

        # The Live context manager — started/stopped externally
        self._live = None

    def start(self) -> Live:
        """Create and return the Live context (caller enters it with `with`)."""
        self._live = Live(
            self._build_layout(),
            console=console,
            refresh_per_second=2,  # 0.5s refresh
            screen=True,           # takes over the full terminal (alt-screen)
        )
        return self._live

    def refresh(self):
        """Push a new render to the Live display."""
        if self._live:
            self._live.update(self._build_layout())

    # --- Engine callbacks ---

    def on_spin_complete(self, data: dict):
        self.last_spin = data
        self.spin_num = data["spin_num"]
        self.balance = data["balance"]
        self.win_rate = data["win_rate"]
        self.roi = data["roi"]
        sk, sv = data["streak"]
        self.streak_str = f"{sk}×{sv}"
        self.total_wins = data.get("total_wins", self.total_wins)
        self.total_losses = data.get("total_losses", self.total_losses)
        if data.get("model_saved"):
            self.status_msg = "💾 Model saved"
        else:
            self.status_msg = ""

        # Add to recent spins log
        self.recent_spins.append(data)
        if len(self.recent_spins) > self.max_recent:
            self.recent_spins = self.recent_spins[-self.max_recent:]

        # Clear advice after spin resolves
        self.current_advice = None
        self.refresh()

    def on_advice(self, data: dict):
        self.current_advice = data
        self.refresh()

    def on_waiting(self, current: int, needed: int):
        self.is_waiting = True
        self.waiting_current = current
        self.waiting_needed = needed
        self.refresh()

    def on_balance_empty(self):
        self.session_over = True
        self.session_over_reason = "⚠  Balance depleted"
        self.refresh()

    def on_model_status(self, msg: str):
        self.status_msg = msg
        self.refresh()

    async def on_milestone(self, spin_num: int):
        """Show a checkpoint banner in the footer and pause 10 s for screenshots."""
        self.milestone_msg = (
            f"📍 Checkpoint @ {spin_num} spins — 📸 screenshot now, continuing in 10 s…"
        )
        self.refresh()
        await asyncio.sleep(10.0)
        self.milestone_msg = ""
        self.refresh()

    # --- Layout builder ---

    def _build_layout(self) -> Layout:
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3),
        )
        layout["body"].split_row(
            Layout(name="left", ratio=1),
            Layout(name="right", ratio=1),
        )
        layout["left"].split_column(
            Layout(name="advice", ratio=1),
            Layout(name="last_result", size=7),
        )
        layout["right"].split_column(
            Layout(name="stats", size=14),
            Layout(name="log", ratio=1),
        )

        layout["header"].update(self._render_header())
        layout["advice"].update(self._render_advice())
        layout["last_result"].update(self._render_last_result())
        layout["stats"].update(self._render_stats())
        layout["log"].update(self._render_log())
        layout["footer"].update(self._render_footer())
        return layout

    def _render_header(self) -> Panel:
        risk_c = RISK_COLOR.get(self.strategy.RISK_LEVEL, "white")
        train = "[green]ON[/green]" if self.auto_train else "[dim]OFF[/dim]"
        elapsed = str(datetime.now() - self.session_start).split(".")[0]
        text = Text.from_markup(
            f"[bold bright_cyan]🎰 DeepRoulette[/bold bright_cyan]  │  "
            f"[bold]{self.strategy.STRATEGY_NAME}[/bold]  │  "
            f"[{risk_c}]{self.strategy.RISK_LEVEL}[/{risk_c}]  │  "
            f"{self.mode_label}  │  "
            f"Auto-Train: {train}  │  "
            f"⏱ {elapsed}"
        )
        text.justify = "center"
        return Panel(text, style="cyan", height=3, expand=True)

    def _render_advice(self) -> Panel:
        if self.session_over:
            return Panel(
                f"[bold red]{self.session_over_reason}[/bold red]",
                title="[bold]Session Ended[/bold]",
                border_style="red",
                expand=True,
            )

        if self.is_waiting and self.current_advice is None:
            filled = int((self.waiting_current / max(self.waiting_needed, 1)) * 20)
            bar = "█" * filled + "░" * (20 - filled)
            return Panel(
                f"[dim]⏳ Building history  [{bar}]  {self.waiting_current}/{self.waiting_needed} spins[/dim]",
                title="[bold cyan]Waiting for Data[/bold cyan]",
                border_style="dim",
                expand=True,
            )

        if self.current_advice is None:
            return Panel(
                "[dim]Waiting for next prediction…[/dim]",
                title="[bold cyan]🎯 AI Bet Advice[/bold cyan]",
                border_style="cyan",
                expand=True,
            )

        adv = self.current_advice
        spin_num = adv.get("spin_num", "?")
        bet_label = adv.get("bet_label")
        bets = adv["bets"]
        total_bet = sum(bets.values())
        bal_after = adv["balance"] - total_bet

        if bet_label:
            content = (
                f"\n  🎲  [bold cyan]{bet_label}[/bold cyan]\n\n"
                f"  Amount: [bold yellow]${total_bet:.2f}[/bold yellow]    "
                f"Balance after: [yellow]${bal_after:.2f}[/yellow]\n"
            )
        else:
            predicted = adv["predicted"]
            probs = adv.get("probabilities")
            lines = []
            for num in sorted(predicted)[:8]:
                color = get_number_color(num)
                emoji = NUMBER_EMOJI[color]
                bet = bets.get(num, 0.0)
                prob = f"{probs[num]*100:.1f}%" if probs is not None else "—"
                lines.append(f"  {emoji} [bold]{num:>2}[/bold]  ${bet:.2f}  ({prob})")
            if len(predicted) > 8:
                lines.append(f"  [dim]+{len(predicted)-8} more…[/dim]")
            lines.append(f"\n  Total: [bold yellow]${total_bet:.2f}[/bold yellow]  "
                         f"│  After: [yellow]${bal_after:.2f}[/yellow]")
            content = "\n".join(lines)

        return Panel(
            content,
            title=f"[bold cyan]🎯 AI Bet Advice — Spin #{spin_num}[/bold cyan]",
            border_style="cyan",
            expand=True,
        )

    def _render_last_result(self) -> Panel:
        if self.last_spin is None:
            return Panel("[dim]No spins yet[/dim]", title="[bold]Last Result[/bold]", border_style="dim", height=7, expand=True)

        s = self.last_spin
        n = s["number"]
        color = get_number_color(n)
        emoji = NUMBER_EMOJI[color]
        is_win = s["is_win"]
        net = s["net"]

        outcome = "[bold green]✨ WIN[/bold green]" if is_win else "[bold red]❌ LOSS[/bold red]"
        net_c = "green" if net >= 0 else "red"
        bet_label = s.get("bet_label")
        hit = n in s["predicted"]
        hit_s = "[green]✓ Hit[/green]" if hit else "[dim]✕ Miss[/dim]"

        if bet_label:
            pick_s = f"Bet: [cyan]{bet_label}[/cyan]"
        else:
            picks = ", ".join(str(p) for p in s["predicted"][:6])
            pick_s = f"Picks: [dim]{picks}[/dim]"

        content = (
            f" {emoji} [bold white]{n:>2}[/bold white]  {outcome}  "
            f"[{net_c}]{net:+.2f}[/{net_c}]  │  {hit_s}\n"
            f" {pick_s}  {self.status_msg}"
        )
        return Panel(content, title=f"[bold]Spin #{s['spin_num']}[/bold]", border_style="yellow", height=7, expand=True)

    def _render_stats(self) -> Panel:
        profit = self.balance - self.initial_balance
        p_color = "green" if profit >= 0 else "red"
        r_color = "green" if self.roi >= 0 else "red"

        tbl = Table(box=box.SIMPLE, show_header=False, padding=(0, 2), expand=True)
        tbl.add_column("Metric", style="bold white", min_width=16)
        tbl.add_column("Value", justify="right", min_width=14)

        tbl.add_row("Balance", f"[bold yellow]${self.balance:.2f}[/bold yellow]")
        tbl.add_row("Profit / Loss", f"[{p_color}]${profit:+.2f}[/{p_color}]")
        tbl.add_row("Total Spins", str(self.spin_num))
        tbl.add_row("Win Rate", f"[cyan]{self.win_rate:.1f}%[/cyan]")
        tbl.add_row("ROI", f"[{r_color}]{self.roi:+.1f}%[/{r_color}]")
        tbl.add_row("Streak", self.streak_str)
        tbl.add_row("Starting Bal.", f"${self.initial_balance:.2f}")

        return Panel(tbl, title="[bold]📊 Session Stats[/bold]", border_style="cyan", expand=True)

    def _render_log(self) -> Panel:
        if not self.recent_spins:
            return Panel("[dim]No spin history yet[/dim]", title="[bold]Recent Spins[/bold]", border_style="dim", expand=True)

        tbl = Table(box=box.SIMPLE_HEAD, show_header=True, padding=(0, 1), expand=True)
        tbl.add_column("#", width=4, justify="right", style="dim")
        tbl.add_column("Num", width=4, justify="center")
        tbl.add_column("Result", width=6, justify="center")
        tbl.add_column("Net", width=8, justify="right")
        tbl.add_column("Balance", width=10, justify="right")

        for sp in self.recent_spins:
            n = sp["number"]
            color = get_number_color(n)
            emoji = NUMBER_EMOJI[color]
            w = "[green]WIN[/green]" if sp["is_win"] else "[red]LOSS[/red]"
            nc = "green" if sp["net"] >= 0 else "red"
            tbl.add_row(
                str(sp["spin_num"]),
                f"{emoji}{n:>2}",
                w,
                f"[{nc}]{sp['net']:+.2f}[/{nc}]",
                f"${sp['balance']:.2f}",
            )

        return Panel(tbl, title="[bold]Recent Spins[/bold]", border_style="dim", expand=True)

    def _render_footer(self) -> Panel:
        if self.milestone_msg:
            text = self.milestone_msg
        elif self.session_over:
            text = " [bold]Session complete — press Ctrl+C to exit[/bold]"
        else:
            text = " [dim]Press  Ctrl+C  to stop[/dim]"
        ft = Text.from_markup(text)
        ft.justify = "center"
        return Panel(ft, style="dim", height=3, expand=True)

    # --- Summary (printed after Live exits) ---

    def print_summary(self, tracker, strategy):
        """Print final session summary to normal console (after Live screen closes)."""
        console.print()
        if tracker.total_spins == 0:
            console.print(Panel("[dim]No spins were recorded.[/dim]", border_style="dim"))
            return

        final = tracker.current_balance
        profit = final - self.initial_balance
        p_c = "green" if profit >= 0 else "red"
        r_c = "green" if tracker.roi >= 0 else "red"
        summary = tracker.summary()

        tbl = Table(title="📊 Session Summary", box=box.ROUNDED, border_style="cyan",
                    show_header=False, padding=(0, 2))
        tbl.add_column("Metric", style="bold white", min_width=18)
        tbl.add_column("Value", justify="right", min_width=16)
        tbl.add_row("Strategy", strategy.STRATEGY_NAME)
        tbl.add_row("Total Spins", str(tracker.total_spins))
        tbl.add_row("Wins", f"[green]{tracker.total_wins}[/green]")
        tbl.add_row("Losses", f"[red]{tracker.total_losses}[/red]")
        tbl.add_row("Win Rate", f"[cyan]{tracker.win_rate:.2f}%[/cyan]")
        tbl.add_row("Total Wagered", f"${tracker.total_wagered:.2f}")
        tbl.add_row("Profit / Loss", f"[{p_c}]${profit:+.2f}[/{p_c}]")
        tbl.add_row("ROI", f"[{r_c}]{tracker.roi:+.2f}%[/{r_c}]")
        tbl.add_row("Starting Balance", f"${self.initial_balance:.2f}")
        tbl.add_row("Final Balance", f"[bold yellow]${final:.2f}[/bold yellow]")
        tbl.add_row("Session Time", summary["duration"])
        console.print(tbl)
        console.print()
