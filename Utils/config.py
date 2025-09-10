import argparse

def setup_perser():
    parser = argparse.ArgumentParser(description=None)
    parser.add_argument('-n', '--newdata', action='store_true', help='Start simulation with new data')
    parser.add_argument('-o', '--olddata', action='store_true', help='Start simulation with old data')

    # choose exactly one model (-m/-v/-k), same names you already use
    parser.add_argument('-m', '--majority', action='store_true', help='Use Majority Rule Model')
    parser.add_argument('-v', '--voter',    action='store_true', help='Use Voter Model')
    parser.add_argument('-k', '--kuramoto', action='store_true', help='Use Kuramoto Model')

    # cap steps per run (SimEnv already supports max_steps)
    parser.add_argument('-t', '--max-steps', type=int, default=0,
                        help='Maximum number of time steps (0 = until window closes)')

    # BATCH & PLOT-ONLY
    parser.add_argument('--batch', action='store_true',
                        help='Run sweep for agents {10,20,30,40} × targets {2,10} for all models; save to CSV')
    parser.add_argument('--csv-out', default='Data/sweep_results.csv',
                        help='CSV path to write when using --batch')
    parser.add_argument('--plot-only', action='store_true',
                        help='Only build figures from CSV (no simulation)')
    parser.add_argument('--csv-in', default='Data/sweep_results.csv',
                        help='CSV path to read with --plot-only')

    # rendering toggle (single runs); batch will force headless
    render_group = parser.add_mutually_exclusive_group()
    render_group.add_argument('--render',   dest='render', action='store_true',  help='Enable windowed rendering')
    render_group.add_argument('--headless', dest='render', action='store_false', help='Disable rendering (dummy SDL)')
    parser.set_defaults(render=True)

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
