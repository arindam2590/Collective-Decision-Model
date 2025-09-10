import random

from Model.ModelAgent import MajorityAgent, VoterAgent, KuramotoAgent

LATENT_AGENT_COLOR = (255, 0, 0)        # Red for latent agents
NON_LATENT_AGENT_COLOR = (0, 255, 255)  # Blue for non-latent agents


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
        # metrics is [direction_mismatches, collisions]
        direction_mismatches = metrics[0]
        collisions = metrics[1] if len(metrics) > 1 else []

        for agent in self.agents:
            agent.get_neighbors(self.agents)

        if time_count % self.consensus_period == 0:
            print('Model has been updated at time: ', time_count)
            print('Info: Opinion occurance is being counted by agents')

            dir_mismatch_per_period = []
            collision_per_period = []

            for agent in self.agents:
                agent.calculate_average_direction()
                agent.compute_opinion(self.targets)
                dir_mismatch_per_period.append(agent.calculate_dir_mismatch())
                collision_per_period.append(agent.compute_collision_count())

            for agent in self.agents:
                if agent.consensus_direction is not None:
                    agent.count_opinion_occurance(self.targets)
                    agent.direction = agent.consensus_direction
                    agent.has_consensus = True

            direction_mismatches.append(dir_mismatch_per_period)
            collisions.append(collision_per_period)

            print('Info: Majority opinion has been selected by the agents')
            print('=' * 60)

        for agent in self.agents:
            if agent.has_consensus:
                agent.update_direction(self.agents, self.swarm_params)
                agent.color = NON_LATENT_AGENT_COLOR if agent.is_latent else LATENT_AGENT_COLOR
            agent.move(hurdles)

        return [direction_mismatches, collisions]


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
        direction_mismatches = metrics[0]
        collisions = metrics[1] if len(metrics) > 1 else []

        for agent in self.agents:
            agent.get_neighbors(self.agents)

        if time_count % self.consensus_period == 0:
            print('Model has been updated at time: ', time_count)
            print('Info: Randomly select a neighbor agent to switch the Opinion')

            dir_mismatch_per_period = []
            collision_per_period = []

            for agent in self.agents:
                agent.calculate_average_direction()
                if agent.consensus_direction is not None:
                    agent.compute_opinion(self.targets)
                    # record BEFORE changing opinions/directions
                    dir_mismatch_per_period.append(abs(agent.consensus_direction - agent.direction))
                    collision_per_period.append(agent.compute_collision_count())
                    agent.switch_opinion()

            direction_mismatches.append(dir_mismatch_per_period)
            collisions.append(collision_per_period)

            print('Info: Opinion has been switched with the randomly selected neighbor agents')
            print('=' * 60)

        for agent in self.agents:
            if agent.has_switched_opinion:
                agent.update_direction(self.agents, self.swarm_params)
                agent.color = NON_LATENT_AGENT_COLOR if agent.is_latent else LATENT_AGENT_COLOR
            agent.move(hurdles)

        return [direction_mismatches, collisions]


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
        direction_mismatches = metrics[0]
        collisions = metrics[1] if len(metrics) > 1 else []

        for agent in self.agents:
            agent.get_neighbors(self.agents)
            agent.get_nearest_goal(self.targets)

        if time_count % self.consensus_period == 0:
            print('Model has been updated at time: ', time_count)
            print('Info: Phase (direction) of the Agent is being computed')

            dir_mismatch_per_period = []
            collision_per_period = []

            for agent in self.agents:
                if agent.coupling_strength_K <= 1.0:
                    agent.has_phase_synched = False
                    agent.calculate_phase_difference()  # sets consensus_direction
                    agent.coupling_strength_K += self.coupling_strength_increment

                if agent.consensus_direction is not None:
                    # record BEFORE applying consensus update
                    dir_mismatch_per_period.append(abs(agent.consensus_direction - agent.direction))
                    collision_per_period.append(agent.compute_collision_count())
                    agent.direction = agent.consensus_direction

            direction_mismatches.append(dir_mismatch_per_period)
            collisions.append(collision_per_period)

            print('Info: Phase (direction) of the Agent has been synchronized with its neighbors')
            print('=' * 60)

        for agent in self.agents:
            if agent.has_phase_synched:
                agent.update_direction(self.agents, self.swarm_params)
                agent.color = NON_LATENT_AGENT_COLOR if agent.is_latent else LATENT_AGENT_COLOR
            agent.move(hurdles)

        return [direction_mismatches, collisions]
