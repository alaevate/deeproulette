"""
strategies/balanced.py
======================
Balanced — bet on the top 6 most likely numbers.
Medium risk. Theoretical hit rate: 6/37 ≈ 16.2%
"""

import numpy as np
from strategies.base import BaseStrategy


class BalancedStrategy(BaseStrategy):

    STRATEGY_NAME   = "⚖️ Balanced"
    RISK_LEVEL      = "Medium"
    NUMBERS_TO_BET  = 6
    TARGET_WIN_RATE = 16.22
    MODEL_LABEL     = "balanced"
    DESCRIPTION     = (
        "Covers 6 numbers — a solid middle ground between risk and reward. "
        "Recommended for most users starting out."
    )

    def select_numbers(self, probabilities: np.ndarray) -> list:
        """Return the top-6 most probable numbers, highest first."""
        return [int(i) for i in np.argsort(probabilities)[-6:][::-1]]
