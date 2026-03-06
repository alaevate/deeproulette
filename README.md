<h1 align="center">
  <br>
  <a href="https://github.com/alaevate/deeproulette"><img src="assets/logo.svg" alt="DeepRoulette" width="200"></a>
  <br>
  DeepRoulette
  <br>
</h1>

<h4 align="center">Professional AI-powered roulette prediction system — Deep LSTM neural networks, real-time casino feed, beautiful terminal UI.</h4>

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
  <a href="#-disclaimer">⚠️ Disclaimer</a> •
  <a href="#-quick-start-no-tech-knowledge-needed">🚀 Quick Start</a> •
  <a href="#-strategies">📊 Strategies</a> •
  <a href="#-project-structure">📁 Structure</a> •
  <a href="#-how-it-works">🧠 How It Works</a> •
  <a href="#%EF%B8%8F-advanced-settings">⚙️ Settings</a>
</p>

<p align="center">
  <img src="assets/image.png" alt="DeepRoulette Demo">
</p>

---

## ⚠️ Disclaimer

> **This software is for educational and research purposes only.**
> Roulette is a game of pure chance. The house always has an edge.
> No AI system can guarantee wins. Never gamble with money you cannot afford to lose.
> Always gamble responsibly.

---

## 🚀 Quick Start — No Tech Knowledge Needed

### Step 1 — Install Python (one-time, skip if already installed)

1. Go to **https://www.python.org/downloads/**
2. Download the latest Python 3 installer
3. Run it and **tick the box** that says **"Add Python to PATH"**
4. Click Install

### Step 2 — Set up the project (one-time)

Double-click **`SETUP.bat`** in the project folder.
It will automatically install everything the program needs.

### Step 3 — Run the program

Double-click **`START.bat`**.

That's it! An interactive menu will guide you through everything — no typing of commands needed.

---

## 📊 Strategies

Choose a strategy in the interactive menu. Each one tells the AI how many numbers to bet on per spin:

| Strategy | Numbers Bet | Win Chance | Risk | Best For |
|---|---|---|---|---|
| 🎯 **Sniper** | 1 | ~2.7% | Extreme | Thrill seekers — huge payouts, rare wins |
| 🔥 **Aggressive** | 3 | ~8.1% | High | Confident sessions with strong AI training |
| ⚖️ **Balanced** | 6 | ~16.2% | Medium | **Recommended starting point** |
| 🛡️ **Conservative** | 18 | ~48.6% | Low | Beginners — most consistent results |
| 🤖 **Adaptive AI** | 1–18 | Varies | Variable | Let the AI decide based on its own confidence |

> **Not sure which to pick?** Start with **Balanced** or **Conservative**.

---

## 📁 Project Structure

```
DeepRoulette/
│
├── START.bat              ← Double-click to run the program
├── SETUP.bat              ← Double-click ONCE to install everything
├── main.py                ← Program entry point
├── requirements.txt       ← Package list (used by SETUP.bat)
│
├── config/
│   └── settings.py        ← All tunable settings in one place
│
├── core/
│   ├── engine.py          ← Main prediction loop
│   └── trainer.py         ← Model training (offline & online)
│
├── data/
│   ├── live_feed.py       ← Live WebSocket connection to casino
│   └── simulator.py       ← Local random spin generator
│
├── models/
│   └── neural_network.py  ← LSTM architecture definition
│
├── strategies/
│   ├── base.py            ← Shared betting logic
│   ├── sniper.py          ← 1 number
│   ├── aggressive.py      ← 3 numbers
│   ├── balanced.py        ← 6 numbers
│   ├── conservative.py    ← 18 numbers
│   └── adaptive.py        ← AI-driven dynamic
│
├── ui/
│   ├── menu.py            ← Interactive startup menu
│   └── display.py         ← Colourful terminal output
│
├── utils/
│   ├── logger.py          ← Session log files
│   └── tracker.py         ← Win/loss statistics
│
├── saved_models/          ← AI model files saved here (.keras)
├── logs/                  ← Session log files saved here
└── data_store/            ← Reserved for future data storage
```

---

## 🧠 How It Works

```
  Roulette Table
       │  (spin result every ~30 seconds)
       ▼
  Live Feed / Simulator
       │  (integer 0–36)
       ▼
  Prediction Engine
       │
       ├── [History buffer]  Collects the last 15 spin results
       │
       ├── [Neural Network]  3-layer LSTM → outputs a probability
       │                     for each of the 37 possible numbers
       │
       ├── [Strategy]        Picks the top N numbers by probability
       │
       ├── [Betting]         Sizes bets as 2% of balance per number
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

- **Architecture**: 3 stacked LSTM layers (256 → 128 → 64 units), followed by 2 Dense layers
- **Input**: The last 15 spin results, normalised to [0, 1]
- **Output**: A probability distribution over all 37 numbers (0–36)
- **Training**: Categorical cross-entropy loss, Adam optimiser, early stopping
- **Online learning**: Optional — the model updates after every spin using the most recent 150 results

---

## ⚙️ Advanced Settings

All settings are in [`config/settings.py`](config/settings.py). Key values:

| Setting | Default | What it controls |
|---|---|---|
| `SEQUENCE_LENGTH` | `15` | Past spins used as AI input |
| `BET_FRACTION` | `0.02` | Fraction of balance bet per number |
| `AUTO_TRAIN_MIN` | `30` | Min spins before online training starts |
| `SPIN_INTERVAL` | `5` | Seconds between simulated spins |
| `RECONNECT_DELAY` | `30` | Seconds before WebSocket reconnect |
| `TRAINING_EPOCHS` | `100` | Epochs for full offline training |

---

## 🤝 Contributing

Pull requests and issues are welcome!

---

## 📄 License

MIT License — see [LICENSE](LICENSE)

---

<div align="center"><sub>Built with ❤️ by <a href="https://github.com/alaevate">alaevate</a></sub></div>

