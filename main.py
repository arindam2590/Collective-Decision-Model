from Environment.SimEnv import SimEnv
from Utils.config import setup_perser, set_params
from Utils.utils import display_simulation_config, simulation_init, read_from_file, plot_performance_graph
from Model.CollectiveDecisionModel import MajorityRuleModel, VoterModel, KuramotoModel


# Defining the main function
def main():
    params = set_params()

    print('\n')
    print('%' * 60)
    if args.newdata:
        is_new_data = True
        print('Simulation has been started with New Data')
    else:
        is_new_data = False
        print('Simulation has been started with Old Data')

    display_simulation_config(params)
    if is_new_data:
        simulation_init(params)

    data_list = read_from_file()
    agent_pos = [tuple(element) for element in data_list[0]]
    targets = [tuple(element) for element in data_list[1]]
    hurdles = [tuple(element) for element in data_list[2]]

    simEnv = SimEnv(params, targets)
    if args.majority:
        simEnv.model = MajorityRuleModel(agent_pos, targets, params)
        print('Model Select :', simEnv.model.Name)
    elif args.voter:
        simEnv.model = VoterModel(agent_pos, targets, params)
        print('Model Select : ', simEnv.model.Name)
    elif args.kuramoto:
        simEnv.model = KuramotoModel(agent_pos, targets, params)
        print('Model Select : ', simEnv.model.Name)
    else:
        print('No Model is selected')

    performance_data = simEnv.run_simulation(hurdles, targets, max_steps=args.max_steps)

    plot_performance_graph(simEnv.model.Name, performance_data, params)

    simEnv.close_sim()


if __name__ == "__main__":
    args = setup_perser()
    main()
