# DeepRoulette — Complete Project Flow Documentation

> Auto-generated deep-dive reference. Every file, class, method, and data path explained line by line.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Directory Structure](#2-directory-structure)
3. [Configuration Layer — `config/settings.py`](#3-configuration-layer--configsettingspy)
4. [Entry Point — `main.py`](#4-entry-point--mainpy)
   - [4.1 Argument Parsing Flow](#41-argument-parsing-flow)
   - [4.2 Logging Setup Flow](#42-logging-setup-flow)
   - [4.3 Strategy Listing Flow](#43-strategy-listing-flow)
   - [4.4 Async Orchestration Flow](#44-async-orchestration-flow)
   - [4.5 run_strategy Flow](#45-run_strategy-flow)
5. [WebSocket Layer — `src/data/websocket_client.py`](#5-websocket-layer--srcdatawebsocket_clientpy)
   - [5.1 Connection Flow](#51-connection-flow)
   - [5.2 Subscription Message Flow](#52-subscription-message-flow)
   - [5.3 Ping / Keepalive Flow](#53-ping--keepalive-flow)
   - [5.4 Listen & Reconnect Flow](#54-listen--reconnect-flow)
   - [5.5 Message Parsing Flow](#55-message-parsing-flow)
   - [5.6 Simulation Mode Flow](#56-simulation-mode-flow)
   - [5.7 Disconnect Flow](#57-disconnect-flow)
6. [Strategy Manager — `src/strategies/strategy_manager.py`](#6-strategy-manager--srcstrategiesstrategy_managerpy)
   - [6.1 Dynamic Loading Flow](#61-dynamic-loading-flow)
   - [6.2 Number Processing Flow](#62-number-processing-flow)
   - [6.3 Win/Loss Accounting Flow](#63-winloss-accounting-flow)
   - [6.4 Auto-Train Flow](#64-auto-train-flow)
7. [Strategy Implementations](#7-strategy-implementations)
   - [7.1 Top-1 Strategy — `top1_strategy.py`](#71-top-1-strategy--top1_strategypy)
   - [7.2 Top-3 Strategy — `top3_strategy.py`](#72-top-3-strategy--top3_strategypy)
   - [7.3 Top-18 Strategy — `top18_strategy.py`](#73-top-18-strategy--top18_strategypy)
8. [LSTM Neural Network Architecture](#8-lstm-neural-network-architecture)
   - [8.1 Model Build Flow](#81-model-build-flow)
   - [8.2 Data Preprocessing Flow](#82-data-preprocessing-flow)
   - [8.3 Prediction Flow](#83-prediction-flow)
9. [Betting Logic Flow](#9-betting-logic-flow)
10. [Complete End-to-End Data Flow](#10-complete-end-to-end-data-flow)
11. [Strategy Comparison](#11-strategy-comparison)
12. [Error Handling & Edge Cases](#12-error-handling--edge-cases)
13. [Dependencies](#13-dependencies)

---

## 1. Project Overview

**NeuralRoulette-AI** is a real-time AI roulette prediction system. It:

- Connects **live** to a Pragmatic Play Live Casino WebSocket feed (`wss://dga.pragmaticplaylive.net/ws`)
- Receives roulette spin results in real-time
- Feeds results into a trained **LSTM (Long Short-Term Memory)** neural network
- Predicts the next most-likely number(s)
- Simulates a virtual bet and tracks balance, win rate, and ROI
- Optionally **auto-retrains** the model online as new data arrives
- Has a **simulation mode** that generates fake spins locally without needing a live connection

The project is built entirely in **Python** using **TensorFlow/Keras** for ML and **websockets** for async I/O.

---

## 2. Directory Structure

```
NeuralRoulette-AI/
│
├── main.py                         ← Application entry point
├── requirements.txt                ← Python package dependencies
├── README.md                       ← Public readme
│
├── config/
│   └── settings.py                 ← All global constants and strategy configs
│
├── src/
│   ├── __init__.py                 ← Package marker
│   ├── data/
│   │   ├── __init__.py             ← Package marker
│   │   └── websocket_client.py     ← Live/simulated data ingestion
│   └── strategies/
│       ├── __init__.py             ← Package marker
│       ├── strategy_manager.py     ← Dynamic loader + spin processor
│       ├── top1_strategy.py        ← Single-number LSTM strategy
│       ├── top3_strategy.py        ← Three-number LSTM strategy
│       └── top18_strategy.py       ← Eighteen-number LSTM strategy
│
├── models/                         ← Persisted .keras model files (auto-created)
├── logs/                           ← Log output files (auto-created)
├── data/                           ← Reserved for future datasets
├── assets/                         ← Logo and image assets
└── tests/                          ← Empty (reserved for future unit tests)
```

---

## 3. Configuration Layer — `config/settings.py`

This file is the **single source of truth** for every tunable constant in the system.

### WebSocket Endpoint

```python
WS_URL    = "wss://dga.pragmaticplaylive.net/ws"  # Pragmatic Play WS endpoint
CASINO_ID = "ppcds00000003709"                     # Operator casino ID
TABLE_ID  = "236"                                  # Specific roulette table
CURRENCY  = "USD"                                  # Currency sent during subscription
```

These four values are read directly by `main.py` and forwarded to `RouletteWebSocketClient`.

### Model Hyperparameters

| Constant | Value | Purpose |
|---|---|---|
| `MODEL_DIR` | `"models"` | Folder where `.keras` files are saved |
| `SEQUENCE_LENGTH` | `10` | How many past spins the LSTM looks at |
| `ROULETTE_RANGE` | `37` | Output classes: numbers 0–36 |
| `EPOCHS` | `50` | Training epochs for offline training |
| `BATCH_SIZE` | `32` | Batch size during training |

### Betting Defaults

| Constant | Value | Purpose |
|---|---|---|
| `STARTING_BALANCE` | `10.00` | Default virtual wallet |
| `MIN_BET_AMOUNT` | `0.01` | Floor bet per number |
| `PAYOUT_RATIO` | `35` | Standard straight-up roulette payout (35:1) |

### `StrategyConfig` Dataclass

```python
@dataclass
class StrategyConfig:
    name: str                  # Human-readable label
    model_file: str            # Filename inside models/
    description: str           # One-line description
    risk_level: str            # "High" | "Medium" | "Low" | "Variable"
    numbers_to_predict: int    # How many numbers the strategy bets on
    bet_multiplier: float      # Fraction of balance per number
    target_win_rate: float     # Statistical win probability (%)
```

### Strategy Registry (`STRATEGIES` dict)

| Key | Name | Numbers | Bet Multiplier | Target Win Rate |
|---|---|---|---|---|
| `top1` | Top-1 Single Number | 1 | 1.0 | 2.71% |
| `top3` | Top-3 Numbers | 3 | 0.33 | 8.11% |
| `top18` | Top-18 Numbers | 18 | 0.055 | 48.65% |
| `topm` | Top-M Dynamic | Dynamic | Dynamic | Dynamic |

> **Note:** `topm` is registered in config but its strategy file is not yet implemented. The loader in `strategy_manager.py` would fail with an `ImportError` if selected.

---

## 4. Entry Point — `main.py`

`main.py` is the **only file the user ever runs**. It orchestrates every other component.

### 4.1 Argument Parsing Flow

**Function:** `parse_arguments()`

Called first before anything else. Uses Python's built-in `argparse`.

```
User runs: python main.py [flags]
              │
              ▼
         argparse.ArgumentParser created
              │
              ├── --strategy   choices: top1 | top3 | top18 | topm   (default: top1)
              ├── --balance    float                                   (default: 10.0)
              ├── --auto-train flag (store_true)                       (default: False)
              ├── --list-strategies flag (store_true)                  (default: False)
              └── --simulate   flag (store_true)                       (default: False)
              │
              ▼
         Returns: args Namespace object
```

- `--strategy` controls which `*_strategy.py` module gets loaded.
- `--balance` sets the starting virtual wallet passed down to the strategy class.
- `--auto-train` enables live online retraining after every spin.
- `--list-strategies` prints info and exits immediately — no WebSocket is opened.
- `--simulate` bypasses the live WebSocket and generates random numbers locally.

---

### 4.2 Logging Setup Flow

**Function:** `setup_logging()`

```
setup_logging()
      │
      ├── os.makedirs("logs", exist_ok=True)      ← creates logs/ folder silently
      │
      └── logging.basicConfig(
              level   = INFO,
              format  = "%(message)s",             ← only the message, no timestamps in stdout
              handlers= [
                  FileHandler("logs/roulette.log") ← all logs go to file
                  StreamHandler()                   ← also mirrors to console
              ]
          )
```

> The format string `"%(message)s"` means console output is clean (no timestamps). The log file receives the same messages.

---

### 4.3 Strategy Listing Flow

**Function:** `list_strategies()`

Only runs when `--list-strategies` is passed.

```
list_strategies()
      │
      └── Iterates over STRATEGIES dict (imported from config.settings)
              │
              For each key, config in STRATEGIES.items():
                  prints: key, config.name, config.description,
                          config.risk_level, config.numbers_to_predict,
                          config.target_win_rate, config.model_file
              │
              ▼
          Program exits
```

---

### 4.4 Async Orchestration Flow

**Function:** `async_main()` ← called via `asyncio.run()` from `main()`

```
main()
  │
  ├── setup_logging()
  └── asyncio.run(async_main())
            │
            ├── args = parse_arguments()
            │
            ├── if args.list_strategies → list_strategies() → return
            │
            ├── os.makedirs("models", exist_ok=True)    ← ensures models/ exists
            │
            ├── Prints startup banner with strategy name, balance, auto-train flag, data source
            │
            ├── Looks up config = STRATEGIES[args.strategy]
            │
            ├── Prints strategy config block
            │
            └── await run_strategy(args.strategy, args.balance, args.auto_train, args.simulate)
```

`main()` wraps `async_main()` in a standard `asyncio.run()` call and catches `KeyboardInterrupt` for a clean Ctrl+C shutdown message.

---

### 4.5 `run_strategy` Flow

**Function:** `run_strategy(strategy_name, balance, auto_train, simulate=False)`

This is the bridge between the CLI and the live/simulated data pipeline.

```
run_strategy(...)
      │
      ├── strategy_manager = StrategyManager(strategy_name, balance, auto_train)
      │
      ├── await strategy_manager.load_strategy()
      │       └── If fails → prints error, returns (no WS connection attempted)
      │
      ├── ws_client = RouletteWebSocketClient(WS_URL, CASINO_ID, TABLE_ID, CURRENCY)
      │
      ├── ws_client.register_callback(strategy_manager.process_number)
      │       └── Every new roulette number triggers strategy_manager.process_number(number)
      │
      ├── try:
      │     if simulate:
      │         await ws_client.simulate_data()          ← local random spin generator
      │     else:
      │         if await ws_client.connect():
      │             await ws_client.listen()             ← live feed loop
      │         else:
      │             falls back to simulate_data()        ← auto-fallback on connection failure
      │
      └── finally:
              if not simulate: await ws_client.disconnect()
```

**Key insight:** The callback pattern decouples the WebSocket client from strategy logic. The WS client doesn't know anything about strategies — it just calls every registered callback with a bare integer (the roulette number).

---

## 5. WebSocket Layer — `src/data/websocket_client.py`

**Class:** `RouletteWebSocketClient`

Responsible for all network I/O. Fully async using the `websockets` library.

### Constructor

```python
__init__(ws_url, casino_id, table_id, currency="USD")
```

Stores connection parameters, initializes state:
- `self.connected = False` — connection guard flag
- `self.websocket = None` — the active websocket object
- `self.callbacks = []` — list of async functions to call on each new number

---

### 5.1 Connection Flow

**Method:** `connect()`

```
connect()
      │
      ├── websockets.connect(self.ws_url)    ← TCP + TLS handshake to Pragmatic Play
      │       sets self.websocket, self.connected = True
      │
      ├── await send_connection_message()    ← sends subscription JSON
      │
      ├── asyncio.create_task(start_ping())  ← background ping loop (non-blocking)
      │
      └── returns True
      
      On any exception:
          logger.error(...)
          returns False
```

---

### 5.2 Subscription Message Flow

**Method:** `send_connection_message()`

Immediately after TCP connection is established, this JSON is sent:

```json
{
  "type": "subscribe",
  "isDeltaEnabled": true,
  "casinoId": "ppcds00000003709",
  "key": ["236"],
  "currency": "USD"
}
```

- `isDeltaEnabled: true` — tells the server to send incremental updates (only changes, not full state).
- `key` is an array containing the table ID.
- Without this message, the server would not stream roulette results.

---

### 5.3 Ping / Keepalive Flow

**Method:** `start_ping()` — runs as a background `asyncio.Task`

```
start_ping()  [background loop]
      │
      └── while self.connected:
              │
              ├── Sends: { "type": "ping", "pingTime": <unix_ms> }
              │
              └── asyncio.sleep(300)    ← waits 5 minutes before next ping
              
      On exception:
          logger.error(...)
          self.connected = False    ← signals listen() to reconnect
```

This prevents the WebSocket server from closing the connection due to inactivity. The `pingTime` is the current UNIX timestamp in **milliseconds**.

---

### 5.4 Listen & Reconnect Flow

**Method:** `listen()`

This is the **main receive loop**. It never exits on its own — it handles disconnects by reconnecting.

```
listen()
      │
      └── while True:  ← outer reconnect loop
              │
              ├── if not self.connected:
              │       if not await connect(): sleep(60); continue
              │
              └── while self.connected:   ← inner receive loop
                      │
                      ├── message = await websocket.recv()
                      ├── await process_message(message)
                      │
                      └── On ConnectionClosed:
                              self.connected = False
                              break → outer loop → reconnect
              │
              └── On fatal exception: self.connected = False
              
          After inner loop exits:
              asyncio.sleep(60)   ← wait 60 seconds before reconnect attempt
```

**Reconnection is automatic and indefinite.** The system will keep retrying every 60 seconds after any disconnection.

---

### 5.5 Message Parsing Flow

**Method:** `process_message(message: str)`

The server sends JSON strings. Two message formats are handled:

#### Format A — Primary (Pragmatic Play format)

```json
{
  "tableId": "236",
  "last20Results": [
    {
      "time": "Aug 16, 2025 08:19:15 PM",
      "result": "16",
      "color": "red",
      "gameId": "abc123"
    }
    // ... up to 20 entries
  ]
}
```

```
Format A detection:
      "tableId" in data  AND  "last20Results" in data  AND  len(last20Results) > 0
              │
              ├── latest_result = data["last20Results"][0]    ← MOST RECENT spin is index 0
              │
              ├── roulette_number = int(latest_result["result"])
              │
              └── for callback in self.callbacks:
                      await callback(roulette_number)          ← fires strategy_manager.process_number
```

#### Format B — Fallback (legacy format)

```json
{
  "result": {
    "number": "22"
  }
}
```

```
Format B detection:
      "result" in data  AND  "number" in data["result"]
              │
              └── roulette_number = int(data["result"]["number"])
                      → callbacks fired same as Format A
```

If neither format matches, the message is silently ignored.

**Error handling inside `process_message`:**
- `json.JSONDecodeError` → logs the raw message
- `ValueError` on int conversion → logs bad result string
- Any other exception → logs error + truncated message (max 200 chars)

---

### 5.6 Simulation Mode Flow

**Method:** `simulate_data()`

Bypasses the network entirely and generates random spins locally.

```
simulate_data()
      │
      ├── self.connected = True
      │
      └── while self.connected:
              │
              ├── roulette_number = random.randint(0, 36)
              │
              ├── Determines color:
              │       red   if number ∈ {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
              │       black if number ∈ {2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35}
              │       green if number == 0
              │
              ├── Builds a fake Format-A JSON message:
              │       { "tableId": "236", "last20Results": [{ "result": "N", "color": "X", ... }] }
              │
              ├── await process_message(json.dumps(simulated_message))
              │       ← reuses the same parser as live mode, ensuring identical downstream behavior
              │
              └── asyncio.sleep(5)    ← simulates ~5 second spin interval
```

> **Design note:** Simulation feeds through `process_message()` not directly through callbacks. This means the same JSON parsing code runs in both live and simulated mode — no separate code path exists.

---

### 5.7 Disconnect Flow

**Method:** `disconnect()`

```
disconnect()
      │
      ├── if self.connected and self.websocket:
      │       await self.websocket.close()
      │       self.connected = False
      │
      └── (no return value)
```

Called in the `finally` block of `run_strategy()` to cleanly close the TCP connection.

---

## 6. Strategy Manager — `src/strategies/strategy_manager.py`

**Class:** `StrategyManager`

Acts as the **controller** between the WebSocket data feed and the actual prediction/betting logic. It dynamically imports strategy modules at runtime.

### Constructor

```python
__init__(strategy_name, balance=10.0, auto_train=False)
```

Stores `strategy_name` (e.g. `"top1"`), `balance`, `auto_train`. `self.strategy` starts as `None` until `load_strategy()` is called.

---

### 6.1 Dynamic Loading Flow

**Method:** `load_strategy()` → `async`, returns `bool`

```
load_strategy()
      │
      ├── class_name  = f"{strategy_name.capitalize()}Strategy"
      │       e.g. "top1" → "Top1Strategy"
      │
      ├── module_name = f"src.strategies.{strategy_name}_strategy"
      │       e.g. "src.strategies.top1_strategy"
      │
      ├── module = importlib.import_module(module_name)
      │       ← Python dynamically imports the .py file
      │
      ├── strategy_class = getattr(module, class_name)
      │       ← retrieves the class object by name
      │
      ├── self.strategy = strategy_class(balance=balance, auto_train=auto_train)
      │       ← instantiates the strategy with the user's balance
      │
      └── returns True
      
      On ImportError or AttributeError:
          logs error
          returns False
```

This design means **adding a new strategy requires only**:
1. Creating `src/strategies/newname_strategy.py` with a class `NewnameStrategy`
2. Adding an entry to `STRATEGIES` in `config/settings.py`

No changes to `strategy_manager.py` or `main.py` are needed.

---

### 6.2 Number Processing Flow

**Method:** `process_number(number: int)` → `async`

This is the **callback** registered with `RouletteWebSocketClient`. It is called once for every roulette spin received (live or simulated).

```
process_number(number)
      │
      ├── self.strategy.game_history.append(number)
      │       ← accumulate spin history on the strategy object
      │
      ├── if len(game_history) < sequence_length (10):
      │       prints: "Not enough history yet (N/10) - please wait..."
      │       returns True
      │       ← strategy needs at least 10 spins before it can predict
      │
      └── if len(game_history) >= 10:
              │
              ├── predicted_numbers = strategy.predict_numbers(game_history)
              │       ← LSTM inference (see §7 and §8)
              │
              ├── bets = strategy.calculate_bets(predicted_numbers)
              │       ← returns dict: {number: bet_amount}
              │
              ├── total_bet = sum(bets.values())
              │
              ├── WIN CHECK: if number in predicted_numbers:
              │       strategy.correct_predictions += 1
              │       winnings = bets[number] * strategy.payout   (35×)
              │       strategy.balance += winnings - total_bet    ← net gain
              │
              ├── LOSS: else:
              │       strategy.balance -= total_bet
              │
              ├── strategy.total_spins += 1
              │
              ├── Computes:
              │       win_rate = correct_predictions / total_spins × 100
              │       roi      = (balance - initial_balance) / initial_balance × 100
              │
              ├── Logs to file: "Number: N, Balance: $X, Win Rate: Y%, ROI: Z%"
              │
              ├── Prints formatted spin summary to console
              │
              ├── if auto_train and len(game_history) >= 20:
              │       → [see §6.4 Auto-Train Flow]
              │
              ├── if len(game_history) > 1000:
              │       game_history = game_history[-1000:]   ← sliding window to cap memory
              │
              └── if balance <= 0:
                      prints "Balance depleted. Stopping strategy."
                      returns False
```

---

### 6.3 Win/Loss Accounting Flow

The accounting formula applied each spin:

**On a WIN:**
$$\text{balance} \mathrel{+}= \left( \text{bets}[\text{number}] \times 35 \right) - \text{total\_bet}$$

> You receive 35× the amount you bet on the winning number, but you lose all other bets placed.

**On a LOSS:**
$$\text{balance} \mathrel{-}= \text{total\_bet}$$

**ROI formula:**
$$\text{ROI} = \frac{\text{current balance} - \text{starting balance}}{\text{starting balance}} \times 100$$

---

### 6.4 Auto-Train Flow

Triggered when `--auto-train` flag is set and `len(game_history) >= 20`.

```
auto_train block
      │
      ├── X, y = strategy.preprocess_data(strategy.game_history)
      │       ← converts history list into LSTM training tensors
      │
      ├── if X is not None and len(X) > 0:
      │       model = strategy.load_model()    ← loads existing .keras or builds fresh
      │       model.fit(X, y,
      │           epochs=5,
      │           batch_size=min(32, len(X)),
      │           verbose=0)                   ← silent training
      │       model.save(strategy.model_file)  ← overwrites the .keras file
      │       prints "Model updated with new data"
      │
      └── On any exception:
              prints warning and continues     ← training failure never crashes the spin loop
```

> **Online learning note:** Only 5 epochs are used per spin update (vs. 50 for offline training), keeping latency low. The model file is overwritten after every successful update.

---

## 7. Strategy Implementations

All three implemented strategies share the **same LSTM architecture and preprocessing pipeline**. They differ only in:
- How many top-N probabilities they extract from the softmax output
- How they distribute the bet across predicted numbers

---

### 7.1 Top-1 Strategy — `top1_strategy.py`

**Class:** `Top1Strategy`

| Property | Value |
|---|---|
| `model_file` | `models/top1_model.keras` |
| `sequence_length` | 10 |
| `bet_amount` | 0.01 |
| `payout` | 35 |
| `numbers_to_predict` | 1 |

**`predict_numbers(recent_results)`**
```
sequence = last 10 numbers / 36.0      ← normalise to [0,1]
sequence reshaped to (1, 10, 1)        ← batch=1, timesteps=10, features=1
probabilities = model.predict(sequence)[0]   ← array of 37 probabilities
top_index = np.argmax(probabilities)   ← index of highest probability
return [int(top_index)]                ← single number list
```

**`calculate_bets(predicted_numbers)`**
```
total_bet = min(balance × 0.1, 0.01)
return { predicted_number: total_bet }
```

> Risk is **highest** here. You bet on exactly 1 of 37 numbers. Theoretical win probability: 1/37 ≈ **2.70%**.

---

### 7.2 Top-3 Strategy — `top3_strategy.py`

**Class:** `Top3Strategy`

| Property | Value |
|---|---|
| `model_file` | `models/top3_model.keras` |
| `numbers_to_predict` | 3 |

**`predict_numbers(recent_results)`**
```
probabilities = model.predict(sequence)[0]
top_indices = np.argsort(probabilities)[-3:][::-1]   ← 3 highest, descending
return [int(idx) for idx in top_indices]
```

**`calculate_bets(predicted_numbers)`**
```
total_bet = min(balance × 0.1, 3 × 0.01)
bet_per_number = total_bet / 3
return { num: bet_per_number for num in predicted_numbers }
```

> Bet is **split equally** across 3 numbers. Theoretical win probability: 3/37 ≈ **8.11%**.

---

### 7.3 Top-18 Strategy — `top18_strategy.py`

**Class:** `Top18Strategy`

| Property | Value |
|---|---|
| `model_file` | `models/top18_model.keras` |
| `numbers_to_predict` | 18 |

**`predict_numbers(recent_results)`**
```
probabilities = model.predict(sequence)[0]
top_indices = np.argsort(probabilities)[-18:][::-1]  ← 18 highest, descending
return [int(idx) for idx in top_indices]
```

**`calculate_bets(predicted_numbers)`**
```
total_bet = min(balance × 0.1, 18 × 0.01)
bet_per_number = total_bet / 18
return { num: bet_per_number for num in predicted_numbers }
```

> Covers **half the wheel**. Theoretical win probability: 18/37 ≈ **48.65%**. But because total bet is spread thin, payout must overcome a 2:1 cost per win to be profitable.

**Extra method in `Top18Strategy`:** `run_simulation()` — a self-contained local simulation loop (100 spins) for standalone testing without the WebSocket stack.

---

## 8. LSTM Neural Network Architecture

All three strategies use **identical** LSTM model architecture, defined in their respective `build_model()` methods.

### 8.1 Model Build Flow

```
build_model()
      │
      └── Sequential([
              LSTM(128, input_shape=(10, 1), return_sequences=True),
              Dropout(0.2),
              LSTM(64, return_sequences=False),
              Dropout(0.2),
              Dense(64, activation="relu"),
              Dense(37, activation="softmax")
          ])
          compiled with:
              loss      = "categorical_crossentropy"
              optimizer = "adam"
              metrics   = ["accuracy"]
```

| Layer | Output Shape | Description |
|---|---|---|
| LSTM(128) | (batch, 10, 128) | First LSTM layer, returns full sequence |
| Dropout(0.2) | (batch, 10, 128) | Drops 20% of units to reduce overfitting |
| LSTM(64) | (batch, 64) | Second LSTM, collapses sequence to single vector |
| Dropout(0.2) | (batch, 64) | Second dropout |
| Dense(64, relu) | (batch, 64) | Hidden layer for non-linear mapping |
| Dense(37, softmax) | (batch, 37) | Output: probability for each number 0–36 |

The **softmax** output means all 37 values sum to 1.0, giving a proper probability distribution over all possible roulette outcomes.

---

### 8.2 Data Preprocessing Flow

**Method:** `preprocess_data(data: list)` — used for training

```
Input: data = [14, 7, 0, 33, 21, ...]   (list of int spin results)

For i in range(len(data) - 10):
    X.append(data[i : i+10])            ← sliding window of 10 spins
    y.append(data[i+10])                ← label = next spin after the window

X = np.array(X) / 36.0                  ← normalise: map 0-36 → 0.0-1.0
X = X.reshape((N, 10, 1))               ← add feature dimension for LSTM
y = to_categorical(y, num_classes=37)   ← one-hot encode: e.g. 5 → [0,0,0,0,0,1,0,...]

Returns: X (N, 10, 1), y (N, 37)
```

If the input list has fewer than 11 items (not enough for even one sample), returns `(None, None)`.

---

### 8.3 Prediction Flow

**Method:** `predict_numbers(recent_results: list)` — used for inference

```
Input: recent_results = [..., 14, 7, 0, 33]   (game_history from strategy_manager)

sequence = np.array(recent_results[-10:]) / 36.0   ← take last 10, normalise
sequence = sequence.reshape((1, 10, 1))             ← single-sample batch

probabilities = model.predict(sequence, verbose=0)[0]   ← shape: (37,)

Strategy-specific extraction:
  top1:  top_index   = np.argmax(probabilities)
  top3:  top_indices = np.argsort(probabilities)[-3:][::-1]
  top18: top_indices = np.argsort(probabilities)[-18:][::-1]

Returns: list of int predicted numbers
```

**`load_model()`** is called inside `predict_numbers()` every spin:
```
load_model()
      │
      ├── if os.path.exists(model_file):
      │       return keras.load_model(model_file)    ← loads saved weights
      │
      └── else:
              return build_model()                   ← fresh untrained model
```

> **Performance note:** Loading the model from disk on every spin is I/O-intensive. For production use, the model should be loaded once and cached in memory.

---

## 9. Betting Logic Flow

The full betting cycle per spin, combining strategy manager and strategy class:

```
New spin number received (e.g. 22)
              │
              ▼
strategy_manager.process_number(22)
              │
              ├── game_history = [5, 11, 0, 22, 7, 3, 36, 18, 4, 9, 22]  (example)
              │
              ├── predict_numbers(game_history)
              │       LSTM → probabilities[37] → top-N indices
              │       e.g. [22, 5, 14]  (for top3)
              │
              ├── calculate_bets([22, 5, 14])
              │       total_bet = min(balance×0.1, 3×0.01)
              │       e.g. {22: 0.01, 5: 0.01, 14: 0.01}
              │
              ├── Is 22 in [22, 5, 14]?  YES → WIN
              │       winnings = 0.01 × 35 = 0.35
              │       net      = 0.35 - 0.03 = +$0.32
              │       balance += 0.32
              │
              └── (if NO → balance -= 0.03)
```

---

## 10. Complete End-to-End Data Flow

```
                    ┌──────────────────────────────────────┐
                    │  Pragmatic Play Live Casino Server    │
                    │  wss://dga.pragmaticplaylive.net/ws  │
                    └──────────────────┬───────────────────┘
                                       │  JSON message (Format A or B)
                                       ▼
              ┌────────────────────────────────────────────────┐
              │       RouletteWebSocketClient.listen()         │
              │  ┌──────────────────────────────────────────┐  │
              │  │         process_message(raw_json)         │  │
              │  │  json.loads → extract roulette_number    │  │
              │  └──────────────────────┬───────────────────┘  │
              └─────────────────────────┼──────────────────────┘
                                        │  int (0–36)
                                        ▼
              ┌────────────────────────────────────────────────┐
              │    StrategyManager.process_number(number)      │
              │                                                │
              │  game_history.append(number)                  │
              │                                                │
              │  if len(history) >= 10:                       │
              │    ┌─────────────────────────────────────┐    │
              │    │  strategy.predict_numbers(history)  │    │
              │    │  LSTM inference → top-N list        │    │
              │    └───────────────┬─────────────────────┘    │
              │                    │  [predicted_numbers]      │
              │    ┌───────────────▼─────────────────────┐    │
              │    │  strategy.calculate_bets(predicted) │    │
              │    │  Returns: {num: amount} dict        │    │
              │    └───────────────┬─────────────────────┘    │
              │                    │                           │
              │    ┌───────────────▼─────────────────────┐    │
              │    │     Win/Loss Accounting              │    │
              │    │     Update balance, stats            │    │
              │    └───────────────┬─────────────────────┘    │
              │                    │                           │
              │    ┌───────────────▼─────────────────────┐    │
              │    │  [optional] Auto-Train LSTM model   │    │
              │    │  Save updated .keras file           │    │
              │    └─────────────────────────────────────┘    │
              │                                                │
              └────────────────────────────────────────────────┘
                                        │
                                        ▼
                          Console output + logs/roulette.log
```

---

## 11. Strategy Comparison

| Metric | Top-1 | Top-3 | Top-18 |
|---|---|---|---|
| Numbers predicted | 1 | 3 | 18 |
| Theoretical hit rate | 2.70% | 8.11% | 48.65% |
| Risk level | High | Medium | Low |
| Bet per number | `min(bal×0.1, 0.01)` | `min(bal×0.1, 0.03) / 3` | `min(bal×0.1, 0.18) / 18` |
| Win multiplier | 35× on 1 number | 35× on winning number | 35× on winning number |
| Model file | `top1_model.keras` | `top3_model.keras` | `top18_model.keras` |
| Break-even hit rate | 1/36 = 2.78% | 3/36 = 8.33% | 18/36 = 50.00% |

> All strategies bet at exactly a **35:1 payout**, which is the standard European roulette straight-up payout. The house edge comes from the 0 pocket which is never in the "natural" payout calculation.

---

## 12. Error Handling & Edge Cases

| Scenario | Handled In | Behavior |
|---|---|---|
| WebSocket connection refused | `connect()` | Returns `False` → `run_strategy` falls back to simulation |
| WebSocket connection drops mid-session | `listen()` | Sets `connected=False`, reconnects after 60s wait |
| Server sends unrecognised JSON format | `process_message()` | Silently ignored (no callbacks fired) |
| Server sends non-integer result string | `process_message()` | `ValueError` caught, logs bad value |
| Strategy module not found | `load_strategy()` | `ImportError` caught, returns `False`, app exits gracefully |
| Model file does not exist | `load_model()` | Calls `build_model()` and returns untrained model |
| Game history too short (< 10 spins) | `process_number()` | Skips prediction, prints waiting message |
| Auto-train fails | `process_number()` | Exception caught, prints warning, spin loop continues |
| Balance reaches zero or below | `process_number()` | Prints message, returns `False` (stops the session) |
| Game history exceeds 1000 entries | `process_number()` | Truncated to last 1000 entries (sliding window) |
| User presses Ctrl+C | `main()` | `KeyboardInterrupt` caught, prints farewell message |

---

## 13. Dependencies

From `requirements.txt`:

| Package | Purpose |
|---|---|
| `tensorflow >= 2.10.0` | LSTM model build, training, and inference via Keras |
| `websockets >= 10.0` | Async WebSocket client for Pragmatic Play connection |
| `numpy >= 1.21.0` | Array math: normalisation, argsort, reshape |
| `asyncio` | Built-in Python stdlib — async event loop |
| `json` | Built-in Python stdlib — JSON encode/decode |
| `datetime` | Built-in Python stdlib — timestamps for logs and sim |
| `os` | Built-in Python stdlib — file existence checks, path operations |

**Python version:** Python 3.8+ required (uses `asyncio.run()`, f-strings, dataclasses, `walrus operator` patterns).

---

*Generated from full line-by-line analysis of all source files — March 2026*
