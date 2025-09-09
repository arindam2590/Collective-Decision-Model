import argparse

def setup_parser():
    parser = argparse.ArgumentParser(description=None)
    parser.add_argument('-n', '--newdata',
                        action='store_true',
                        help='Start simulation with new data: use argument -n or --newdata')
    parser.add_argument('-o', '--olddata',
                        action='store_true',
                        help='Start simulation with old data: use argument -o or --olddata')
    parser.add_argument('-m', '--majority',
                        action='store_true',
                        help='Simulate the environment with Majority Rule Model: use argument -m or --majority')
    parser.add_argument('-v', '--voter',
                        action='store_true',
                        help='Simulate the environment with Voter Model: use argument -v or --voter')
    parser.add_argument('-k', '--kuramoto',
                        action='store_true',
                        help='Simulate the environment with Kuramoto Model: use argument -k or --kuramoto')
    return parser.parse_args()

# Backward-compatible alias (so main.py keeps working without edits)
def setup_perser():
    return setup_parser()


def set_params():
    env_params = {
        'FULSCRN': False,
        'SCREEN_WIDTH': 1200,
        'SCREEN_HEIGHT': 700,
        'FPS': 60,
        'NUM_TARGET': 2,
        'TARGET_SIZE': 20,
        'NUM_HURDLE': 10
    }

    swarm_params = {
        'NUM_AGENTS': 10,
        'START_AREA_LEN': 20,
        'STARTING_AREA_WIDTH': 20,
        'INTERACTION_RADIUS': 30,
        'CONSENSUS_PERIOD': 10,
        'AGENT_SPEED': 1.0,
        'SEPERATION_DISTANCE': 25,
        'SEPERATION_STRENGTH': 0.17,
        'ALIGNMENT_STRENGTH': 0.1,
        'ATTRACT_STRENGTH': 0.02,
        'REPULSION_RADIUS': 50,
        'K_INCREMENT': 0.01
    }

    return [env_params, swarm_params]
