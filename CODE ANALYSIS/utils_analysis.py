############### YOUR PATHS HERE ############################################
pathname_articleinfo=f'../CODE_EXPERIMENT/my_survey_static/article_info.csv'
DATA_FOLDER='../DATA'

############################################################################


import pandas as pd
import numpy as np

POSSIBLE_STANCES=[-2,-1,0,1,2]

N2TOPIC={
    1:'gender',
    2:'vaccines',
    3:'immigration',
    4:'climate',
}

DROP_RULES=[]

def ideology_to_value(ideology):
    try:
        if ideology[0]=='D':
            return -1
        if ideology[0]=='R':
            return 1
        return 0
    except:
        return -1

def strength_to_value(strength):
    if strength[0]=='C':
        return 1
    if strength[0]=='M':
        return 1
    if strength[0]=='S':
        return 2
    
def center_to_value(center):
    if center[0]=='C':
        return 0
    if center[0]=='D':
        return -1
    if center[0]=='R':
        return 1
    
def gender_to_value(gender):
    if gender[0]=='M':
        return -1
    if gender[0]=='F':
        return 1
    return 0
    
def age_to_value(age):
    if age[0].startswith('P'):
        return -1
    return int(age[0])    



def load_results(experiment_versions):
    N_ROUNDS=4
    
    if not isinstance(experiment_versions, list):
        experiment_versions=[experiment_versions]
#     RES=pd.DataFrame()
    dfs = []

    for ev in experiment_versions:
        pathname = f"{DATA_FOLDER}/data_exp_static/{ev}/results.csv"
        print(ev)
        df = pd.read_csv(pathname)
        dfs.append(df)

    RES = pd.concat(dfs, ignore_index=True)
    
    
    print("Number of valid entries:", len(RES[~RES['demographics_and_payment.1.player.gender'].isna()]))
    RES=RES[~RES['demographics_and_payment.1.player.gender'].isna()]
    
    A_INFO=pd.read_csv(pathname_articleinfo)
    
    AID2STANCE=A_INFO.set_index('article_id')['stance'].to_dict()
    AID2SOURCE=A_INFO.set_index('article_id')['source'].to_dict()

    for i in range(1, N_ROUNDS+1):
        RES[f'my_survey_static.{i}.player.positioning_true']=\
        RES[f'my_survey_static.{i}.player.click_id'].map(lambda x: AID2STANCE[int(x)])

    PARTICIPANT_LABEL=[]

    for i in range(1,N_ROUNDS+1):
        PARTICIPANT_LABEL+=RES['participant.label'].tolist()

    ROUND_COLUMN=[]

    for i in range(1,N_ROUNDS+1):
        ROUND_COLUMN+=[i]*len(RES)

    ROUND_TOPIC=[]

    for i in range(1, N_ROUNDS+1):
        ROUND_TOPIC+=RES[f'my_survey_static.{i}.player.topic_number'].map(int).tolist()
    


    GENDER=[]
    AGE=[]

    for i in range(1,N_ROUNDS+1):
        GENDER+=RES['demographics_and_payment.1.player.gender'].map(gender_to_value).tolist()
        AGE+=RES['demographics_and_payment.1.player.age'].map(age_to_value).tolist()


    STANCE_GEN=[]
    STANCE_GEN_CENTERED=[]

    for i in range(1,N_ROUNDS+1):
        stance_gen=RES['ideology.1.player.leaning'].map(ideology_to_value)
        stance_gen*=RES['ideology.1.player.leaning_strength'].fillna("C").map(strength_to_value)
        STANCE_GEN_CENTERED+=stance_gen.tolist()
        stance_gen+=RES['ideology.1.player.center_strength'].fillna("C").map(center_to_value)
        STANCE_GEN+=stance_gen.tolist()


    STANCE_GEN=[]
    STANCE_GEN_CENTERED=[]

    for i in range(1,N_ROUNDS+1):
        stance_gen=RES['ideology.1.player.leaning'].map(ideology_to_value)
        stance_gen*=RES['ideology.1.player.leaning_strength'].fillna("C").map(strength_to_value)
        STANCE_GEN_CENTERED+=stance_gen.tolist()
        stance_gen+=RES['ideology.1.player.center_strength'].fillna("C").map(center_to_value)
        STANCE_GEN+=stance_gen.tolist()

    STANCE_TOPICWISE=[]

    for i in range(1,N_ROUNDS+1):
        STANCE_TOPICWISE+=RES[f'my_survey_static.{i}.player.positioning_user'].tolist()

    CLICK_ID=[]
    CLICK_RANK=[]
    HIGHLIGHT=[]
    STANCE_TEXT_PERCEIVED=[]
    STANCE_TEXT_TRUE=[]


    for i in range(1,N_ROUNDS+1):
        CLICK_ID+=RES[f'my_survey_static.{i}.player.click_id'].tolist()
        CLICK_RANK+=RES[f'my_survey_static.{i}.player.click_rank'].tolist()
        HIGHLIGHT+=RES[f'my_survey_static.{i}.player.highlight'].tolist()
        STANCE_TEXT_PERCEIVED+=RES[f'my_survey_static.{i}.player.positioning_text'].tolist()
        STANCE_TEXT_TRUE+=RES[f'my_survey_static.{i}.player.positioning_true'].tolist()

    NEWS_SOURCE=[AID2SOURCE[idx] for idx in CLICK_ID]

    T_POSITIONING= []
    T_TAKSEXPLAINATION= []
    T_RANKING= []
    T_HIGHLIGHT= []

    for i in range(1,N_ROUNDS+1):
        T_POSITIONING+=RES[f'my_survey_static.{i}.player.time_positioning'].tolist()
        T_TAKSEXPLAINATION+=RES[f'my_survey_static.{i}.player.time_taskexplaination'].tolist()
        T_RANKING+=RES[f'my_survey_static.{i}.player.time_rankig'].tolist()
        T_HIGHLIGHT+=RES[f'my_survey_static.{i}.player.time_highlight'].tolist()


    RESULTS=pd.DataFrame()

    RESULTS['player_id']=PARTICIPANT_LABEL
    RESULTS['round']=ROUND_COLUMN
    RESULTS['topic']=ROUND_TOPIC


    RESULTS['gender']=GENDER
    RESULTS['age']=AGE

    RESULTS['stance_user']=STANCE_GEN
    RESULTS['stance_user_topicwise']=STANCE_TOPICWISE

    RESULTS['click_id']=CLICK_ID
    RESULTS['click_rank']=CLICK_RANK
    RESULTS['highlight']=HIGHLIGHT
    RESULTS['share']=RESULTS['highlight'].map(lambda x: 1 if x in [1,2] else 0)

    RESULTS['stance_text_perc']=STANCE_TEXT_PERCEIVED
    RESULTS['stance_text_true']=STANCE_TEXT_TRUE

    RESULTS['perception_distance']=np.abs(RESULTS['stance_text_perc']-RESULTS['stance_text_true'])

    RESULTS['stance_distance']=np.abs(RESULTS['stance_text_true']-RESULTS['stance_user_topicwise'])

    RESULTS['partition_user']=RESULTS['stance_user'].map(lambda x: np.sign(x))
    RESULTS['partition_user_topicwise']=RESULTS['stance_user_topicwise'].map(lambda x: np.sign(x))
    RESULTS['partition_text_perc']=RESULTS['stance_text_perc'].map(lambda x: np.sign(x))
    RESULTS['partition_text_true']=RESULTS['stance_text_true'].map(lambda x: np.sign(x))

    RESULTS['click_same_partition']=np.abs(RESULTS['partition_user_topicwise']-RESULTS['partition_text_true']).map(lambda x: 1 if x>=1 else 0)

    RESULTS['news_source']=NEWS_SOURCE

    RESULTS['time_positioning']=T_POSITIONING
    RESULTS['time_taskexplaination']=T_TAKSEXPLAINATION
    RESULTS['time_ranking']=T_RANKING
    RESULTS['time_highlight']=T_HIGHLIGHT

    RESULTS['stance_text_error']=np.abs(RESULTS['stance_text_true']-RESULTS['stance_text_perc'])

    U2ERROR={}

    for user in RESULTS['player_id'].unique():
        u_res=RESULTS[RESULTS['player_id']==user]
        U2ERROR[user]=u_res['stance_text_error'].mean()

    RESULTS['user_avgerror']=RESULTS['player_id'].map(lambda x: U2ERROR[x])

    RESULTS['time_decision']=0
    for c in ['time_positioning', 'time_ranking', 'time_highlight']:
        RESULTS['time_decision']+= RESULTS[c]

    user_to_avgtime = (
        RESULTS.groupby('player_id')['time_decision']
        .mean()
        .to_dict()
    )    
    RESULTS['user_avgtime']=RESULTS['player_id'].map(lambda x: user_to_avgtime[x])

    user_to_mintime=RESULTS.groupby('player_id').min()['time_decision'].to_dict()
    RESULTS['user_mintime']=RESULTS['player_id'].map(lambda x: user_to_mintime[x])
    
    return RESULTS
    
from copy import deepcopy

import numpy as np

import matplotlib.pyplot as plt

DROP_RULES=[]

ANALYSIS_RES={}


# if in the behavioral parameter extraction you want to select participants cutting off by some of these criteria
# results in the paper are obtained with all of them (no cutoff is applied)
CUTOFF_USER_MAX_AVGERR=None
CUTOFF_USER_MIN_AVGTIME=None
CUTOFF_USER_MIN_MINTIME=None

def apply_cutoffs(results, cutoff_avgerr=None, cutoff_avgtime=None, cutoff_mintime=None):
    res=deepcopy(results)
    if cutoff_avgerr==None:
        cutoff_avgerr=CUTOFF_USER_MAX_AVGERR
    if cutoff_avgtime==None:
        cutoff_avgtime=CUTOFF_USER_MIN_AVGTIME
    if cutoff_mintime==None:
        cutoff_mintime=CUTOFF_USER_MIN_MINTIME
        
    if cutoff_avgerr!=None:
        res=res[res['user_avgerror']<cutoff_avgerr]
    if cutoff_avgtime!=None:
        res=res[res['user_avgtime']>cutoff_avgtime]
    if cutoff_mintime!=None:
        res=res[res['user_mintime']>cutoff_mintime]
        
    print("Applying cutoff:", len(res)/4, "users remaining (",len(res)/len(results)*100,"% of total)")
    return res

def _make_drop_trigger_column(results, drop_rules):
    if drop_rules==None:
        drop_rules=DROP_RULES
    res=deepcopy(results)
    res['drop_trigger']=1
    for feat_name, drop_map in drop_rules.items():
        res['drop_trigger']*=res[feat_name].map(drop_map)
    return res['drop_trigger']

def apply_drop_rules_entrywise(results, drop_rules, return_dropped=False):
    """
    drop rules: [{feature_name: map function of 1 if to drop else 0}]
    """
    if drop_rules==None:
        drop_rules=DROP_RULES
        
    res=deepcopy(results)
    initial_len=len(res)
    
    if not isinstance(drop_rules, list):
        print("isinstance")
        drop_rules=[drop_rules]
        
    for i, drop_rules_set in enumerate(drop_rules):
        res[f'drop_trigger_{i}']=_make_drop_trigger_column(res, drop_rules_set)
    
    res['drop_trigger']=0
    for i in range(len(drop_rules)):
        res['drop_trigger']+=res[f'drop_trigger_{i}']
    res['drop_trigger']=res['drop_trigger'].map(lambda x: 1 if x>=1 else 0)

    if return_dropped:
        res=res[res['user_drop']>=1]
        print(f"{len(res)} entries dropped, {len(res)/initial_len*100:.2f}% of initial ones")
        return res
    res=res[res['drop_trigger']==0]
    print(f"{len(res)} entries remaining, {len(res)/initial_len*100:.2f}% of initial ones")
    return res

def apply_drop_rules_userwise(results, drop_rules, max_val=2, return_dropped=False):
    """
    if the user triggers the drop rule more or equal than max_val, it gets dropped
    """
    if drop_rules==None:
        drop_rules=DROP_RULES
        
    res=deepcopy(results)
    initial_len=len(res)
    
    if not isinstance(drop_rules, list):
        drop_rules=[drop_rules]
        
    for i, drop_rules_set in enumerate(drop_rules):
        res[f'drop_trigger_{i}']=_make_drop_trigger_column(res, drop_rules_set)
        
    res['drop_trigger']=0
    for i in range(len(drop_rules)):
        res['drop_trigger']+=res[f'drop_trigger_{i}']
    res['drop_trigger']=res['drop_trigger'].map(lambda x: 1 if x>=1 else 0)
        
    u2droptriggers=res.groupby('player_id').sum()[f'drop_trigger'].to_dict()
    res[f'user_drop_triggers']=res['player_id'].map(lambda x: u2droptriggers[x])

    if return_dropped:
        res=res[res['user_drop_triggers']>=max_val]
        print(f"{len(res)} entries dropped, {len(res)/initial_len*100:.2f}% of initial ones")
        return res
    
    res=res[res['user_drop_triggers']<max_val]
    print(f"{len(res)} entries remaining, {len(res)/initial_len*100:.2f}% of initial ones")
    return res    
    
def results_to_beta_plot(results, plot=True, return_data=False, title=''):
    r2c={r: c for r, c in sorted(results['click_rank'].value_counts().to_dict().items(), key=lambda x: x[0])}

    rc=[c for r, c in r2c.items()]
    rc=np.array(rc)

    ratios=[]
    for i in range(len(rc)-1):
        ratio=rc[i]/rc[i+1]
        ratios.append(ratio)
#         print(np.log(ratio))
    
    log_ratios=np.array(np.log(ratios))
    beta_ext_avg=np.exp(log_ratios.mean())
#     print(beta_ext_avg, '-'*50)
    beta_ext_std=np.exp(log_ratios.std())
    
    prob_ext_avg=np.array([beta_ext_avg**(len(rc)-r+1) for r in r2c.keys()])
    prob_ext_avg=prob_ext_avg/prob_ext_avg.sum()
    if plot:
        plt.bar(range(len(rc)), rc/rc.sum() )
        plt.plot(range(len(rc)), prob_ext_avg, color='red')
        plt.title(f"{title}$\\beta$={beta_ext_avg:.3f}+- ??")#"{beta_ext_std:.3f}")
        plt.grid()
    if return_data:
        return beta_ext_avg, beta_ext_std    

        

def make_conf_dict(x_axis, y_axis, df, map_x=lambda x:x, map_y=lambda y:y, \
                   counting_z=False, map_z=lambda z:z, normalize_z=False):  
    df_mapped=df.copy()
    df_mapped[x_axis]=df_mapped[x_axis].map(map_x)
    df_mapped[y_axis]=df_mapped[y_axis].map(map_y)
    if counting_z:
        df_mapped[counting_z]=df_mapped[counting_z].map(map_z)
    
    cm={x:{y: 0 for y in sorted(df_mapped[y_axis].unique()) } for x in sorted(df_mapped[x_axis].unique())}
    nz={x:{y: 0 for y in sorted(df_mapped[y_axis].unique()) } for x in sorted(df_mapped[x_axis].unique())}
    
    for _, row in df_mapped.iterrows():
        x=row[x_axis]
        y=row[y_axis]
        if not counting_z:
            cm[x][y]+=1
        else:
            cm[x][y]+=row[counting_z]
            if normalize_z:
                nz[x][y]+=1
                
    if normalize_z:
        for x, yv in cm.items():
            for y, v in yv.items():
                if nz[x][y]!=0:
                    cm[x][y]/=nz[x][y]
        
    return cm

def plot_conf_dict(cd, normalize=False, return_data=True):
    cm=[list(cd[x].values()) for x in cd.keys()]
    cm=np.array(cm).T
    
    if normalize!=False or normalize=='z':
        if normalize=='columns':
            cm=cm.dot(np.diag(1/cm.sum(axis=0)))
        if normalize=='rows':
            cm=cm.dot(np.diag(1/cm.sum(axis=1)))
            
    plt.imshow(cm)
    plt.colorbar()
    
    # Annotate each cell with the value
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            plt.text(j, i, f'{cm[i, j]:.2f}', ha='center', va='center', color='white')
            
    if return_data:
        return cm
    


def get_d(res, x_name='stance_user_topicwise'):
    d=res[x_name].value_counts().to_dict()
#     print(d)
    d=[v[1] for v in sorted(d.items(), key=lambda x: x[0])]
#     print(d)
    d=np.array(d)/sum(d)
    return d

def get_C(res, x_name='stance_user_topicwise'):
    cd=make_conf_dict(x_name, 'stance_text_true', res)
#     print(cd)
    
    cm=[list(cd[x].values()) for x in cd.keys()]
    cm=np.array(cm).T
    
    cm=cm.dot(np.diag(1/cm.sum(axis=0)))
    
    return cm

def get_H(res, map_highlight, x_name='stance_user_topicwise'):
    cd=make_conf_dict(x_name, 'stance_text_true', res, 
                      counting_z='highlight', normalize_z=True, map_z=map_highlight)
    cm=[list(cd[x].values()) for x in cd.keys()]
    cm=np.array(cm).T
    
    return cm

def get_dch(RESULTS,
            map_highlight,
            x_name='stance_user_topicwise',
            apply_droprule=True,
            drop_rules=None,
            apply_cutoff=False,
            cutoff_avgerr=None, cutoff_avgtime=None, cutoff_mintime=None,
           ):
    if apply_cutoff:
        results=apply_cutoffs(RESULTS, cutoff_avgerr=cutoff_avgerr, cutoff_avgtime=cutoff_avgtime,cutoff_mintime=cutoff_mintime)
    else:
        results=deepcopy(RESULTS)
    if apply_droprule:
        results=apply_drop_rules_userwise(results, drop_rules=drop_rules)
    else:
        results=deepcopy(results)
        
    d=get_d(results, x_name=x_name)
    C=get_C(results, x_name=x_name)
    H=get_H(results, map_highlight, x_name=x_name)
    
    return d, C, H

def plot_dch(d, C, H):
#     plt.figure(figsize=(15,5))
    plt.subplot(1,4,2) #<--- (1,4,1) taken by beta fit plot
    plt.title("Distribution readers by stance")
    plt.bar(POSSIBLE_STANCES, d)  
    plt.grid()
    plt.subplot(1,4,3)
    plt.title("Behavior clicking")
    plt.imshow(C)
    plt.xlabel("user_stance")
    plt.xticks(range(0,5), range(-2,3))
    plt.ylabel("news_stance")
    plt.xticks(range(0,5), range(-2,3))
    plt.colorbar()
    plt.subplot(1,4,4)
    plt.title("Behavior highlighting")
    plt.imshow(H)
    plt.xlabel("user_stance")
    plt.xticks(range(0,5), range(-2,3))
    plt.ylabel("news_stance")
    plt.xticks(range(0,5), range(-2,3))
    plt.colorbar()
    

def results_to_simulation_inputs(RESULTS,
                                 map_highlight,
                                 use_beta_powerlow=False, # if you want to fit with powerlow instead of exp decay (paper as latter)
                                 topic_i=None,
                                 plot=True, 
                                 apply_droprule=False,
                                 drop_rules=None,
                                 apply_cutoff=False,
                                 cutoff_avgerr=None, cutoff_avgtime=None, cutoff_mintime=None):
    if apply_cutoff:
        results=apply_cutoffs(RESULTS, cutoff_avgerr=cutoff_avgerr, cutoff_avgtime=cutoff_avgtime,cutoff_mintime=cutoff_mintime)
    else:
        results=deepcopy(RESULTS)
    if apply_droprule:
        results=apply_drop_rules_userwise(results, drop_rules=drop_rules)
    else:
        results=deepcopy(results)
        
    if topic_i!=None:
        results=results[results['topic']==topic_i]
        
    d,C,H=get_dch(results, map_highlight, apply_droprule=False) #because already applied
    if plot:
        plt.figure(figsize=(20,7))
        plt.subplot(1,4,1) 
    if use_beta_powerlow:
        beta_info_dict = results_to_powerlaw_plot(results, plot=plot, return_data=True)
        beta_avg=beta_info_dict['b']
    else:
        beta_avg, beta_std=results_to_beta_plot(results, plot=plot, return_data=True)
    if plot:
        plot_dch(d, C, H) #<--- this intersects with results_to_beta_plot
    return beta_avg, d, C, H


########################### for ranking effect power low
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt


import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

def power_law(x, a, b):
    return a * np.power(x, b)

def results_to_powerlaw_plot(results, plot=True, return_data=False, title=''):
    # count clicks per rank (same as before)
    r2c = {r: c for r, c in sorted(results['click_rank'].value_counts().to_dict().items(), key=lambda x: x[0])}

    rc = np.array([c for r, c in r2c.items()])
    ranks = np.array(list(r2c.keys()))

    # normalize to probabilities (like your bar plot)
    probs = rc / rc.sum()

    # avoid zeros for log
    mask = (ranks > 0) & (probs > 0)
    x = ranks[mask]
    y = probs[mask]

    # log-log transform
    log_x = np.log(x)
    log_y = np.log(y)

    # linear fit in log-log space
    b, log_a = np.polyfit(log_x, log_y, 1)
    a = np.exp(log_a)

    # std estimate (similar spirit to your beta std)
    residuals = log_y - (b * log_x + log_a)
    b_std = residuals.std()

    # reconstruct fitted distribution
    prob_fit = a * np.power(ranks, b)
    prob_fit = prob_fit / prob_fit.sum()

    if plot:
        plt.bar(range(len(rc)), probs)
        plt.plot(range(len(rc)), prob_fit, color='red')
        plt.title(f"{title}power-law: b={b:.3f} ± {b_std:.3f}")
        plt.grid()

    if return_data:
        return {'a':a, 'b':b, 'b_std':b_std}
    

    

def fit_powerlaw(
    RESULTS,
    fit_topicwise=False,
    title='',
    plot=True,
    return_data=True,
):
    
    if plot:
        plt.figure(figsize=(15,6))
        plt.subplot(2,4,(1,6))

    power_overall = results_to_powerlaw_plot(
        RESULTS, plot=plot, return_data=return_data, title='Overall: '
    )

    if fit_topicwise:
        power_topicwise = []
        for i in range(1, 4+1):
            t_res = RESULTS[RESULTS['topic'] == i]
            
            if plot:
                plt.subplot(2,4,2+i+2*(i//3))
            
            power_topicwise.append(
                results_to_powerlaw_plot(
                    t_res,
                    plot=plot,
                    return_data=return_data,
                    title=f'{N2TOPIC[i]}: '
                )
            )
        
        if plot:
            plt.tight_layout()

    if return_data:
        return power_overall['b'] #<---- don't need parameter a since it's normalize anyway
# ############################################################################################################################











################################################ fit beta
def fit_beta(#apply_droprule=True,
#              drop_rules=None,
#              apply_cutoff=True,
#              cutoff_avgerr=None, cutoff_avgtime=None, cutoff_mintime=None,    
#              analysis_res_name=None,
             RESULTS,
             fit_topicwise=False,
             title='',
             plot=True,
             return_data=True,
            ):
    
    if plot:
        plt.figure(figsize=(15,6))
        plt.subplot(2,4,(1,6))
    beta_overall=results_to_beta_plot(RESULTS, plot=plot, return_data=return_data, title='Overall: ')
    if fit_topicwise:
        beta_topicwise=[]
        for i in range(1,4+1):
            t_res=RESULTS[RESULTS['topic']==i]
            if plot:
                plt.subplot(2,4,2+i+2*(i//3))
            beta_topicwise.append(results_to_beta_plot(t_res, plot=plot, return_data=return_data, title=f'{N2TOPIC[i]}: '))
        if plot:
            plt.tight_layout()
    if return_data:
        return beta_overall


def results_to_beta_plot(results, plot=True, return_data=False, title=''):
    r2c={r: c for r, c in sorted(results['click_rank'].value_counts().to_dict().items(), key=lambda x: x[0])}

    rc=[c for r, c in r2c.items()]
    rc=np.array(rc)

    ratios=[]
    for i in range(len(rc)-1):
        ratio=rc[i]/rc[i+1]
        ratios.append(ratio)
#         print(np.log(ratio))
    
    log_ratios=np.array(np.log(ratios))
    beta_ext_avg=np.exp(log_ratios.mean())
#     print(beta_ext_avg, '-'*50)
    beta_ext_std=np.exp(log_ratios.std())
    
    prob_ext_avg=np.array([beta_ext_avg**(len(rc)-r+1) for r in r2c.keys()])
    prob_ext_avg=prob_ext_avg/prob_ext_avg.sum()
    if plot:
        plt.bar(range(len(rc)), rc/rc.sum() )
        plt.plot(range(len(rc)), prob_ext_avg, color='red')
        plt.title(f"{title}$\\beta$={beta_ext_avg:.3f}+- ??")#"{beta_ext_std:.3f}")
        plt.grid()
    if return_data:
        return beta_ext_avg#, beta_ext_std
    
def make_conf_dict(x_axis, y_axis, df, map_x=lambda x:x, map_y=lambda y:y, \
                   counting_z=False, map_z=lambda z:z, normalize_z=False):  
    df_mapped=df.copy()
    df_mapped[x_axis]=df_mapped[x_axis].map(map_x)
    df_mapped[y_axis]=df_mapped[y_axis].map(map_y)
    if counting_z:
        df_mapped[counting_z]=df_mapped[counting_z].map(map_z)
    
    cm={x:{y: 0 for y in sorted(df_mapped[y_axis].unique()) } for x in sorted(df_mapped[x_axis].unique())}
    nz={x:{y: 0 for y in sorted(df_mapped[y_axis].unique()) } for x in sorted(df_mapped[x_axis].unique())}
    
    for _, row in df_mapped.iterrows():
        x=row[x_axis]
        y=row[y_axis]
        if not counting_z:
            cm[x][y]+=1
        else:
            cm[x][y]+=row[counting_z]
            if normalize_z:
                nz[x][y]+=1
                
    if normalize_z:
        for x, yv in cm.items():
            for y, v in yv.items():
                if nz[x][y]!=0:
                    cm[x][y]/=nz[x][y]
        
    return cm