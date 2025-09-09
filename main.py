import random
import numpy as np

from Environment.SimEnv import SimEnv
from Utils.config import setup_parser, set_params
from Utils.utils import display_simulation_config, simulation_init, read_from_file, plot_performance_graph
from Model.CollectiveDecisionModel import MajorityRuleModel, VoterModel, KuramotoModel


def main():
    args = setup_parser()
    params = set_params()
    env_params, swarm_params = params

    # apply CLI overrides
    env_params['FPS'] = args.fps
    env_params['FULSCRN'] = bool(args.fullscreen)

    # seeding for reproducibility
    random.seed(args.seed)
    np.random.seed(args.seed)

    print('\n' + '%' * 60)
    is_new_data = bool(args.newdata)
    print('Simulation has been started with {} Data'.format('New' if is_new_data else 'Old'))

    display_simulation_config(params)
    if is_new_data:
        simulation_init(params)

    # load starting data
    data_list = read_from_file()
    agent_pos = [tuple(element) for element in data_list[0]]
    targets = [tuple(element) for element in data_list[1]]
    hurdles = [tuple(element) for element in data_list[2]]

    simEnv = SimEnv(params, targets, FULSCRN=env_params['FULSCRN'])

    if args.majority:
        simEnv.model = MajorityRuleModel(agent_pos, targets, params)
    elif args.voter:
        simEnv.model = VoterModel(agent_pos, targets, params)
    elif args.kuramoto:
        simEnv.model = KuramotoModel(agent_pos, targets, params)
    else:
        raise SystemExit("No model selected. Use one of -m / -v / -k.")

    print('Model Select :', simEnv.model.Name)

    metrics = simEnv.run_simulation(hurdles, targets, max_steps=args.max_steps)

    plot_performance_graph(simEnv.model.Name, metrics)

    simEnv.close_sim()


if __name__ == "__main__":
    main()
