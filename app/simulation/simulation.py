import numpy as np
from .agent import Agent, AgentState
from .environment import Environment
from .disease import Disease

class Simulation:
    """
    Manages the simulation of the disease spread.
    """
    def __init__(
        self,
        num_agents,
        area_size,
        mobility,
        disease,
        environment=None,
        initial_infected=1,
    ):
        self.num_agents = num_agents
        self.area_size = area_size
        self.environment = environment if environment else Environment(area_size)
        self.disease = disease
        self.time_step = 0
        self.agents = self.initialize_agents(mobility, initial_infected)
        self.history = {
            'susceptible': [],
            'ill': [],
            'immune': [],
            'dead': [],
            'total_cases': [],
        }

    def initialize_agents(self, mobility, initial_infected):
        agents = []
        for i in range(self.num_agents):
            position = np.random.uniform(0, self.area_size, size=2)
            agent_mobility = (
                mobility[i] if isinstance(mobility, list) else mobility
            )
            agent = Agent(position, agent_mobility)
            agents.append(agent)

        # Infect initial agents
        initial_infected_agents = np.random.choice(
            agents, initial_infected, replace=False
        )
        for agent in initial_infected_agents:
            agent.state = AgentState.ILL
            agent.infection_time = self.time_step
        return agents

    def step(self):
        self.time_step += 1

        # Move agents
        for agent in self.agents:
            agent.move()
            self.environment.apply_boundary_conditions(agent)

        # Check for infections
        positions = np.array(
            [agent.position for agent in self.agents if agent.state != AgentState.DEAD]
        )
        states = np.array(
            [agent.state for agent in self.agents if agent.state != AgentState.DEAD]
        )
        ill_indices = np.where(states == AgentState.ILL)[0]
        susceptible_indices = np.where(states == AgentState.SUSCEPTIBLE)[0]

        # Infection spread
        for ill_idx in ill_indices:
            ill_agent = self.agents[ill_idx]
            for sus_idx in susceptible_indices:
                susceptible_agent = self.agents[sus_idx]
                distance = np.linalg.norm(
                    ill_agent.position - susceptible_agent.position
                )
                if distance <= self.disease.infection_distance:
                    if np.random.rand() < self.disease.infection_probability:
                        susceptible_agent.state = AgentState.ILL
                        susceptible_agent.infection_time = self.time_step
                        ill_agent.infections_caused += 1

        # Update agent states
        for agent in self.agents:
            agent.update_state(self.time_step, self.disease)

        self.record_history()

    def record_history(self):
        states = [agent.state for agent in self.agents]
        self.history['susceptible'].append(states.count(AgentState.SUSCEPTIBLE))
        self.history['ill'].append(states.count(AgentState.ILL))
        self.history['immune'].append(states.count(AgentState.IMMUNE))
        self.history['dead'].append(states.count(AgentState.DEAD))
        total_cases = self.num_agents - states.count(AgentState.SUSCEPTIBLE)
        self.history['total_cases'].append(total_cases)

    def calculate_R0(self):
        total_new_infections = 0
        total_ill_agents = 0

        for agent in self.agents:
            if hasattr(agent, 'infections_caused'):
                total_new_infections += agent.infections_caused
                total_ill_agents += 1

        if total_ill_agents == 0:
            return 0
        return total_new_infections / total_ill_agents

    def run(self, steps):
        for _ in range(steps):
            self.step()
