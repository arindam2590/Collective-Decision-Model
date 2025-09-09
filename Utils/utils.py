import json
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt

FILE_NAME = 'Data/data.txt'


def display_simulation_config(params):
    env_params, swarm_params = params
    print('#' * 17, 'SIMULATION CONFIGURATION', '#' * 17)
    print('Number of Agents : ', swarm_params['NUM_AGENTS'])
    print('Number of Targets : ', env_params['NUM_TARGET'])
    print('Number of Hurdles : ', env_params['NUM_HURDLE'])
    print('Start Time :', datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
    print('#' * 60)


def write_to_file(data):
    Path("Data").mkdir(parents=True, exist_ok=True)
    with open(FILE_NAME, 'w') as file:
        json.dump(data, file)


def read_from_file():
    with open(FILE_NAME, 'r') as file:
        data = json.load(file)
    return data


def plot_performance_graph(model_name: str, metrics: dict):
    """
    Expected metrics:
      metrics = {
         "time": [1,2,...,T],
         "dir_mismatch": [[... per-agent list ...] at each logging step],
         "consensus_counts": [{(x,y): n, ...} per logging step]  # tuple keys
      }
    """
    from pathlib import Path
    Path("Data").mkdir(parents=True, exist_ok=True)

    t = metrics.get("time", [])
    cc = metrics.get("consensus_counts", [])
    dm = metrics.get("dir_mismatch", [])

    # Plot consensus counts by target (tuple keys kept intact)
    if cc:
        keys = sorted(set().union(*[d.keys() for d in cc]))
        for k in keys:
            series = [d.get(k, 0) for d in cc]
            plt.plot(t[:len(series)], series, label=f"Target {k}")
        plt.xlabel("Time step")
        plt.ylabel("Agents favoring target")
        plt.title(f"Consensus over time - {model_name}")
        plt.legend()
        out = f"Data/Consensus_{model_name.replace(' ', '_')}.png"
        plt.tight_layout()
        plt.savefig(out, dpi=150)
        plt.close()

    # Plot average direction mismatch over logging periods
    if dm:
        avg_dm = [sum(row) / max(1, len(row)) for row in dm]
        x = list(range(len(avg_dm)))
        plt.plot(x, avg_dm, label="Avg. direction mismatch")
        plt.xlabel("Consensus periods")
        plt.ylabel("Mismatch (rad)")
        plt.title(f"Direction mismatch - {model_name}")
        plt.legend()
        out = f"Data/DirMismatch_{model_name.replace(' ', '_')}.png"
        plt.tight_layout()
        plt.savefig(out, dpi=150)
        plt.close()


    # Plot average direction mismatch over logging periods
    if dm:
        avg_dm = [sum(row) / max(1, len(row)) for row in dm]
        # Align x values to logging instants (subset of time)
        x = list(range(len(avg_dm)))
        plt.plot(x, avg_dm, label="Avg. direction mismatch")
        plt.xlabel("Consensus periods")
        plt.ylabel("Mismatch (rad)")
        plt.title(f"Direction mismatch - {model_name}")
        plt.legend()
        out = f"Data/DirMismatch_{model_name.replace(' ', '_')}.png"
        plt.tight_layout()
        plt.savefig(out, dpi=150)
        plt.close()


def simulation_init(params):
    import random
    env_params, swarm_params = params

    Path("Data").mkdir(parents=True, exist_ok=True)

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
