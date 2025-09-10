import argparse

def setup_perser():
    parser = argparse.ArgumentParser(description=None)
    parser.add_argument('-n', '--newdata', action='store_true', help='Start simulation with new data')
    parser.add_argument('-o', '--olddata', action='store_true', help='Start simulation with old data')

    # Model picks (single run)
    parser.add_argument('-m', '--majority', action='store_true', help='Use Majority Rule Model')
    parser.add_argument('-v', '--voter',    action='store_true', help='Use Voter Model')
    parser.add_argument('-k', '--kuramoto', action='store_true', help='Use Kuramoto Model')

    # Step cap
    parser.add_argument('-t', '--max-steps', type=int, default=0,
                        help='Maximum number of time steps (0 = until window closes)')

    # Batch + CSV
    parser.add_argument('--batch', action='store_true',
                        help='Run sweep: agents {10,20,30,40} × targets {2,10} × all models; save to CSV')
    parser.add_argument('--csv-out', default='Data/sweep_results.csv',
                        help='CSV path to write when using --batch')

    # Plot-only from CSV
    parser.add_argument('--plot-only', action='store_true',
                        help='Build direction-mismatch figures from CSV (no simulation)')
    parser.add_argument('--csv-in', default='Data/sweep_results.csv',
                        help='CSV path to read with --plot-only/--plot-collision')

    # NEW: plot collision figures from CSV
    parser.add_argument('--plot-collision', action='store_true',
                        help='Build collision figures from CSV (no simulation)')

    return parser.parse_args()


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
