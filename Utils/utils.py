# Utils/utils.py
import random
import json
import csv
import os
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime

FILE_NAME = 'Data/data.txt'


def _ensure_data_dir():
    Path("Data").mkdir(parents=True, exist_ok=True)


def display_simulation_config(params):
    env_params, swarm_params = params
    print('#' * 17, 'SIMULATION CONFIGURATION', '#' * 17)
    print('Number of Agents : ', swarm_params['NUM_AGENTS'])
    print('Number of Targets : ', env_params['NUM_TARGET'])
    print('Number of Hurdles : ', env_params['NUM_HURDLE'])
    print('Start Time :', datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
    print('#' * 60)


def write_to_file(data):
    _ensure_data_dir()
    with open(FILE_NAME, 'w') as file:
        json.dump(data, file)


def read_from_file():
    with open(FILE_NAME, 'r') as file:
        data = json.load(file)
    return data


def simulation_init(params):
    """
    Creates initial agent positions, targets, and hurdles and writes them to Data/data.txt
    (no change to your original placement logic).
    """
    env_params, swarm_params = params

    agent_init_pos = [
        (random.uniform(0, swarm_params['START_AREA_LEN']),
         random.uniform(env_params['SCREEN_HEIGHT'] / 3,
                        env_params['SCREEN_HEIGHT'] / 3 + swarm_params['START_AREA_LEN']))
        for _ in range(swarm_params['NUM_AGENTS'])
    ]

    targets = []
    for _ in range(env_params['NUM_TARGET']):
        target_x = env_params['SCREEN_WIDTH'] - swarm_params['STARTING_AREA_WIDTH'] - env_params['TARGET_SIZE'] / 2
        target_y = random.uniform(50, env_params['SCREEN_HEIGHT'] - 50)
        targets.append((target_x, target_y))

    hurdles = []
    for _ in range(env_params['NUM_HURDLE']):
        hurdle_x = random.uniform(env_params['SCREEN_WIDTH'] / 3, env_params['SCREEN_WIDTH'] * 4 / 5)
        hurdle_y = random.uniform(0, env_params['SCREEN_HEIGHT'] - 50)
        amplitude = random.choice([1, 2])
        frequency = random.uniform(0.0, 0.1)
        hurdles.append((hurdle_x, hurdle_y, amplitude, frequency))

    write_to_file([agent_init_pos, targets, hurdles])


# -------- metrics helpers for CSV + plotting --------

def _avg_mismatch_series(performance_data):
    """
    Extract average direction mismatch per consensus checkpoint.
    Expected: performance_data[0] is list of per-agent mismatch lists.
    """
    if not isinstance(performance_data, (list, tuple)) or not performance_data:
        return []
    series = performance_data[0] if isinstance(performance_data[0], list) else performance_data
    out = []
    for step in series:
        if isinstance(step, (list, tuple)) and len(step) > 0:
            out.append(sum(step) / len(step))
        else:
            out.append(0.0)
    return out


def _ensure_csv_with_header(csv_path):
    _ensure_data_dir()
    if not os.path.exists(csv_path) or os.path.getsize(csv_path) == 0:
        with open(csv_path, 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(['agents', 'targets', 'model', 'checkpoint', 'avg_dir_mismatch'])


def append_series_to_csv(csv_path, agents, targets, model_name, series):
    """
    Append one run's averaged mismatch series to a CSV.
    Columns: agents, targets, model, checkpoint, avg_dir_mismatch
    """
    _ensure_csv_with_header(csv_path)
    with open(csv_path, 'a', newline='') as f:
        w = csv.writer(f)
        for i, val in enumerate(series, start=1):
            w.writerow([agents, targets, model_name, i, float(val)])


def plot_figures_from_csv(csv_path):
    """
    Build four figures: one per agent size {10,20,30,40},
    each with two subplots: left (2 targets), right (10 targets).
    Each subplot: three lines (Majority, Voter, Kuramoto).
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f'CSV not found: {csv_path}')

    # Load
    rows = []
    with open(csv_path, 'r', newline='') as f:
        r = csv.DictReader(f)
        for row in r:
            try:
                rows.append({
                    'agents': int(row['agents']),
                    'targets': int(row['targets']),
                    'model': row['model'],
                    'checkpoint': int(row['checkpoint']),
                    'y': float(row['avg_dir_mismatch']),
                })
            except Exception:
                continue

    # Organize
    wanted_agents = [10, 20, 30, 40]
    wanted_targets = [2, 10]
    model_order = ['Majority Model', 'Voter Model', 'Kuramoto Model']

    for A in wanted_agents:
        data_2 = {m: [] for m in model_order}
        data_10 = {m: [] for m in model_order}

        for r in rows:
            if r['agents'] != A or r['targets'] not in wanted_targets:
                continue
            if r['model'] not in data_2:  # only known models
                continue
            if r['targets'] == 2:
                data_2[r['model']].append((r['checkpoint'], r['y']))
            else:
                data_10[r['model']].append((r['checkpoint'], r['y']))

        # sort by checkpoint
        for m in model_order:
            data_2[m].sort(key=lambda t: t[0])
            data_10[m].sort(key=lambda t: t[0])

        # plot
        _ensure_data_dir()
        fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)

        # Left: 2 targets
        ax = axes[0]
        for m in model_order:
            if data_2[m]:
                xs, ys = zip(*data_2[m])
                ax.plot(xs, ys, label=m)
        ax.set_title(f'{A} agents, 2 targets')
        ax.set_xlabel('Consensus checkpoints')
        ax.set_ylabel('Avg. direction mismatch (rad)')
        ax.legend()

        # Right: 10 targets
        ax = axes[1]
        for m in model_order:
            if data_10[m]:
                xs, ys = zip(*data_10[m])
                ax.plot(xs, ys, label=m)
        ax.set_title(f'{A} agents, 10 targets')
        ax.set_xlabel('Consensus checkpoints')
        ax.legend()

        fig.suptitle(f'Collective Decision — {A} agents', fontsize=12)
        fig.tight_layout(rect=[0, 0, 1, 0.95])
        out = f'Data/DirectionMismatch_{A}A_2T_vs_10T.png'
        fig.savefig(out, dpi=150)
        plt.close(fig)


# (Optional single-model plot you already use)
def plot_performance_graph(model_name, performance_data, params=None):
    _ensure_data_dir()
    num_agents = None
    num_targets = None
    if params is not None and isinstance(params, (list, tuple)) and len(params) == 2:
        env_params, swarm_params = params
        num_agents = swarm_params.get('NUM_AGENTS', None)
        num_targets = env_params.get('NUM_TARGET', None)

    if not isinstance(performance_data, (list, tuple)) or not performance_data:
        return
    dir_mismatch_series = performance_data[0] if isinstance(performance_data[0], list) else performance_data
    if not dir_mismatch_series:
        return

    x = list(range(1, len(dir_mismatch_series) + 1))
    y_avg = [(sum(step) / len(step)) if step else 0.0 for step in dir_mismatch_series]

    plt.plot(x, y_avg, label='Avg. direction mismatch')
    plt.xlabel('Consensus checkpoints')
    plt.ylabel('Average mismatch (rad)')
    plt.title(f'Direction mismatch over time – {model_name}')
    plt.legend()

    model_slug = model_name.replace(' ', '_')
    a_part = f"_{num_agents}A" if num_agents is not None else ""
    t_part = f"_{num_targets}T" if num_targets is not None else ""
    out = f"Data/DirectionMismatch_{model_slug}{a_part}{t_part}.png"

    plt.tight_layout()
    plt.savefig(out, dpi=150)
    plt.close()
