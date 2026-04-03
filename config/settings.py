"""DeepRoulette — Central Configuration."""

# Casino WebSocket Connection
CASINO_WS_URL = "wss://dga.pragmaticplaylive.net/ws"
CASINO_ID = "ppcds00000003709"
TABLE_ID = "236"
CURRENCY = "USD"

# Neural Network Architecture
SEQUENCE_LENGTH = 15
ROULETTE_NUMBERS = 37

LSTM_UNITS_1 = 256
LSTM_UNITS_2 = 128
LSTM_UNITS_3 = 64
DENSE_UNITS = 128
DROPOUT_RATE = 0.25
LEARNING_RATE = 0.001

# Training
BATCH_SIZE = 16
TRAINING_EPOCHS = 150
ONLINE_EPOCHS = 5
AUTO_TRAIN_MIN = 20
AUTO_SAVE_EVERY = 30
ONLINE_HISTORY_WINDOW = 150     # recent spins used per incremental update

# Betting
DEFAULT_BALANCE = 100.0
DEFAULT_BET_AMOUNT = 1.00
MIN_BET = 0.10
PAYOUT_RATIO = 35

# System
MAX_HISTORY = 2000
RECONNECT_DELAY = 30

# Checkpoint Mode — pauses at 100/250/500/1000 spins for screenshot comparison
CHECKPOINT_MODE = True

# File Paths
SAVED_MODELS_DIR = "saved_models"
REAL_MODELS_DIR = "saved_models/real"           # live + manual share one model (same wheel data)
SIMULATION_MODELS_DIR = "saved_models/simulation"  # kept separate — uses random.randint, not real data
LIVE_MODELS_DIR = REAL_MODELS_DIR               # alias — live now points to real
MANUAL_MODELS_DIR = REAL_MODELS_DIR             # alias — manual now points to real
LOGS_DIR = "logs"
DATA_STORE_DIR = "data_store"
TRAINING_FILES_DIR = "data_store/training_files"   # drop .txt files here for batch file-training
