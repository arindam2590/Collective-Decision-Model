import argparse

def setup_perser():
    parser = argparse.ArgumentParser(description=None)
    parser.add_argument('-n', '--newdata',
                        action='store_true',
                        help='Start simulation with new data')
    parser.add_argument('-o', '--olddata',
                        action='store_true',
                        help='Start simulation with old data')
    parser.add_argument('-m', '--majority',
                        action='store_true',
                        help='Use Majority Rule Model')
    parser.add_argument('-v', '--voter',
                        action='store_true',
                        help='Use Voter Model')
    parser.add_argument('-k', '--kuramoto',
                        action='store_true',
                        help='Use Kuramoto Model')
    parser.add_argument('-t', '--max-steps',
                        type=int,
                        default=0,
                        help='Maximum number of time steps to run (0 = run until window closed)')
    return parser.parse_args()

# Backward-compatible alias (so main.py keeps working without edits)


def set_params():
    env_params = {
        'FULSCRN': False,
        'SCREEN_WIDTH': 1200,
        'SCREEN_HEIGHT': 900,
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
