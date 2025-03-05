import numpy as np
import random
from ..simulation.disease import DiseaseSeverity


class AgentState:
    SUSCEPTIBLE = 'susceptible'
    EXPOSED = 'exposed'         # Infected but not yet infectious
    PRESYMPTOMATIC = 'presymptomatic'  # Infectious but no symptoms yet
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
        state: Current health state
        infection_time: Time step when infection occurred
        infections_caused: Count of infections this agent has caused
        isolation_factor: Reduction in mobility when symptomatic (0-1)
        age_group: Age group for determining mortality risk
        severity: Severity of disease if infected
        recovery_time: Calculated recovery time based on severity
        exposure_time: Time step when the agent was exposed to the virus
        symptom_onset_time: Time step when symptoms will appear
        mask_wearing: Whether the agent wears a mask
        vaccinated: Whether the agent is vaccinated
    """

    def __init__(self, position, mobility, state=AgentState.SUSCEPTIBLE, isolation_factor=0.0,
                 age_group=None, mask_wearing=False, vaccinated=False):
        self.position = np.array(position)
        self.initial_mobility = mobility
        self.mobility = mobility
        self.state = state
        self.infection_time = None
        self.exposure_time = None
        self.infections_caused = 0
        self.isolation_factor = isolation_factor

        # Age-related factors
        self.age_group = age_group or random.choice(["0-9", "10-19", "20-29", "30-39",
                                                     "40-49", "50-59", "60-69", "70-79", "80+"])

        # Disease characteristics - will be set when infected
        self.severity = None
        self.recovery_time = None
        self.symptom_onset_time = None

        # Protective measures
        self.mask_wearing = mask_wearing
        self.vaccinated = vaccinated

        # If vaccinated, increased chance of being immune
        if self.vaccinated and state == AgentState.SUSCEPTIBLE:
            if random.random() < 0.70:  # 70% chance of immunity from vaccination
                self.state = AgentState.IMMUNE

    def move(self):
        """
        Move the agent randomly based on current mobility.
        Immobile agents (dead or isolated ill agents) don't move.
        """
        if self.state != AgentState.DEAD and self.mobility > 0:
            # Different movement patterns based on state
            if self.state == AgentState.ILL:
                # Ill people move less and more locally
                angle = np.random.uniform(0, 2 * np.pi)
                distance = np.random.uniform(0, self.mobility)
            else:
                # Normal movement pattern
                angle = np.random.uniform(0, 2 * np.pi)
                distance = np.random.uniform(0, 2 * self.mobility)

            dx = distance * np.cos(angle)
            dy = distance * np.sin(angle)
            self.position += np.array([dx, dy])

    def infect(self, current_time, disease):
        """
        Infect this agent and determine disease progression details.

        Args:
            current_time: Current simulation time
            disease: Disease object with parameters
        """
        if self.state != AgentState.SUSCEPTIBLE:
            return False

        # Mark as exposed (infected but not infectious yet)
        self.state = AgentState.EXPOSED
        self.exposure_time = current_time

        # Determine severity based on disease model
        self.severity = disease.get_random_severity()

        # Vaccination reduces severity by one level if possible
        if self.vaccinated and self.severity != DiseaseSeverity.ASYMPTOMATIC:
            severities = [DiseaseSeverity.ASYMPTOMATIC, DiseaseSeverity.MILD,
                          DiseaseSeverity.MODERATE, DiseaseSeverity.SEVERE,
                          DiseaseSeverity.CRITICAL]
            current_index = severities.index(self.severity)
            self.severity = severities[max(0, current_index - 1)]

        # Calculate recovery time based on severity
        self.recovery_time = disease.get_recovery_time(self.severity)

        # Calculate when symptoms will appear (incubation + random factor)
        incubation_variation = random.uniform(0.7, 1.3)  # ±30%
        self.symptom_onset_time = current_time + \
            int(disease.incubation_time * incubation_variation)

        return True

    def update_state(self, current_time, disease):
        """
        Update the agent's state based on disease progression.

        Args:
            current_time: Current simulation time step
            disease: Disease object with parameters
        """
        # Handle exposed state - transition to presymptomatic after incubation period starts
        if self.state == AgentState.EXPOSED and self.exposure_time is not None:
            time_since_exposure = current_time - self.exposure_time
            presymptomatic_start = disease.incubation_time - \
                disease.presymptomatic_infectious_period

            if time_since_exposure >= presymptomatic_start:
                self.state = AgentState.PRESYMPTOMATIC
                self.infection_time = current_time

        # Handle presymptomatic - transition to ill after full incubation
        elif self.state == AgentState.PRESYMPTOMATIC and self.exposure_time is not None:
            if current_time >= self.symptom_onset_time:
                self.state = AgentState.ILL

                # Reduce mobility based on severity
                if self.severity == DiseaseSeverity.ASYMPTOMATIC:
                    # Asymptomatic people don't change behavior much
                    self.mobility = self.initial_mobility * 0.8
                elif self.severity == DiseaseSeverity.MILD:
                    # Mild cases reduce movement but don't isolate completely
                    self.mobility = self.initial_mobility * 0.5
                else:
                    # Moderate to critical cases isolate more strictly
                    self.mobility = self.initial_mobility * self.isolation_factor

        # Handle illness progression
        elif self.state == AgentState.ILL and self.exposure_time is not None:
            time_since_exposure = current_time - self.exposure_time

            # Check if recovery or death occurs
            if time_since_exposure >= self.recovery_time:
                # Calculate mortality based on severity and age
                mortality = disease.get_mortality_rate(
                    self.severity, self.age_group)

                if random.random() < mortality:
                    self.state = AgentState.DEAD
                    self.mobility = 0
                else:
                    self.state = AgentState.IMMUNE
                    self.mobility = self.initial_mobility  # Restore mobility

    def is_infectious(self):
        """
        Determine if the agent is currently infectious.

        Returns:
            bool: True if agent can infect others
        """
        return self.state in [AgentState.PRESYMPTOMATIC, AgentState.ILL]

    def get_infection_risk(self, distance, other_agent=None):
        """
        Calculate infection risk based on distance and other factors.

        Args:
            distance: Distance to potential infectee
            other_agent: The other agent who might be infected

        Returns:
            float: Risk factor (0-1)
        """
        if not self.is_infectious():
            return 0.0

        # Base risk decreases with distance
        base_risk = max(0, 1 - (distance / 2.0))

        # Modify risk based on severity
        severity_factor = 1.0
        if self.severity == DiseaseSeverity.ASYMPTOMATIC:
            severity_factor = 0.5  # Lower viral load
        elif self.severity == DiseaseSeverity.CRITICAL:
            severity_factor = 0.3  # Critical patients typically isolated
        elif self.severity == DiseaseSeverity.SEVERE:
            severity_factor = 0.6  # Severe patients more isolated

        # Modify risk based on protective measures
        mask_factor = 0.4 if self.mask_wearing else 1.0  # Masks reduce transmission
        other_mask = 0.5 if other_agent and other_agent.mask_wearing else 1.0

        # Vaccination reduces risk of transmitting
        vaccine_factor = 0.7 if self.vaccinated else 1.0

        # Combine all factors
        return base_risk * severity_factor * mask_factor * other_mask * vaccine_factor
