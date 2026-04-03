## Copyright 2026 alaevate
# Licensed under the Apache License, Version 2.0
"""Fusion — combines 1 to 5 outside bets based on AI probability analysis."""

import numpy as np
from strategies.base import BaseStrategy
from strategies.outside_bets import OUTSIDE_CATEGORIES
from config.settings import MIN_BET

_GROUPS = [
    ("Color", ["RED", "BLACK"]),
    ("Parity", ["ODD", "EVEN"]),
    ("Range", ["SMALL", "BIG"]),
    ("Dozen", ["1st 12", "2nd 12", "3rd 12"]),
    ("Column", ["Col 1", "Col 2", "Col 3"]),
]


class FusionStrategy(BaseStrategy):
    """Picks the best option from each outside-bet category, places 1-5 bets."""

    STRATEGY_NAME = "🧠 Fusion"
    RISK_LEVEL = "Variable"
    NUMBERS_TO_BET = 0
    TARGET_WIN_RATE = 0.0
    MODEL_LABEL = "fusion"
    DESCRIPTION = "Combines up to 5 outside bets using AI probability analysis."

    def __init__(self):
        super().__init__()
        self._active_bets = []

    def _evaluate_groups(self, probabilities: np.ndarray) -> list:
        """For each category group, find the best option and its edge over baseline."""
        results = []
        for group_name, labels in _GROUPS:
            best_label, best_mass, best_nums, best_payout = "", -1.0, set(), 1
            for label in labels:
                nums, payout = OUTSIDE_CATEGORIES[label]
                mass = float(sum(probabilities[n] for n in nums))
                if mass > best_mass:
                    best_label, best_mass = label, mass
                    best_nums, best_payout = nums, payout
            baseline = len(best_nums) / 37.0
            edge = best_mass - baseline
            results.append((group_name, best_label, best_nums, best_payout, edge))
        return results

    def select_numbers(self, probabilities: np.ndarray) -> list:
        groups = self._evaluate_groups(probabilities)
        groups.sort(key=lambda x: x[4], reverse=True)

        self._active_bets = [groups[0]]
        for g in groups[1:]:
            if g[4] > 0.015 and len(self._active_bets) < 5:
                self._active_bets.append(g)

        self.NUMBERS_TO_BET = len(self._active_bets)
        covered = set()
        for _, _, nums, _, _ in self._active_bets:
            covered.update(nums)
        return sorted(covered)

    def get_display_label(self) -> str:
        return " + ".join(b[1] for b in self._active_bets)

    def calculate_bets(self, numbers: list, balance: float, bet_per_number: float = None) -> dict:
        if not numbers or not self._active_bets:
            return {}
        total_per_bet = max(float(bet_per_number or 1.00), MIN_BET)
        total_amount = total_per_bet * len(self._active_bets)
        per_number = round(total_amount / len(numbers), 4)
        return {n: per_number for n in numbers}

    def evaluate_result(self, actual: int, predicted: list, bets: dict, balance: float) -> tuple:
        """Evaluate each outside bet independently with correct payouts."""
        total_wagered = sum(bets.values())
        bet_per_category = total_wagered / max(len(self._active_bets), 1)

        net = 0.0
        any_win = False
        for _, _, nums, payout, _ in self._active_bets:
            if actual in nums:
                net += bet_per_category * payout
                any_win = True
            else:
                net -= bet_per_category

        return any_win, round(net, 2), round(balance + net, 2)

