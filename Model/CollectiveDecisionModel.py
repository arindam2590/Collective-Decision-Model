import random
import numpy as np

from Model.ModelAgent import MajorityAgent, VoterAgent, KuramotoAgent

LATENT_AGENT_COLOR = (255, 0, 0)        # Red
NON_LATENT_AGENT_COLOR = (0, 255, 255)  # Blue


def _decision_accuracy(agents, target_radius):
    """Proportion of agents that are inside their selected target (agent.nearest_goal)."""
    successes = 0
    counted = 0
    r2 = float(target_radius) ** 2
    for a in agents:
        if getattr(a, 'nearest_goal', None) is None:
            continue
        dx = a.position[0] - a.nearest_goal[0]
        dy = a.position[1] - a.nearest_goal[1]
        if dx * dx + dy * dy <= r2:
            successes += 1
        counted += 1
    return (successes / counted) if counted > 0 else 0.0


class MajorityRuleModel:
    def __init__(self, agent_pos, targets, params):
        self.Name = 'Majority Model'
        self.env_params, self.swarm_params = params
        self.consensus_period = self.swarm_params['CONSENSUS_PERIOD']
        self.targets = targets
        self.agents = []
        for pos in agent_pos:
            is_latent = random.choice([True, False])
            opn_count = {target: 0 for target in self.targets}
            self.agents.append(
                MajorityAgent(pos, is_latent, self.env_params['SCREEN_WIDTH'], self.env_params['SCREEN_HEIGHT'],
                              self.swarm_params['INTERACTION_RADIUS'], self.swarm_params['REPULSION_RADIUS'],
                              self.swarm_params['SEPERATION_DISTANCE'], self.swarm_params['AGENT_SPEED'], opn_count))

    def update(self, time_count, hurdles, metrics):
        # metrics: [dir_mismatch, collisions, decision_accuracy]
        direction_mismatches = metrics[0]
        collisions = metrics[1]
        decision_accuracy = metrics[2]

        for agent in self.agents:
            agent.get_neighbors(self.agents)

        if time_count % self.consensus_period == 0:
            print('Model has been updated at time: ', time_count)
            print('Info: Opinion occurrence is being counted by agents')

            dir_mismatch_step = []
            collision_step = []

            for agent in self.agents:
                agent.calculate_average_direction()
                agent.compute_opinion(self.targets)
                dir_mismatch_step.append(agent.calculate_dir_mismatch())
                collision_step.append(agent.compute_collision_count())

            for agent in self.agents:
                if agent.consensus_direction is not None:
                    agent.count_opinion_occurance(self.targets)
                    agent.direction = agent.consensus_direction
                    agent.has_consensus = True

            # decision-making accuracy (proportion inside selected targets)
            acc = _decision_accuracy(self.agents, self.env_params['TARGET_SIZE'])

            direction_mismatches.append(dir_mismatch_step)
            collisions.append(collision_step)
            decision_accuracy.append([acc])  # keep shape consistent (list of scalars)

            print('Info: Majority opinion selected')
            print('=' * 60)

        for agent in self.agents:
            if agent.has_consensus:
                agent.update_direction(self.agents, self.swarm_params)
                agent.color = NON_LATENT_AGENT_COLOR if agent.is_latent else LATENT_AGENT_COLOR
            agent.move(hurdles)

        return [direction_mismatches, collisions, decision_accuracy]


class VoterModel:
    def __init__(self, agent_pos, targets, params):
        self.Name = 'Voter Model'
        self.env_params, self.swarm_params = params
        self.consensus_period = self.swarm_params['CONSENSUS_PERIOD']
        self.targets = targets
        self.agents = []
        for pos in agent_pos:
            is_latent = random.choice([True, False])
            self.agents.append(VoterAgent(pos, is_latent, self.targets, self.env_params['SCREEN_WIDTH'],
                                          self.env_params['SCREEN_HEIGHT'],
                                          self.swarm_params['INTERACTION_RADIUS'],
                                          self.swarm_params['REPULSION_RADIUS'],
                                          self.swarm_params['SEPERATION_DISTANCE'], self.swarm_params['AGENT_SPEED']))

    def update(self, time_count, hurdles, metrics):
        # metrics: [dir_mismatch, collisions, decision_accuracy]
        direction_mismatches = metrics[0]
        collisions = metrics[1]
        decision_accuracy = metrics[2]

        for agent in self.agents:
            agent.get_neighbors(self.agents)

        if time_count % self.consensus_period == 0:
            print('Model has been updated at time: ', time_count)
            print('Info: Randomly select a neighbor agent to switch opinion')

            dir_mismatch_step = []
            collision_step = []

            for agent in self.agents:
                agent.calculate_average_direction()
                if agent.consensus_direction is not None:
                    agent.compute_opinion(self.targets)
                    dir_mismatch_step.append(abs(agent.consensus_direction - agent.direction))
                    collision_step.append(agent.compute_collision_count())
                    agent.switch_opinion()

            # decision-making accuracy
            acc = _decision_accuracy(self.agents, self.env_params['TARGET_SIZE'])

            direction_mismatches.append(dir_mismatch_step)
            collisions.append(collision_step)
            decision_accuracy.append([acc])

            print('Info: Opinion switched')
            print('=' * 60)

        for agent in self.agents:
            if agent.has_switched_opinion:
                agent.update_direction(self.agents, self.swarm_params)
                agent.color = NON_LATENT_AGENT_COLOR if agent.is_latent else LATENT_AGENT_COLOR
            agent.move(hurdles)

        return [direction_mismatches, collisions, decision_accuracy]


class KuramotoModel:
    def __init__(self, agent_pos, targets, params):
        self.Name = 'Kuramoto Model'
        self.env_params, self.swarm_params = params
        self.consensus_period = self.swarm_params['CONSENSUS_PERIOD']
        self.coupling_strength_increment = self.swarm_params['K_INCREMENT']
        self.targets = targets
        self.agents = []
        for pos in agent_pos:
            is_latent = random.choice([True, False])
            self.agents.append(
                KuramotoAgent(pos, is_latent, self.env_params['SCREEN_WIDTH'], self.env_params['SCREEN_HEIGHT'],
                              self.swarm_params['INTERACTION_RADIUS'], self.swarm_params['REPULSION_RADIUS'],
                              self.swarm_params['SEPERATION_DISTANCE'], self.swarm_params['AGENT_SPEED']))

    def update(self, time_count, hurdles, metrics):
        # metrics: [dir_mismatch, collisions, phase_sync, decision_accuracy]
        direction_mismatches = metrics[0]
        collisions = metrics[1]
        phase_synchronization = metrics[2]
        decision_accuracy = metrics[3]

        for agent in self.agents:
            agent.get_neighbors(self.agents)
            agent.get_nearest_goal(self.targets)

        if time_count % self.consensus_period == 0:
            print('Model has been updated at time: ', time_count)
            print('Info: Phase (direction) of the Agent is being computed')

            dir_mismatch_step = []
            collision_step = []
            phase_step = []

            for agent in self.agents:
                if agent.coupling_strength_K <= 1.0:
                    agent.has_phase_synched = False
                    agent.calculate_phase_difference()  # sets consensus_direction
                    agent.coupling_strength_K = min(agent.coupling_strength_K + self.coupling_strength_increment, 1.0)

                if agent.consensus_direction is not None:
                    dir_mismatch_step.append(abs(agent.consensus_direction - agent.direction))
                    collision_step.append(agent.compute_collision_count())
                    # store per-agent scalar (you already compute .agent_phase; averaging will be done later)
                    phase_step.append(agent.agent_phase)
                    agent.direction = agent.consensus_direction

            # decision-making accuracy
            acc = _decision_accuracy(self.agents, self.env_params['TARGET_SIZE']+10)

            direction_mismatches.append(dir_mismatch_step)
            collisions.append(collision_step)
            # Save per-step average (list-of-scalars acceptable in utils)
            phase_synchronization.append(float(np.mean(phase_step)) if len(phase_step) else 0.0)
            decision_accuracy.append([acc])

            print('Info: Phase synchronized')
            print('=' * 60)

        for agent in self.agents:
            if agent.has_phase_synched:
                agent.update_direction(self.agents, self.swarm_params)
                agent.color = NON_LATENT_AGENT_COLOR if agent.is_latent else LATENT_AGENT_COLOR
            agent.move(hurdles)

        return [direction_mismatches, collisions, phase_synchronization, decision_accuracy]
