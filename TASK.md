# COVID Simulator

## Problem Description

Write a agent-based simulator visualizing spread of an infectious disease. An agent is a single point in 2D space, representing a human being. The rules of the simulation are as follows:

1. The simulation should consist of a number of time-steps, in which each agent moves randomly by a distance defined by its mobility parameter _V_. The distance every agent moves in one time-step is chosen randomly in the range [0, 2×*V*].
2. Every agent can be in one of three states: _susceptible_, _ill_, or _immune_ (either vaccinated or after recovery). There is one more state possible: _dead_, which is equivalent to removing the agent from the simulation (however, the death count should be tracked).
3. If an _susceptible_ agent is within the distance _d_ (for COVID19 it is estimated to 1–2 m) from the _ill_ agent, there is a _p_ probability of changing the state to _ill_.
4. After incubation time _t_<sub>1</sub> (measured in time steps) from the infection, the mobility _v_ of the _ill_ agent is reduced to 0 (the person has developed symptoms and has been isolated).
5. After time _t_<sub>2</sub> from the infection, the state of _ill_ agent is changed to _immune_ or _dead_. The mortality rate _m_ is the probability of death.

Your task is to create an animation of the disease spread and plot the number of total cases, active cases and deaths as a function of time. You should investigate the spread of the disease depending on the parameters _V_, _p_, _t_<sub>1</sub>, _t_<sub>2</sub>, and _m_ and also of the total population number and average population density (average distance between the agents). In each case, estimate the number _R_<sub>0</sub>, which is an average number of _susceptible_ people every _ill_ person can infect. Investigate the impact of the social distancing (_V_ parameter — mind that it does not need to be equal for every individual) on the spread of the disease.

You can see a similar (although with different assumptions) simulation in a [Washington Post article](https://www.washingtonpost.com/graphics/2020/world/corona-simulator/). You are free to propose any improvements to the model to make it more realistic. Discuss it with the teacher as it can significantly improve your score.

## Program Requirements

Your code must be object-oriented and written in such a way that it can be easily improved and extended. In particular numerical part must be separate from input/output and data visualization. For making plots and animations you **must** use either Matplotlib or Plotly. However, changing the presentation part to something else should be straightforward.

The simulation code should allow to launch simulations, specify parameters and see the results. **In addition** you must present some investigations of the questions raised in the problem description (e.g. the impact of social distancing). Preferable format of such report is a Jupyter Notebook importing your module and running your code.

Your program should be started trough the `main.py` file.

Your mark will depend on two factors: how well your code fulfills the task (including model improvements) and the elegance and legibility of the code (you may want to read [Python Style Guide](https://www.python.org/dev/peps/pep-0008/) for some hints).
