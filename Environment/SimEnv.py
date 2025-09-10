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

        # NEW: per-timestep count of agents that reached any target (for plotting/saving)
        self.reached_counts = []

    def event_on_game_window(self):
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

        pygame.display.flip()
        self.clock.tick(self.fps)

    def _count_agents_reached_any_target(self):
        """Return number of agents whose position lies inside any target (within target radius)."""
        r = float(self.target_size)
        r2 = r * r
        cnt = 0
        for a in self.model.agents:
            ax, ay = a.position
            # inside ANY target
            for tx, ty in self.target_object:
                dx = ax - tx
                dy = ay - ty
                if dx * dx + dy * dy <= r2:
                    cnt += 1
                    break
        return cnt

    def run_simulation(self, hurdles, targets, max_steps=0):
        pygame.display.set_caption("Collective Decision Making of Swarm : " + self.model.Name)

        # Metrics (models will append into these)
        direction_mismatches = []
        collisions = []
        phase_synchronization = []
        decision_accuracy = []  # left as-is for compatibility elsewhere

        if self.model.Name == 'Kuramoto Model':
            metrics = [direction_mismatches, collisions, phase_synchronization, decision_accuracy]
        else:
            metrics = [direction_mismatches, collisions, decision_accuracy]

        # Build hurdles for this run
        self.hurdles = []
        for x, y, amplitude, frequency in hurdles:
            self.hurdles.append(Hurdle(x, y, amplitude, frequency))

        # reset per-timestep reached series
        self.reached_counts = []

        time_count = 1
        while self.running:
            if max_steps and time_count > max_steps:
                break
            self.event_on_game_window()
            self.screen.fill(self.BGCOLOR)
            self.hurdle_movement(time_count)

            # Model updates and writes into metrics
            performance_data = self.model.update(time_count, self.hurdles, metrics)

            # NEW: record per-timestep #agents that reached ANY target
            self.reached_counts.append(self._count_agents_reached_any_target())

            self.render()
            time_count += 1

        # Keep return shape unchanged; append time_count at the end
        performance_data.append(time_count)
        return performance_data

    def close_sim(self):
        pygame.quit()
