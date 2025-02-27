# COVID-19 Simulation

An agent-based simulation model for visualizing and analyzing the spread of COVID-19 in a population.

## Features

-   Agent-based modeling of disease spread
-   Configurable simulation parameters
-   Real-time visualization of infection dynamics
-   Statistical tracking and reporting
-   Calculation of R0 (basic reproduction number)

## Requirements

-   Python 3.8+
-   Dependencies listed in `requirements.txt`

## Installation

1. Clone the repository
2. Create a virtual environment:
    ```
    python -m venv .venv
    ```
3. Activate the virtual environment:
    - Windows: `.venv\Scripts\activate`
    - Mac/Linux: `source .venv/bin/activate`
4. Install dependencies:
    ```
    pip install -r requirements.txt
    ```

## Usage

Run the simulation with default parameters:

```
python main.py
```

## Configuration

You can modify the simulation parameters in `config.yaml`:

```yaml
simulation:
    num_agents: 200 # Number of individuals
    area_size: 100 # Size of the simulation area
    mobility: 1.0 # Movement range per step
    initial_infected: 15 # Initial number of infected agents

disease:
    infection_distance: 2.0 # Distance within which infection can occur
    infection_probability: 0.3 # Probability of infection per contact
    incubation_time: 1 # Time steps before symptoms appear
    illness_duration: 14 # Total duration of illness
    mortality_rate: 0.02 # Probability of death
```

## Project Structure

-   `app/` - Main application code
    -   `simulation/` - Core simulation logic
    -   `visualization/` - Plotting and animation code
    -   `utils/` - Utility functions
-   `main.py` - Entry point for running the simulation
-   `config.yaml` - Configuration parameters

## Extending the Simulation

The modular design allows for easy extension:

-   Add new agent types by extending the `Agent` class
-   Implement different infection models in the `Disease` class
-   Create custom environments by modifying the `Environment` class

## License

MIT
