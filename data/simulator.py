"""
data/simulator.py
=================
Local roulette simulator — generates random spin results without any
internet connection.

Produces the exact same callback interface as LiveFeed so the rest of
the system works identically in both live and simulated modes.
"""

import asyncio
import random
import logging
from datetime import datetime

from config.settings import SPIN_INTERVAL, RED_NUMBERS, BLACK_NUMBERS


class Simulator:
    """
    Generates random roulette numbers (0–36) at a configurable rate.
    Register a callback with  on_number(async_fn)  to receive each spin.
    """

    def __init__(self, spin_interval: float = SPIN_INTERVAL):
        self.spin_interval   = spin_interval
        self.running         = False
        self._callbacks      = []
        self._before_callbacks = []
        self._log            = logging.getLogger("Simulator")
        self._spin_count     = 0

    def on_number(self, callback):
        """Register an async function to receive each simulated spin."""
        self._callbacks.append(callback)

    def on_before_spin(self, callback):
        """Register an async function called BEFORE each number is generated."""
        self._before_callbacks.append(callback)

    async def run(self):
        """
        Start generating spins.  Runs until  stop()  is called or the task
        is cancelled.

        Order per iteration:
          1. Call before_spin callbacks  (AI shows advice)
          2. Sleep spin_interval         (user reads and places bets)
          3. Generate number             (wheel spins)
          4. Call number callbacks       (engine evaluates + shows result)
        """
        self.running     = True
        self._spin_count = 0
        self._log.info("Simulator started.")

        try:
            while self.running:
                # ── 1. Show AI bet advice ────────────────────────────
                for cb in self._before_callbacks:
                    await cb()

                # ── 2. Pause (user reads advice / places bets) ──────────
                if self.spin_interval > 0:
                    await asyncio.sleep(self.spin_interval)

                if not self.running:
                    break

                # ── 3. Generate result ──────────────────────────────
                number = random.randint(0, 36)
                self._spin_count += 1
                self._log.debug(
                    f"Sim spin #{self._spin_count}: {number} "
                    f"({self._get_color(number)})"
                )

                # ── 4. Dispatch to engine ────────────────────────────
                for cb in self._callbacks:
                    await cb(number)

        except asyncio.CancelledError:
            pass
        finally:
            self.running = False
            self._log.info(f"Simulator stopped after {self._spin_count} spins.")

    def stop(self):
        """Signal the simulator to stop after the current spin."""
        self.running = False

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _get_color(number: int) -> str:
        if number == 0:
            return "green"
        if number in RED_NUMBERS:
            return "red"
        return "black"
