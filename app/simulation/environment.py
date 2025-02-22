import numpy as np

class Environment:
    """
    Represents the simulation environment.
    """
    def __init__(self, area_size):
        self.area_size = area_size

    def apply_boundary_conditions(self, agent):
        """
        Ensure the agent stays within the area boundaries.
        """
        agent.position = np.mod(agent.position, self.area_size)
