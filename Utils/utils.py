import random
import json
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime

FILE_NAME = 'Data/data.txt'


def display_simulation_config(params):
    env_params, swarm_params = params
    print('#' * 17, 'SIMULATION CONFIGURATION', '#' * 17)
    print('Number of Agents : ', swarm_params['NUM_AGENTS'])
    print('Number of Targets : ', env_params['NUM_TARGET'])
    print('Number of Hurdles : ', env_params['NUM_HURDLE'])
    print('Start Time :', datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
    print('#' * 60)


def _ensure_data_dir():
    Path("Data").mkdir(parents=True, exist_ok=True)


def write_to_file(data):
    _ensure_data_dir()
    with open(FILE_NAME, 'w') as file:
        json.dump(data, file)


def read_from_file():
    with open(FILE_NAME, 'r') as file:
        data = json.load(file)
    return data


def plot_performance_graph(model_name, performance_data):
    """
    Current pipeline returns:
      performance_data[0] -> list of direction_mismatch lists (one list per consensus check)
      performance_data[1] -> final time_count (int)

    We plot the average direction mismatch over successive checkpoints.
    """
    _ensure_data_dir()

    if not performance_data or len(performance_data) < 1:
        return

    dir_mismatch_series = performance_data[0]  # list[list[per-agent mismatch]]
    if not dir_mismatch_series:
        return

    # x-axis as checkpoints (1..N) because the raw clock isn't carried alongside
    x = list(range(1, len(dir_mismatch_series) + 1))
    y_avg = [sum(step) / max(len(step), 1) for step in dir_mismatch_series]

    plt.plot(x, y_avg, label='Avg. direction mismatch')
    plt.xlabel('Consensus checkpoints')
    plt.ylabel('Average mismatch (rad)')
    plt.title(f'Direction mismatch over time – {model_name}')
    plt.legend()
    out = f'Data/DirectionMismatch_{model_name.replace(" ", "_")}.png'
    plt.tight_layout()
    plt.savefig(out, dpi=150)
    plt.close()
