"""
strategies/adaptive.py
======================
Adaptive AI — the model decides how many numbers to bet on each spin
based on its own confidence level.

Confidence thresholds:
  ≥ 15%  → Sniper   (1 number)
  ≥  8%  → Aggressive (3 numbers)
  ≥  5%  → Balanced  (6 numbers)
  <  5%  → Conservative (18 numbers)

The AI shifts risk dynamically — more aggressive when certain,
more conservative when uncertain.
"""

import numpy as np
from strategies.base import BaseStrategy


class AdaptiveStrategy(BaseStrategy):

    STRATEGY_NAME   = "🤖 Adaptive AI"
    RISK_LEVEL      = "Variable"
    NUMBERS_TO_BET  = 0       # changes every spin
    TARGET_WIN_RATE = 0.0     # varies with confidence
    MODEL_LABEL     = "adaptive"
    DESCRIPTION     = (
        "The AI reads its own confidence each spin and automatically adjusts "
        "how many numbers to bet on. Safest when uncertain, boldest when sure."
    )

    # Confidence thresholds
    _SNIPER_THRESHOLD      = 0.15   # max prob ≥ 15% → bet 1 number
    _AGGRESSIVE_THRESHOLD  = 0.08   # max prob ≥  8% → bet 3 numbers
    _BALANCED_THRESHOLD    = 0.05   # max prob ≥  5% → bet 6 numbers
    # below 5% → bet 18 numbers

    def select_numbers(self, probabilities: np.ndarray) -> list:
        """
        Inspect the maximum probability and pick the appropriate coverage width.
        Updates NUMBERS_TO_BET so the display can show the current mode.
        """
        max_prob = float(np.max(probabilities))

        if max_prob >= self._SNIPER_THRESHOLD:
            n = 1
        elif max_prob >= self._AGGRESSIVE_THRESHOLD:
            n = 3
        elif max_prob >= self._BALANCED_THRESHOLD:
            n = 6
        else:
            n = 18

        self.NUMBERS_TO_BET = n
        return [int(i) for i in np.argsort(probabilities)[-n:][::-1]]

    def confidence_label(self, probabilities: np.ndarray) -> str:
        """Return a human-readable confidence label for the current spin."""
        max_prob = float(np.max(probabilities))
        if max_prob >= self._SNIPER_THRESHOLD:
            return f"Very High ({max_prob:.1%})"
        if max_prob >= self._AGGRESSIVE_THRESHOLD:
            return f"High ({max_prob:.1%})"
        if max_prob >= self._BALANCED_THRESHOLD:
            return f"Medium ({max_prob:.1%})"
        return f"Low ({max_prob:.1%})"
