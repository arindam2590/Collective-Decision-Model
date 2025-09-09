# Utils/utils.py
import random
import json
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
    (kept consistent with your original shape/logic).
    """
    env_params, swarm_params = params

    # Agent start area: same logic as your original
    agent_init_pos = [
        (random.uniform(0, swarm_params['START_AREA_LEN']),
         random.uniform(env_params['SCREEN_HEIGHT'] / 3,
                        env_params['SCREEN_HEIGHT'] / 3 + swarm_params['START_AREA_LEN']))
        for _ in range(swarm_params['NUM_AGENTS'])
    ]

    # Targets along the right side
    targets = []
    for _ in range(env_params['NUM_TARGET']):
        target_x = env_params['SCREEN_WIDTH'] - swarm_params['STARTING_AREA_WIDTH'] - env_params['TARGET_SIZE'] / 2
        target_y = random.uniform(50, env_params['SCREEN_HEIGHT'] - 50)
        targets.append((target_x, target_y))

    # Moving vertical hurdles in the middle-right band
    hurdles = []
    for _ in range(env_params['NUM_HURDLE']):
        hurdle_x = random.uniform(env_params['SCREEN_WIDTH'] / 3, env_params['SCREEN_WIDTH'] * 4 / 5)
        hurdle_y = random.uniform(0, env_params['SCREEN_HEIGHT'] - 50)
        amplitude = random.choice([1, 2])
        frequency = random.uniform(0.0, 0.1)
        hurdles.append((hurdle_x, hurdle_y, amplitude, frequency))

    write_to_file([agent_init_pos, targets, hurdles])


def plot_performance_graph(model_name, performance_data, params=None):
    """
    Save plot as:
      Data/DirectionMismatch_<ModelName>_<NumAgents>A_<NumTargets>T.png

    Args:
        model_name (str)
        performance_data (list | tuple)
        params (tuple | list) optional: (env_params, swarm_params)
    """
    _ensure_data_dir()

    # --- infer counts (from params if provided) ---
    num_agents = None
    num_targets = None
    if params is not None and isinstance(params, (list, tuple)) and len(params) == 2:
        env_params, swarm_params = params
        num_agents = swarm_params.get('NUM_AGENTS', None)
        num_targets = env_params.get('NUM_TARGET', None)

    # --- handle shapes robustly (same as before) ---
    if not isinstance(performance_data, (list, tuple)) or not performance_data:
        return
    if len(performance_data) >= 1 and isinstance(performance_data[0], list):
        dir_mismatch_series = performance_data[0]
    else:
        dir_mismatch_series = performance_data

    if not dir_mismatch_series:
        return

    x = list(range(1, len(dir_mismatch_series) + 1))
    y_avg = []
    for step in dir_mismatch_series:
        if isinstance(step, (list, tuple)) and len(step) > 0:
            y_avg.append(sum(step) / len(step))
        else:
            y_avg.append(0.0)

    plt.plot(x, y_avg, label='Avg. direction mismatch')
    plt.xlabel('Consensus checkpoints')
    plt.ylabel('Average mismatch (rad)')
    plt.title(f'Direction mismatch over time – {model_name}')
    plt.legend()

    # --- build filename with model + counts ---
    model_slug = model_name.replace(' ', '_')
    a_part = f"_{num_agents}A" if num_agents is not None else ""
    t_part = f"_{num_targets}T" if num_targets is not None else ""
    out = f"Data/DirectionMismatch_{model_slug}{a_part}{t_part}.png"

    plt.tight_layout()
    plt.savefig(out, dpi=150)
    plt.close()