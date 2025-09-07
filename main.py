from Environment.SimEnv import SimEnv
from Utils.utils import setup_perser, simulation_init, read_from_file
from Model.CollectiveDecisionModel import MajorityRuleModel, VoterModel, KuramotoModel

#parameters
WIDTH = 900
HEIGHT = 500
NUM_AGENTS = 20
NUM_TARGET = 2
NUM_HURDLE = 10

# Defining the main function
def main():
    print('\n')
    print('%'*60)
    if args.newdata:
        is_new_data = True
        print('Simulation has been started with New Data')
    else:
        is_new_data = False
        print('Simulation has been started with Old Data')

    
    if is_new_data:
        simulation_init(WIDTH, HEIGHT, NUM_AGENTS, NUM_TARGET, NUM_HURDLE)
    
    data_list = read_from_file()
    agent_pos = [tuple(element) for element in data_list[0]]
    targets = [tuple(element) for element in data_list[1]]
    hurdles = [tuple(element) for element in data_list[2]] 
    simEnv = SimEnv(WIDTH, HEIGHT, NUM_AGENTS, NUM_TARGET, targets, NUM_HURDLE, hurdles)
    
    if args.majority:
        simEnv.model = MajorityRuleModel(agent_pos, NUM_TARGET, targets)
        print('Model Select : ', simEnv.model.Name)
    elif args.voter:
        simEnv.model = VoterModel(agent_pos)
        print('Model Select : ', simEnv.model.Name)
    elif args.kuramoto:
        simEnv.model = KuramotoModel(agent_pos)
        print('Model Select : ', simEnv.model.Name)
    else:
        print('No Model is selected')
        
    simEnv.run_simulation()
        
    simEnv.close_sim()
    
if __name__=="__main__":
    args = setup_perser()
    main()
