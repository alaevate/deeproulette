# Copyright 2026 alaevate
# Licensed under the Apache License, Version 2.0
"""Aggressive — top 3 straight-up bets."""

import numpy as np
from strategies.base import BaseStrategy


class AggressiveStrategy(BaseStrategy):

    STRATEGY_NAME  = "🔥 Aggressive"
    RISK_LEVEL     = "High"
    NUMBERS_TO_BET = 3
    TARGET_WIN_RATE = 8.11
    MODEL_LABEL    = "aggressive"
    DESCRIPTION    = "Covers the top 3 AI predictions. High reward, moderate spread."

    def select_numbers(self, probabilities: np.ndarray) -> list:
        return [int(i) for i in np.argsort(probabilities)[-3:][::-1]]
