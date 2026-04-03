"""Adaptive AI — dynamically picks 1-6 numbers based on model confidence."""

import numpy as np
from strategies.base import BaseStrategy


class AdaptiveStrategy(BaseStrategy):

    STRATEGY_NAME  = "🤖 Adaptive AI"
    RISK_LEVEL     = "Variable"
    NUMBERS_TO_BET = 0
    TARGET_WIN_RATE = 0.0
    MODEL_LABEL    = "adaptive"
    DESCRIPTION    = "Reads model confidence each spin and picks 1-6 numbers accordingly."

    _THRESHOLDS = [
        (0.18, 1),
        (0.12, 2),
        (0.08, 3),
        (0.06, 4),
        (0.04, 5),
    ]
    _DEFAULT_COUNT = 6

    def select_numbers(self, probabilities: np.ndarray) -> list:
        """Pick N numbers where N depends on highest probability value."""
        max_prob = float(np.max(probabilities))
        n = self._DEFAULT_COUNT
        for threshold, count in self._THRESHOLDS:
            if max_prob >= threshold:
                n = count
                break
        self.NUMBERS_TO_BET = n
        return [int(i) for i in np.argsort(probabilities)[-n:][::-1]]

    def confidence_label(self, probabilities: np.ndarray) -> str:
        """Return a human-readable confidence badge for display."""
        max_prob = float(np.max(probabilities))
        if max_prob >= 0.18:
            return f"🎯 Very High ({max_prob:.1%})"
        if max_prob >= 0.12:
            return f"📈 High ({max_prob:.1%})"
        if max_prob >= 0.08:
            return f"⚖️  Medium ({max_prob:.1%})"
        return f"📉 Low ({max_prob:.1%})"

