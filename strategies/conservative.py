"""Conservative color betting strategy (red/black)."""

import numpy as np
from strategies.base import BaseStrategy
from config.settings import MIN_BET


class ConservativeStrategy(BaseStrategy):

    STRATEGY_NAME   = "🛡️ Conservative"
    RISK_LEVEL      = "Very Low"
    NUMBERS_TO_BET  = 1
    TARGET_WIN_RATE = 48.65
    MODEL_LABEL     = "conservative"
    DESCRIPTION     = (
        "Bets only on RED or BLACK based on AI prediction. "
        "One outside-bet decision per spin with even-money payout logic."
    )

    # European Roulette color mapping
    RED_NUMBERS = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
    BLACK_NUMBERS = {2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35}

    def __init__(self):
        super().__init__()
        self._selected_color = "RED"  # Track which color was selected

    def select_numbers(self, probabilities: np.ndarray) -> list:
        """Pick red or black, then return that color's covered numbers."""
        red_probs = sum(probabilities[num] for num in self.RED_NUMBERS)
        black_probs = sum(probabilities[num] for num in self.BLACK_NUMBERS)

        if red_probs >= black_probs:
            self._selected_color = "RED"
            selected = self.RED_NUMBERS
        else:
            self._selected_color = "BLACK"
            selected = self.BLACK_NUMBERS

        ranked = sorted(selected, key=lambda n: probabilities[n], reverse=True)
        return [int(n) for n in ranked]

    def calculate_bets(self, numbers: list, balance: float, bet_per_number: float = None) -> dict:
        """Split one outside bet equally across the selected color numbers."""
        if not numbers:
            return {}

        if bet_per_number is None:
            bet_per_number = 1.00

        total_bet = max(float(bet_per_number), MIN_BET)
        per_number = round(total_bet / len(numbers), 4)
        return {num: per_number for num in numbers}

    def evaluate_result(self, actual: int, predicted: list, bets: dict, balance: float) -> tuple:
        """Evaluate an even-money color bet using 1:1 payout."""
        total_bet = sum(bets.values())

        if actual in predicted:
            net = total_bet
        else:
            net = -total_bet

        return (actual in predicted), round(net, 2), round(balance + net, 2)

    def get_color_to_bet(self) -> str:
        """Return the color selected for this spin."""
        return self._selected_color


