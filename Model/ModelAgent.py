import random
import numpy as np

from Environment.SimAgent import Agent


class MajorityAgent(Agent):
    def __init__(self, pos, is_latent, bound_x, bound_y, interaction_radius, repulsion_radius, sep_dist, speed, opn_count):
        super().__init__(pos, speed, bound_x-10, bound_y-10, interaction_radius, repulsion_radius, sep_dist)
        self.is_latent = is_latent
        self.consensus_direction = 0.0
        self.opinion_count = opn_count
        self.has_consensus = False
        self.nearest_goal = None

    def display_agents(self, screen):
        super().draw_agents(screen)

    def calculate_dir_mismatch(self):
        return abs(self.consensus_direction - self.direction)

    def count_opinion_occurance(self, targets):
        # Guard against neighbors with unknown goals
        for neighbor in self.neighbors:
            if neighbor.nearest_goal is None:
                continue
            goal = tuple(neighbor.nearest_goal)
            if goal not in self.opinion_count:
                self.opinion_count[goal] = 0
            self.opinion_count[goal] += 1

        if self.opinion_count:
            max_occurance = max(self.opinion_count, key=self.opinion_count.get)
            if self.nearest_goal is None or tuple(self.nearest_goal) != max_occurance:
                self.nearest_goal = np.array(max_occurance)


class VoterAgent(Agent):
    def __init__(self, pos, is_latent, targets, bound_x, bound_y, interaction_radius, repulsion_radius, sep_dist, speed):
        super().__init__(pos, speed, bound_x-10, bound_y-10, interaction_radius, repulsion_radius, sep_dist)
        self.is_latent = is_latent
        self.consensus_direction = 0.0
        self.nearest_goal = random.choice(targets)
        self.has_switched_opinion = False

    def display_agents(self, screen):
        super().draw_agents(screen)

    def switch_opinion(self):
        if self.neighbors:
            random_neighbor = random.choice(self.neighbors)
            if random_neighbor.nearest_goal is None:
                return
            if np.array_equal(self.nearest_goal, random_neighbor.nearest_goal):
                self.direction = self.consensus_direction
            else:
                self.nearest_goal = random_neighbor.nearest_goal
                self.direction = random_neighbor.consensus_direction
            self.has_switched_opinion = True


class KuramotoAgent(Agent):
    def __init__(self, pos, is_latent, bound_x, bound_y, interaction_radius, repulsion_radius, sep_dist, speed):
        super().__init__(pos, speed, bound_x-10, bound_y-10, interaction_radius, repulsion_radius, sep_dist)
        self.is_latent = is_latent
        self.omega = 0.0
        self.nearest_goal = None
        self.consensus_direction = 0.0
        self.has_phase_synched = True
        self.coupling_strength_K = 0.0

    def display_agents(self, screen):
        super().draw_agents(screen)

    def calculate_phase_difference(self):
        if self.neighbors:
            # Use agent's current K (grown by model each consensus phase)
            K = max(float(self.coupling_strength_K), 0.0)
            neighbor_directions = np.array([agent.direction for agent in self.neighbors])
            avg_phase_diff = K * np.mean(np.sin(neighbor_directions - self.direction), axis=0)
            agent_phase = self.omega + avg_phase_diff
            direction = np.array([np.cos(agent_phase), np.sin(agent_phase)])
            self.consensus_direction = np.arctan2(direction[1], direction[0])
            self.has_phase_synched = True

    def get_nearest_goal(self, targets):
        targets = np.array(targets)
        distance_to_goal = np.linalg.norm(targets - self.position, axis=1)
        nearest_goal_index = np.argmin(distance_to_goal)
        self.nearest_goal = targets[nearest_goal_index]
        direction = self.position - np.array(self.nearest_goal)
        self.omega = np.arctan2(direction[1], direction[0])
