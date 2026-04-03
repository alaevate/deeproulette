# Copyright 2026 alaevate
# Licensed under the Apache License, Version 2.0
"""Abstract base class for all betting strategies."""

from abc import ABC, abstractmethod
import numpy as np
from config.settings import MIN_BET, PAYOUT_RATIO


class BaseStrategy(ABC):

    STRATEGY_NAME = "Base Strategy"
    RISK_LEVEL = "Unknown"
    NUMBERS_TO_BET = 0
    TARGET_WIN_RATE = 0.0
    DESCRIPTION = ""
    MODEL_LABEL = "base"

    @abstractmethod
    def select_numbers(self, probabilities: np.ndarray) -> list:
        """Return a list of roulette numbers to bet on given model probabilities."""
        ...

    def get_display_label(self) -> str:
        """Override in outside/combo strategies to return a label like 'RED' or 'RED + ODD'."""
        return None

    def calculate_bets(self, numbers: list, balance: float, bet_per_number: float = None) -> dict:
        """Place a flat bet on each chosen number."""
        if not numbers:
            return {}
        if bet_per_number is None:
            bet_per_number = 1.00
        per_number = max(bet_per_number, MIN_BET)
        per_number = round(round(per_number / 0.10) * 0.10, 2)
        per_number = max(per_number, MIN_BET)
        return {num: per_number for num in numbers}

    def evaluate_result(self, actual: int, predicted: list, bets: dict, balance: float) -> tuple:
        """Win pays 35:1 on the matched number (stake returned + 35× profit) minus total wagered."""
        total_bet = sum(bets.values())
        if actual in predicted:
            winnings = bets[actual] * (PAYOUT_RATIO + 1)   # 36 units back (35 profit + original bet)
            net = winnings - total_bet
        else:
            net = -total_bet
        return (actual in predicted), round(net, 2), round(balance + net, 2)

    @property
    def model_filename(self) -> str:
        return f"{self.MODEL_LABEL}_model"

    def info(self) -> dict:
        return {
            "name": self.STRATEGY_NAME,
            "risk": self.RISK_LEVEL,
            "numbers": self.NUMBERS_TO_BET,
            "win_chance": f"{self.TARGET_WIN_RATE:.1f}%",
            "description": self.DESCRIPTION,
        }
