import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Patch
from ..simulation.agent import AgentState


def animate_simulation_with_stats(simulation, frames=100, interval=200):
    """
    Animate the simulation and display real-time statistics.

    Args:
        simulation: Simulation object to animate
        frames: Number of frames to animate
        interval: Time between frames in milliseconds

    Returns:
        Animation object
    """
    # Set up the figure and subplots
    fig, (ax_sim, ax_stats) = plt.subplots(1, 2, figsize=(16, 8))

    # Simulation plot
    ax_sim.set_xlim(0, simulation.area_size)
    ax_sim.set_ylim(0, simulation.area_size)
    scatter = ax_sim.scatter([], [], s=30, alpha=0.8)
    ax_sim.set_title("COVID-19 Simulation")
    ax_sim.set_xlabel("X coordinate")
    ax_sim.set_ylabel("Y coordinate")

    # Draw obstacles if any
    for x, y, radius in simulation.environment.obstacles:
        circle = plt.Circle((x, y), radius, color='gray', alpha=0.5)
        ax_sim.add_patch(circle)

    # Add grid to simulation
    ax_sim.grid(linestyle='--', alpha=0.7)

    # Stats plot
    ax_stats.set_xlim(0, frames)
    ax_stats.set_ylim(0, simulation.num_agents)
    stats_lines = {
        'susceptible': ax_stats.plot([], [], label='Susceptible', lw=2, color='blue')[0],
        'exposed': ax_stats.plot([], [], label='Exposed', lw=2, color='orange')[0],
        'presymptomatic': ax_stats.plot([], [], label='Presymptomatic', lw=2, color='yellow')[0],
        'ill': ax_stats.plot([], [], label='Ill', lw=2, color='red')[0],
        'immune': ax_stats.plot([], [], label='Immune', lw=2, color='green')[0],
        'dead': ax_stats.plot([], [], label='Dead', lw=2, color='black')[0],
    }
    ax_stats.legend(loc='upper right')
    ax_stats.set_title("Disease Statistics")
    ax_stats.set_xlabel("Time Step")
    ax_stats.set_ylabel("Number of Agents")
    ax_stats.grid(True, linestyle='--', alpha=0.7)

    # Add a text annotation for R0
    r0_text = ax_sim.text(
        0.05, 0.95, "R₀: 0.00",
        transform=ax_sim.transAxes,
        fontsize=12,
        bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray')
    )

    # Add text annotations for current stats
    stats_text = ax_sim.text(
        0.05, 0.05,
        "",
        transform=ax_sim.transAxes,
        fontsize=9,
        bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray')
    )

    # Add new cases counter
    new_cases_text = ax_sim.text(
        0.05, 0.85, "New cases: 0",
        transform=ax_sim.transAxes,
        fontsize=10,
        bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray')
    )

    # Add legend for agent states
    state_legend_elements = [
        Patch(facecolor='blue', label='Susceptible'),
        Patch(facecolor='orange', label='Exposed'),
        Patch(facecolor='yellow', label='Presymptomatic'),
        Patch(facecolor='red', label='Ill'),
        Patch(facecolor='green', label='Immune'),
        Patch(facecolor='black', label='Dead'),
    ]
    ax_sim.legend(handles=state_legend_elements, loc='lower right',
                  title="Agent States", framealpha=0.7)

    # Data to be updated
    time_data = []
    stats_data = {
        'susceptible': [],
        'exposed': [],
        'presymptomatic': [],
        'ill': [],
        'immune': [],
        'dead': [],
    }

    # Define colors with better contrast
    colors = {
        AgentState.SUSCEPTIBLE: 'blue',
        AgentState.EXPOSED: 'orange',
        AgentState.PRESYMPTOMATIC: 'yellow',
        AgentState.ILL: 'red',
        AgentState.IMMUNE: 'green',
        AgentState.DEAD: 'black',
    }

    def update(frame):
        simulation.step()

        # Update scatter plot
        positions = np.array(
            [agent.position for agent in simulation.agents if agent.state != AgentState.DEAD]
        )
        states = [
            agent.state for agent in simulation.agents if agent.state != AgentState.DEAD]
        scatter.set_offsets(positions)
        scatter.set_color([colors[state] for state in states])

        # Update statistics
        time_data.append(frame)
        stats_data['susceptible'].append(simulation.history['susceptible'][-1])
        stats_data['exposed'].append(simulation.history['exposed'][-1])
        stats_data['presymptomatic'].append(
            simulation.history['presymptomatic'][-1])
        stats_data['ill'].append(simulation.history['ill'][-1])
        stats_data['immune'].append(simulation.history['immune'][-1])
        stats_data['dead'].append(simulation.history['dead'][-1])

        for stat, line in stats_lines.items():
            line.set_data(time_data, stats_data[stat])

        # Calculate R0 and update the text
        r0 = simulation.calculate_R0()
        r0_text.set_text(f"R₀: {r0:.2f}")

        # Update stats text
        stats_text.set_text(
            f"Susceptible: {simulation.history['susceptible'][-1]}\n"
            f"Exposed: {simulation.history['exposed'][-1]}\n"
            f"Presymptomatic: {simulation.history['presymptomatic'][-1]}\n"
            f"Ill: {simulation.history['ill'][-1]}\n"
            f"Immune: {simulation.history['immune'][-1]}\n"
            f"Dead: {simulation.history['dead'][-1]}"
        )

        # Update new cases text
        new_cases = simulation.history['new_cases'][-1] if simulation.history['new_cases'] else 0
        new_cases_text.set_text(f"New cases: {new_cases}")

        # Update plot limits if needed
        ax_stats.relim()
        ax_stats.autoscale_view()

        # Add a title with simulation time
        fig.suptitle(f"COVID-19 Simulation - Time Step: {frame} (Days)")

        return (scatter, *stats_lines.values(), r0_text, stats_text, new_cases_text)

    # Create animation
    anim = FuncAnimation(
        fig, update, frames=frames, interval=interval, blit=False
    )
    plt.tight_layout()
    plt.show()
    return anim
