This repository contains code and data relative to paper:
Rewarding Engagement and Personalization in Popularity-Based Rankings Amplifies Extremism and Polarization - D'Ignazi et al - KDD2026
arxiv: https://arxiv.org/abs/2510.24354
DOI: 10.1145/3770855.3818037
For any question or assistance using the code, contact me at jacopo.dignazi@upf.edu or jacopodignazi@gmail.com

In this folder:
- CODE_EXPERIMENT: OTREE code used for the experiment
- DATA: resulting data from those experiments, in csv
- CODE_SIMULATION: python code to run all simulations in that paper, based on the data of the experiment
- RESULTS_SIMULATION: pkl data results of the simulations, used in the final analysis
- CODE_ANALYSIS: python code to reproduce the analysis on experimental and simulated results
- environment.yml is the conda environment used across the whole work (all libraries and versions)

some parts of the code take data from other folders:
- simulation take data from DATA
- analysis takes data from DATA, CODE_SIMULATION, RESULTS_SIMULATION
- experiment code is a standalone and can be loaded on a server as it is (check readme in that folder for more details)
make sure to have the paths set up correctly, as all of the data loading use *relative* paths across folders

all provided data is user level and anonymus, with all information from our experiment questionnaire
data_exp_dynamic corresponds to E2 data
data_exp_static corresponds to E1 data

## Citation

If you use, reproduce, modify, extend, or build upon any part of the code, data, or materials contained in this repository, please cite the associated publication:

Jacopo D'Ignazi, Emma Fraxanet Morales, Andreas Kaltenbrunner, Gaël Le Mens, Fabrizio Germano, and Vicenç Gómez. *Rewarding Engagement and Personalization in Popularity-Based Rankings Amplifies Extremism and Polarization*. Proceedings of the 32nd ACM SIGKDD Conference on Knowledge Discovery and Data Mining (KDD '26), ACM, 2026. DOI: 10.1145/3770855.3818037.

Please also cite the corresponding Zenodo record for the specific artifact version used.

@inproceedings{dignazi2026rewarding,
  author = {Jacopo D'Ignazi and Emma Fraxanet Morales and Andreas Kaltenbrunner and Ga{\"e}l Le Mens and Fabrizio Germano and Vicen{\c{c}} G{\'o}mez},
  title = {Rewarding Engagement and Personalization in Popularity-Based Rankings Amplifies Extremism and Polarization},
  booktitle = {Proceedings of the 32nd ACM SIGKDD Conference on Knowledge Discovery and Data Mining (KDD '26)},
  year = {2026},
  publisher = {ACM},
  address = {Jeju Island, Republic of Korea},
  doi = {10.1145/3770855.3818037}
}


