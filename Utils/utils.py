import random, json, csv, os
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
    with open(FILE_NAME, 'w') as f:
        json.dump(data, f)

def read_from_file():
    with open(FILE_NAME, 'r') as f:
        return json.load(f)

def simulation_init(params):
    """
    Initializes agents, non-overlapping targets, and hurdles.
    Targets are placed so that pairwise center distances >= 2*TARGET_SIZE (radius),
    preventing any overlap.
    """
    import math
    env_params, swarm_params = params

    # ---------- Agents (unchanged) ----------
    agent_init_pos = [
        (random.uniform(0, swarm_params['START_AREA_LEN']),
         random.uniform(env_params['SCREEN_HEIGHT'] / 3,
                        env_params['SCREEN_HEIGHT'] / 3 + swarm_params['START_AREA_LEN']))
        for _ in range(swarm_params['NUM_AGENTS'])
    ]

    # ---------- Targets (non-overlapping) ----------
    R = float(env_params['TARGET_SIZE'])            # radius
    min_dist = 2.0 * R                              # min center-to-center distance
    x_fixed = env_params['SCREEN_WIDTH'] - swarm_params['STARTING_AREA_WIDTH'] - R / 2.0  # keep original column
    y_min = 50.0 + R                                # keep a margin + radius so circle stays on-screen
    y_max = float(env_params['SCREEN_HEIGHT']) - 50.0 - R

    num_targets = int(env_params['NUM_TARGET'])
    max_attempts = 10000

    targets = []
    attempts = 0
    while len(targets) < num_targets and attempts < max_attempts:
        attempts += 1
        y = random.uniform(y_min, y_max)
        candidate = (x_fixed, y)

        ok = True
        for (px, py) in targets:
            # Euclidean distance since x is fixed (reduces to |y - py| but keep general)
            if math.hypot(candidate[0] - px, candidate[1] - py) < min_dist:
                ok = False
                break
        if ok:
            targets.append(candidate)

    # Fallback: deterministic spacing if random sampling couldn't place all
    if len(targets) < num_targets:
        span = y_max - y_min
        # place evenly with at least min_dist spacing
        step = max(min_dist, span / (num_targets + 1))
        targets = []
        y = y_min + step
        for _ in range(num_targets):
            if y > y_max:  # clamp if rounding pushes out of bounds
                y = y_max
            targets.append((x_fixed, y))
            y += step

    # ---------- Hurdles (unchanged) ----------
    hurdles = []
    for _ in range(env_params['NUM_HURDLE']):
        hurdle_x = random.uniform(env_params['SCREEN_WIDTH'] / 3, env_params['SCREEN_WIDTH'] * 4 / 5)
        hurdle_y = random.uniform(0, env_params['SCREEN_HEIGHT'] - 50)
        amplitude = random.choice([1, 2])
        frequency = random.uniform(0.0, 0.1)
        hurdles.append((hurdle_x, hurdle_y, amplitude, frequency))

    write_to_file([agent_init_pos, targets, hurdles])

# ---- metrics helpers for CSV + plotting ----
def _avg_mismatch_series(perf):
    if not isinstance(perf, (list, tuple)) or not perf:
        return []
    series = perf[0] if isinstance(perf[0], list) else perf
    out = []
    for step in series:
        if isinstance(step, (list, tuple)) and step:
            out.append(sum(step) / len(step))
        else:
            out.append(0.0)
    return out

def _ensure_csv_with_header(csv_path):
    _ensure_data_dir()
    if not os.path.exists(csv_path) or os.path.getsize(csv_path) == 0:
        with open(csv_path, 'w', newline='') as f:
            csv.writer(f).writerow(['agents','targets','model','checkpoint','avg_dir_mismatch'])

def append_series_to_csv(csv_path, agents, targets, model_name, series):
    _ensure_csv_with_header(csv_path)
    with open(csv_path, 'a', newline='') as f:
        w = csv.writer(f)
        for i, val in enumerate(series, start=1):
            w.writerow([agents, targets, model_name, i, float(val)])

def plot_figures_from_csv(csv_path):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f'CSV not found: {csv_path}')
    rows = []
    with open(csv_path, 'r', newline='') as f:
        for row in csv.DictReader(f):
            try:
                rows.append({
                    'agents': int(row['agents']),
                    'targets': int(row['targets']),
                    'model': row['model'],
                    'checkpoint': int(row['checkpoint']),
                    'y': float(row['avg_dir_mismatch']),
                })
            except:  # skip bad rows
                pass

    wanted_agents = [10, 20, 30, 40]
    wanted_targets = [2, 10]
    model_order = ['Majority Model', 'Voter Model', 'Kuramoto Model']

    for A in wanted_agents:
        data_2 = {m: [] for m in model_order}
        data_10 = {m: [] for m in model_order}
        for r in rows:
            if r['agents'] != A or r['targets'] not in wanted_targets: continue
            if r['model'] not in data_2: continue
            (data_2 if r['targets'] == 2 else data_10)[r['model']].append((r['checkpoint'], r['y']))

        for m in model_order:
            data_2[m].sort(key=lambda t: t[0])
            data_10[m].sort(key=lambda t: t[0])

        _ensure_data_dir()
        fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)

        ax = axes[0]
        for m in model_order:
            if data_2[m]:
                xs, ys = zip(*data_2[m])
                ax.plot(xs, ys, label=m)
        ax.set_title(f'{A} agents, 2 targets')
        ax.set_xlabel('Consensus checkpoints')
        ax.set_ylabel('Avg. direction mismatch (rad)')
        ax.legend()

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
        fig.savefig(f'Data/DirectionMismatch_{A}A_2T_vs_10T.png', dpi=150)
        plt.close(fig)

# (retain your single-model plot if you use it elsewhere)
def plot_performance_graph(model_name, performance_data, params=None):
    _ensure_data_dir()
    num_agents = num_targets = None
    if params and isinstance(params, (list,tuple)) and len(params)==2:
        env_params, swarm_params = params
        num_agents = swarm_params.get('NUM_AGENTS')
        num_targets = env_params.get('NUM_TARGET')
    series = performance_data[0] if isinstance(performance_data[0], list) else performance_data
    if not series: return
    x = list(range(1, len(series)+1))
    y = [(sum(step)/len(step)) if step else 0.0 for step in series]
    plt.plot(x, y, label='Avg. direction mismatch')
    plt.xlabel('Consensus checkpoints'); plt.ylabel('Average mismatch (rad)'); plt.legend()
    slug = model_name.replace(' ','_'); a=f'_{num_agents}A' if num_agents is not None else ''; t=f'_{num_targets}T' if num_targets is not None else ''
    plt.title(f'Direction mismatch over time – {model_name}')
    plt.tight_layout(); plt.savefig(f'Data/DirectionMismatch_{slug}{a}{t}.png', dpi=150); plt.close()
