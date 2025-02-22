import matplotlib.pyplot as plt

def plot_history(simulation):
    plt.figure(figsize=(10, 6))
    plt.plot(simulation.history['susceptible'], label='Susceptible')
    plt.plot(simulation.history['ill'], label='Ill')
    plt.plot(simulation.history['immune'], label='Immune')
    plt.plot(simulation.history['dead'], label='Dead')
    plt.plot(simulation.history['total_cases'], label='Total Cases')
    plt.xlabel('Time Step')
    plt.ylabel('Number of Agents')
    plt.legend()
    plt.title('Disease Spread Over Time')
    plt.show()
