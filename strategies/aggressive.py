"""
strategies/aggressive.py
========================
Aggressive — bet on the top 3 most likely numbers.
High risk. Theoretical hit rate: 3/37 ≈ 8.1%
"""

import numpy as np
from strategies.base import BaseStrategy


class AggressiveStrategy(BaseStrategy):

    STRATEGY_NAME   = "🔥 Aggressive"
    RISK_LEVEL      = "High"
    NUMBERS_TO_BET  = 3
    TARGET_WIN_RATE = 8.11
    MODEL_LABEL     = "aggressive"
    DESCRIPTION     = (
        "Covers the top 3 AI predictions. High reward potential "
        "with moderate bet distribution. Good for confident AI sessions."
    )

    def select_numbers(self, probabilities: np.ndarray) -> list:
        """Return the top-3 most probable numbers, highest first."""
        return [int(i) for i in np.argsort(probabilities)[-3:][::-1]]
