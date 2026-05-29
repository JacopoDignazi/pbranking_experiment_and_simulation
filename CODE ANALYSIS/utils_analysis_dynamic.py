############### YOUR PATHS HERE ############################################
pathname_articleinfo=f'../CODE_EXPERIMENT/my_survey_static/article_info.csv'
DATA_FOLDER='../DATA'

############################################################################

import pandas as pd
# MODEL_VERSION='A'
# MODEL_VERSION='A_unnorm'
# MODEL_VERSION='A_bal'
# MODEL_VERSION='A_unnorm_bal'
# MODEL_VERSION='B'
# MODEL_VERSION='B_unnorm'
MODEL_VERSION='C'


WINDOW_METRICS=200

METRIC_WINDOW=WINDOW_METRICS

IE=pd.read_csv(f'{DATA_FOLDER}/data_exp_dynamic/interaction_events.csv')
IE['seed']=IE['seed'].map(str)

SEEDS=sorted(IE['seed'].unique())


SEED2EVENTS={s: IE[IE['seed']==s] for s in SEEDS}
for s in SEEDS:
    SEED2EVENTS[s]['time_seed']=range(1, len(SEED2EVENTS[s])+1)
    
    
def check_model_version(model_v):
    if model_v[0] in ['A','B','C']:
        raise ImportError(model_v)
    if len(model_v)>2:
        if model_v[0]=='A':
            if not model_v[2:] in ['unnorm','bal','unnorm_bal']:
                raise ImportError(model_v)
        if model_v[2:] in ['unnorm']:
            raise ImportError(model_v)
import numpy as np

def get_seed_event_window(seed_events, time, window):
    min_idx=max(time-window, 0)
    max_idx=min(time, len(seed_events))
    event_window=seed_events[seed_events['time_seed']>min_idx][seed_events['time_seed']<=max_idx]
#     print(len(seed_events), min_idx, max_idx, len(event_window))
    return event_window

def seedevents2extremism(seed_events, time, window=WINDOW_METRICS):
    event_window=get_seed_event_window(seed_events, time, window)
    return np.abs(event_window['news_stance']).mean()

def seedevents2polarization(seed_events, time, window=WINDOW_METRICS):
    event_window=get_seed_event_window(seed_events, time, window)
    left_events=event_window[event_window['user_partition']==-1]
    right_events=event_window[event_window['user_partition']==1]
    if len(right_events)==0 or len(left_events)==0:
        return 0
    return np.abs(right_events['news_stance'].mean()-left_events['news_stance'].mean())

########################################### {seed: {time: ext and polarization}}
SEED2TIME_EXTREMISM={s:[1] for s in SEEDS}
SEED2TIME_POLARIZATION={s:[0] for s in SEEDS}

for time in range(1, int(np.ceil(len(IE)/len(SEEDS))+1+1)):
    for s in SEEDS:
#         print(time, s)
        SEED2TIME_EXTREMISM[s].append(seedevents2extremism(SEED2EVENTS[s], time))
        SEED2TIME_POLARIZATION[s].append(seedevents2polarization(SEED2EVENTS[s], time))

########################################### {seed: last value of ext and polarization}}
SEED2EXTREMISM={}
SEED2POLARIZATION={}

for s in SEEDS:
    SEED2EXTREMISM[s]=SEED2TIME_EXTREMISM[s][-1]
    SEED2POLARIZATION[s]=SEED2TIME_POLARIZATION[s][-1]
        
########################################### {par*topic:{time: avg and std, ext and pol across the 3 repetitions}}
pt2extremism_avg={}
pt2extremism_std={}
pt2polarization_avg={}
pt2polarization_std={}
for par in [1,2]:
    for top in [1,2,3,4]:
        pt2extremism_avg[str(par)+'*'+str(top)]=[]
        pt2extremism_std[str(par)+'*'+str(top)]=[]
        pt2polarization_avg[str(par)+'*'+str(top)]=[]
        pt2polarization_std[str(par)+'*'+str(top)]=[]

        for time in range(1, int(np.ceil(len(IE)/len(SEEDS))+1+1)):
            t_ext=[]
            t_pol=[]
            for exp in [1,2,3]:
                t_ext.append(SEED2TIME_EXTREMISM[str(par)+str(exp)+str(top)][time]) 
                t_pol.append(SEED2TIME_POLARIZATION[str(par)+str(exp)+str(top)][time]) 
            pt2extremism_avg[str(par)+'*'+str(top)].append(np.mean(t_ext))
            pt2extremism_std[str(par)+'*'+str(top)].append(np.std(t_ext))
            pt2polarization_avg[str(par)+'*'+str(top)].append(np.mean(t_pol))
            pt2polarization_std[str(par)+'*'+str(top)].append(np.std(t_pol))
            
            
METRICS_LAST_VALUE={'delta_extremism':{}, 'delta_polarization':{}}

for topic in [1,2,3,4]:
    METRICS_LAST_VALUE['delta_polarization'][topic]=(np.array(pt2polarization_avg['2*'+str(topic)])-np.array(pt2polarization_avg['1*'+str(topic)]))[-1]
    METRICS_LAST_VALUE['delta_extremism'][topic]=(np.array(pt2extremism_avg['2*'+str(topic)])-np.array(pt2extremism_avg['1*'+str(topic)]))[-1]
    
########################################### {par*topic: final value avg and std of ext and pol across the 3 repetitions}}

PT2FINAL_EXTREMISM_AVG=pd.DataFrame.from_dict(pd.DataFrame(pt2extremism_avg).iloc[-1].to_dict(), orient='index', columns=['obs_extremism_avg'])
PT2FINAL_EXTREMISM_STD=pd.DataFrame.from_dict(pd.DataFrame(pt2extremism_std).iloc[-1].to_dict(), orient='index', columns=['obs_extremism_std'])

PT2FINAL_POLARIZATION_AVG=pd.DataFrame.from_dict(pd.DataFrame(pt2polarization_avg).iloc[-1].to_dict(), orient='index', columns=['obs_polarization_avg'])
PT2FINAL_POLARIZATION_STD=pd.DataFrame.from_dict(pd.DataFrame(pt2polarization_std).iloc[-1].to_dict(), orient='index', columns=['obs_polarization_std'])

########################################### {par:{time: avg and std of ext and pol across all exp with the same parametrization}}
overall_s2ext_avg={1:[], 2:[]}
overall_s2ext_std={1:[], 2:[]}

for time in range(1, int(np.ceil(len(IE)/len(SEEDS))+1+1)):
    val_1=[]
    val_2=[]
    for s, v in SEED2TIME_EXTREMISM.items():
        if s.startswith('1'):
            val_1.append(v[time])
        if s.startswith('2'):
            val_2.append(v[time])
            
    overall_s2ext_avg[1].append(np.mean(val_1))
    overall_s2ext_std[1].append(np.std(val_1))
    
    overall_s2ext_avg[2].append(np.mean(val_2))
    overall_s2ext_std[2].append(np.std(val_2))
    
overall_s2pol_avg={1:[], 2:[]}
overall_s2pol_std={1:[], 2:[]}

for time in range(1, int(np.ceil(len(IE)/len(SEEDS))+1+1)):
    val_1=[]
    val_2=[]
    for s, v in SEED2TIME_POLARIZATION.items():
        if s.startswith('1'):
            val_1.append(v[time])
        if s.startswith('2'):
            val_2.append(v[time])
            
    overall_s2pol_avg[1].append(np.mean(val_1))
    overall_s2pol_std[1].append(np.std(val_1))
    
    overall_s2pol_avg[2].append(np.mean(val_2))
    overall_s2pol_std[2].append(np.std(val_2))
    
overall_s2ext_delta=np.array(overall_s2ext_avg[2])-np.array(overall_s2ext_avg[1])
overall_s2pol_delta=np.array(overall_s2pol_avg[2])-np.array(overall_s2pol_avg[1])



################################## chi square test
def get_seed_event_window(seed_events, time, window):
    min_idx=max(time-window, 0)
    max_idx=min(time, len(seed_events))
    event_window=seed_events[seed_events['time_seed']>min_idx][seed_events['time_seed']<=max_idx]
#     print(len(seed_events), min_idx, max_idx, len(event_window))
    return event_window

#------------------ topic: parametrization: dataframe of events
PT2EV={t:{p:[] for p in [1,2]}for t in [1,2,3,4]}
for par in [1,2]:
    for topic in [1,2,3,4]:
        for iteration in [1,2,3]:
            seed=str(par)+str(iteration)+str(topic)
            PT2EV[topic][par].append(get_seed_event_window(SEED2EVENTS[seed], len(SEED2EVENTS[seed]), METRIC_WINDOW))
        PT2EV[topic][par]=pd.concat(PT2EV[topic][par], ignore_index=True)
        
#------------------ parametrization: dataframe of events
P2EV={p:[] for p in [1,2]}
for par in [1,2]:
    for topic in [1,2,3,4]:
        for iteration in [1,2,3]:
            seed=str(par)+str(iteration)+str(topic)
#             print(par, seed)
            P2EV[par].append(get_seed_event_window(SEED2EVENTS[seed], len(SEED2EVENTS[seed]), METRIC_WINDOW))
    P2EV[par]=pd.concat(P2EV[par], ignore_index=True)
        
import random as rnd

def click_list_to_count(click_list):
    count={v: 0 for v in [-2,-1,0,1,2]}
    for v in click_list:
        count[v]+=1
    return count

def boostrap_click_list(click_list, n_samples=100):
    distributions=[]
    
    for _ in range(n_samples):
        resampled_click_list=rnd.choices(click_list, k=len(click_list))
        count=click_list_to_count(resampled_click_list)
        distributions.append([count[v] for v in [-2,-1,0,1,2]])
    distributions=np.array(distributions)
    
    distr_avg=distributions.mean(axis=0)
    distr_std=distributions.std(axis=0)
    
#     print(distributions)
    
    return distr_avg, distr_std


import numpy as np
from scipy.stats import chi2_contingency

import matplotlib.pyplot as plt

def chi2_test(list_1, list_2, title_prefix='', colors=('c','r')):
    cc_1=click_list_to_count(list_1)
    print(cc_1)
    cc_2=click_list_to_count(list_2)
    
    cc_1_avg, cc_1_std=boostrap_click_list(list_1)
    cc_2_avg, cc_2_std=boostrap_click_list(list_2)
    print(        [cc_1[v] for v in [-2,-1,0,1,2]])
    table=np.array([
        [cc_1[v] for v in [-2,-1,0,1,2]],
        [cc_2[v] for v in [-2,-1,0,1,2]],
    ]
    )
    
    chi2, p, dof, expected = chi2_contingency(table)
    residuals = (table - expected) / np.sqrt(expected)
    
    plt.bar(np.array([-2,-1,0,1,2])-0.2, cc_1_avg/cc_1_avg.sum(), yerr=cc_1_std/cc_1_avg.sum(), 
            color=colors[0], capsize=3, width=0.35, label='par 1')
    plt.bar(np.array([-2,-1,0,1,2])+0.2, cc_2_avg/cc_2_avg.sum(), yerr=cc_2_std/cc_2_avg.sum(), 
            color=colors[1], capsize=3, width=0.35, label='par 2')
    plt.title(title_prefix+f" p={p:.3f}")
    plt.xticks([-2,-1,0,1,2], ['EL','ML','C','MR','ER'])
    plt.xlabel("News stance")
    plt.legend()
#     plt.grid()
    
    print("Table:")
    print(table/table.sum(axis=1, keepdims=True))
    print("Chi-square statistic:", chi2)
    print("p-value:", p)
#     print("Expected counts:\n", expected)
    print("Standardized residuals:\n", residuals.round(2))
    
    return (cc_1_avg, cc_1_std), (cc_2_avg, cc_2_std)
    
    
# chi2_test(PT2EV[topic][1]['news_stance'].tolist(), PT2EV[topic][2]['news_stance'].tolist())

def treeway_chi2_test(list_1, list_2, list_3, title_prefix=''):
    cc_1=click_list_to_count(list_1)
    cc_2=click_list_to_count(list_2)
    cc_3=click_list_to_count(list_3)

    
    table_12=np.array([
        [cc_1[v] for v in [-2,-1,0,1,2]],
        [cc_2[v] for v in [-2,-1,0,1,2]],
    ]
    )
    table_23=np.array([
        [cc_2[v] for v in [-2,-1,0,1,2]],
        [cc_3[v] for v in [-2,-1,0,1,2]],
    ]
    )
    table_13=np.array([
        [cc_1[v] for v in [-2,-1,0,1,2]],
        [cc_3[v] for v in [-2,-1,0,1,2]],
    ]
    )
    
    
    chi2_12, p_12, dof_12, expected_12 = chi2_contingency(table_12)
    residuals_12 = (table_12 - expected_12) / np.sqrt(expected_12)
    chi2_23, p_23, dof_23, expected_23 = chi2_contingency(table_23)
    residuals_23 = (table_23 - expected_23) / np.sqrt(expected_23)
    chi2_13, p_13, dof_13, expected_13 = chi2_contingency(table_13)
    residuals_13 = (table_13 - expected_13) / np.sqrt(expected_13)
    
    cc_1_avg, cc_1_std=boostrap_click_list(list_1)
    cc_2_avg, cc_2_std=boostrap_click_list(list_2)
    cc_3_avg, cc_3_std=boostrap_click_list(list_3)

    plt.bar(np.array([-2,-1,0,1,2])-0.25, cc_1_avg/cc_1_avg.sum(), yerr=cc_1_std/cc_1_avg.sum(), capsize=2, width=0.20, label='par 1')
    plt.bar(np.array([-2,-1,0,1,2])+0.0, cc_2_avg/cc_2_avg.sum(), yerr=cc_2_std/cc_2_avg.sum(), capsize=2, width=0.20, label='static')
    plt.bar(np.array([-2,-1,0,1,2])+0.25, cc_3_avg/cc_3_avg.sum(), yerr=cc_3_std/cc_3_avg.sum(), capsize=2, width=0.20, label='par 2')
    
    plt.title(title_prefix+f" p=({p_12:.3f},{p_23:.3f},{p_13:.3f})")
    plt.xticks([-2,-1,0,1,2], ['EL','ML','C','MR','ER'])
    plt.xlabel("News stance")
    plt.legend()
    plt.grid()
    
#     print("Table:")
#     print(table/table.sum(axis=1, keepdims=True))
#     print("Chi-square statistic:", chi2)
    print(f" p=({p_12:.3f},{p_23:.3f},{p_13:.3f})")
#     print("Expected counts:\n", expected)
#     print("Standardized residuals:\n", residuals.round(2))
    return (cc_1_avg, cc_1_std), (cc_2_avg, cc_2_std), (cc_3_avg, cc_3_std)

################################################## comparison with simulation
EXPERIMENT_RESULTS=pd.merge(PT2FINAL_EXTREMISM_AVG,PT2FINAL_EXTREMISM_STD, left_index=True, right_index=True)
EXPERIMENT_RESULTS=pd.merge(EXPERIMENT_RESULTS,PT2FINAL_POLARIZATION_AVG, left_index=True, right_index=True)
EXPERIMENT_RESULTS=pd.merge(EXPERIMENT_RESULTS,PT2FINAL_POLARIZATION_STD, left_index=True, right_index=True)

import pickle
input_path = f"../RESULTS_SIMULATION/simulation_metrics.pkl"
with open(input_path, "rb") as f:
    TABLE_RESULTS = pickle.load(f)
SIMULATION_RESULTS=pd.DataFrame(TABLE_RESULTS).T
 
DYNAMIC_RESULTS=pd.merge(EXPERIMENT_RESULTS, SIMULATION_RESULTS, left_index=True, right_index=True)

_RES_COLS=['obs_extremism_avg','obs_extremism_std','sim_extremism_avg','sim_extremism_std','obs_polarization_avg','obs_polarization_std','sim_polarization_avg','sim_polarization_std']
DYNAMIC_RESULTS=DYNAMIC_RESULTS[_RES_COLS]

RESULTS_DISPLAY=pd.DataFrame(index=DYNAMIC_RESULTS.index)
RESULTS_DISPLAY['obs_extremism']=DYNAMIC_RESULTS.round(2)['obs_extremism_avg'].map(str)+'+-'+DYNAMIC_RESULTS.round(2)['obs_extremism_std'].map(str)
RESULTS_DISPLAY['sim_extremism']=DYNAMIC_RESULTS.round(2)['sim_extremism_avg'].map(str)+'+-'+DYNAMIC_RESULTS.round(2)['sim_extremism_std'].map(str)

RESULTS_DISPLAY['obs_polarization']=DYNAMIC_RESULTS.round(2)['obs_polarization_avg'].map(str)+'+-'+DYNAMIC_RESULTS.round(2)['obs_polarization_std'].map(str)
RESULTS_DISPLAY['sim_polarization']=DYNAMIC_RESULTS.round(2)['sim_polarization_avg'].map(str)+'+-'+DYNAMIC_RESULTS.round(2)['sim_polarization_std'].map(str)


RESULTS_DELTA={t:{} for t in [1,2,3,4]}

for topic in [1,2,3,4]:
    RESULTS_DELTA[topic]['delta_extremism_obs']=(DYNAMIC_RESULTS.loc[f'2*{topic}']-DYNAMIC_RESULTS.loc[f'1*{topic}'])['obs_extremism_avg']
    RESULTS_DELTA[topic]['delta_extremism_sim']=(DYNAMIC_RESULTS.loc[f'2*{topic}']-DYNAMIC_RESULTS.loc[f'1*{topic}'])['sim_extremism_avg']
    RESULTS_DELTA[topic]['delta_polarization_obs']=(DYNAMIC_RESULTS.loc[f'2*{topic}']-DYNAMIC_RESULTS.loc[f'1*{topic}'])['obs_polarization_avg']
    RESULTS_DELTA[topic]['delta_polarization_sim']=(DYNAMIC_RESULTS.loc[f'2*{topic}']-DYNAMIC_RESULTS.loc[f'1*{topic}'])['sim_polarization_avg']


# ----------- loading from data
input_path = f"../RESULTS_SIMULATION/simulation_clicks.pkl"
with open(input_path, "rb") as f:
    CLICK_PARTITIONWISE_SIMULATED = pickle.load(f)