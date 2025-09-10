import random
import json
import csv
import os
import math
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
    Initializes agents, non-overlapping targets (>= 2*TARGET_SIZE gap), and hurdles.
    Writes [agent_init_pos, targets, hurdles] to Data/data.txt
    """
    env_params, swarm_params = params

    # Agents: random cluster on the left third
    agent_init_pos = [
        (random.uniform(0, swarm_params['START_AREA_LEN']),
         random.uniform(env_params['SCREEN_HEIGHT'] / 3,
                        env_params['SCREEN_HEIGHT'] / 3 + swarm_params['START_AREA_LEN']))
        for _ in range(swarm_params['NUM_AGENTS'])
    ]

    # Targets: vertical column near the right side, min spacing >= 2*R
    R = float(env_params['TARGET_SIZE'])
    min_dist = 2.0 * R
    x_fixed = env_params['SCREEN_WIDTH'] - swarm_params['STARTING_AREA_WIDTH'] - R / 2.0
    y_min = 50.0 + R
    y_max = float(env_params['SCREEN_HEIGHT']) - 50.0 - R
    num_targets = int(env_params['NUM_TARGET'])
    targets = []
    attempts, max_attempts = 0, 10000
    while len(targets) < num_targets and attempts < max_attempts:
        attempts += 1
        y = random.uniform(y_min, y_max)
        cand = (x_fixed, y)
        ok = True
        for (px, py) in targets:
            if math.hypot(cand[0] - px, cand[1] - py) < min_dist:
                ok = False
                break
        if ok:
            targets.append(cand)
    if len(targets) < num_targets:
        # deterministic fallback spacing
        span = y_max - y_min
        step = max(min_dist, span / (num_targets + 1))
        targets = []
        y = y_min + step
        for _ in range(num_targets):
            if y > y_max:
                y = y_max
            targets.append((x_fixed, y))
            y += step

    # Hurdles: random band in the middle-right
    hurdles = []
    for _ in range(env_params['NUM_HURDLE']):
        hurdle_x = random.uniform(env_params['SCREEN_WIDTH'] / 3, env_params['SCREEN_WIDTH'] * 4 / 5)
        hurdle_y = random.uniform(0, env_params['SCREEN_HEIGHT'] - 50)
        amplitude = random.choice([1, 2])
        frequency = random.uniform(0.0, 0.1)
        hurdles.append((hurdle_x, hurdle_y, amplitude, frequency))

    write_to_file([agent_init_pos, targets, hurdles])


# ---------- Metric helpers (existing) ----------

def _series_from_perf(perf, key):
    """
    Extract series for a given metric key from performance_data.
    Expected layouts:
        Kuramoto: [dir_mismatch, collisions, phase_synchronization, decision_accuracy, time_count]
        Others:   [dir_mismatch, collisions, decision_accuracy, time_count]
    """
    if not isinstance(perf, (list, tuple)) or not perf:
        return []
    if key == 'dir_mismatch':
        return perf[0] if len(perf) >= 1 else []
    if key == 'collisions':
        return perf[1] if len(perf) >= 2 else []
    if key == 'phase_synchronization':
        return perf[2] if len(perf) >= 3 else []
    if key == 'decision_accuracy':
        if len(perf) >= 5:   # Kuramoto
            return perf[3]
        if len(perf) >= 4:   # Others
            return perf[2]
        return []
    return []


def _avg_series(perf, key):
    series = _series_from_perf(perf, key)
    if not isinstance(series, list):
        return []
    out = []
    for step in series:
        if isinstance(step, (list, tuple)):
            out.append((sum(step) / len(step)) if len(step) > 0 else 0.0)
        else:
            try:
                out.append(float(step))
            except Exception:
                out.append(0.0)
    return out


def _avg_mismatch_series(perf):
    return _avg_series(perf, 'dir_mismatch')


def _avg_collision_series(perf):
    return _avg_series(perf, 'collisions')


def _avg_phase_series(perf):
    return _avg_series(perf, 'phase_synchronization')


def _avg_accuracy_series(perf):
    return _avg_series(perf, 'decision_accuracy')


# ---------- Existing CSV I/O for checkpoint metrics ----------

_HEADER = [
    'agents', 'targets', 'model', 'checkpoint',
    'avg_dir_mismatch', 'avg_collisions', 'avg_phase_sync', 'avg_decision_accuracy'
]

def _ensure_csv_with_header(csv_path: str):
    os.makedirs(os.path.dirname(csv_path) or ".", exist_ok=True)
    if os.path.exists(csv_path) and os.path.getsize(csv_path) > 0:
        with open(csv_path, 'r', newline='') as f:
            r = csv.reader(f)
            hdr = next(r, [])
            if hdr == _HEADER:
                return
        rows = []
        with open(csv_path, 'r', newline='') as f:
            r = csv.reader(f)
            _ = next(r, None)
            rows = [row for row in r]
        with open(csv_path, 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(_HEADER)
            for row in rows:
                w.writerow((row + [''] * len(_HEADER))[:len(_HEADER)])
        return
    with open(csv_path, 'w', newline='') as f:
        csv.writer(f).writerow(_HEADER)


def append_metrics_to_csv(csv_path: str, agents: int, targets: int, model_name: str,
                          mismatch_series, collision_series, phase_series=None, accuracy_series=None):
    _ensure_csv_with_header(csv_path)
    mismatch_series  = list(mismatch_series or [])
    collision_series = list(collision_series or [])
    phase_series     = list(phase_series or [])
    accuracy_series  = list(accuracy_series or [])

    n = max(len(mismatch_series), len(collision_series), len(phase_series), len(accuracy_series))
    if n == 0:
        return

    rows = []
    for i in range(n):
        y_mis = float(mismatch_series[i])   if i < len(mismatch_series)  else 0.0
        y_col = float(collision_series[i])  if i < len(collision_series) else 0.0
        y_phs = float(phase_series[i])      if i < len(phase_series)     else 0.0
        y_acc = float(accuracy_series[i])   if i < len(accuracy_series)  else 0.0
        rows.append([agents, targets, model_name, i + 1, y_mis, y_col, y_phs, y_acc])

    with open(csv_path, 'a', newline='') as f:
        csv.writer(f).writerows(rows)


# ---------- NEW: per-time-step agents-reached timeseries CSV ----------

_REACHED_CSV = 'Data/reached_timeseries.csv'
_REACHED_HDR = ['agents', 'targets', 'model', 'step', 'agents_reached']

def _ensure_reached_csv(csv_path=_REACHED_CSV):
    os.makedirs(os.path.dirname(csv_path) or ".", exist_ok=True)
    if not (os.path.exists(csv_path) and os.path.getsize(csv_path) > 0):
        with open(csv_path, 'w', newline='') as f:
            csv.writer(f).writerow(_REACHED_HDR)


def append_reached_timeseries(agents: int, targets: int, model_name: str, reached_series, csv_path=_REACHED_CSV):
    """Write per-time-step counts: one row per time step."""
    _ensure_reached_csv(csv_path)
    rows = []
    for i, val in enumerate(reached_series, start=1):
        try:
            y = int(val)
        except Exception:
            y = 0
        rows.append([agents, targets, model_name, i, y])
    with open(csv_path, 'a', newline='') as f:
        csv.writer(f).writerows(rows)


def _read_csv_dicts(csv_path):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f'CSV not found: {csv_path}')
    with open(csv_path, 'r', newline='') as f:
        r = csv.DictReader(f)
        fields = r.fieldnames or []
        rows = [row for row in r]
    return fields, rows


# ---------- Plotting ----------

def _plot_by_agents_targets(csv_path, value_key, fig_prefix, ylabel, xlabel, ylim=None, model_filter=None, legend_title='Model'):
    fields, rows_src = _read_csv_dicts(csv_path)
    if value_key not in fields:
        raise ValueError(f"CSV does not contain '{value_key}': {csv_path}")

    rows = []
    for row in rows_src:
        try:
            model = row['model']
            if model_filter is not None:
                if isinstance(model_filter, set):
                    if model not in model_filter:
                        continue
                elif callable(model_filter):
                    if not model_filter(model):
                        continue
            rows.append({
                'agents': int(row['agents']),
                'targets': int(row['targets']),
                'model': model,
                'x': int(row.get('checkpoint', row.get('step'))),  # supports both styles
                'y': float(row[value_key]),
            })
        except Exception:
            continue

    wanted_agents = [10, 20, 30, 40]
    wanted_targets = [2, 10]
    model_order = ['Majority Model', 'Voter Model', 'Kuramoto Model']

    for A in wanted_agents:
        data_2 = {}
        data_10 = {}
        for r in rows:
            if r['agents'] != A or r['targets'] not in wanted_targets:
                continue
            bucket = data_2 if r['targets'] == 2 else data_10
            bucket.setdefault(r['model'], []).append((r['x'], r['y']))

        for bucket in (data_2, data_10):
            for k in list(bucket.keys()):
                bucket[k].sort(key=lambda t: t[0])

        _ensure_data_dir()
        fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)

        # left: 2 targets
        ax = axes[0]
        plotted = False
        for m in model_order:
            if m in data_2 and data_2[m]:
                xs, ys = zip(*data_2[m])
                ax.plot(xs, ys, label=m)
                plotted = True
        # ax.set_title(f'{A} agents, 2 targets')
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        if ylim is not None:
            ax.set_ylim(*ylim)
        if plotted:
            ax.legend(title=legend_title, loc='best')

        # right: 10 targets
        ax = axes[1]
        plotted = False
        for m in model_order:
            if m in data_10 and data_10[m]:
                xs, ys = zip(*data_10[m])
                ax.plot(xs, ys, label=m)
                plotted = True
        # ax.set_title(f'{A} agents, 10 targets')
        ax.set_xlabel(xlabel)
        if ylim is not None:
            ax.set_ylim(*ylim)
        if plotted:
            ax.legend(title=legend_title, loc='best')

        # fig.suptitle(f'{ylabel} — {A} agents', fontsize=12)
        fig.tight_layout(rect=[0, 0, 1, 0.95])
        fig.savefig(f'Data/{fig_prefix}_{A}A_2T_vs_10T.png', dpi=150)
        plt.close(fig)


# Existing comparison plots (unchanged)
def plot_figures_from_csv(csv_path):
    _plot_by_agents_targets(csv_path, 'avg_dir_mismatch', 'DirectionMismatch',
                            'Avg. direction mismatch (rad)', 'Consensus Period', ylim=None, model_filter=None, legend_title='Model')


def plot_collision_figures_from_csv(csv_path):
    _plot_by_agents_targets(csv_path, 'avg_collisions', 'Collision',
                            'Avg. collision count', 'Consensus Period', ylim=None, model_filter=None, legend_title='Model')


def plot_phase_figures_from_csv(csv_path):
    _plot_by_agents_targets(csv_path, 'avg_phase_sync', 'PhaseSync',
                            'Avg. phase synchronization', 'Consensus Period', ylim=None, model_filter={'Kuramoto Model'}, legend_title='Kuramoto')


# NEW: per-time-step agents reached
def plot_reached_figures_from_csv(csv_path='Data/reached_timeseries.csv'):
    _plot_by_agents_targets(csv_path, 'agents_reached', 'AgentsReached',
                            'Decision Accuracy (Agent reached target)', 'Time Step', ylim=None, model_filter=None, legend_title='Model')


# Optional single-run quick plot (unchanged)
def plot_performance_graph(model_name, performance_data, params=None):
    _ensure_data_dir()

    num_agents = num_targets = None
    if params and isinstance(params, (list, tuple)) and len(params) == 2:
        env_params, swarm_params = params
        num_agents = swarm_params.get('NUM_AGENTS')
        num_targets = env_params.get('NUM_TARGET')

    series = _series_from_perf(performance_data, 'dir_mismatch')
    if not series:
        return

    x = list(range(1, len(series) + 1))
    y = [(sum(step) / len(step)) if step else 0.0 for step in series]
    plt.plot(x, y, label='Avg. direction mismatch')
    plt.xlabel('Consensus checkpoints')
    plt.ylabel('Average mismatch (rad)')
    plt.title(f'Direction mismatch over time – {model_name}')
    plt.legend()

    slug = model_name.replace(' ', '_')
    a_part = f'_{num_agents}A' if num_agents is not None else ''
    t_part = f'_{num_targets}T' if num_targets is not None else ''
    out = f'Data/DirectionMismatch_{slug}{a_part}{t_part}.png'
    plt.tight_layout()
    plt.savefig(out, dpi=150)
    plt.close()
