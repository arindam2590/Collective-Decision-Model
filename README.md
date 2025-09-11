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
