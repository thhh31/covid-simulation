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
        """
        Initialize the simulation.

        Args:
            num_agents: Number of agents in the simulation
            area_size: Size of the square area (area_size x area_size)
            mobility: Mobility parameter(s) - can be a single float or a list of floats
            disease: Disease object with infection parameters
            environment: Custom environment (optional)
            initial_infected: Number of initially infected agents
        """
        self.num_agents = num_agents
        self.area_size = area_size
        self.environment = environment if environment else Environment(
            area_size)
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
        """
        Initialize agents with given mobility and infect the initial set.

        Args:
            mobility: Mobility parameter(s) - can be a single float or a list of floats
            initial_infected: Number of initially infected agents

        Returns:
            List of initialized Agent objects
        """
        agents = []

        # Handle different mobility specifications
        if isinstance(mobility, (int, float)):
            # Single mobility value for all agents
            mobilities = [mobility] * self.num_agents
        elif isinstance(mobility, list) and len(mobility) == self.num_agents:
            # Different mobility for each agent
            mobilities = mobility
        elif isinstance(mobility, list) and len(mobility) != self.num_agents:
            # List provided but wrong length
            raise ValueError(
                f"Mobility list length ({len(mobility)}) must match number of agents ({self.num_agents})")
        else:
            raise TypeError("Mobility must be a number or a list of numbers")

        # Create agents with random positions using the environment
        for i in range(self.num_agents):
            position = self.environment.get_random_position(
                avoid_obstacles=True)
            agent = Agent(position, mobilities[i])
            agents.append(agent)

        # Infect initial agents
        if initial_infected > self.num_agents:
            raise ValueError(
                f"Initial infected count ({initial_infected}) cannot exceed total agents ({self.num_agents})")

        initial_infected_agents = np.random.choice(
            agents, initial_infected, replace=False
        )
        for agent in initial_infected_agents:
            agent.state = AgentState.ILL
            agent.infection_time = self.time_step

        return agents

    def step(self):
        """
        Advance the simulation by one time step. This includes:
        1. Moving agents
        2. Checking for infections
        3. Updating agent states
        4. Recording history
        """
        self.time_step += 1

        # Move agents and handle collisions with obstacles
        for agent in self.agents:
            # Store original position to revert if needed
            original_position = agent.position.copy()

            # Move agent
            agent.move()

            # Apply boundary conditions
            self.environment.apply_boundary_conditions(agent)

            # Check for obstacle collisions and revert if necessary
            if self.environment.check_obstacle_collision(agent.position):
                agent.position = original_position

        # Get alive agents' positions and states for vectorized operations
        alive_agents = [
            agent for agent in self.agents if agent.state != AgentState.DEAD]

        # Check for infections using vectorized operations
        ill_agents = [
            agent for agent in alive_agents if agent.state == AgentState.ILL]
        susceptible_agents = [
            agent for agent in alive_agents if agent.state == AgentState.SUSCEPTIBLE]

        # Infection spread - optimize by checking only relevant agents
        for ill_agent in ill_agents:
            # Only check if agent can spread (before isolation)
            if ill_agent.mobility > 0:
                for susceptible_agent in susceptible_agents:
                    distance = np.linalg.norm(
                        ill_agent.position - susceptible_agent.position
                    )
                    if distance <= self.disease.infection_distance:
                        if np.random.rand() < self.disease.infection_probability:
                            susceptible_agent.state = AgentState.ILL
                            susceptible_agent.infection_time = self.time_step
                            ill_agent.infections_caused += 1
                            # Remove from susceptible list to avoid double counting
                            susceptible_agents.remove(susceptible_agent)

        # Update agent states
        for agent in self.agents:
            agent.update_state(self.time_step, self.disease)

        self.record_history()

    def record_history(self):
        """
        Record the current state of the simulation for later analysis.
        """
        states = [agent.state for agent in self.agents]
        self.history['susceptible'].append(
            states.count(AgentState.SUSCEPTIBLE))
        self.history['ill'].append(states.count(AgentState.ILL))
        self.history['immune'].append(states.count(AgentState.IMMUNE))
        self.history['dead'].append(states.count(AgentState.DEAD))
        total_cases = self.num_agents - states.count(AgentState.SUSCEPTIBLE)
        self.history['total_cases'].append(total_cases)

    def calculate_R0(self):
        """
        Calculate the basic reproduction number (R0) for the simulation.

        Returns:
            float: Average number of infections caused by each infected agent
        """
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
        """
        Run the simulation for the specified number of steps.

        Args:
            steps: Number of time steps to run
        """
        for _ in range(steps):
            self.step()

    def save_results(self, filename):
        """
        Save simulation results to a file.

        Args:
            filename: Path to the output file
        """
        import json
        import os

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)

        # Prepare data for serialization
        data = {
            'configuration': {
                'num_agents': self.num_agents,
                'area_size': self.area_size,
                'disease': {
                    'infection_distance': self.disease.infection_distance,
                    'infection_probability': self.disease.infection_probability,
                    'incubation_time': self.disease.incubation_time,
                    'illness_duration': self.disease.illness_duration,
                    'mortality_rate': self.disease.mortality_rate,
                }
            },
            'history': self.history,
            'final_state': {
                'susceptible': self.history['susceptible'][-1] if self.history['susceptible'] else 0,
                'ill': self.history['ill'][-1] if self.history['ill'] else 0,
                'immune': self.history['immune'][-1] if self.history['immune'] else 0,
                'dead': self.history['dead'][-1] if self.history['dead'] else 0,
                'r0': self.calculate_R0(),
                'time_steps': self.time_step
            }
        }

        # Save to file
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

        return data
