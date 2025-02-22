from .simulation.simulation import Simulation
from .simulation.disease import Disease
from .visualization.animate import animate_simulation_with_stats
from .visualization.plot import plot_history
from .utils.logger import setup_logger
from .utils.config import Config

def start_simulation():
    logger = setup_logger(__name__)

    config = Config('config.yaml')
    sim_params = config.get('simulation')
    disease_params = config.get('disease')

    # Simulation parameters
    num_agents = sim_params['num_agents']
    area_size = sim_params['area_size']
    mobility = sim_params['mobility']
    initial_infected = sim_params['initial_infected']

    # Disease parameters
    disease = Disease(**disease_params)

    logger.info("Initializing simulation")
    sim = Simulation(
        num_agents=num_agents,
        area_size=area_size,
        mobility=mobility,
        disease=disease,
        initial_infected=initial_infected,
    )

    # Run animation
    logger.info("Starting animation")
    animate_simulation_with_stats(sim, frames=200, interval=100)

    # Alternatively, run simulation without animation and plot results
    # steps = 100
    # sim.run(steps)
    # plot_history(sim)
