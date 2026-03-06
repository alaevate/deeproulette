"""
core/trainer.py
===============
Model trainer — handles both:
  1. Full offline training  (train_offline)  — used when no model exists yet
  2. Online incremental     (train_online)   — called every N spins with auto-train
"""

import logging
from models.neural_network import RouletteNeuralNetwork
from config.settings import (
    TRAINING_EPOCHS, ONLINE_EPOCHS, BATCH_SIZE, AUTO_SAVE_EVERY,
    OFFLINE_MODELS_DIR, ONLINE_MODELS_DIR,
)


class ModelTrainer:
    """
    Wraps a RouletteNeuralNetwork and provides easy train / update methods.

    train_offline() → always saves to  saved_models/offline/
    train_online()  → saves to offline/ when simulating, online/ when live
    """

    def __init__(self, neural_net: RouletteNeuralNetwork, verbose: bool = False, use_live: bool = True):
        self.nn            = neural_net
        self.verbose       = verbose
        self.use_live      = use_live
        self._auto_save_dir = ONLINE_MODELS_DIR if use_live else OFFLINE_MODELS_DIR
        self._log          = logging.getLogger("ModelTrainer")
        self._updates_since_save = 0

    # ── Full offline training ─────────────────────────────────────────────────

    def train_offline(self, history: list) -> bool:
        """
        Full training run on all accumulated history.
        Uses early stopping and learning-rate scheduling.
        Best for initial training or periodic full retraining.

        Returns True if training succeeded, False if not enough data.
        """
        X, y = RouletteNeuralNetwork.build_training_data(history)
        if X is None or len(X) < 10:
            self._log.warning(
                f"Not enough data for training. "
                f"Need at least {15 + 1} spins, got {len(history)}."
            )
            return False

        if self.nn.model is None:
            self.nn.load()

        verbosity = 1 if self.verbose else 0
        self._log.info(
            f"Starting full training on {len(X)} samples "
            f"(up to {TRAINING_EPOCHS} epochs)..."
        )

        self.nn.model.fit(
            X, y,
            epochs=TRAINING_EPOCHS,
            batch_size=BATCH_SIZE,
            validation_split=0.1,
            callbacks=self.nn.get_callbacks(),
            verbose=verbosity,
        )

        self._save_to(OFFLINE_MODELS_DIR)
        self._log.info(f"Full training complete. Model saved → {OFFLINE_MODELS_DIR}")
        return True

    # ── Online incremental update ─────────────────────────────────────────────

    def train_online(self, history: list) -> bool:
        """
        Quick incremental update using recent history.
        Designed to run after every spin — uses only a few epochs and
        the most recent data to keep latency low.

        Returns True if the model was also saved to disk this call.
        """
        # Use up to the last 150 spins for online updates
        recent = history[-150:]
        X, y   = RouletteNeuralNetwork.build_training_data(recent)

        if X is None or len(X) < 5:
            return False

        self.nn.model.fit(
            X, y,
            epochs=ONLINE_EPOCHS,
            batch_size=min(BATCH_SIZE, len(X)),
            verbose=0,
        )

        self._updates_since_save += 1
        if self._updates_since_save >= AUTO_SAVE_EVERY:
            self._save_to(self._auto_save_dir)
            self._updates_since_save = 0
            self._log.info(f"Auto-train checkpoint saved → {self._auto_save_dir}")
            return True   # indicates a save occurred

        return False

    # ── Internal helper ───────────────────────────────────────────────────────

    def _save_to(self, directory: str):
        """Save current model weights into a specific directory."""
        import os
        os.makedirs(directory, exist_ok=True)
        path = os.path.join(directory, os.path.basename(self.nn.model_path))
        self.nn.model.save(path)
        self._log.debug(f"Model saved → {path}")
