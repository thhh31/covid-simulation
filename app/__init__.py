import argparse
import os
import sys

from .simulation.simulation import Simulation
from .simulation.disease import Disease
from .visualization.animate import animate_simulation_with_stats
from .visualization.plot import plot_history, plot_r0
from .utils.logger import setup_logger
from .utils.config import Config


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='COVID-19 Simulation')
    parser.add_argument('--config', type=str, default='config.yaml',
                        help='Path to configuration file')
    parser.add_argument('--no-animation', action='store_true',
                        help='Run simulation without animation')
    parser.add_argument('--steps', type=int, default=200,
                        help='Number of simulation steps')
    parser.add_argument('--interval', type=int, default=100,
                        help='Animation interval in milliseconds')
    parser.add_argument('--save-plots', action='store_true',
                        help='Save plots to output directory')
    parser.add_argument('--output-dir', type=str, default='output',
                        help='Directory for output files')
    return parser.parse_args()


def start_simulation():
    """
    Start the COVID-19 simulation with parameters from config or command line.
    """
    # Parse command line arguments
    args = parse_args()

    # Setup logger
    logger = setup_logger(__name__)

    # Create output directory if saving plots
    if args.save_plots:
        os.makedirs(args.output_dir, exist_ok=True)
        logger.info(f"Output will be saved to {args.output_dir}")

    # Load configuration
    try:
        config = Config(args.config)
        sim_params = config.get('simulation')
        disease_params = config.get('disease')
        env_params = config.get('environment', {})
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        sys.exit(1)

    # Simulation parameters
    num_agents = sim_params.get('num_agents', 200)
    area_size = sim_params.get('area_size', 100)
    mobility = sim_params.get('mobility', 1.0)
    initial_infected = sim_params.get('initial_infected', 5)

    # Environment setup
    boundary_type = env_params.get('boundary_type', 'periodic')
    from .simulation.environment import BoundaryType, Environment

    # Create environment with specified boundary type
    if boundary_type.lower() == 'periodic':
        env_boundary = BoundaryType.PERIODIC
    elif boundary_type.lower() == 'reflecting':
        env_boundary = BoundaryType.REFLECTING
    elif boundary_type.lower() == 'absorbing':
        env_boundary = BoundaryType.ABSORBING
    else:
        logger.warning(
            f"Unknown boundary type '{boundary_type}', using 'periodic'")
        env_boundary = BoundaryType.PERIODIC

    environment = Environment(area_size, boundary_type=env_boundary)

    # Add obstacles if specified
    obstacles = env_params.get('obstacles', [])
    for obstacle in obstacles:
        try:
            x, y, radius = obstacle
            environment.add_obstacle(x, y, radius)
            logger.info(f"Added obstacle at ({x}, {y}) with radius {radius}")
        except (ValueError, TypeError):
            logger.warning(
                f"Invalid obstacle format: {obstacle}. Expected (x, y, radius)")

    # Disease parameters
    disease = Disease(**disease_params)

    logger.info(f"Initializing simulation with {num_agents} agents")
    sim = Simulation(
        num_agents=num_agents,
        area_size=area_size,
        mobility=mobility,
        disease=disease,
        environment=environment,
        initial_infected=initial_infected,
    )

    # Run simulation
    if args.no_animation:
        logger.info(
            f"Running simulation for {args.steps} steps without animation")
        sim.run(args.steps)

        # Save results if requested
        if args.save_plots:
            results_file = os.path.join(args.output_dir, 'results.json')
            sim.save_results(results_file)
            logger.info(f"Saved results to {results_file}")

        # Generate and save plots
        logger.info("Generating plots")
        if args.save_plots:
            plot_history(sim, save_path=os.path.join(
                args.output_dir, 'history.png'))
            plot_r0(sim, save_path=os.path.join(args.output_dir, 'r0.png'))
        else:
            plot_history(sim)
            plot_r0(sim)

        # Print summary statistics
        print("\nSimulation Summary:")
        print(f"Total population: {sim.num_agents}")
        print(
            f"Final susceptible: {sim.history['susceptible'][-1]} ({sim.history['susceptible'][-1]/sim.num_agents*100:.1f}%)")
        print(
            f"Final ill: {sim.history['ill'][-1]} ({sim.history['ill'][-1]/sim.num_agents*100:.1f}%)")
        print(
            f"Final immune: {sim.history['immune'][-1]} ({sim.history['immune'][-1]/sim.num_agents*100:.1f}%)")
        print(
            f"Final dead: {sim.history['dead'][-1]} ({sim.history['dead'][-1]/sim.num_agents*100:.1f}%)")
        print(f"Basic reproduction number (R₀): {sim.calculate_R0():.2f}")
    else:
        # Run animation
        logger.info(
            f"Starting animation for {args.steps} frames with {args.interval}ms interval")
        animate_simulation_with_stats(
            sim, frames=args.steps, interval=args.interval)
