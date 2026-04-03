"""Local roulette simulator — generates random spins for offline testing."""

import asyncio
import random
import logging
from datetime import datetime

from utils.constants import RED_NUMBERS, BLACK_NUMBERS, SPIN_INTERVAL


class Simulator:
    """Generates random roulette numbers (0–36) at a configurable rate."""

    def __init__(self, spin_interval: float = SPIN_INTERVAL):
        self.spin_interval = spin_interval
        self.running = False
        self._callbacks = []
        self._before_callbacks = []
        self._log = logging.getLogger("Simulator")
        self._spin_count = 0

    def on_number(self, callback):
        """Register an async function to receive each simulated spin."""
        self._callbacks.append(callback)

    def on_before_spin(self, callback):
        """Register an async function called BEFORE each number is generated."""
        self._before_callbacks.append(callback)

    async def run(self):
        """Spin loop: before_callbacks → sleep → generate number → callbacks."""
        self.running     = True
        self._spin_count = 0
        self._log.info("Simulator started.")

        try:
            while self.running:
                for cb in self._before_callbacks:
                    await cb()

                if self.spin_interval > 0:
                    await asyncio.sleep(self.spin_interval)

                if not self.running:
                    break

                number = random.randint(0, 36)
                self._spin_count += 1
                self._log.debug(
                    f"Sim spin #{self._spin_count}: {number} "
                    f"({self._get_color(number)})"
                )

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


    @staticmethod
    def _get_color(number: int) -> str:
        if number == 0:
            return "green"
        if number in RED_NUMBERS:
            return "red"
        return "black"
