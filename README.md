# Collective Decision Model (Majority / Voter / Kuramoto)

A lightweight swarm simulation to study **collective decision making** and **coordination** under three canonical models:

- **Majority Rule**
- **Voter**
- **Kuramoto** (phase-based synchronization)

The simulator runs in **pygame**, logs per–consensus-checkpoint metrics to CSV, and renders comparison plots across agent sizes and target counts. A batch mode sweeps common configurations and writes all results under `Data/`.

---

## Contents

- [Features](#features)
- [Repository Structure](#repository-structure)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [CLI Usage](#cli-usage)
- [Batch Sweep](#batch-sweep)
- [Outputs & File Naming](#outputs--file-naming)
- [Evaluation Metrics (Mathematical Framework)](#evaluation-metrics-mathematical-framework)
- [Plotting](#plotting)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Extending](#extending)
- [License](#license)

---

## Features

- Flocking dynamics (cohesion / separation / alignment) + target pursuit + obstacle avoidance.
- Three decision / consensus models: **Majority**, **Voter**, **Kuramoto**.
- Periodic “consensus checkpoints” (every `CONSENSUS_PERIOD` steps) where metrics are sampled.
- Batch sweep across **agents ∈ {10,20,30,40} × targets ∈ {2,10} × models**.
- CSV logging and comparison plots:
  - **Direction mismatch**
  - **Collision count**
  - **Phase synchronization** (Kuramoto only)
  - **Decision Making Accuracy** (number of agents reached target per time step)

---

## Repository Structure

    ```bash
    .
    ├── src/
    │   ├── main.py
    │   └── utils/
    │       └── helper.py
    ├── tests/
    │   └── test_main.py
    ├── README.md
    └── requirements.txt 

> Minor naming differences are ok (e.g., `Model` vs `Models`) — use whatever your local code has.
.
├─ main.py
├─ config.py # argparse / default params (or: Utils/config.py in some setups)
├─ Environment/
│ ├─ SimEnv.py # pygame loop, rendering, time-step logic
│ └─ SimHurdle.py # simple moving obstacles
├─ Models/ # or: Model/
│ ├─ CollectiveDecisionModel.py # MajorityRuleModel / VoterModel / KuramotoModel
│ └─ ModelAgent.py # Agent classes / helpers used by each model
├─ Utils/
│ └─ utils.py # init scenario, CSV I/O, metric averaging, plotting helpers
├─ Data/ # auto-created; CSV + figures land here
└─ scripts/
└─ write_readme.py # (optional) script that writes this README.md
