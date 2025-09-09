import argparse

def setup_parser():
    p = argparse.ArgumentParser(description="Collective decision-making simulation")
    data = p.add_mutually_exclusive_group()
    data.add_argument('-n', '--newdata', action='store_true', help='Generate new randomized start data')
    data.add_argument('-o', '--olddata', action='store_true', help='Use saved data (default)')

    model = p.add_mutually_exclusive_group(required=True)
    model.add_argument('-m', '--majority', action='store_true', help='Run Majority Rule model')
    model.add_argument('-v', '--voter', action='store_true', help='Run Voter model')
    model.add_argument('-k', '--kuramoto', action='store_true', help='Run Kuramoto model')

    p.add_argument('--seed', type=int, default=42, help='Random seed')
    p.add_argument('--max-steps', type=int, default=3000, help='Max steps before auto-quit')
    p.add_argument('--fps', type=int, default=60, help='Frames per second')
    p.add_argument('--fullscreen', action='store_true', help='Fullscreen mode')
    return p.parse_args()


def set_params():
    env_params = {
        'FULSCRN' : False,
        'SCREEN_WIDTH' : 1200,
        'SCREEN_HEIGHT' : 700,
        'FPS' : 60,
        'NUM_TARGET' : 2,
        'TARGET_SIZE' : 20,
        'NUM_HURDLE' : 10
    }

    swarm_params = {
        'NUM_AGENTS' : 10,
        'START_AREA_LEN' : 20,
        'STARTING_AREA_WIDTH' : 20,
        'INTERACTION_RADIUS' : 30,
        'CONSENSUS_PERIOD' : 10,
        'AGENT_SPEED' : 1.0,
        'SEPERATION_DISTANCE' : 25,
        'SEPERATION_STRENGTH' : 0.17,
        'ALIGNMENT_STRENGTH' : 0.08,
        'ATTRACT_STRENGTH' : 0.002,
        'REPULSION_RADIUS' : 50,
        'K_INCREMENT' : 0.01
    }

    return [env_params, swarm_params]
