import numpy as np

class AgentState:
    SUSCEPTIBLE = 'susceptible'
    ILL = 'ill'
    IMMUNE = 'immune'
    DEAD = 'dead'

class Agent:
    """
    Represents an individual in the simulation.
    """
    def __init__(self, position, mobility, state=AgentState.SUSCEPTIBLE):
        self.position = np.array(position)
        self.initial_mobility = mobility  # Store the initial mobility
        self.mobility = mobility
        self.state = state
        self.infection_time = None # Time step when the agent was infected
        self.infections_caused = 0  # Number of people this agent has infected

    def move(self):
        if self.state != AgentState.DEAD and self.mobility > 0:
            angle = np.random.uniform(0, 2 * np.pi)
            distance = np.random.uniform(0, 2 * self.mobility)
            dx = distance * np.cos(angle)
            dy = distance * np.sin(angle)
            self.position += np.array([dx, dy])

    def update_state(self, current_time, disease):
        """
        Update the agent's state based on disease progression.
        """
        if self.state == AgentState.ILL:
            time_since_infection = current_time - self.infection_time
            if time_since_infection >= disease.incubation_time:
                self.mobility = 0  # Agent is isolated after incubation time
            if time_since_infection >= disease.illness_duration:
                if np.random.rand() < disease.mortality_rate:
                    self.state = AgentState.DEAD
                    self.mobility = 0
                else:
                    self.state = AgentState.IMMUNE
                    self.mobility = self.initial_mobility  # Restore mobility
