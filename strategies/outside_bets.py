## Copyright 2026 alaevate
# Licensed under the Apache License, Version 2.0
"""Outside-bet strategies (color, parity, range, dozen, column)."""

import numpy as np
from strategies.base import BaseStrategy
from config.settings import MIN_BET

RED = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
BLACK = {2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35}

OUTSIDE_CATEGORIES = {
    "RED": (RED, 1), "BLACK": (BLACK, 1),
    "ODD": ({n for n in range(1, 37) if n % 2 == 1}, 1),
    "EVEN": ({n for n in range(1, 37) if n % 2 == 0}, 1),
    "SMALL": (set(range(1, 19)), 1), "BIG": (set(range(19, 37)), 1),
    "1st 12": (set(range(1, 13)), 2), "2nd 12": (set(range(13, 25)), 2), "3rd 12": (set(range(25, 37)), 2),
    "Col 1": ({1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34}, 2),
    "Col 2": ({2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35}, 2),
    "Col 3": ({3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36}, 2),
}


class _OutsideBetStrategy(BaseStrategy):
    """Base for single outside-bet strategies that pick from a pair/group of sets."""

    SETS = {}

    def __init__(self):
        super().__init__()
        self._pick = ""
        self._pick_numbers = set()
        self._pick_payout = 1

    def select_numbers(self, probabilities: np.ndarray) -> list:
        """Pick the set option with the highest probability mass."""
        best_label, best_mass = "", -1.0
        for label, (numbers, _) in self.SETS.items():
            mass = float(sum(probabilities[n] for n in numbers))
            if mass > best_mass:
                best_label, best_mass = label, mass
        nums, payout = self.SETS[best_label]
        self._pick = best_label
        self._pick_numbers = nums
        self._pick_payout = payout
        return sorted(nums)

    def get_display_label(self) -> str:
        return self._pick

    def calculate_bets(self, numbers: list, balance: float, bet_per_number: float = None) -> dict:
        """Single outside bet — total amount equals bet_per_number."""
        if not numbers:
            return {}
        total = max(float(bet_per_number or 1.00), MIN_BET)
        per = round(total / len(numbers), 4)
        return {n: per for n in numbers}

    def evaluate_result(self, actual: int, predicted: list, bets: dict, balance: float) -> tuple:
        """Outside-bet payout: 1:1 for even-money, 2:1 for dozens/columns."""
        total_bet = sum(bets.values())
        if actual in self._pick_numbers:
            net = total_bet * self._pick_payout
        else:
            net = -total_bet
        return (actual in self._pick_numbers), round(net, 2), round(balance + net, 2)


class RedBlackStrategy(_OutsideBetStrategy):
    STRATEGY_NAME = "🔴⚫ Red/Black"
    RISK_LEVEL = "Low"
    NUMBERS_TO_BET = 1
    TARGET_WIN_RATE = 48.65
    MODEL_LABEL = "redblack"
    DESCRIPTION = "Bets on red or black."
    SETS = {"RED": (RED, 1), "BLACK": (BLACK, 1)}


class OddEvenStrategy(_OutsideBetStrategy):
    STRATEGY_NAME = "🔢 Odd/Even"
    RISK_LEVEL = "Low"
    NUMBERS_TO_BET = 1
    TARGET_WIN_RATE = 48.65
    MODEL_LABEL = "oddeven"
    DESCRIPTION = "Bets on odd or even."
    SETS = {
        "ODD": ({n for n in range(1, 37) if n % 2 == 1}, 1),
        "EVEN": ({n for n in range(1, 37) if n % 2 == 0}, 1),
    }


class LowHighStrategy(_OutsideBetStrategy):
    STRATEGY_NAME = "📏 Small/Big"
    RISK_LEVEL = "Low"
    NUMBERS_TO_BET = 1
    TARGET_WIN_RATE = 48.65
    MODEL_LABEL = "lowhigh"
    DESCRIPTION = "Bets on small (1-18) or big (19-36)."
    SETS = {"SMALL": (set(range(1, 19)), 1), "BIG": (set(range(19, 37)), 1)}


class DozensStrategy(_OutsideBetStrategy):
    STRATEGY_NAME = "🧩 Dozens"
    RISK_LEVEL = "Medium"
    NUMBERS_TO_BET = 1
    TARGET_WIN_RATE = 32.43
    MODEL_LABEL = "dozens"
    DESCRIPTION = "Bets on the strongest dozen: 1-12, 13-24, or 25-36."
    SETS = {
        "1st 12": (set(range(1, 13)), 2),
        "2nd 12": (set(range(13, 25)), 2),
        "3rd 12": (set(range(25, 37)), 2),
    }


class ColumnsStrategy(_OutsideBetStrategy):
    STRATEGY_NAME = "📊 Columns"
    RISK_LEVEL = "Medium"
    NUMBERS_TO_BET = 1
    TARGET_WIN_RATE = 32.43
    MODEL_LABEL = "columns"
    DESCRIPTION = "Bets on the strongest table column."
    SETS = {
        "Col 1": ({1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34}, 2),
        "Col 2": ({2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35}, 2),
        "Col 3": ({3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36}, 2),
    }
