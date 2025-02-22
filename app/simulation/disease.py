class Disease:
    """
    Represents the disease and its parameters.
    """
    def __init__(
        self,
        infection_distance=1.0,
        infection_probability=0.3,
        incubation_time=5,
        illness_duration=14,
        mortality_rate=0.02,
    ):
        self.infection_distance = infection_distance
        self.infection_probability = infection_probability
        self.incubation_time = incubation_time
        self.illness_duration = illness_duration
        self.mortality_rate = mortality_rate
