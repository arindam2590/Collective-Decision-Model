import pygame
import numpy as np


def circ_mean(angles):
    s = np.sin(angles).mean()
    c = np.cos(angles).mean()
    return np.arctan2(s, c)


def angle_diff(a, b):
    d = (a - b + np.pi) % (2 * np.pi) - np.pi
    return d


class Agent:
    def __init__(self, pos, speed, bound_x, bound_y, inter_range, repul_rad, sep_dist, rad=10):
        self.position = np.array(pos, dtype=float)
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
        pygame.draw.circle(screen, self.color, self.position.astype(int), int(self.radius))

    def move(self, hurdles):
        self.position += self.speed * np.array([np.cos(self.direction), np.sin(self.direction)])
        self.compute_repulsion_force(hurdles)
        self.position = np.clip(self.position, [0, 0], [self.limit_x_bound, self.limit_y_bound])

    def get_neighbors(self, agents):
        self.neighbors.clear()
        self_pos = np.expand_dims(self.position, axis=0)
        other_pos = np.array([agent.position for agent in agents])
        distances = np.linalg.norm(self_pos - other_pos, axis=1)
        self.neighbors.extend(
            [agent for agent, dist in zip(agents, distances) if dist <= self.interaction_radius and agent is not self]
        )

    def calculate_average_direction(self):
        if not self.neighbors:
            return
        neighbor_directions = np.array([agent.direction for agent in self.neighbors])
        avg_direction = circ_mean(neighbor_directions)
        # store as an angle
        self.consensus_direction = avg_direction

    def compute_opinion(self, targets):
        targets = np.array(targets)
        distance_to_goal = np.linalg.norm(targets - self.position, axis=1)
        nearest_goal_index = np.argmin(distance_to_goal)
        self.nearest_goal = targets[nearest_goal_index]

    def compute_alignment(self):
        if not self.neighbors:
            return 0.0
        neighbor_directions = np.array([agent.direction for agent in self.neighbors])
        avg_direction = circ_mean(neighbor_directions)
        return angle_diff(avg_direction, self.direction)

    def compute_cohesion(self, agents):
        agent_pos = np.array([agent.position for agent in agents])
        avg_position = np.mean(agent_pos, axis=0)
        return (avg_position - self.position)

    def compute_separation(self):
        if not self.neighbors:
            return np.zeros(2, dtype=float)
        neighbor_positions = np.array([agent.position for agent in self.neighbors])
        deltas = self.position - neighbor_positions
        distances = np.linalg.norm(deltas, axis=1)
        mask = distances < self.separation_distance
        if not mask.any():
            return np.zeros(2, dtype=float)
        # Avoid division by zero
        safe_dist = np.maximum(distances[mask], 1e-6)
        sep_vecs = (deltas[mask].T / safe_dist).T
        return np.sum(sep_vecs, axis=0)

    def get_com_force(self, center_of_mass):
        com_diff = np.array(self.nearest_goal) - center_of_mass
        force_vector = com_diff * 0.04
        return force_vector

    def get_target_force(self):
        position_diff = np.array(self.nearest_goal) - self.position
        direction = np.arctan2(position_diff[1], position_diff[0])
        force_vector = 0.02 * angle_diff(direction, self.direction)
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

            # Convert scalar alignment to a unit vector toward + angle
            align_vec = np.array([np.cos(self.direction + alignment_force), np.sin(self.direction + alignment_force)])
            total_force = align_vec + separation_force + cohesion_force + target_force
            self.direction = np.arctan2(total_force[1], total_force[0])
            self.is_latent = False
        else:
            target_force = self._move_towards(agents)
            self.direction = np.arctan2(target_force[1], target_force[0])
            self.is_latent = True

    def compute_repulsion_force(self, hurdles):
        for hurdle in hurdles:
            center_point = np.array([hurdle.x + hurdle.hurdle_width // 2, hurdle.y + hurdle.hurdle_height // 2], dtype=float)
            delta = center_point - self.position
            dist = np.hypot(delta[0], delta[1])
            if dist <= 0:
                continue
            if dist < self.repulsion_radius:
                repulsion_factor = (self.repulsion_radius - dist) / max(dist, 1e-6)
                self.position -= repulsion_factor * delta
