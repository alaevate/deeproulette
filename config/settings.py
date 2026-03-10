"""
DeepRoulette — Central Configuration
==========================================
All settings live here. Change values to customize the system.
"""

# ── Casino WebSocket Connection ───────────────────────────────────────────────
CASINO_WS_URL = "wss://dga.pragmaticplaylive.net/ws"
CASINO_ID     = "ppcds00000003709"
TABLE_ID      = "236"
CURRENCY      = "USD"

# ── Neural Network Architecture ───────────────────────────────────────────────
SEQUENCE_LENGTH  = 15      # How many past spins the AI uses as input
ROULETTE_NUMBERS = 37      # Possible outcomes: 0 through 36

LSTM_UNITS_1  = 256        # First LSTM layer size  (bigger = smarter but slower)
LSTM_UNITS_2  = 128        # Second LSTM layer size
LSTM_UNITS_3  = 64         # Third LSTM layer size
DENSE_UNITS   = 128        # Fully-connected hidden layer
DROPOUT_RATE  = 0.25       # Regularization — prevents the model from memorizing noise
LEARNING_RATE = 0.001      # How fast the model adjusts its weights

# ── Training ──────────────────────────────────────────────────────────────────
BATCH_SIZE        = 32     # Samples per training step
TRAINING_EPOCHS   = 100    # Max epochs for a full offline training run
ONLINE_EPOCHS     = 3      # Epochs used for per-spin online updates
AUTO_TRAIN_MIN    = 30     # Minimum spins collected before online training begins
AUTO_SAVE_EVERY   = 50     # Persist model to disk every N online updates

# ── Betting ───────────────────────────────────────────────────────────────────
DEFAULT_BALANCE = 100.0    # Default starting wallet
MIN_BET         = 0.10     # Minimum bet per number
BET_FRACTION    = 0.02     # Fraction of balance wagered per number each spin
PAYOUT_RATIO    = 35       # Standard straight-up roulette payout (35 : 1)

# ── System ────────────────────────────────────────────────────────────────────
MAX_HISTORY      = 2000    # Max spins kept in memory (sliding window)
RECONNECT_DELAY  = 30      # Seconds to wait before WebSocket reconnect

# ── Checkpoint Mode ─────────────────────────────────────────────────────────
CHECKPOINT_MODE = True    # pauses at 100 / 250 / 500 / 1000 spins

# ── File Paths ────────────────────────────────────────────────────────────────
SAVED_MODELS_DIR        = "saved_models"          # Root models directory
OFFLINE_MODELS_DIR      = "saved_models/offline"  # Models trained offline (full dataset)
ONLINE_MODELS_DIR       = "saved_models/online"   # Models updated online (per-spin incremental)
LOGS_DIR                = "logs"                  # Where session logs are written
DATA_STORE_DIR          = "data_store"            # Reserved for future dataset storage
