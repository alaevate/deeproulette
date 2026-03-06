"""
strategies/base.py
==================
Abstract base class that every strategy must inherit from.

Subclasses only need to implement `select_numbers()`.
Bet sizing and win/loss evaluation are handled here, shared by all strategies.
"""

from abc import ABC, abstractmethod
import numpy as np
from config.settings import MIN_BET, BET_FRACTION, PAYOUT_RATIO


class BaseStrategy(ABC):
    """
    Contract for all prediction strategies.

    Required override:
        select_numbers(probabilities) → list[int]

    Optional override:
        calculate_bets(numbers, balance) → dict[int, float]
    """

    # ── Class-level metadata (override in each subclass) ──────────────────────
    STRATEGY_NAME   = "Base Strategy"
    RISK_LEVEL      = "Unknown"
    NUMBERS_TO_BET  = 0
    TARGET_WIN_RATE = 0.0
    DESCRIPTION     = ""
    MODEL_LABEL     = "base"   # used for saved model filename

    # ── Abstract interface ────────────────────────────────────────────────────

    @abstractmethod
    def select_numbers(self, probabilities: np.ndarray) -> list:
        """
        Given the model's output probability array (shape: 37,),
        return a list of integers (roulette numbers) to bet on.
        """
        ...

    # ── Shared logic (works for all strategies) ───────────────────────────────

    def calculate_bets(self, numbers: list, balance: float) -> dict:
        """
        Spread BET_FRACTION of the current balance equally across all chosen numbers.
        Each number always receives at least MIN_BET.

        Returns: { number: bet_amount, ... }
        """
        if not numbers:
            return {}

        total_available = max(balance * BET_FRACTION, MIN_BET * len(numbers))
        per_number      = total_available / len(numbers)
        per_number      = max(per_number, MIN_BET)
        # Round to nearest $0.10 so bets only change in $0.10 steps
        per_number      = round(round(per_number / 0.10) * 0.10, 2)
        per_number      = max(per_number, MIN_BET)
        return {num: per_number for num in numbers}

    def evaluate_result(self, actual: int, predicted: list,
                        bets: dict, balance: float) -> tuple:
        """
        Determine whether the spin was a win or loss and compute the net change.

        On a win:  net = bets[actual] × 35  −  total_bet
        On a loss: net = −total_bet

        Returns: (is_win: bool, net: float, new_balance: float)
        """
        total_bet = sum(bets.values())
        if actual in predicted:
            winnings = bets[actual] * PAYOUT_RATIO
            net      = winnings - total_bet
        else:
            net = -total_bet

        return (actual in predicted), round(net, 2), round(balance + net, 2)

    @property
    def model_filename(self) -> str:
        """The saved model filename derived from the strategy label."""
        return f"{self.MODEL_LABEL}_model"

    def info(self) -> dict:
        """Return a summary dict for display in the UI."""
        return {
            "name":        self.STRATEGY_NAME,
            "risk":        self.RISK_LEVEL,
            "numbers":     self.NUMBERS_TO_BET,
            "win_chance":  f"{self.TARGET_WIN_RATE:.1f}%",
            "description": self.DESCRIPTION,
        }
