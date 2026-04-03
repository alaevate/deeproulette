"""Hybrid — combines inside straight-up bets with outside category bets."""

import numpy as np
from strategies.base import BaseStrategy
from strategies.outside_bets import OUTSIDE_CATEGORIES
from config.settings import MIN_BET, PAYOUT_RATIO

_GROUPS = [
    ("Color", ["RED", "BLACK"]),
    ("Parity", ["ODD", "EVEN"]),
    ("Range", ["SMALL", "BIG"]),
    ("Dozen", ["1st 12", "2nd 12", "3rd 12"]),
    ("Column", ["Col 1", "Col 2", "Col 3"]),
]


class HybridStrategy(BaseStrategy):
    """Picks straight-up numbers AND outside bets in one combined play."""

    STRATEGY_NAME = "🎲 Hybrid"
    RISK_LEVEL = "Variable"
    NUMBERS_TO_BET = 0
    TARGET_WIN_RATE = 0.0
    MODEL_LABEL = "hybrid"
    DESCRIPTION = "AI picks inside numbers and outside bets together for maximum coverage."

    def __init__(self):
        super().__init__()
        self._inside = []
        self._outside = []

    def _best_outside(self, probabilities):
        """Evaluate each outside-bet category and return ranked picks."""
        results = []
        for _, labels in _GROUPS:
            best_label, best_mass, best_nums, best_payout = "", -1.0, set(), 1
            for label in labels:
                nums, payout = OUTSIDE_CATEGORIES[label]
                mass = float(sum(probabilities[n] for n in nums))
                if mass > best_mass:
                    best_label, best_mass = label, mass
                    best_nums, best_payout = nums, payout
            baseline = len(best_nums) / 37.0
            edge = best_mass - baseline
            results.append((best_label, best_nums, best_payout, edge))
        results.sort(key=lambda x: x[3], reverse=True)
        return results

    def select_numbers(self, probabilities: np.ndarray) -> list:
        max_prob = float(np.max(probabilities))

        if max_prob >= 0.12:
            inside_n = 1
        elif max_prob >= 0.07:
            inside_n = 2
        else:
            inside_n = 3

        self._inside = [int(i) for i in np.argsort(probabilities)[-inside_n:][::-1]]

        ranked = self._best_outside(probabilities)
        self._outside = [ranked[0]]
        if len(ranked) > 1 and ranked[1][3] > 0.015:
            self._outside.append(ranked[1])

        self.NUMBERS_TO_BET = len(self._inside)
        covered = set(self._inside)
        for _, nums, _, _ in self._outside:
            covered.update(nums)
        return sorted(covered)

    def get_display_label(self) -> str:
        inside_str = ", ".join(str(n) for n in self._inside)
        outside_str = " + ".join(b[0] for b in self._outside)
        return f"[{inside_str}] + {outside_str}"

    def calculate_bets(self, numbers: list, balance: float, bet_per_number: float = None) -> dict:
        if not numbers:
            return {}
        amount = max(float(bet_per_number or 1.00), MIN_BET)
        bets = {}
        for n in self._inside:
            bets[n] = amount
        outside_nums = set()
        for _, nums, _, _ in self._outside:
            outside_nums.update(nums)
        outside_only = outside_nums - set(self._inside)
        if outside_only:
            outside_total = amount * len(self._outside)
            per = round(outside_total / len(outside_only), 4)
            for n in outside_only:
                bets[n] = per
        return bets

    def evaluate_result(self, actual: int, predicted: list, bets: dict, balance: float) -> tuple:
        """Evaluate inside bets at 35:1 and outside bets at their category payout."""
        total_bet = sum(bets.values())
        net = 0.0
        any_win = False

        inside_bet_amount = bets.get(self._inside[0], 0) if self._inside else 0
        for num in self._inside:
            if actual == num:
                net += inside_bet_amount * PAYOUT_RATIO
                any_win = True
            else:
                net -= inside_bet_amount

        outside_nums = set()
        for _, nums, _, _ in self._outside:
            outside_nums.update(nums)
        outside_only = outside_nums - set(self._inside)
        outside_total = sum(bets.get(n, 0) for n in outside_only)
        per_cat = outside_total / max(len(self._outside), 1)

        for _, nums, payout, _ in self._outside:
            if actual in nums:
                net += per_cat * payout
                any_win = True
            else:
                net -= per_cat

        return any_win, round(net, 2), round(balance + net, 2)
