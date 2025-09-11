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
  - *(optional, if present in your `Utils.utils`)* agents reached per time step

---
