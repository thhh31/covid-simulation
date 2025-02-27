import numpy as np


class BoundaryType:
    PERIODIC = 'periodic'  # Agents wrap around edges
    REFLECTING = 'reflecting'  # Agents bounce off edges
    ABSORBING = 'absorbing'  # Agents stop at edges


class Environment:
    """
    Represents the simulation environment with customizable properties.
    """

    def __init__(self, area_size, boundary_type=BoundaryType.PERIODIC, obstacles=None):
        """
        Initialize the environment.

        Args:
            area_size: Size of the square area (area_size x area_size)
            boundary_type: Type of boundary condition (periodic, reflecting, absorbing)
            obstacles: List of obstacles as (x, y, radius) tuples
        """
        self.area_size = area_size
        self.boundary_type = boundary_type
        self.obstacles = obstacles or []

    def apply_boundary_conditions(self, agent):
        """
        Ensure the agent stays within the area boundaries according to the boundary type.

        Args:
            agent: Agent to apply boundary conditions to
        """
        if self.boundary_type == BoundaryType.PERIODIC:
            # Wrap around edges (torus topology)
            agent.position = np.mod(agent.position, self.area_size)

        elif self.boundary_type == BoundaryType.REFLECTING:
            # Bounce off edges
            for i in range(2):  # For both x and y coordinates
                if agent.position[i] < 0:
                    agent.position[i] = -agent.position[i]  # Reflect
                elif agent.position[i] >= self.area_size:
                    agent.position[i] = 2 * self.area_size - \
                        agent.position[i]  # Reflect

        elif self.boundary_type == BoundaryType.ABSORBING:
            # Stop at edges
            agent.position = np.clip(agent.position, 0, self.area_size - 0.1)

    def check_obstacle_collision(self, position, radius=0):
        """
        Check if a position collides with any obstacle.

        Args:
            position: Position to check
            radius: Radius around the position to check

        Returns:
            bool: True if collision, False otherwise
        """
        for obstacle_x, obstacle_y, obstacle_radius in self.obstacles:
            obstacle_pos = np.array([obstacle_x, obstacle_y])
            distance = np.linalg.norm(position - obstacle_pos)
            if distance < (obstacle_radius + radius):
                return True
        return False

    def add_obstacle(self, x, y, radius):
        """
        Add an obstacle to the environment.

        Args:
            x: X coordinate
            y: Y coordinate
            radius: Radius of the obstacle
        """
        self.obstacles.append((x, y, radius))

    def get_random_position(self, avoid_obstacles=True, margin=0):
        """
        Get a random position within the environment.

        Args:
            avoid_obstacles: If True, ensure position doesn't overlap with obstacles
            margin: Minimum distance from boundaries

        Returns:
            np.array: Random position
        """
        if not avoid_obstacles or not self.obstacles:
            # Simple case: no obstacles to avoid
            return np.random.uniform(margin, self.area_size - margin, size=2)

        # With obstacles, we need to check for collision
        max_attempts = 100
        for _ in range(max_attempts):
            position = np.random.uniform(
                margin, self.area_size - margin, size=2)
            if not self.check_obstacle_collision(position):
                return position

        # If we couldn't find a valid position, return one anyway
        return np.random.uniform(margin, self.area_size - margin, size=2)
