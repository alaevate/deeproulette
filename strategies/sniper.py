"""
strategies/sniper.py
====================
Sniper — bet on the single most likely number.
Highest risk, highest reward. Theoretical hit rate: 1/37 ≈ 2.7%
"""

import numpy as np
from strategies.base import BaseStrategy


class SniperStrategy(BaseStrategy):

    STRATEGY_NAME   = "🎯 Sniper"
    RISK_LEVEL      = "Extreme"
    NUMBERS_TO_BET  = 1
    TARGET_WIN_RATE = 2.70
    MODEL_LABEL     = "sniper"
    DESCRIPTION     = (
        "Bets on the single number the AI is most confident about. "
        "Huge payout (35×) but wins are rare. For thrill seekers only."
    )

    def select_numbers(self, probabilities: np.ndarray) -> list:
        """Return only the top-1 most probable number."""
        return [int(np.argmax(probabilities))]
