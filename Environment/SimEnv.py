import pygame
import random

from Environment.SimHurdle import Hurdle

TARGET_SIZE = 40

class SimEnv:
    def __init__(self, WIDTH, HEIGHT,  n, n_targets, targets, n_hurdles, hurdles, FULSCRN=False):
        pygame.init()
        self.win_height, self.win_width = HEIGHT, WIDTH
        
        if FULSCRN:
            resol = (pygame.display.Info().current_w, pygame.display.Info().current_h)
            self.screen = pygame.display.set_mode(resol, pygame.SCALED)
        else: self.screen = pygame.display.set_mode((self.win_width, self.win_height), pygame.RESIZABLE)
        
        self.BGCOLOR = (255, 255, 255)
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.running = True
        
        self.num_agents = n
        self.num_targets = n_targets
        self.target_object = targets
        self.num_hurdles = n_hurdles
        self.hurdles = []
        for hurdle in hurdles:
            x, y, amplitude, frequency = hurdle
            self.hurdles.append(Hurdle(x, y, amplitude, frequency))
        self.model = None

    def event_on_game_window(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False   
        
    def draw_targets(self, point):
        x, y = point[0], point[1]
        pygame.draw.circle(self.screen, (0, 0, 255), (int(x), int(y)), TARGET_SIZE)
                
    def close_sim(self):
        pygame.quit()
    
    def hurdle_movement(self, time_count):
        for hurdle in self.hurdles:
            hurdle.update_hurdle_position(time_count)
            
    def run_simulation(self):
        pygame.display.set_caption("Collective Decision Making of Swarm : "+self.model.Name)
        time_count = 1
        
        print('='*60)
        print('Model Simulation has been started...\n')
        while self.running:
            self.event_on_game_window()
            
            self.screen.fill(self.BGCOLOR)
            self.hurdle_movement(time_count)
            self.model.update(time_count, self.target_object, self.hurdles, self.win_width, self.win_height)            

            self.render()
            time_count += 1
               
    def render(self):
        for agent in self.model.agents:
            agent.display_agents(self.screen)
        
        for target_point in self.target_object:
            self.draw_targets(target_point)
        
        for hurdle in self.hurdles:
            hurdle.draw_hurdles(self.screen)
            
        pygame.display.flip()
        self.clock.tick(self.fps)
