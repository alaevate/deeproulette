# Copyright 2026 alaevate
# Licensed under the Apache License, Version 2.0
"""Statistics tracker — records every spin and computes live performance metrics."""

from datetime import datetime


class StatsTracker:
    """Tracks wins, losses, balance history, and performance KPIs for one session."""

    def __init__(self):
        self.reset()

    def reset(self):
        self.total_spins = 0
        self.total_wins = 0
        self.total_losses = 0
        self.total_wagered = 0.0
        self.total_profit = 0.0
        self.history = []
        self.session_start = datetime.now()

    def record(self, number: int, predicted: list, bets: dict,
               is_win: bool, net: float, balance: float):
        """Add one spin to the session history."""
        self.total_spins += 1
        self.total_wagered += sum(bets.values())
        self.total_profit += net

        if is_win:
            self.total_wins   += 1
        else:
            self.total_losses += 1

        self.history.append({
            "spin_num":  self.total_spins,
            "result":    number,
            "predicted": predicted,
            "is_win":    is_win,
            "net":       net,
            "balance":   balance,
        })

    @property
    def win_rate(self) -> float:
        """Percentage of spins that were wins."""
        if self.total_spins == 0:
            return 0.0
        return (self.total_wins / self.total_spins) * 100

    @property
    def roi(self) -> float:
        """Return on investment — profit as a percentage of total amount wagered."""
        if self.total_wagered == 0:
            return 0.0
        return (self.total_profit / self.total_wagered) * 100

    @property
    def current_balance(self) -> float:
        return self.history[-1]["balance"] if self.history else 0.0

    def streak(self) -> tuple:
        """Current streak as (kind, length) where kind is 'W' or 'L'."""
        if not self.history:
            return "N", 0
        kind  = "W" if self.history[-1]["is_win"] else "L"
        count = 0
        for entry in reversed(self.history):
            if entry["is_win"] == (kind == "W"):
                count += 1
            else:
                break
        return kind, count

    def summary(self) -> dict:
        duration = datetime.now() - self.session_start
        return {
            "spins":         self.total_spins,
            "wins":          self.total_wins,
            "losses":        self.total_losses,
            "win_rate":      f"{self.win_rate:.2f}%",
            "roi":           f"{self.roi:.2f}%",
            "total_wagered": f"${self.total_wagered:.2f}",
            "total_profit":  f"${self.total_profit:+.2f}",
            "duration":      str(duration).split(".")[0],
        }
