import pygame
import random
import math
import numpy as np

from Environment.SimAgent import Agent

INTERACTION_RADIUS = 30
CONSENSUS_PERIOD = 100
AGENT_SPEED = 1.0
NEIGHBOR_RADIUS = 25
REPULSION_RADIUS = 2 * NEIGHBOR_RADIUS
REPULSION_STRENGTH = 0.5
ALIGNMENT_STRENGTH = 0.9
ATTRACT_STRENGTH = 0.8

LATENT_AGENT_COLOR = (255, 0, 0)  # Red color for latent agents
NON_LATENT_AGENT_COLOR = (0, 255, 255)  # Blue color for non-latent agents
OMEGA_RANGE = (2, 8)  # Range of natural frequencies
K = 0.1    # Coupling strength
 
class MajorityAgent(Agent):
    def __init__(self, x, y, start_direction, is_latent, n_targets, targets):
        super().__init__(x, y)
        self.direction = start_direction
        self.is_latent = is_latent
        self.has_consensus = False
        self.reached_goal = False
        self.neighbors = []
        self.consensus_direction = 0.0
        self.nearest_goal = None
        self.next_prob_pos = None
        self.opinion_count = {target: 0 for target in targets}
    
    def move(self):
        if self.nearest_goal:
            dx = self.nearest_goal[0] - self.x
            dy = self.nearest_goal[1] - self.y
            distance_to_goal = math.hypot(dx, dy)
            
            if distance_to_goal > 0:
                self.x += dx / distance_to_goal * AGENT_SPEED
                self.y += dy / distance_to_goal * AGENT_SPEED
            else:
                self.reached_goal = True
                
        if not self.reached_goal:
            self.x += math.cos(self.direction) * AGENT_SPEED
            self.y += math.sin(self.direction) * AGENT_SPEED
                
    def update_direction(self, hurdles):
        if len(self.neighbors)>0:
            # Compute forces acting on the agent from its neighbors
            repulsion_x, repulsion_y = 0, 0
            alignment_x, alignment_y = 0, 0
            attract_x, attract_y = 0, 0
            
            for neighbor in self.neighbors:
                dx = neighbor.x - self.x
                dy = neighbor.y - self.y
                dist = math.sqrt(dx ** 2 + dy ** 2)
                
                if dist < NEIGHBOR_RADIUS:
                    repulsion_x += (NEIGHBOR_RADIUS - dx) / dx
                    repulsion_y += (NEIGHBOR_RADIUS - dy) / dy
                else:
                    attract_x += dx
                    attract_y += dy
                    
                alignment_x += math.cos(neighbor.direction)
                alignment_y += math.sin(neighbor.direction)

            # Compute the new direction based on the forces
            repulsion_force = REPULSION_STRENGTH * math.atan2(repulsion_y, repulsion_x)
            attraction_force = ATTRACT_STRENGTH * math.atan2(attract_y, attract_x)
            alignment_force = ALIGNMENT_STRENGTH * math.atan2(alignment_y, alignment_x)
            
            self.direction += attraction_force + alignment_force - repulsion_force
            self.is_latent = False
        else:
            self.is_latent = True  # Latent agent doesn't have any neighbors to make decision
            
        # Apply collision avoidance with hurdles
        for hurdle in hurdles:
            dx = hurdle.x - self.x
            dy = hurdle.y - self.y
            dist = math.sqrt(dx ** 2 + dy ** 2)
            
            if dist < REPULSION_RADIUS:
                repulsion_force = (REPULSION_RADIUS - dist) / dist
                self.x -= repulsion_force * dx
                self.y -= repulsion_force * dy
            
    def get_neighbors(self, agents):
        for neighbour_agent in agents:
            if neighbour_agent != self:
                dist = math.sqrt((neighbour_agent.x - self.x) ** 2 + (neighbour_agent.y - self.y) ** 2)
                if dist <= INTERACTION_RADIUS:
                    self.neighbors.append(neighbour_agent)
        
    def calculate_average_direction(self):
        if not self.neighbors:
            return None
            
        total_direction_x, total_direction_y = 0, 0
        for neighbor in self.neighbors:
            total_direction_x += math.cos(neighbor.direction)
            total_direction_y += math.sin(neighbor.direction)
            
        self.consensus_direction = math.atan2(total_direction_y, total_direction_x)
    
    def find_nearest_goal(self, targets):
        self.next_prob_pos = np.array((self.x, self.y))
        self.next_prob_pos[0] += math.cos(self.consensus_direction) * AGENT_SPEED
        self.next_prob_pos[1] += math.sin(self.consensus_direction) * AGENT_SPEED
        
        nearest_goal_distance = float('inf')
        for target in targets:
            distance_to_goal = math.hypot(target[0] - self.x, target[1] - self.y) # Euclidean norm
            if distance_to_goal < nearest_goal_distance:
                nearest_goal_distance = distance_to_goal
                self.nearest_goal = target
            
    def neighbors_opinion(self, targets):
        for neighbor in self.neighbors:
            neighbor.find_nearest_goal(targets)
    
    def count_opinion_occurance(self):
        for neighbor in self.neighbors:
            goal = neighbor.nearest_goal
            self.opinion_count[goal] += 1
        # Get the key with the maximum value
        max_occurance = max(self.opinion_count, key=self.opinion_count.get)
        self.nearest_goal = max_occurance        
            
    def display_agents(self, screen):
        super().draw_agents(screen)
        
class MajorityRuleModel:
    def __init__(self, agent_pos, NUM_TARGET, targets):
        self.Name = 'Majority Model'
        self.agents = []
        for pos in agent_pos:
            x, y = pos[0], pos[1]
            start_direction = random.uniform(0, 2 * math.pi)
            is_latent = random.choice([True, False])
            self.agents.append(MajorityAgent(x, y, start_direction, is_latent, NUM_TARGET, targets)) 
    
    def update(self, time_count, targets, hurdles, WIDTH, HEIGHT):
        for agent in self.agents:
            agent.neighbors = []
            agent.get_neighbors(self.agents)
        
        if time_count % CONSENSUS_PERIOD == 0:  # Perform consensus phase every CONSENSUS_PERIOD frames
            print('Model has been updated at time: ',time_count)
            print('Info: Opinion occurance is being counted by agents')
            
            for agent in self.agents:
                agent.calculate_average_direction()
                if agent.consensus_direction is not None:
                    agent.neighbors_opinion(targets)
                    agent.count_opinion_occurance()
                    agent.direction = agent.consensus_direction
                    agent.has_consensus = True
            
            print('Info: Majority opinion has been selected by the agents')
            print('='*60)
        
        for agent in self.agents:            
            if agent.has_consensus:
                agent.update_direction(hurdles)
                agent.move()
            
            if agent.is_latent and agent.has_consensus:
                agent.color = NON_LATENT_AGENT_COLOR
            else:
                agent.color = LATENT_AGENT_COLOR

class VoterAgent(Agent):
    def __init__(self, x, y, start_direction, is_latent):
        super().__init__(x, y)
        self.direction = start_direction
        self.is_latent = is_latent
        self.reached_goal = False
        self.has_switch_opinion = False
        self.neighbors = []
        self.consensus_direction = 0.0
        self.nearest_goal_opinion = None        
    
    def move(self):
        if self.nearest_goal_opinion:
            dx = self.nearest_goal_opinion[0] - self.x
            dy = self.nearest_goal_opinion[1] - self.y
            distance_to_goal = math.hypot(dx, dy)
            
            if distance_to_goal > 0:
                self.x += dx / distance_to_goal * AGENT_SPEED
                self.y += dy / distance_to_goal * AGENT_SPEED
            else:
                self.reached_goal = True
        
        if not self.reached_goal:
            self.x += math.cos(self.direction) * AGENT_SPEED
            self.y += math.sin(self.direction) * AGENT_SPEED
        
    def get_neighbors(self, agents):
        for neighbour_agent in agents:
            if neighbour_agent != self:
                dist = math.sqrt((neighbour_agent.x - self.x) ** 2 + (neighbour_agent.y - self.y) ** 2)
                if dist <= INTERACTION_RADIUS:
                    self.neighbors.append(neighbour_agent)
    
    def update_direction(self, hurdles):
        # Compute forces acting on the agent from its neighbors
        repulsion_x, repulsion_y = 0, 0
        alignment_x, alignment_y = 0, 0
        attract_x, attract_y = 0, 0
            
        if len(self.neighbors)>0:
            for neighbor in self.neighbors:
                dx = neighbor.x - self.x
                dy = neighbor.y - self.y
                dist = math.sqrt(dx ** 2 + dy ** 2)
                
                if dist < NEIGHBOR_RADIUS:
                    repulsion_x += (NEIGHBOR_RADIUS - dx) / dx
                    repulsion_y += (NEIGHBOR_RADIUS - dy) / dy
                else:
                    attract_x += dx
                    attract_y += dy
                    
                alignment_x += math.cos(neighbor.direction)
                alignment_y += math.sin(neighbor.direction)
                
            # Compute the new direction based on the forces
            repulsion_force = REPULSION_STRENGTH * math.atan2(repulsion_y, repulsion_x)
            attraction_force = ATTRACT_STRENGTH * math.atan2(attract_y, attract_x)
            alignment_force = ALIGNMENT_STRENGTH * math.atan2(alignment_y, alignment_x)
            
            self.direction += attraction_force + alignment_force - repulsion_force
        # Apply collision avoidance with hurdles
        for hurdle in hurdles:
            dx = hurdle.x - self.x
            dy = hurdle.y - self.y
            dist = math.sqrt(dx ** 2 + dy ** 2)
            
            if dist < REPULSION_RADIUS:
                repulsion_force = (REPULSION_RADIUS - dist) / dist
                self.x -= repulsion_force * dx
                self.y -= repulsion_force * dy
                
    def calculate_average_direction(self):
        if not self.neighbors:
            return None
            
        total_direction_x, total_direction_y = 0, 0
        for neighbor in self.neighbors:
            total_direction_x += math.cos(neighbor.direction)
            total_direction_y += math.sin(neighbor.direction)
            
        self.consensus_direction = math.atan2(total_direction_y, total_direction_x)
        
    def switch_opinion(self):
        if len(self.neighbors)>0:
            random_neighbor = random.choice(self.neighbors)
            self.nearest_goal_opinion = random_neighbor.nearest_goal_opinion
            self.is_latent = False
        else:
            self.is_latent = True
            
    def compute_opinion(self, targets):
        self.next_prob_pos = np.array((self.x, self.y))
        self.next_prob_pos[0] += math.cos(self.consensus_direction) * AGENT_SPEED
        self.next_prob_pos[1] += math.sin(self.consensus_direction) * AGENT_SPEED
        
        nearest_goal_distance = float('inf')
        for target in targets:
            distance_to_goal = math.hypot(target[0] - self.x, target[1] - self.y) # Euclidean norm
            if distance_to_goal < nearest_goal_distance:
               nearest_goal_distance = distance_to_goal
               self.nearest_goal_opinion = target
                
    def display_agents(self, screen):
        super().draw_agents(screen)
                                                 
class VoterModel:
    def __init__(self, agent_pos):
        self.Name = 'Voter Model'
        self.agents = []
        for pos in agent_pos:
            x, y = pos[0], pos[1]
            start_direction = random.uniform(0, 2 * math.pi)
            is_latent = random.choice([True, False])
            self.agents.append(VoterAgent(x, y, start_direction, is_latent))
            
    def update(self, time_count, targets, hurdles, WIDTH, HEIGHT):
        for agent in self.agents:
            agent.neighbors = []
            agent.get_neighbors(self.agents)
            
        if time_count % CONSENSUS_PERIOD == 0:  # Perform consensus phase every CONSENSUS_PERIOD frames
            print('Model has been updated at time: ',time_count)
            print('Info: Randomly select a neighbor agent to switch the Opinion')
            
            for agent in self.agents:
                agent.calculate_average_direction()
                if agent.consensus_direction is not None:
                    agent.compute_opinion(targets) # Calculate nearest goal based on the consensus direction
                    agent.switch_opinion() # Switch opinion with the randomly selected neighbor
                    agent.direction = agent.consensus_direction
                    agent.has_switch_opinion = True
            print('Info: Opinion has been switched with the randomly selected neighbor agents')
            print('='*60)
            
        for agent in self.agents:
            if agent.has_switch_opinion:
                agent.update_direction(hurdles)
                agent.move()
                
            if agent.is_latent and agent.has_switch_opinion:
                agent.color = NON_LATENT_AGENT_COLOR
            else:
                agent.color = LATENT_AGENT_COLOR

class KuramotoAgent(Agent):
    def __init__(self, x, y, phase, omega, start_direction, is_latent):
        super().__init__(x, y)
        self.phase = phase
        self.omega = omega
        self.direction = start_direction
        #self.is_latent = is_latent
        self.reached_goal = False
        #self.has_switch_opinion = False
        self.neighbors = []
        #self.consensus_direction = 0.0
        #self.nearest_goal_opinion = None

    def move(self, targets):
        dt = 0.01
        cursor_position = random.choice(targets)
        steering_force = pygame.Vector2(cursor_position) - pygame.Vector2(self.x, self.y)
        steering_force = steering_force.normalize()
        
        self.x += (AGENT_SPEED * math.cos(self.phase) + steering_force.x) * dt
        self.y += (AGENT_SPEED * math.sin(self.phase) + steering_force.y) * dt
        
    def get_neighbors(self, agents):
        for neighbour_agent in agents:
            if neighbour_agent != self:
                dist = math.sqrt((neighbour_agent.x - self.x) ** 2 + (neighbour_agent.y - self.y) ** 2)
                if dist <= INTERACTION_RADIUS:
                    self.neighbors.append(neighbour_agent)
                    
    def calculate_average_phase(self):
        if not self.neighbors:
            return None
        
        dt = 0.01
        N = len(self.neighbors)
        avg_phase_diff = 0.0
        for neighbor in self.neighbors:
            diff = neighbor.phase - self.phase
            avg_phase_diff += math.sin(diff)
        avg_phase_diff /= N
        
        # Update the phase using the Kuramoto model
        self.phase += (self.omega + K * avg_phase_diff) * dt
           
    def display_agents(self, screen):
        super().draw_agents(screen)
                    
class KuramotoModel:
    def __init__(self, agent_pos):
        self.Name = 'Kuramoto Model'
        self.agents = []
        for pos in agent_pos:
            x, y = pos[0], pos[1]
            phase = random.uniform(0, 2 * math.pi)
            omega = random.uniform(*OMEGA_RANGE)
            start_direction = random.uniform(0, 2 * math.pi)
            is_latent = random.choice([True, False])
            self.agents.append(KuramotoAgent(x, y, phase, omega, start_direction, is_latent))
            
    def update(self, time_count, targets, hurdles, WIDTH, HEIGHT):
        for agent in self.agents:
            agent.neighbors = []
            agent.get_neighbors(self.agents)
            
        if time_count % CONSENSUS_PERIOD == 0:  # Perform consensus phase every CONSENSUS_PERIOD frames
            print('Model has been updated at time: ',time_count)
            print('Info: Randomly select a neighbor agent to switch the Opinion')
            
            # Calculate the average position of the swarm
            avg_position = pygame.Vector2()
            N = len(self.agents)
            for agent in self.agents:
                avg_position += pygame.Vector2(agent.x, agent.y)
            avg_position /= N
            
            for agent in self.agents:
                agent.calculate_average_phase()
                agent.move(targets)
                
