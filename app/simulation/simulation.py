import numpy as np
import random
from .agent import Agent, AgentState
from .environment import Environment
from .disease import Disease, DiseaseSeverity


class Simulation:
    """
    Manages the simulation of the disease spread with realistic COVID-19 parameters.
    """

    def __init__(
        self,
        num_agents,
        area_size,
        mobility,
        disease,
        environment=None,
        initial_infected=1,
        mask_usage=0.0,
        vaccination_rate=0.0,
        age_distribution=None,
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
            mask_usage: Proportion of population using masks (0-1)
            vaccination_rate: Proportion of population vaccinated (0-1)
            age_distribution: Custom age distribution, or None for default
        """
        self.num_agents = num_agents
        self.area_size = area_size
        self.environment = environment if environment else Environment(
            area_size)
        self.disease = disease
        self.time_step = 0
        self.mask_usage = mask_usage
        self.vaccination_rate = vaccination_rate
        self.age_distribution = age_distribution

        # Initialize agents with demographics
        self.agents = self.initialize_agents(mobility, initial_infected)

        # Extended history tracking
        self.history = {
            'susceptible': [],
            'exposed': [],
            'presymptomatic': [],
            'ill': [],
            'immune': [],
            'dead': [],
            'total_cases': [],
            'new_cases': [],
            'r0': [],
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

        # Create agents with random positions, masks, and vaccination status
        for i in range(self.num_agents):
            position = self.environment.get_random_position(
                avoid_obstacles=True)

            # Determine mask usage and vaccination randomly based on rates
            wears_mask = random.random() < self.mask_usage
            is_vaccinated = random.random() < self.vaccination_rate

            # Add different isolation factors by agent
            # Most people isolate well when sick
            isolation_factor = random.uniform(0.0, 0.3)

            agent = Agent(
                position=position,
                mobility=mobilities[i],
                mask_wearing=wears_mask,
                vaccinated=is_vaccinated,
                isolation_factor=isolation_factor
            )
            agents.append(agent)

        # Infect initial agents
        if initial_infected > self.num_agents:
            raise ValueError(
                f"Initial infected count ({initial_infected}) cannot exceed total agents ({self.num_agents})")

        # Choose non-immune agents to infect initially
        susceptible_agents = [
            a for a in agents if a.state == AgentState.SUSCEPTIBLE]
        if len(susceptible_agents) < initial_infected:
            initial_infected = len(susceptible_agents)

        initial_infected_agents = np.random.choice(
            susceptible_agents, initial_infected, replace=False
        )

        for agent in initial_infected_agents:
            # Use the new infection method
            agent.infect(self.time_step, self.disease)

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
        new_infections = 0

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

        # Get alive agents for infection checks
        alive_agents = [
            agent for agent in self.agents if agent.state != AgentState.DEAD]

        # Get infectious and susceptible agents
        infectious_agents = [
            agent for agent in alive_agents if agent.is_infectious()]
        susceptible_agents = [
            agent for agent in alive_agents if agent.state == AgentState.SUSCEPTIBLE]

        # Process infections using the more complex infection model
        for infectious_agent in infectious_agents:
            # Copy to avoid modifying during iteration
            for susceptible_agent in susceptible_agents[:]:
                distance = np.linalg.norm(
                    infectious_agent.position - susceptible_agent.position
                )

                if distance <= self.disease.infection_distance:
                    # Calculate infection risk based on various factors
                    infection_risk = infectious_agent.get_infection_risk(
                        distance, susceptible_agent)

                    # Adjust by base disease infectiousness
                    infection_probability = infection_risk * self.disease.infection_probability

                    if random.random() < infection_probability:
                        # Infect the agent
                        susceptible_agent.infect(self.time_step, self.disease)
                        infectious_agent.infections_caused += 1

                        # Count new infections
                        new_infections += 1

                        # Remove from susceptible list to avoid double counting
                        susceptible_agents.remove(susceptible_agent)

        # Update agent states
        for agent in self.agents:
            agent.update_state(self.time_step, self.disease)

        # Record history with new metrics
        self.record_history(new_infections)

        # Calculate and record R0 periodically
        if self.time_step % 10 == 0:
            r0 = self.calculate_R0()
            self.history['r0'].append(r0)
        else:
            # Maintain the same R0 value for non-calculation steps
            if self.history['r0']:
                self.history['r0'].append(self.history['r0'][-1])
            else:
                self.history['r0'].append(0)

    def record_history(self, new_infections=0):
        """
        Record the current state of the simulation for later analysis.

        Args:
            new_infections: Number of new infections in this time step
        """
        states = [agent.state for agent in self.agents]
        self.history['susceptible'].append(
            states.count(AgentState.SUSCEPTIBLE))
        self.history['exposed'].append(states.count(AgentState.EXPOSED))
        self.history['presymptomatic'].append(
            states.count(AgentState.PRESYMPTOMATIC))
        self.history['ill'].append(states.count(AgentState.ILL))
        self.history['immune'].append(states.count(AgentState.IMMUNE))
        self.history['dead'].append(states.count(AgentState.DEAD))
        total_cases = self.num_agents - states.count(AgentState.SUSCEPTIBLE)
        self.history['total_cases'].append(total_cases)
        self.history['new_cases'].append(new_infections)

    def calculate_R0(self):
        """
        Calculate the basic reproduction number (R0) for the simulation.

        Returns:
            float: Average number of infections caused by each infected agent
        """
        total_new_infections = 0
        total_infectors = 0

        for agent in self.agents:
            if agent.infections_caused > 0:
                total_new_infections += agent.infections_caused
                total_infectors += 1

        if total_infectors == 0:
            return 0
        return total_new_infections / total_infectors

    def run(self, steps):
        """
        Run the simulation for the specified number of steps.

        Args:
            steps: Number of time steps to run
        """
        for _ in range(steps):
            self.step()

    def get_stats_by_severity(self):
        """
        Get statistics on disease severity among ill and recovered agents.

        Returns:
            dict: Counts and percentages of each severity level
        """
        severity_counts = {
            DiseaseSeverity.ASYMPTOMATIC: 0,
            DiseaseSeverity.MILD: 0,
            DiseaseSeverity.MODERATE: 0,
            DiseaseSeverity.SEVERE: 0,
            DiseaseSeverity.CRITICAL: 0,
            'unknown': 0
        }

        # Count agents by severity
        ill_or_immune_agents = [a for a in self.agents if a.state in
                                [AgentState.ILL, AgentState.IMMUNE, AgentState.DEAD]]

        for agent in ill_or_immune_agents:
            if agent.severity:
                severity_counts[agent.severity] += 1
            else:
                severity_counts['unknown'] += 1

        # Calculate percentages
        total = len(ill_or_immune_agents)
        severity_percentages = {}

        if total > 0:
            for severity, count in severity_counts.items():
                severity_percentages[severity] = (count / total) * 100
        else:
            for severity in severity_counts:
                severity_percentages[severity] = 0

        return {
            'counts': severity_counts,
            'percentages': severity_percentages,
            'total': total
        }

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
                'mask_usage': self.mask_usage,
                'vaccination_rate': self.vaccination_rate,
                'disease': {
                    'infection_distance': self.disease.infection_distance,
                    'infection_probability': self.disease.infection_probability,
                    'incubation_time': self.disease.incubation_time,
                    'illness_duration': self.illness_duration if hasattr(self.disease, 'illness_duration') else None,
                    'mortality_rate': self.disease.mortality_rate,
                }
            },
            'history': self.history,
            'final_state': {
                'susceptible': self.history['susceptible'][-1] if self.history['susceptible'] else 0,
                'exposed': self.history['exposed'][-1] if self.history['exposed'] else 0,
                'presymptomatic': self.history['presymptomatic'][-1] if self.history['presymptomatic'] else 0,
                'ill': self.history['ill'][-1] if self.history['ill'] else 0,
                'immune': self.history['immune'][-1] if self.history['immune'] else 0,
                'dead': self.history['dead'][-1] if self.history['dead'] else 0,
                'r0': self.calculate_R0(),
                'time_steps': self.time_step
            },
            'severity_stats': self.get_stats_by_severity()
        }

        # Save to file
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

        return data
