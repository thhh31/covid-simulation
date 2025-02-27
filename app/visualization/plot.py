import matplotlib.pyplot as plt
import numpy as np


def plot_history(simulation, title=None, save_path=None):
    """
    Plot the history of the simulation.

    Args:
        simulation: Simulation object with history data
        title: Optional custom title for the plot
        save_path: Optional path to save the figure
    """
    plt.figure(figsize=(12, 8))

    # Plot absolute numbers
    plt.subplot(2, 1, 1)
    plt.plot(simulation.history['susceptible'],
             label='Susceptible', color='blue', linewidth=2)
    plt.plot(simulation.history['ill'], label='Ill', color='red', linewidth=2)
    plt.plot(simulation.history['immune'],
             label='Immune', color='green', linewidth=2)
    plt.plot(simulation.history['dead'],
             label='Dead', color='black', linewidth=2)
    plt.plot(simulation.history['total_cases'], label='Total Cases',
             color='purple', linewidth=2, linestyle='--')

    plt.xlabel('Time Step')
    plt.ylabel('Number of Agents')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.title(title or 'Disease Spread Over Time')

    # Plot percentages
    plt.subplot(2, 1, 2)
    total_agents = simulation.num_agents
    susceptible_pct = [s/total_agents *
                       100 for s in simulation.history['susceptible']]
    ill_pct = [i/total_agents*100 for i in simulation.history['ill']]
    immune_pct = [im/total_agents*100 for im in simulation.history['immune']]
    dead_pct = [d/total_agents*100 for d in simulation.history['dead']]

    plt.stackplot(
        range(len(susceptible_pct)),
        [susceptible_pct, ill_pct, immune_pct, dead_pct],
        labels=['Susceptible', 'Ill', 'Immune', 'Dead'],
        colors=['blue', 'red', 'green', 'black'],
        alpha=0.7
    )

    plt.xlabel('Time Step')
    plt.ylabel('Percentage of Population')
    plt.legend(loc='upper right')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.title('Population Percentages Over Time')

    plt.tight_layout()

    # Save figure if path is provided
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')

    plt.show()


def plot_r0(simulation, window_size=5, save_path=None):
    """
    Plot the R0 value over time using a sliding window.

    Args:
        simulation: Simulation object
        window_size: Window size for calculating average R0
        save_path: Optional path to save the figure
    """
    # Calculate cumulative infections
    infections = [agent.infections_caused for agent in simulation.agents]
    total_infections = sum(infections)
    ill_count = sum(1 for agent in simulation.agents
                    if hasattr(agent, 'infections_caused') and agent.infections_caused > 0)

    # Calculate overall R0
    r0 = total_infections / max(1, ill_count)

    plt.figure(figsize=(10, 6))
    plt.bar(range(len(infections)), sorted(
        infections, reverse=True), color='red', alpha=0.7)
    plt.axhline(y=r0, color='black', linestyle='--',
                label=f'Average R₀: {r0:.2f}')

    plt.xlabel('Agent Index (sorted by infections caused)')
    plt.ylabel('Infections Caused')
    plt.title('Distribution of Infections Caused by Agents')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)

    # Save figure if path is provided
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')

    plt.show()
