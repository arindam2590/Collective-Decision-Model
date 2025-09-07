import argparse
import random
import json

FILE_NAME = 'data.txt'
STARTING_AREA_WIDTH = 100
STARTING_AREA_HEIGHT = 100

def setup_perser():
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
    									
    args = parser.parse_args()
    return args

def write_to_file(data):
    with open(FILE_NAME, 'w') as file:
        json.dump(data, file)

def read_from_file():
    with open(FILE_NAME, 'r') as file:
        data = json.load(file)
    return data
            
def simulation_init(WIDTH, HEIGHT, NUM_AGENTS, NUM_TARGET, NUM_HURDLE, TARGET_SIZE = 40):
    agent_init_pos = [(random.uniform(0, STARTING_AREA_WIDTH),
                       random.uniform(HEIGHT/3, HEIGHT*2/3)) for _ in range(NUM_AGENTS)]
                       
    targets = []
    for _ in range(NUM_TARGET):
        target_x = WIDTH - STARTING_AREA_WIDTH - TARGET_SIZE / 2
        target_y = random.uniform(50, HEIGHT-50)
        targets.append((target_x, target_y))
    
    hurdles = []
    for _ in range(NUM_HURDLE):
        hurdle_x = random.uniform(WIDTH/3, WIDTH*4/5)
        hurdle_y = random.uniform(0, HEIGHT-50)
        amplitude = random.choice([1, 2])
        frequency = random.uniform(0.0, 0.1)
        hurdles.append((hurdle_x, hurdle_y, amplitude, frequency))
         
    data_list =[agent_init_pos, targets, hurdles]
    write_to_file(data_list)
