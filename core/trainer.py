# Copyright 2026 alaevate
# Licensed under the Apache License, Version 2.0
"""Model trainer — full offline training and online incremental updates."""

import logging
import os
from models.neural_network import RouletteNeuralNetwork
from config.settings import TRAINING_EPOCHS, ONLINE_EPOCHS, BATCH_SIZE, AUTO_SAVE_EVERY, SEQUENCE_LENGTH, ONLINE_HISTORY_WINDOW


class ModelTrainer:
    """Wraps a RouletteNeuralNetwork and provides train / update methods."""

    def __init__(self, neural_net: RouletteNeuralNetwork, verbose: bool = False, save_dir: str = "saved_models"):
        self.nn = neural_net
        self.verbose = verbose
        self._auto_save_dir = save_dir
        self._log = logging.getLogger("ModelTrainer")
        self._updates_since_save = 0

    def train_offline(self, history: list) -> bool:
        """Full training run on all accumulated history. Returns True on success."""
        X, y = RouletteNeuralNetwork.build_training_data(history)
        if X is None or len(X) < 10:
            self._log.warning(
                f"Not enough data for training. "
                f"Need at least {SEQUENCE_LENGTH + 10} spins, got {len(history)}."
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

        self._save_to(self._auto_save_dir)
        self._log.info(f"Full training complete. Model saved → {self._auto_save_dir}")
        return True

    def train_online(self, history: list) -> bool:
        """Quick incremental update using recent history. Returns True if model was saved."""
        recent = history[-ONLINE_HISTORY_WINDOW:]  # only recent data so the model adapts to current table trends
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

    def _save_to(self, directory: str):
        """Save current model weights into a specific directory."""
        os.makedirs(directory, exist_ok=True)
        path = os.path.join(directory, os.path.basename(self.nn.model_path))
        self.nn.model.save(path)
        self._log.debug(f"Model saved → {path}")
