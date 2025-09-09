import random
import json
import matplotlib.pyplot as plt

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


def write_to_file(data):
    with open(FILE_NAME, 'w') as file:
        json.dump(data, file)


def read_from_file():
    with open(FILE_NAME, 'r') as file:
        data = json.load(file)
    return data


def plot_performance_graph(model_name, performance_data):
    time_steps, direction_mismatches, collision_values, obstacle_navigation_values, _ = performance_data
    direction_mismatches, steps = performance_data
    # time_count = [i for i in range(len(collision_values))]
    # time_steps = [i for i in range(1, steps+1, 10)]
    # print(len(time_steps))
    # print(direction_mismatches)
    # Plot the Direction Mismatch graph
    # filename = 'Data/DirectionMismatch_' + model_name
    # for i in range(1, len(direction_mismatches)+1):
    # plt.plot(time_steps, direction_mismatches[i])
    # plt.xlabel('Time')
    # plt.ylabel('Direction Mismatch')
    # plt.title('Direction Mismatch of Agents Over Time')
    # plt.savefig(filename)
    # plt.clf()

    # Plot the Collision Avoidance graph
    # filename = 'Data/CollisionAvoidance_' + model_name
    # plt.plot(time_count, collision_values)
    # plt.xlabel('Time')
    # plt.ylabel('Collision Avoidance')
    # plt.title('Collision Avoidance of Agents Over Time')
    # plt.savefig(filename)
    # plt.clf()

    # Plot the Obstacle Navigation graph
    # filename = 'Data/ObstacleNavigation_' + model_name
    # plt.plot(time_count, obstacle_navigation_values)
    # plt.xlabel('Time Step')
    # plt.ylabel('Obstacle Navigation')
    # plt.title('Obstacle Navigation of Agents Over Time')
    # plt.savefig(filename)
    # plt.clf()

    consensus_decision_accuracy = performance_data

    # Plot the Consensus Decision graph
    filename = 'Data/ConsensusDecision_' + model_name
    plt.plot(time_steps, consensus_decision_accuracy, label='Consensus Decision Accuracy')
    target1_data = [item[0] for item in consensus_decision_accuracy]
    target2_data = [item[1] for item in consensus_decision_accuracy]
    plt.plot(time_steps, target1_data, label='Target1')
    plt.plot(time_steps, target2_data, label='Target2')
    plt.xlabel('Time Step')
    plt.ylabel('Agents')
    plt.title('Consensus Decision Making Over Time')
    plt.legend()
    plt.savefig(filename)


def simulation_init(params):
    env_params, swarm_params = params

    agent_init_pos = [(random.uniform(0, swarm_params['START_AREA_LEN']),
                       random.uniform(env_params['SCREEN_HEIGHT'] / 3,
                                      env_params['SCREEN_HEIGHT'] / 3 + swarm_params['START_AREA_LEN']))
                      for _ in range(swarm_params['NUM_AGENTS'])]

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
