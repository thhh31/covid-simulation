import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from ..simulation.agent import AgentState

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from ..simulation.agent import AgentState

def animate_simulation_with_stats(simulation, frames=100, interval=200):
    """
    Animate the simulation and display real-time statistics.
    """
    # Set up the figure and subplots
    fig, (ax_sim, ax_stats) = plt.subplots(1, 2, figsize=(15, 7))
    
    # Simulation plot
    ax_sim.set_xlim(0, simulation.area_size)
    ax_sim.set_ylim(0, simulation.area_size)
    scatter = ax_sim.scatter([], [], s=10)
    ax_sim.set_title("Simulation")

    # Stats plot
    ax_stats.set_xlim(0, frames)
    ax_stats.set_ylim(0, simulation.num_agents)
    stats_lines = {
        'susceptible': ax_stats.plot([], [], label='Susceptible', lw=2)[0],
        'ill': ax_stats.plot([], [], label='Ill', lw=2)[0],
        'immune': ax_stats.plot([], [], label='Immune', lw=2)[0],
        'dead': ax_stats.plot([], [], label='Dead', lw=2)[0],
    }
    ax_stats.legend()
    ax_stats.set_title("Real-Time Statistics")
    ax_stats.set_xlabel("Time Step")
    ax_stats.set_ylabel("Number of Agents")

    # Data to be updated
    time_data = []
    stats_data = {
        'susceptible': [],
        'ill': [],
        'immune': [],
        'dead': [],
    }

    colors = {
        AgentState.SUSCEPTIBLE: 'blue',
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
        states = [agent.state for agent in simulation.agents if agent.state != AgentState.DEAD]
        scatter.set_offsets(positions)
        scatter.set_color([colors[state] for state in states])

        # Update statistics
        time_data.append(frame)
        stats_data['susceptible'].append(simulation.history['susceptible'][-1])
        stats_data['ill'].append(simulation.history['ill'][-1])
        stats_data['immune'].append(simulation.history['immune'][-1])
        stats_data['dead'].append(simulation.history['dead'][-1])

        for stat, line in stats_lines.items():
            line.set_data(time_data, stats_data[stat])

        ax_stats.relim()
        ax_stats.autoscale_view()

        return scatter, *stats_lines.values()

    # Create animation
    anim = FuncAnimation(
        fig, update, frames=frames, interval=interval, blit=False
    )
    plt.show()
    return anim
