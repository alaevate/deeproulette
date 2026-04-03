"""Prediction Engine — orchestrates the full pipeline for every roulette spin."""

import asyncio
import logging

from models.neural_network import RouletteNeuralNetwork
from strategies.base import BaseStrategy
from core.trainer import ModelTrainer
from utils.tracker import StatsTracker
from utils.logger import setup_logger
from config.settings import (
    SEQUENCE_LENGTH, MAX_HISTORY, AUTO_TRAIN_MIN,
    CASINO_WS_URL, CASINO_ID, TABLE_ID, CURRENCY,
    MANUAL_MODELS_DIR, SIMULATION_MODELS_DIR, LIVE_MODELS_DIR,
    CHECKPOINT_MODE,
)


# Checkpoint mode pauses at these spin counts to show stats
SPIN_MILESTONES = (100, 250, 500, 1000) if CHECKPOINT_MODE else ()


class PredictionEngine:
    """Central controller — pairs any BaseStrategy with any data feed."""

    def __init__(
        self,
        strategy: BaseStrategy,
        initial_balance: float,
        bet_per_number: float = 1.00,
        auto_train: bool = False,
        use_live: bool = True,
        spin_interval: float = 5.0,
        manual_mode: bool = False,
    ):
        self.strategy = strategy
        self.balance = initial_balance
        self._init_balance = initial_balance
        self.bet_per_number = bet_per_number
        self.auto_train = auto_train
        self.use_live = use_live
        self.spin_interval = spin_interval
        self.manual_mode = manual_mode

        self.history = []
        self.tracker = StatsTracker()
        self._log = setup_logger()
        self._running = True

        self._pending_predicted = None
        self._pending_bets = None
        self._pending_probs = None

        self.on_spin_complete = None
        self.on_waiting = None
        self.on_model_status = None
        self.on_balance_empty = None
        self.on_advice = None
        self.on_milestone = None

        self._feed = None
        self.checkpoint_mode_complete = False

        # Models are stored per operating mode to avoid cross-contamination
        if manual_mode:
            model_dir = MANUAL_MODELS_DIR
        elif use_live:
            model_dir = LIVE_MODELS_DIR
        else:
            model_dir = SIMULATION_MODELS_DIR

        self.nn = RouletteNeuralNetwork(
            model_name=strategy.model_filename,
            save_dir=model_dir,
        )
        self.nn.load()

        # Online trainer writes checkpoints — folder depends on live vs sim
        self.trainer = ModelTrainer(self.nn, verbose=False, save_dir=model_dir)

    def report_model_status(self):
        """Fire the model-status callback (call AFTER wiring up callbacks)."""
        if self.on_model_status:
            is_fresh = not self.nn.is_trained()
            status = "New untrained model created." if is_fresh else "Existing model loaded."
            self.on_model_status(status)

    async def handle_spin(self, number: int):
        """Called by the data feed for every new roulette number."""
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


        if self._pending_predicted is not None:
            # Reuse prediction from show_advice() so the user sees the same numbers
            predicted               = self._pending_predicted
            bets = self._pending_bets
            probabilities = self._pending_probs
            self._pending_predicted = None
            self._pending_bets = None
            self._pending_probs = None
        else:
            input_tensor = RouletteNeuralNetwork.build_prediction_input(self.history)
            probabilities = self.nn.model.predict(input_tensor, verbose=0)[0]
            predicted = self.strategy.select_numbers(probabilities)
            bets = self.strategy.calculate_bets(predicted, self.balance, self.bet_per_number)

        total_bet = sum(bets.values())


        is_win, net, new_balance = self.strategy.evaluate_result(
            number, predicted, bets, self.balance
        )
        self.balance = new_balance


        self.tracker.record(number, predicted, bets, is_win, net, self.balance)


        model_saved = False
        if self.auto_train and len(self.history) >= AUTO_TRAIN_MIN:
            model_saved = self.trainer.train_online(self.history)


        self._log.info(
            f"Spin {self.tracker.total_spins:>5} | "
            f"Result: {number:>2} | "
            f"{'WIN ' if is_win else 'LOSS'} {net:>+7.2f} | "
            f"Balance: {self.balance:>8.2f} | "
            f"WR: {self.tracker.win_rate:>5.1f}% | "
            f"ROI: {self.tracker.roi:>+6.1f}%"
        )

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
                "bet_label":     self.strategy.get_display_label(),
                "total_wins":    self.tracker.total_wins,
                "total_losses":  self.tracker.total_losses,
            })


        if (not self.use_live and not self.manual_mode
                and self.tracker.total_spins in SPIN_MILESTONES):
            if self.on_milestone:
                await self.on_milestone(self.tracker.total_spins)
            if self.tracker.total_spins == SPIN_MILESTONES[-1]:
                self.checkpoint_mode_complete = True
                self._running = False
                if self._feed is not None:
                    self._feed.stop()
                return

        if self.balance <= 0:
            self._running = False
            if self._feed is not None:
                self._feed.stop()
            if self.on_balance_empty:
                self.on_balance_empty()
            return
        # Live mode: show advice after each result (before next spin)
        if self.use_live and self._running:
            await self.show_advice()


    async def show_advice(self):
        """Compute AI recommendation and fire the on_advice callback."""
        if not self._running:
            return
        if len(self.history) < SEQUENCE_LENGTH:
            if self.on_waiting and not self.use_live:
                self.on_waiting(len(self.history), SEQUENCE_LENGTH)
            self._pending_predicted = None
            self._pending_bets = None
            self._pending_probs = None
            return

        input_tensor = RouletteNeuralNetwork.build_prediction_input(self.history)
        probabilities = self.nn.model.predict(input_tensor, verbose=0)[0]
        predicted = self.strategy.select_numbers(probabilities)
        bets = self.strategy.calculate_bets(predicted, self.balance, self.bet_per_number)

        self._pending_predicted = predicted
        self._pending_bets = bets
        self._pending_probs = probabilities

        if self.on_advice:
            self.on_advice({
                "predicted":     predicted,
                "bets":          bets,
                "balance":       self.balance,
                "probabilities": probabilities,
                "spin_num":      self.tracker.total_spins + 1,
                "bet_label":     self.strategy.get_display_label(),
            })

    async def run(self):
        """Start the engine using the configured data source."""
        self.report_model_status()

        if self.manual_mode:
            from data.manual_feed import ManualFeed
            feed = ManualFeed()
            self._feed = feed
            feed.on_before_spin(self.show_advice)
            feed.on_number(self.handle_spin)
            await feed.run()
        elif self.use_live:
            from data.live_feed import LiveFeed
            feed = LiveFeed(CASINO_WS_URL, CASINO_ID, TABLE_ID, CURRENCY)
            self._feed = feed
            feed.on_number(self.handle_spin)
            await feed.listen()
        else:
            from data.simulator import Simulator
            feed = Simulator(spin_interval=self.spin_interval)
            self._feed = feed
            feed.on_before_spin(self.show_advice)
            feed.on_number(self.handle_spin)
            await feed.run()
