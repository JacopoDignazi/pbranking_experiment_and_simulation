utils_analysis, utils_analysis_dynamic and load_dyn_data take care of loading data from all needed sources and define some macros for analysis

hypothesis_test includes all analysis reported in the paper in results section

MW_time_dependent is the statistical test on the metrics (ext and pol) done block-wise with different sizes to account for tipe dependency in the metrics. Values of significance for ext and pol metrics are obtained in hypothesis_test with the smallest block size, aggregating all clicks for each metric and topic

final analysis extract data from all adjacent folders:
- takes from CODE_EXPERIMENT for article info, topic info, popularities.csv and previous_events.csv
- takes from RESULTS_SIMULATION to estimated simulated metrics and simulated click distributions (see fig 7-8)
- takes from DATA to
- - data_exp_static verify H1-H3 on E1
- - data exp_dynamic for metrics on E2

loading can be susceptible to pandas version so make sure to install environment.yml to reproduce or build upon these results