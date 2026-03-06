"""
strategies/conservative.py
===========================
Conservative — bet on the top 18 numbers (half the wheel).
Low risk. Theoretical hit rate: 18/37 ≈ 48.6%
"""

import numpy as np
from strategies.base import BaseStrategy


class ConservativeStrategy(BaseStrategy):

    STRATEGY_NAME   = "🛡️ Conservative"
    RISK_LEVEL      = "Low"
    NUMBERS_TO_BET  = 18
    TARGET_WIN_RATE = 48.65
    MODEL_LABEL     = "conservative"
    DESCRIPTION     = (
        "Covers half the wheel. Wins roughly half the time. "
        "Lower individual payouts but very consistent. Great for beginners."
    )

    def select_numbers(self, probabilities: np.ndarray) -> list:
        """Return the top-18 most probable numbers, highest first."""
        return [int(i) for i in np.argsort(probabilities)[-18:][::-1]]
