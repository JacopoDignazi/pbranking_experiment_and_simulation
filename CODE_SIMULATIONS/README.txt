simulation_corner_cases generates simulation for the extreme cases of ranking algorithm parametrization (see fig.6 of the paper)

simulation_grid generate simulations for pairs within those corners, as in figure 5; as well as long-time simulation, as in figure 4.

simulation_grid_plots takes data from simulation_grid to generate graphs corresponding to figure 4,5

utils_analisys_for_simulation.py takes care of loading the data from data_exp_static (E1) and extracting behavioral parameters (see get_dch and fit_beta functions in that file)

simulation_functions.py contains functions to run the simulations, from single run level to grid and corner repetitions

all settings (ie metric window, number of repetitions, simulation length) are the same as the paper

All simulations use behavioral parameters estimated from data_exp_static, corresponding to data of E1 