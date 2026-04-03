<h1 align="center">
  <a href="https://github.com/alaevate/deeproulette"><img src="assets/logo.png" alt="DeepRoulette" width="200"></a>
  <br>
  DeepRoulette
</h1>

<h4 align="center">Transformer + BiLSTM roulette predictor<br>real-time learning, inside & outside bets, works with any table.</h4>

<p align="center">
  <a href="https://github.com/alaevate/deeproulette/issues">
    <img alt="GitHub Issues" src="https://img.shields.io/github/issues/alaevate/deeproulette?style=plastic">
  </a>
  <a href="https://github.com/alaevate/deeproulette/pulls">
    <img alt="GitHub Pull Requests" src="https://img.shields.io/github/issues-pr/alaevate/deeproulette?style=plastic">
  </a>
  <a href="https://discord.gg/UPyggZ2cK8">
    <img alt="Discord" src="https://img.shields.io/discord/827945236218904627?style=plastic&label=discord">
  </a>
  <a href="https://github.com/alaevate/deeproulette/graphs/contributors">
    <img alt="GitHub contributors" src="https://img.shields.io/github/contributors/alaevate/deeproulette?style=plastic">
  </a>
</p>

<p align="center">
  <a href="#-quick-start--no-tech-knowledge-needed">🚀 Quick Start</a> •
  <a href="#-strategies">📊 Strategies</a> •
  <a href="#-project-structure">📁 Structure</a> •
  <a href="#-how-it-works">🧠 How It Works</a> •
  <a href="#%EF%B8%8F-advanced-settings">⚙️ Settings</a>
</p>

<p align="center">
  <img src="assets/image.png" alt="DeepRoulette Demo">
</p>

## ⚠️ Disclaimer

> **This software is for educational and research purposes only.**
> Roulette is a game of pure chance. The house always has an edge.
> No AI system can guarantee wins. Never gamble with money you cannot afford to lose.
> Always gamble responsibly.

---

## 🚀 Quick Start — No Tech Knowledge Needed

### ⚡ Option 1 — Download the EXE (Windows only, easiest)

1. Go to **[Releases](https://github.com/alaevate/deeproulette/releases/latest)**
2. Under **Assets**, download **`DeepRoulette-v2.0-windows.exe`**
3. Run it — no Python, no setup, nothing to install

> ⚠️ The file is ~400–700 MB because it bundles the full AI (TensorFlow) inside.

---

### 🛠️ Option 2 — Run from Source

#### Step 1 — Install Python 3.10 (one-time, skip if already installed)

> ⚠️ **Important:** For best compatibility with TensorFlow, use **Python 3.10** (not the latest version).

1. Go to **https://www.python.org/downloads/**
2. Download the Python 3.10 installer
3. **Windows**: Run the installer and tick **"Add Python to PATH"**
4. **Linux**: `sudo apt install python3.10 python3.10-venv python3-pip`
5. **macOS**: Use `brew install python@3.10` or download from python.org

#### Step 2 — Set up the project (one-time)

| OS | Command |
|---|---|
| 🪟 Windows | Double-click **`scripts/install.bat`** |
| 🐧 Linux | `bash scripts/install.sh` |
| 🍎 macOS | `bash scripts/install.sh` |

#### Step 3 — Run the program

| OS | Command |
|---|---|
| 🪟 Windows | Double-click **`scripts/run.bat`** |
| 🐧 Linux | `bash scripts/run.sh` |
| 🍎 macOS | `bash scripts/run.sh` |

That's it! An interactive menu will guide you through everything — no typing of commands needed.

---

## 📊 Strategies

Choose a strategy in the interactive menu. Strategies are split into three categories:

### Inside Bets (Straight-up 35:1)

| Strategy | Numbers | Win Chance | Risk | Best For |
|---|---|---|---|---|
| 🎯 **Sniper** | 1 | ~2.7% | Extreme | Thrill seekers — huge payouts, rare wins |
| 🔥 **Aggressive** | 3 | ~8.1% | High | Confident sessions with strong AI training |
| ⚖️ **Balanced** | 6 | ~16.2% | Medium | **Recommended starting point** |

### Outside Bets

| Strategy | Bet | Win Chance | Payout | Best For |
|---|---|---|---|---|
| 🔴⚫ **Red/Black** | 1 bet | ~48.6% | 1:1 | Simple color prediction |
| 🔢 **Odd/Even** | 1 bet | ~48.6% | 1:1 | Parity-based betting |
| 📏 **Small/Big** | 1 bet | ~48.6% | 1:1 | Range-based betting (1-18 or 19-36) |
| 🧩 **Dozens** | 1 bet | ~32.4% | 2:1 | Best of 3 dozens (1-12, 13-24, 25-36) |
| 📊 **Columns** | 1 bet | ~32.4% | 2:1 | Best of 3 table columns |

### AI-Powered

| Strategy | Bets | Win Chance | Risk | Best For |
|---|---|---|---|---|
| 🤖 **Adaptive AI** | 1-6 | Varies | Variable | AI reads its own confidence, adjusts coverage |
| 🧠 **Fusion** | 1-5 bets | Varies | Variable | Combines up to 5 outside bets using AI analysis |
| 🎲 **Hybrid** | Mixed | Varies | Variable | Inside numbers + outside bets combined |

> **Not sure which to pick?** Start with **Balanced** or **Red/Black**.

---

## 🧠 How It Works

```
  Roulette Table  (live, online, or manual entry)
       │  (spin result every ~30 seconds)
       ▼
  Live Feed / Simulator
       │  (integer 0–36)
       ▼
  Prediction Engine
       │
       ├── [History buffer]  Collects the last 15 spin results
       │
      ├── [Neural Network]  Hybrid Transformer + BiLSTM → outputs a probability
       │                     for each of the 37 possible numbers
       │
       ├── [Strategy]        Picks the top N numbers by probability
       │
      ├── [Betting]         Supports straight-up and outside-bet payout logic
       │
       ├── [Accounting]      Win: +35× the winning bet − all bets
       │                     Loss: −all bets
       │
       ├── [Statistics]      Updates win rate, ROI, streak
       │
       └── [Auto-train]      (if enabled) Re-trains the model on
                             recent history — model improves over time
```

### The AI Model

- **Architecture**: Transformer attention block + bidirectional LSTM stack + dense head
- **Input**: Last 15 spins with engineered features (number, color, parity, range, dozen, column)
- **Output**: Probability distribution over all 37 numbers (0–36)
- **Training**: Label-smoothed categorical cross-entropy, Adam optimizer, early stopping
- **Online learning**: Optional — model updates after every spin using recent 150 results
- **Model storage**: Separate directories per mode — `saved_models/manual/`, `saved_models/simulation/`, `saved_models/live/`

---

## ⚙️ Advanced Settings

All settings are in [`config/settings.py`](config/settings.py). Key values:

| Setting | Default | What it controls |
|---|---|---|
| `SEQUENCE_LENGTH` | `15` | Past spins used as AI input |
| `DEFAULT_BET_AMOUNT` | `1.00` | Default bet amount per number (in dollars) |
| `AUTO_TRAIN_MIN` | `20` | Min spins before online training starts |
| `RECONNECT_DELAY` | `30` | Seconds before WebSocket reconnect |
| `TRAINING_EPOCHS` | `150` | Epochs for full offline training |
| `CHECKPOINT_MODE` | `True` | Pause at 100/250/500/1000 spins to show stats |

---

## 🤝 Contributing

Pull requests and issues are welcome!

---

## 📄 License

Apache License 2.0 — see [LICENSE](LICENSE)

---

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/image?repos=alaevate/deeproulette&type=Date&theme=dark" width="100%" height="auto" />
  <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/image?repos=alaevate/deeproulette&type=Date" width="100%" height="auto" />
  <img alt="Star History Chart" src="https://api.star-history.com/image?repos=alaevate/deeproulette&type=Date" width="100%" height="auto" />
</picture>

<div align="center"><sub>Built with ❤️ by <a href="https://github.com/alaevate">Alaevate</a></sub></div>
