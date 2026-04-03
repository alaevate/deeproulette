# Copyright 2026 alaevate
# Licensed under the Apache License, Version 2.0
"""Centralised logging — one log file per session."""

import logging
import os
from datetime import datetime
from config.settings import LOGS_DIR


def setup_logger(name: str = "DeepRoulette") -> logging.Logger:
    """Create (or reuse) a named logger that writes to logs/session_<timestamp>.log."""
    os.makedirs(LOGS_DIR, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Attach a file handler only once (avoid duplicate handlers on reload)
    if not logger.handlers:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path  = os.path.join(LOGS_DIR, f"session_{timestamp}.log")
        handler   = logging.FileHandler(log_path, encoding="utf-8")
        handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s")
        )
        logger.addHandler(handler)

    return logger
