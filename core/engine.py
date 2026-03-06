"""
core/engine.py
==============
Prediction Engine — the heart of DeepRoulette.

Orchestrates the full pipeline for every roulette spin:
  Data feed  →  History  →  AI prediction  →  Bet sizing
  →  Win / Loss accounting  →  Stats update  →  UI callback
  →  (optional) Online model update

Usage:
    engine = PredictionEngine(strategy, balance, auto_train, use_live)
    engine.on_spin_complete = my_display_fn
    await engine.run()
"""

import asyncio
import logging

from models.neural_network  import RouletteNeuralNetwork
from strategies.base        import BaseStrategy
from core.trainer           import ModelTrainer
from utils.tracker          import StatsTracker
from utils.logger           import setup_logger
from config.settings        import (
    SEQUENCE_LENGTH, MAX_HISTORY, AUTO_TRAIN_MIN,
    CASINO_WS_URL, CASINO_ID, TABLE_ID, CURRENCY,
    OFFLINE_MODELS_DIR, ONLINE_MODELS_DIR,
)


class PredictionEngine:
    """
    Central controller.  Works with any BaseStrategy subclass and any
    data source (LiveFeed or Simulator).

    UI hooks (all optional):
        on_spin_complete(spin_data: dict)   — called after each evaluated spin
        on_waiting(current, needed)         — called while history is being built
        on_model_status(message: str)       — called when model loads / trains
        on_balance_empty()                  — called when balance reaches zero
    """

    def __init__(
        self,
        strategy:        BaseStrategy,
        initial_balance: float,
        auto_train:      bool  = False,
        use_live:        bool  = True,
        spin_interval:   float = 5.0,
        manual_mode:     bool  = False,
    ):
        self.strategy        = strategy
        self.balance         = initial_balance
        self._init_balance   = initial_balance
        self.auto_train      = auto_train
        self.use_live        = use_live
        self.spin_interval   = spin_interval
        self.manual_mode     = manual_mode

        self.history         = []
        self.tracker         = StatsTracker()
        self._log            = setup_logger()
        self._running        = True

        # ── Pending state for manual mode (pre-computed advice) ──
        self._pending_predicted = None
        self._pending_bets      = None
        self._pending_probs     = None

        # ── UI callbacks ──
        self.on_spin_complete  = None
        self.on_waiting        = None
        self.on_model_status   = None
        self.on_balance_empty  = None
        self.on_advice         = None   # manual mode: fired before each spin

        # ── Neural network ──
        # Load from offline folder (trained weights); online updates save to online folder
        self.nn = RouletteNeuralNetwork(
            model_name=strategy.model_filename,
            save_dir=OFFLINE_MODELS_DIR,
        )
        self.nn.load()

        is_fresh = not self.nn.is_trained()
        if self.on_model_status:
            status = "New untrained model created." if is_fresh else "Existing model loaded."
            self.on_model_status(status)

        # Online trainer writes checkpoints — folder depends on live vs sim
        self.trainer = ModelTrainer(self.nn, verbose=False, use_live=use_live)

    # ── Spin handler ──────────────────────────────────────────────────────────

    async def handle_spin(self, number: int):
        """
        Called by the data feed for every new roulette number.
        Full pipeline: record → predict → bet → evaluate → report
        """
        if not self._running:
            return

        # Append and trim history
        self.history.append(number)
        if len(self.history) > MAX_HISTORY:
            self.history = self.history[-MAX_HISTORY:]

        # Need at least SEQUENCE_LENGTH spins before predicting
        if len(self.history) < SEQUENCE_LENGTH:
            if self.on_waiting and self.use_live:
                # Sim/manual waiting is shown by show_advice (before_spin hook)
                self.on_waiting(len(self.history), SEQUENCE_LENGTH)
            return

        # ── 1 & 2. Predict and size bets ────────────────────────────────────
        if self._pending_predicted is not None:
            # Use the pre-spin advice already shown to the user (all non-live modes)
            predicted               = self._pending_predicted
            bets                    = self._pending_bets
            probabilities           = self._pending_probs
            self._pending_predicted = None
            self._pending_bets      = None
            self._pending_probs     = None
        else:
            input_tensor  = RouletteNeuralNetwork.build_prediction_input(self.history)
            probabilities = self.nn.model.predict(input_tensor, verbose=0)[0]
            predicted     = self.strategy.select_numbers(probabilities)
            bets          = self.strategy.calculate_bets(predicted, self.balance)

        total_bet = sum(bets.values())

        # ── 3. Evaluate result ───────────────────────────────────────────────
        is_win, net, new_balance = self.strategy.evaluate_result(
            number, predicted, bets, self.balance
        )
        self.balance = new_balance

        # ── 4. Record stats ──────────────────────────────────────────────────
        self.tracker.record(number, predicted, bets, is_win, net, self.balance)

        # ── 5. Online training ───────────────────────────────────────────────
        model_saved = False
        if self.auto_train and len(self.history) >= AUTO_TRAIN_MIN:
            model_saved = self.trainer.train_online(self.history)

        # ── 6. Log to file ───────────────────────────────────────────────────
        self._log.info(
            f"Spin {self.tracker.total_spins:>5} | "
            f"Result: {number:>2} | "
            f"{'WIN ' if is_win else 'LOSS'} {net:>+7.2f} | "
            f"Balance: {self.balance:>8.2f} | "
            f"WR: {self.tracker.win_rate:>5.1f}% | "
            f"ROI: {self.tracker.roi:>+6.1f}%"
        )

        # ── 7. Notify UI ─────────────────────────────────────────────────────
        if self.on_spin_complete:
            self.on_spin_complete({
                "number":        number,
                "predicted":     predicted,
                "bets":          bets,
                "total_bet":     total_bet,
                "is_win":        is_win,
                "net":           net,
                "balance":       self.balance,
                "win_rate":      self.tracker.win_rate,
                "roi":           self.tracker.roi,
                "spin_num":      self.tracker.total_spins,
                "streak":        self.tracker.streak(),
                "model_saved":   model_saved,
                "probabilities": probabilities,
            })

        # ── 8. Balance check ─────────────────────────────────────────────────
        if self.balance <= 0:
            self._running = False
            if self.on_balance_empty:
                self.on_balance_empty()
        # ── 9. Pre-compute next advice for live mode ───────────────────────
        # Sim and manual show advice BEFORE the spin via on_before_spin.
        # Live mode has no before_spin hook, so advice is shown after each result
        # (which is immediately before the next spin arrives).
        if self.use_live and self._running:
            await self.show_advice()
    # ── Manual mode advice ────────────────────────────────────────────────────

    async def show_advice(self):
        """
        Called by ManualFeed before the user types the spin result.
        Computes the AI recommendation and fires the on_advice callback.
        """
        if len(self.history) < SEQUENCE_LENGTH:
            if self.on_waiting and not self.use_live:
                self.on_waiting(len(self.history), SEQUENCE_LENGTH)
            self._pending_predicted = None
            self._pending_bets      = None
            self._pending_probs     = None
            return

        input_tensor  = RouletteNeuralNetwork.build_prediction_input(self.history)
        probabilities = self.nn.model.predict(input_tensor, verbose=0)[0]
        predicted     = self.strategy.select_numbers(probabilities)
        bets          = self.strategy.calculate_bets(predicted, self.balance)

        # Store so handle_spin can reuse without re-predicting
        self._pending_predicted = predicted
        self._pending_bets      = bets
        self._pending_probs     = probabilities

        if self.on_advice:
            self.on_advice({
                "predicted":     predicted,
                "bets":          bets,
                "balance":       self.balance,
                "probabilities": probabilities,
                "spin_num":      self.tracker.total_spins + 1,
            })

    # ── Main run loop ─────────────────────────────────────────────────────────

    async def run(self):
        """
        Start the engine using the configured data source.
        Runs until cancelled (Ctrl+C) or balance is depleted.
        """
        if self.manual_mode:
            from data.manual_feed import ManualFeed
            feed = ManualFeed()
            feed.on_before_spin(self.show_advice)
            feed.on_number(self.handle_spin)
            await feed.run()
        elif self.use_live:
            from data.live_feed import LiveFeed
            feed = LiveFeed(CASINO_WS_URL, CASINO_ID, TABLE_ID, CURRENCY)
            feed.on_number(self.handle_spin)
            await feed.listen()
        else:
            from data.simulator import Simulator
            feed = Simulator(spin_interval=self.spin_interval)
            feed.on_before_spin(self.show_advice)
            feed.on_number(self.handle_spin)
            await feed.run()
