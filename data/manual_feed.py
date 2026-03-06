"""
data/manual_feed.py
===================
Manual entry mode — the user types each roulette result themselves.

Before each prompt the engine's `show_advice` callback fires so the AI
can display exactly where to bet and how much.  Uses the same callback
interface as LiveFeed and Simulator so the rest of the system is unchanged.
"""

import asyncio
import logging


class ManualFeed:
    """
    Prompts the user to enter each spin result (0–36) manually.

    Flow per spin:
        1. Call on_before_spin callback → engine shows AI bet advice
        2. Prompt user for the actual result
        3. Call on_number callbacks → engine evaluates and updates stats
    """

    def __init__(self):
        self._number_callbacks     = []
        self._before_spin_callback = None
        self.running               = True
        self._log                  = logging.getLogger("ManualFeed")

    def on_number(self, callback):
        """Register an async function to receive each entered number."""
        self._number_callbacks.append(callback)

    def on_before_spin(self, callback):
        """Register an async function called BEFORE the user is prompted."""
        self._before_spin_callback = callback

    async def run(self):
        """Run the manual input loop until the user quits or Ctrl+C."""
        loop = asyncio.get_event_loop()

        while self.running:
            # ── Step 1: show AI bet advice ───────────────────────────────
            if self._before_spin_callback:
                await self._before_spin_callback()

            if not self.running:
                break

            # ── Step 2: blocking input in a thread so the async loop stays alive
            number = await loop.run_in_executor(None, self._prompt)

            if number is None:
                break

            # ── Step 3: dispatch to engine ───────────────────────────────
            for cb in self._number_callbacks:
                await cb(number)

    # ── Internal ──────────────────────────────────────────────────────────────

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
