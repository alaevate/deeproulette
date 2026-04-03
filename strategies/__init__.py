"""Strategy registry."""

from strategies.sniper       import SniperStrategy
from strategies.aggressive   import AggressiveStrategy
from strategies.balanced     import BalancedStrategy
from strategies.adaptive     import AdaptiveStrategy
from strategies.outside_bets import (
    RedBlackStrategy,
    OddEvenStrategy,
    LowHighStrategy,
    DozensStrategy,
    ColumnsStrategy,
)
from strategies.fusion       import FusionStrategy
from strategies.hybrid       import HybridStrategy

INSIDE_STRATEGIES = [
    SniperStrategy,
    AggressiveStrategy,
    BalancedStrategy,
]

OUTSIDE_STRATEGIES = [
    RedBlackStrategy,
    OddEvenStrategy,
    LowHighStrategy,
    DozensStrategy,
    ColumnsStrategy,
]

AI_STRATEGIES = [
    AdaptiveStrategy,
    FusionStrategy,
    HybridStrategy,
]

ALL_STRATEGIES = INSIDE_STRATEGIES + OUTSIDE_STRATEGIES + AI_STRATEGIES

__all__ = [
    "SniperStrategy",
    "AggressiveStrategy",
    "BalancedStrategy",
    "AdaptiveStrategy",
    "RedBlackStrategy",
    "OddEvenStrategy",
    "LowHighStrategy",
    "DozensStrategy",
    "ColumnsStrategy",
    "FusionStrategy",
    "HybridStrategy",
    "INSIDE_STRATEGIES",
    "OUTSIDE_STRATEGIES",
    "AI_STRATEGIES",
    "ALL_STRATEGIES",
]
