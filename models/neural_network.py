"""
models/neural_network.py
========================
Deep LSTM neural network for roulette number prediction.

Architecture:
  Input (15 past spins)
    → LSTM(256) → Dropout
    → LSTM(128) → Dropout
    → LSTM(64)  → Dropout
    → Dense(128, relu) → Dropout
    → Dense(64, relu)
    → Dense(37, softmax)   ← probability for each number 0–36
"""

import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras.utils import to_categorical

from config.settings import (
    SEQUENCE_LENGTH, ROULETTE_NUMBERS,
    LSTM_UNITS_1, LSTM_UNITS_2, LSTM_UNITS_3,
    DENSE_UNITS, DROPOUT_RATE, LEARNING_RATE,
    SAVED_MODELS_DIR, OFFLINE_MODELS_DIR, ONLINE_MODELS_DIR,
)


class RouletteNeuralNetwork:
    """
    Manages the LSTM model lifecycle:
      build  → train  → save  → load  → predict
    """

    def __init__(self, model_name: str = "roulette_model", save_dir: str = None):
        self.model_name = model_name
        _dir = save_dir if save_dir is not None else SAVED_MODELS_DIR
        self.model_path = os.path.join(_dir, f"{model_name}.keras")
        self.model: tf.keras.Model = None

    # ── Architecture ──────────────────────────────────────────────────────────

    def build(self) -> tf.keras.Model:
        """Construct and compile the LSTM model from scratch."""
        model = Sequential(name="roulette_predictor")

        # ── Recurrent layers ──
        model.add(LSTM(LSTM_UNITS_1,
                       input_shape=(SEQUENCE_LENGTH, 1),
                       return_sequences=True,
                       name="lstm_1"))
        model.add(Dropout(DROPOUT_RATE, name="drop_1"))

        model.add(LSTM(LSTM_UNITS_2,
                       return_sequences=True,
                       name="lstm_2"))
        model.add(Dropout(DROPOUT_RATE, name="drop_2"))

        model.add(LSTM(LSTM_UNITS_3,
                       return_sequences=False,
                       name="lstm_3"))
        model.add(Dropout(DROPOUT_RATE, name="drop_3"))

        # ── Fully-connected layers ──
        model.add(Dense(DENSE_UNITS, activation="relu", name="dense_1"))
        model.add(Dropout(0.15, name="drop_4"))
        model.add(Dense(64, activation="relu", name="dense_2"))

        # ── Output layer: probability distribution over 37 numbers ──
        model.add(Dense(ROULETTE_NUMBERS, activation="softmax", name="output"))

        model.compile(
            optimizer=Adam(learning_rate=LEARNING_RATE),
            loss="categorical_crossentropy",
            metrics=["accuracy"],
        )
        return model

    # ── Load / Save ───────────────────────────────────────────────────────────

    def load(self) -> tf.keras.Model:
        """Load model from disk if it exists, otherwise build a fresh one."""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        if os.path.exists(self.model_path):
            self.model = load_model(self.model_path)
        else:
            self.model = self.build()
        return self.model

    def save(self):
        """Persist the model weights to disk."""
        if self.model is not None:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            self.model.save(self.model_path)

    def is_trained(self) -> bool:
        """True if a saved model file exists on disk."""
        return os.path.exists(self.model_path)

    # ── Training helpers ──────────────────────────────────────────────────────

    def get_callbacks(self) -> list:
        """Standard Keras callbacks used during full training runs."""
        return [
            EarlyStopping(
                monitor="val_loss",
                patience=12,
                restore_best_weights=True,
                verbose=0,
            ),
            ReduceLROnPlateau(
                monitor="val_loss",
                factor=0.5,
                patience=6,
                min_lr=1e-6,
                verbose=0,
            ),
            ModelCheckpoint(
                self.model_path,
                monitor="val_loss",
                save_best_only=True,
                verbose=0,
            ),
        ]

    # ── Data helpers ──────────────────────────────────────────────────────────

    @staticmethod
    def build_training_data(history: list):
        """
        Convert a flat list of spin results into (X, y) tensors.

        Sliding window of SEQUENCE_LENGTH spins → predict the next spin.
        X shape: (N, SEQUENCE_LENGTH, 1)
        y shape: (N, 37)  — one-hot encoded
        """
        if len(history) < SEQUENCE_LENGTH + 1:
            return None, None

        X, y = [], []
        for i in range(len(history) - SEQUENCE_LENGTH):
            X.append(history[i: i + SEQUENCE_LENGTH])
            y.append(history[i + SEQUENCE_LENGTH])

        X = np.array(X, dtype=np.float32) / 36.0          # normalise → [0, 1]
        X = X.reshape((-1, SEQUENCE_LENGTH, 1))
        y = to_categorical(y, num_classes=ROULETTE_NUMBERS)
        return X, y

    @staticmethod
    def build_prediction_input(recent: list) -> np.ndarray:
        """
        Prepare the last SEQUENCE_LENGTH spins for a single inference call.
        Returns shape: (1, SEQUENCE_LENGTH, 1)
        """
        seq = np.array(recent[-SEQUENCE_LENGTH:], dtype=np.float32) / 36.0
        return seq.reshape((1, SEQUENCE_LENGTH, 1))
