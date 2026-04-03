# Copyright 2026 alaevate
# Licensed under the Apache License, Version 2.0
"""Manual entry feed — user types each roulette result for AI advisory mode."""

import asyncio
import logging


class ManualFeed:
    """Prompts the user to type each spin result (0–36). before_spin → prompt → callbacks."""

    def __init__(self):
        self._number_callbacks = []
        self._before_spin_callback = None
        self.running = True
        self._log = logging.getLogger("ManualFeed")

    def on_number(self, callback):
        """Register an async function to receive each entered number."""
        self._number_callbacks.append(callback)

    def on_before_spin(self, callback):
        """Register an async function called BEFORE the user is prompted."""
        self._before_spin_callback = callback

    def stop(self):
        """Signal the manual feed to stop."""
        self.running = False

    async def run(self):
        """Run the manual input loop until the user quits or Ctrl+C."""
        loop = asyncio.get_event_loop()

        while self.running:
            if self._before_spin_callback:
                await self._before_spin_callback()

            if not self.running:
                break

            number = await loop.run_in_executor(None, self._prompt)

            if number is None:
                break

            for cb in self._number_callbacks:
                await cb(number)


    def _prompt(self):
        """Blocking prompt — runs inside a thread-pool executor."""
        while True:
            try:
                raw = input("\n  🎰  Enter result (0-36)  or  'q' to quit: ").strip()
            except (KeyboardInterrupt, EOFError):
                self.running = False
                return None

            if raw.lower() in ("q", "quit", "exit"):
                self.running = False
                return None

            try:
                n = int(raw)
                if 0 <= n <= 36:
                    return n
                print("  ⚠  Number must be between 0 and 36. Try again.")
            except ValueError:
                print("  ⚠  Invalid input — please type a number from 0 to 36.")
