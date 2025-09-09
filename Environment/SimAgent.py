import pygame
import math
import numpy as np


class Agent:
    def __init__(self, pos, speed, bound_x, bound_y, inter_range, repul_rad, sep_dist, rad=10):
        self.position = np.array(pos)
        self.speed = speed
        self.direction = np.random.uniform(0, 2 * np.pi)
        self.neighbors = []
        self.interaction_radius = inter_range
        self.separation_distance = sep_dist
        self.repulsion_radius = repul_rad
        self.radius = rad
        self.color = (255, 0, 0)
        self.limit_x_bound, self.limit_y_bound = bound_x, bound_y

    def draw_agents(self, screen):
        pygame.draw.circle(screen, self.color, self.position, self.radius)

    def move(self, hurdles):
        self.position += self.speed * np.array([np.cos(self.direction), np.sin(self.direction)])
        self.compute_repulsion_force(hurdles)
        self.position = np.clip(self.position, 0, [self.limit_x_bound, self.limit_y_bound])

    def get_neighbors(self, agents):
        self.neighbors.clear()
        self_pos = np.expand_dims(self.position, axis=0)
        other_pos = np.array([agent.position for agent in agents])
        distances = np.linalg.norm(self_pos - other_pos, axis=1)
        self.neighbors.extend(
            [agent for agent, dist in zip(agents, distances) if dist <= self.interaction_radius and agent != self])

    def calculate_average_direction(self):
        if not self.neighbors:
            return np.zeros(2, dtype=float)
        neighbor_directions = np.array([agent.direction for agent in self.neighbors])
        avg_direction = np.mean(neighbor_directions, axis=0)

        direction = np.array([np.cos(avg_direction), np.sin(avg_direction)])
        self.consensus_direction = np.arctan2(direction[1], direction[0])

    def compute_opinion(self, targets):
        next_prob_pos = self.position
        next_prob_pos += self.speed * np.array([np.cos(self.consensus_direction), np.sin(self.consensus_direction)])
        targets = np.array(targets)

        distance_to_goal = np.linalg.norm(targets - self.position, axis=1)
        nearest_goal_index = np.argmin(distance_to_goal)
        self.nearest_goal = targets[nearest_goal_index]
        # print('Self : ',self.nearest_goal)

    def compute_alignment(self):
        if not self.neighbors:
            return np.zeros(2, dtype=float)  # No neighbors, return zero vector
        neighbor_directions = np.array([agent.direction for agent in self.neighbors])
        avg_direction = np.mean(neighbor_directions, axis=0)
        return (avg_direction - self.direction)

    def compute_cohesion(self, agents):
        agent_pos = np.array([agent.position for agent in agents])
        avg_position = np.mean(agent_pos, axis=0)
        return (avg_position - self.position)

    def compute_separation(self):
        if not self.neighbors:
            return np.zeros(2, dtype=float)
        neighbor_positions = np.array([agent.position for agent in self.neighbors])
        distances = np.linalg.norm(self.position - neighbor_positions, axis=1)
        too_close_mask = distances < self.separation_distance
        separation_vectors = (self.position - neighbor_positions[too_close_mask])
        return np.sum(separation_vectors, axis=0)

    def get_com_force(self, center_of_mass):
        com_diff = np.array(self.nearest_goal) - center_of_mass
        force_vector = com_diff * 0.04
        return force_vector

    def get_target_force(self):
        position_diff = np.array(self.nearest_goal) - self.position
        direction = np.arctan2(position_diff[1], position_diff[0])
        force_vector = 0.02 * (direction - self.direction)
        return force_vector

    def _move_towards(self, agents):
        agent_pos = np.array([agent.position for agent in agents])
        center_of_mass = np.mean(agent_pos, axis=0)
        com_force = self.get_com_force(center_of_mass)
        ind_force = self.get_target_force()
        target_force = com_force * 0.05 + ind_force * 0.03
        return target_force

    def update_direction(self, agents, swarm_params):
        if self.neighbors:
            alignment_force = self.compute_alignment() * swarm_params['ALIGNMENT_STRENGTH']
            cohesion_force = self.compute_cohesion(agents) * swarm_params['ATTRACT_STRENGTH']
            separation_force = self.compute_separation() * swarm_params['SEPERATION_STRENGTH']
            target_force = self._move_towards(agents)

            total_force = alignment_force + separation_force + cohesion_force + target_force
            self.direction = np.arctan2(total_force[1], total_force[0])
            self.is_latent = False
        else:
            target_force = self._move_towards(agents)
            self.direction = np.arctan2(target_force[1], target_force[0])
            self.is_latent = True

    def compute_repulsion_force(self, hurdles):
        for hurdle in hurdles:
            center_point = np.array([hurdle.x + hurdle.hurdle_width // 2, hurdle.y + hurdle.hurdle_height // 2])
            dx = center_point[0] - self.position[0]
            dy = center_point[1] - self.position[1]
            dist = np.sqrt(dx ** 2 + dy ** 2)
            if dist < self.repulsion_radius:
                repulsion_factor = (self.repulsion_radius - dist) / dist
                self.position[0] -= repulsion_factor * dx
                self.position[1] -= repulsion_factor * dy
