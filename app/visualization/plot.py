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
    plt.figure(figsize=(12, 10))

    # Plot absolute numbers
    plt.subplot(3, 1, 1)
    plt.plot(simulation.history['susceptible'],
             label='Susceptible', color='blue', linewidth=2)
    plt.plot(simulation.history['exposed'],
             label='Exposed', color='orange', linewidth=2)
    plt.plot(simulation.history['presymptomatic'],
             label='Presymptomatic', color='yellow', linewidth=2)
    plt.plot(simulation.history['ill'], label='Ill', color='red', linewidth=2)
    plt.plot(simulation.history['immune'],
             label='Immune', color='green', linewidth=2)
    plt.plot(simulation.history['dead'],
             label='Dead', color='black', linewidth=2)
    plt.plot(simulation.history['total_cases'], label='Total Cases',
             color='purple', linewidth=2, linestyle='--')

    plt.xlabel('Time Step (Days)')
    plt.ylabel('Number of Agents')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.title(title or 'Disease Spread Over Time')

    # Plot percentages
    plt.subplot(3, 1, 2)
    total_agents = simulation.num_agents
    susceptible_pct = [s/total_agents *
                       100 for s in simulation.history['susceptible']]
    exposed_pct = [e/total_agents *
                   100 for e in simulation.history['exposed']]
    presymptomatic_pct = [p/total_agents *
                          100 for p in simulation.history['presymptomatic']]
    ill_pct = [i/total_agents*100 for i in simulation.history['ill']]
    immune_pct = [im/total_agents*100 for im in simulation.history['immune']]
    dead_pct = [d/total_agents*100 for d in simulation.history['dead']]

    plt.stackplot(
        range(len(susceptible_pct)),
        [susceptible_pct, exposed_pct, presymptomatic_pct,
            ill_pct, immune_pct, dead_pct],
        labels=['Susceptible', 'Exposed',
                'Presymptomatic', 'Ill', 'Immune', 'Dead'],
        colors=['blue', 'orange', 'yellow', 'red', 'green', 'black'],
        alpha=0.7
    )

    plt.xlabel('Time Step (Days)')
    plt.ylabel('Percentage of Population')
    plt.legend(loc='upper right')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.title('Population Percentages Over Time')

    # Plot new cases per day
    plt.subplot(3, 1, 3)
    plt.bar(range(len(simulation.history['new_cases'])),
            simulation.history['new_cases'],
            color='red', alpha=0.7)
    plt.xlabel('Time Step (Days)')
    plt.ylabel('New Cases')
    plt.title('New COVID-19 Cases Per Day')
    plt.grid(True, linestyle='--', alpha=0.7)

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

    plt.figure(figsize=(10, 8))

    # Plot R0 over time
    plt.subplot(2, 1, 1)
    plt.plot(simulation.history['r0'],
             label='R₀ over time', color='red', linewidth=2)
    plt.axhline(y=r0, color='black', linestyle='--',
                label=f'Average R₀: {r0:.2f}')
    plt.xlabel('Time Step (Days)')
    plt.ylabel('R₀ Value')
    plt.title('Reproduction Number Over Time')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)

    # Plot distribution of infections
    plt.subplot(2, 1, 2)
    plt.bar(range(len(infections)), sorted(
        infections, reverse=True), color='red', alpha=0.7)
    plt.axhline(y=r0, color='black', linestyle='--',
                label=f'Average R₀: {r0:.2f}')
    plt.xlabel('Agent Index (sorted by infections caused)')
    plt.ylabel('Infections Caused')
    plt.title('Distribution of Infections Caused by Agents')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)

    plt.tight_layout()

    # Save figure if path is provided
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')

    plt.show()


def plot_severity_distribution(simulation, save_path=None):
    """
    Plot the distribution of disease severity among infected agents.

    Args:
        simulation: Simulation object
        save_path: Optional path to save the figure
    """
    stats = simulation.get_stats_by_severity()

    # Create pie chart of severity percentages
    plt.figure(figsize=(12, 6))

    # Filter out unknown and zero values
    labels = []
    sizes = []
    colors = ['lightgreen', 'yellow', 'orange', 'red', 'darkred']
    filtered_values = [(k, v) for k, v in stats['percentages'].items()
                       if k != 'unknown' and v > 0]

    for severity, percentage in filtered_values:
        labels.append(f"{severity}: {percentage:.1f}%")
        sizes.append(stats['counts'][severity])

    plt.subplot(1, 2, 1)
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
            shadow=True, startangle=90)
    # Equal aspect ratio ensures that pie is drawn as a circle
    plt.axis('equal')
    plt.title('COVID-19 Severity Distribution')

    # Create bar chart of case counts
    plt.subplot(1, 2, 2)
    severity_order = ['asymptomatic', 'mild', 'moderate', 'severe', 'critical']
    counts = [stats['counts'][sev]
              for sev in severity_order if stats['counts'][sev] > 0]
    labels = [sev for sev in severity_order if stats['counts'][sev] > 0]

    plt.bar(labels, counts, color=colors[:len(labels)])
    plt.xlabel('Severity Level')
    plt.ylabel('Number of Cases')
    plt.title('COVID-19 Case Counts by Severity')
    plt.xticks(rotation=45)

    plt.tight_layout()

    # Save figure if path is provided
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')

    plt.show()
