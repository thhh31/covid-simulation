class DiseaseSeverity:
    ASYMPTOMATIC = 'asymptomatic'
    MILD = 'mild'
    MODERATE = 'moderate'
    SEVERE = 'severe'
    CRITICAL = 'critical'


class Disease:
    """
    Represents the disease and its parameters based on realistic COVID-19 data.
    """

    def __init__(
        self,
        infection_distance=1.5,
        infection_probability=0.3,
        incubation_time=5,
        presymptomatic_infectious_period=2,
        illness_duration=14,
        mortality_rate=0.02,
        severity_distribution=None,
        age_mortality_modifier=None,
        time_to_recovery=None
    ):
        """
        Initialize the disease model with realistic COVID-19 parameters.

        Args:
            infection_distance: Distance within which infection can occur (meters)
            infection_probability: Base probability of infection per contact
            incubation_time: Average time before symptoms appear
            presymptomatic_infectious_period: Days before symptoms when already infectious
            illness_duration: Average total duration of illness in days
            mortality_rate: Base probability of death
            severity_distribution: Distribution of case severities
            age_mortality_modifier: How age affects mortality rates
            time_to_recovery: Time to recovery by severity level
        """
        self.infection_distance = infection_distance
        self.infection_probability = infection_probability
        self.incubation_time = incubation_time
        self.presymptomatic_infectious_period = presymptomatic_infectious_period
        self.illness_duration = illness_duration
        self.mortality_rate = mortality_rate

        # Default severity distribution based on CDC/WHO data
        self.severity_distribution = severity_distribution or {
            DiseaseSeverity.ASYMPTOMATIC: 0.30,  # 30% asymptomatic
            DiseaseSeverity.MILD: 0.40,          # 40% mild symptoms
            DiseaseSeverity.MODERATE: 0.20,      # 20% moderate symptoms
            DiseaseSeverity.SEVERE: 0.08,        # 8% severe symptoms
            DiseaseSeverity.CRITICAL: 0.02       # 2% critical symptoms
        }

        # Age-based mortality rate modifiers (multipliers)
        self.age_mortality_modifier = age_mortality_modifier or {
            "0-9": 0.01,
            "10-19": 0.05,
            "20-29": 0.2,
            "30-39": 0.4,
            "40-49": 0.8,
            "50-59": 1.5,
            "60-69": 3.0,
            "70-79": 8.0,
            "80+": 15.0
        }

        # Recovery times by severity (in time steps)
        self.time_to_recovery = time_to_recovery or {
            DiseaseSeverity.ASYMPTOMATIC: 10,   # 10 days for asymptomatic
            DiseaseSeverity.MILD: 14,           # 14 days for mild cases
            DiseaseSeverity.MODERATE: 21,       # 21 days for moderate cases
            DiseaseSeverity.SEVERE: 28,         # 28 days for severe cases
            DiseaseSeverity.CRITICAL: 42        # 42 days for critical cases
        }

        # Mortality rates by severity
        self.mortality_by_severity = {
            DiseaseSeverity.ASYMPTOMATIC: 0.0001,
            DiseaseSeverity.MILD: 0.001,
            DiseaseSeverity.MODERATE: 0.01,
            DiseaseSeverity.SEVERE: 0.08,
            DiseaseSeverity.CRITICAL: 0.40
        }

    def get_random_severity(self):
        """
        Get a random disease severity based on the distribution.

        Returns:
            str: One of the DiseaseSeverity constants
        """
        import random
        rand = random.random()
        cumulative = 0
        for severity, probability in self.severity_distribution.items():
            cumulative += probability
            if rand <= cumulative:
                return severity
        return DiseaseSeverity.MILD  # Fallback

    def get_mortality_rate(self, severity, age_group=None):
        """
        Get mortality rate adjusted for severity and age.

        Args:
            severity: Disease severity
            age_group: Optional age group as string

        Returns:
            float: Adjusted mortality rate
        """
        base_rate = self.mortality_by_severity.get(
            severity, self.mortality_rate)

        if age_group and age_group in self.age_mortality_modifier:
            return base_rate * self.age_mortality_modifier[age_group]

        return base_rate

    def get_recovery_time(self, severity):
        """
        Get recovery time based on severity.

        Args:
            severity: Disease severity

        Returns:
            int: Time steps until recovery
        """
        # Add some randomness to recovery time
        import random
        base_time = self.time_to_recovery.get(severity, self.illness_duration)
        # ±20% variation in recovery time
        return int(base_time * random.uniform(0.8, 1.2))
