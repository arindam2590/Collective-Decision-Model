import pygame

from Environment.SimHurdle import Hurdle


class SimEnv:
    def __init__(self, params, targets, FULSCRN=False):
        pygame.init()
        self.env_params, self.swarm_params = params
        self.win_height, self.win_width = self.env_params['SCREEN_HEIGHT'], self.env_params['SCREEN_WIDTH']

        if FULSCRN:
            resol = (pygame.display.Info().current_w, pygame.display.Info().current_h)
            self.screen = pygame.display.set_mode(resol, pygame.SCALED)
        else:
            self.screen = pygame.display.set_mode((self.win_width, self.win_height), pygame.RESIZABLE)

        self.BGCOLOR = (255, 255, 255)
        self.clock = pygame.time.Clock()
        self.fps = self.env_params['FPS']
        self.running = True
        self.num_hurdles = self.env_params['NUM_HURDLE']
        self.hurdles = []
        self.num_targets = self.env_params['NUM_TARGET']
        self.target_object = targets
        self.target_size = self.env_params['TARGET_SIZE']
        self.model = None

    def event_on_game_window(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False

    def hurdle_movement(self, time_count):
        for hurdle in self.hurdles:
            hurdle.update_hurdle_position(time_count)

    def draw_targets(self, point):
        x, y = int(point[0]), int(point[1])
        pygame.draw.circle(self.screen, (0, 0, 255), (x, y), self.target_size)

    def render(self):
        for agent in self.model.agents:
            agent.display_agents(self.screen)

        for hurdle in self.hurdles:
            hurdle.draw_hurdles(self.screen)

        for target_point in self.target_object:
            self.draw_targets(target_point)

        pygame.display.flip()
        self.clock.tick(self.fps)

    def run_simulation(self, hurdles, targets):
        pygame.display.set_caption("Collective Decision Making of Swarm : " + self.model.Name)

        direction_mismatches = []
        metrics = [direction_mismatches]  # keep existing structure

        for x, y, amplitude, frequency in hurdles:
            self.hurdles.append(Hurdle(x, y, amplitude, frequency))

        print('=' * 60)
        print('Model Simulation has been started...\n')
        time_count = 1
        while self.running:
            self.event_on_game_window()
            self.screen.fill(self.BGCOLOR)
            self.hurdle_movement(time_count)
            _ = self.model.update(time_count, self.hurdles, metrics)
            self.render()
            time_count += 1

        # Keep current return format (list + final time_count)
        performance_data = [direction_mismatches]
        performance_data.append(time_count)
        return performance_data

    def close_sim(self):
        pygame.quit()
