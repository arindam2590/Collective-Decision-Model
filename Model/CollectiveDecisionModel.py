import random
import numpy as np

from Model.ModelAgent import MajorityAgent, VoterAgent, KuramotoAgent

LATENT_AGENT_COLOR = (255, 0, 0)       # Red
NON_LATENT_AGENT_COLOR = (0, 255, 255) # Cyan


class MajorityRuleModel:
    def __init__(self, agent_pos, targets, params):
        self.Name = 'Majority Model'
        self.env_params, self.swarm_params = params
        self.consensus_period = self.swarm_params['CONSENSUS_PERIOD']
        self.targets = [tuple(t) for t in targets]
        self.agents = []
        for pos in agent_pos:
            is_latent = random.choice([True, False])
            opn_count = {tuple(target): 0 for target in self.targets}
            self.agents.append(
                MajorityAgent(
                    pos, is_latent,
                    self.env_params['SCREEN_WIDTH'], self.env_params['SCREEN_HEIGHT'],
                    self.swarm_params['INTERACTION_RADIUS'], self.swarm_params['REPULSION_RADIUS'],
                    self.swarm_params['SEPERATION_DISTANCE'], self.swarm_params['AGENT_SPEED'], opn_count
                )
            )

    def update(self, time_count, hurdles, metrics):
        # metrics is a dict owned by SimEnv
        for agent in self.agents:
            agent.get_neighbors(self.agents)

        if time_count % self.consensus_period == 0:
            dir_mismatch_per_period = []
            for agent in self.agents:
                agent.calculate_average_direction()
                agent.compute_opinion(self.targets)
                dir_mismatch_per_period.append(agent.calculate_dir_mismatch())

            # Opinion counting & commit consensus
            for agent in self.agents:
                if agent.consensus_direction is not None:
                    # guard None nearest_goal in neighbors
                    agent.count_opinion_occurance(self.targets)
                    agent.direction = agent.consensus_direction
                    agent.has_consensus = True

            metrics["dir_mismatch"].append(dir_mismatch_per_period)

            # snapshot of consensus counts
            snap = {}
            for a in self.agents:
                if a.nearest_goal is not None:
                    key = tuple(a.nearest_goal)
                    snap[key] = snap.get(key, 0) + 1
            metrics["consensus_counts"].append(snap)

        # Move phase
        for agent in self.agents:
            if agent.has_consensus:
                agent.update_direction(self.agents, self.swarm_params)
                agent.color = NON_LATENT_AGENT_COLOR if agent.is_latent else LATENT_AGENT_COLOR
            agent.move(hurdles)
        return metrics


class VoterModel:
    def __init__(self, agent_pos, targets, params):
        self.Name = 'Voter Model'
        self.env_params, self.swarm_params = params
        self.consensus_period = self.swarm_params['CONSENSUS_PERIOD']
        self.targets = [tuple(t) for t in targets]
        self.agents = []
        for pos in agent_pos:
            is_latent = random.choice([True, False])
            self.agents.append(
                VoterAgent(
                    pos, is_latent, self.targets,
                    self.env_params['SCREEN_WIDTH'], self.env_params['SCREEN_HEIGHT'],
                    self.swarm_params['INTERACTION_RADIUS'], self.swarm_params['REPULSION_RADIUS'],
                    self.swarm_params['SEPERATION_DISTANCE'], self.swarm_params['AGENT_SPEED']
                )
            )

    def update(self, time_count, hurdles, metrics):
        for agent in self.agents:
            agent.get_neighbors(self.agents)

        if time_count % self.consensus_period == 0:
            for agent in self.agents:
                agent.calculate_average_direction()
                if agent.consensus_direction is not None:
                    agent.compute_opinion(self.targets)
                    agent.switch_opinion()

            # optional mismatch snapshot (after switch)
            dm = [a.calculate_dir_mismatch() for a in self.agents]
            metrics["dir_mismatch"].append(dm)

            snap = {}
            for a in self.agents:
                if a.nearest_goal is not None:
                    key = tuple(a.nearest_goal)
                    snap[key] = snap.get(key, 0) + 1
            metrics["consensus_counts"].append(snap)

        for agent in self.agents:
            if agent.has_switched_opinion:
                agent.update_direction(self.agents, self.swarm_params)
                agent.color = NON_LATENT_AGENT_COLOR if agent.is_latent else LATENT_AGENT_COLOR
            agent.move(hurdles)
        return metrics


class KuramotoModel:
    def __init__(self, agent_pos, targets, params):
        self.Name = 'Kuramoto Model'
        self.env_params, self.swarm_params = params
        self.consensus_period = self.swarm_params['CONSENSUS_PERIOD']
        self.coupling_strength_increment = self.swarm_params['K_INCREMENT']
        self.targets = [tuple(t) for t in targets]
        self.agents = []
        for pos in agent_pos:
            is_latent = random.choice([True, False])
            self.agents.append(
                KuramotoAgent(
                    pos, is_latent,
                    self.env_params['SCREEN_WIDTH'], self.env_params['SCREEN_HEIGHT'],
                    self.swarm_params['INTERACTION_RADIUS'], self.swarm_params['REPULSION_RADIUS'],
                    self.swarm_params['SEPERATION_DISTANCE'], self.swarm_params['AGENT_SPEED']
                )
            )

    def update(self, time_count, hurdles, metrics):
        for agent in self.agents:
            agent.get_neighbors(self.agents)
            agent.get_nearest_goal(self.targets)

        if time_count % self.consensus_period == 0:
            for agent in self.agents:
                if agent.coupling_strength_K <= 1.0:
                    agent.has_phase_synched = False
                    # use the agent's K (grows over time)
                    agent.calculate_phase_difference(K=agent.coupling_strength_K if agent.coupling_strength_K > 0 else 0.8)
                    agent.coupling_strength_K += self.coupling_strength_increment

                if agent.consensus_direction is not None:
                    agent.direction = agent.consensus_direction

            dm = [a.calculate_dir_mismatch() for a in self.agents]
            metrics["dir_mismatch"].append(dm)

            snap = {}
            for a in self.agents:
                if a.nearest_goal is not None:
                    key = tuple(a.nearest_goal)
                    snap[key] = snap.get(key, 0) + 1
            metrics["consensus_counts"].append(snap)

        for agent in self.agents:
            if agent.has_phase_synched:
                agent.update_direction(self.agents, self.swarm_params)
                agent.color = NON_LATENT_AGENT_COLOR if agent.is_latent else LATENT_AGENT_COLOR
            agent.move(hurdles)
        return metrics
