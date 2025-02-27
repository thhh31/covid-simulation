import numpy as np


class AgentState:
    SUSCEPTIBLE = 'susceptible'
    ILL = 'ill'
    IMMUNE = 'immune'
    DEAD = 'dead'


class Agent:
    """
    Represents an individual in the simulation.

    Attributes:
        position: 2D array representing the agent's position
        mobility: Current mobility value (can change during simulation)
        initial_mobility: Original mobility value (used for restoring after recovery)
        state: Current health state (susceptible, ill, immune, or dead)
        infection_time: Time step when infection occurred
        infections_caused: Count of infections this agent has caused
        isolation_factor: Reduction in mobility when symptomatic (0-1)
    """

    def __init__(self, position, mobility, state=AgentState.SUSCEPTIBLE, isolation_factor=0.0):
        self.position = np.array(position)
        self.initial_mobility = mobility  # Store the initial mobility
        self.mobility = mobility
        self.state = state
        self.infection_time = None  # Time step when the agent was infected
        self.infections_caused = 0  # Number of people this agent has infected
        # 0 = complete isolation, 1 = no isolation
        self.isolation_factor = isolation_factor

    def move(self):
        """
        Move the agent randomly based on current mobility.
        Immobile agents (dead or isolated ill agents) don't move.
        """
        if self.state != AgentState.DEAD and self.mobility > 0:
            angle = np.random.uniform(0, 2 * np.pi)
            distance = np.random.uniform(0, 2 * self.mobility)
            dx = distance * np.cos(angle)
            dy = distance * np.sin(angle)
            self.position += np.array([dx, dy])

    def update_state(self, current_time, disease):
        """
        Update the agent's state based on disease progression.

        Args:
            current_time: Current simulation time step
            disease: Disease object with parameters
        """
        if self.state == AgentState.ILL:
            time_since_infection = current_time - self.infection_time

            # After incubation period, reduce mobility (isolate)
            if time_since_infection >= disease.incubation_time:
                self.mobility = self.initial_mobility * self.isolation_factor

            # After illness duration, recover or die
            if time_since_infection >= disease.illness_duration:
                if np.random.rand() < disease.mortality_rate:
                    self.state = AgentState.DEAD
                    self.mobility = 0
                else:
                    self.state = AgentState.IMMUNE
                    self.mobility = self.initial_mobility  # Restore mobility
