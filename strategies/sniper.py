"""Sniper — single number straight-up bet."""

import numpy as np
from strategies.base import BaseStrategy


class SniperStrategy(BaseStrategy):

    STRATEGY_NAME  = "🎯 Sniper"
    RISK_LEVEL     = "Extreme"
    NUMBERS_TO_BET = 1
    TARGET_WIN_RATE = 2.70
    MODEL_LABEL    = "sniper"
    DESCRIPTION    = "Bets on the single most confident number. 35x payout, rare wins."

    def select_numbers(self, probabilities: np.ndarray) -> list:
        return [int(np.argmax(probabilities))]
