# Environment/SimEnv.py
import pygame
from Environment.SimHurdle import Hurdle

class SimEnv:
    def __init__(self, params, targets, render=True, FULSCRN=False):  # NEW: render flag
        self.render_enabled = render                                   # NEW
        pygame.init()

        self.env_params, self.swarm_params = params
        self.win_height, self.win_width = self.env_params['SCREEN_HEIGHT'], self.env_params['SCREEN_WIDTH']

        if self.render_enabled:
            if FULSCRN:
                resol = (pygame.display.Info().current_w, pygame.display.Info().current_h)
                self.screen = pygame.display.set_mode(resol, pygame.SCALED)
            else:
                self.screen = pygame.display.set_mode((self.win_width, self.win_height), pygame.RESIZABLE)
        else:
            # Headless: draw onto an offscreen Surface (no window)
            self.screen = pygame.Surface((self.win_width, self.win_height))

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
        if not self.render_enabled:
            return  # no event pump needed when headless
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
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

        if self.render_enabled:
            pygame.display.flip()
        self.clock.tick(self.fps)

    # Environment/SimEnv.py

    def run_simulation(self, hurdles, targets, max_steps=0):
        import pygame
        from Environment.SimHurdle import Hurdle

        # (Title only matters if you’re rendering)
        try:
            pygame.display.set_caption("Collective Decision Making of Swarm : " + self.model.Name)
        except Exception:
            pass

        direction_mismatches = []
        performance_data = []
        metrics = [direction_mismatches]

        # (Re)build hurdles list
        self.hurdles = []
        for x, y, amplitude, frequency in hurdles:
            self.hurdles.append(Hurdle(x, y, amplitude, frequency))

        time_count = 1
        while self.running:
            # Respect max_steps if provided (>0)
            if max_steps and time_count > max_steps:
                break

            self.event_on_game_window()
            self.screen.fill(self.BGCOLOR)
            self.hurdle_movement(time_count)

            # Your model returns performance_data in the same shape as before
            performance_data = self.model.update(time_count, self.hurdles, metrics)

            self.render()
            time_count += 1

        performance_data.append(time_count)
        return performance_data

    def close_sim(self):
        pygame.quit()
