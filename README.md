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
    .
    ├── Data/
    │   └── data.txt
    ├── Environment/
    │   ├── SimAgent.py
    │   ├── SimEnv.py
    │   ├── SimHurdle.py
    │   └── __init__.py
    ├── Models/
    │   ├── CollectiveDecisionModel.py
    │   └── ModelAgent.py
    ├── Utils/
    │   ├── utils.py
    │   └── config.json
    ├── README.md
    ├── main.py
    └── requirements.txt 
## Quick Start

Run a single interactive sim (window opens) with a chosen model:

```bash
# Majority model
python main.py -m

# Voter model
python main.py -v

# Kuramoto model
python main.py -k
```

Limit the run length:

```bash
python main.py -k -t 600
```

Use previously saved initial conditions:

```bash
python main.py -o -k
```
(Use `-n to generate new data, if your version supports it.)
