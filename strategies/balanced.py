"""Balanced — top 6 straight-up bets."""

import numpy as np
from strategies.base import BaseStrategy


class BalancedStrategy(BaseStrategy):

    STRATEGY_NAME  = "⚖️ Balanced"
    RISK_LEVEL     = "Medium"
    NUMBERS_TO_BET = 6
    TARGET_WIN_RATE = 16.22
    MODEL_LABEL    = "balanced"
    DESCRIPTION    = "Covers 6 numbers. Good middle ground between risk and reward."

    def select_numbers(self, probabilities: np.ndarray) -> list:
        return [int(i) for i in np.argsort(probabilities)[-6:][::-1]]
