from any question contact me at jacopo.dignazi@upf.edu or jacopodignazi@gmail.com

my_survey_static.__init__.py  will try to load "initial_popularity".csv and "previous_events.csv" upon starting
initial_popularity.csv contains seed-news-popularity float value for the first round of the experiment
previous_events contains all interactions from previous users (MUST match with initial_popularity.csv)
This is because the experiment carried on through multiple days and had to resume from previous state

If you want to continue from where our paper left, do not change anything and system will load most updated version of these files

If you want to start the experiment again, 
previous_events can be an empty csv
initial_popularity can be a csv of same current structure with any initial values of popularity 

INITIAL_initial_popularities is the values that the experiment E2 began with
which consisted in random small values (<1) to have an initial random ranking

initial_popularities is where the last step of the experiment began from
popularities is the final state of popularities (reports on paper are based on that file)


The code in code_simulation was the version used to run E2 of the paper
To run E1 (behavioral parameters estimation) set RAKING_RANDOMIZED=True in my_survey_static.__init__. This makes a lot of the code redundant (no need to update popularities) but works by randomizing ranking at each interaction, which is what E1 is built upon (see paper). 
For E1, during the experiment you can download data from otree interface; that can be straightforward loaded by simulation functions to extract behavioral parameters and run simulations
For E2, the analysis relies on interaction_events.csv data, that is generated through admin report of otree during the experiment. That file can be straightforward loaded by analysis functions to run E2 analysis (ex click distributions and metrics)
