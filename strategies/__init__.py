"""
strategies/__init__.py
======================
Strategy registry — all available strategies in one place.
"""

from strategies.sniper       import SniperStrategy
from strategies.aggressive   import AggressiveStrategy
from strategies.balanced     import BalancedStrategy
from strategies.conservative import ConservativeStrategy
from strategies.adaptive     import AdaptiveStrategy

# Ordered list shown in the interactive menu
ALL_STRATEGIES = [
    SniperStrategy,
    AggressiveStrategy,
    BalancedStrategy,
    ConservativeStrategy,
    AdaptiveStrategy,
]

__all__ = [
    "SniperStrategy",
    "AggressiveStrategy",
    "BalancedStrategy",
    "ConservativeStrategy",
    "AdaptiveStrategy",
    "ALL_STRATEGIES",
]
