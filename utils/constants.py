# Copyright 2026 alaevate
# Licensed under the Apache License, Version 2.0
"""Internal roulette constants."""

SPIN_INTERVAL = 5      # seconds between spins in simulation mode
PING_INTERVAL = 60     # seconds between WebSocket keepalive pings
# Each entry: (label, description, spin_interval_seconds)
SPEED_PRESETS = [
    ("Normal",   "1 spin every 5 seconds  (realistic)",   5.0),
    ("Fast",     "1 spin every 2 seconds",                2.0),
    ("Turbo",    "1 spin every 0.5 seconds",              0.5),
]
RED_NUMBERS   = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
BLACK_NUMBERS = {2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35}


def get_number_color(n: int) -> str:
    """Return 'red', 'black', or 'green' for a given roulette number."""
    if n == 0:
        return "green"
    if n in RED_NUMBERS:
        return "red"
    return "black"
