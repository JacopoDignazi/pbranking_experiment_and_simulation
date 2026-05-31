import random as rnd
import numpy as np

from copy import deepcopy

from tqdm.notebook import tqdm

N_CLASSES=2


from time import time
DEBUG_LATEST_CALLS=[]
DEBUG_LATEST_TIME='ph'

TEMP_TIMERS={}
TEMP_COUNTERS={}

def reset_timers():
    global TEMP_TIMERS
    TEMP_TIMERS={timer_name:0 for timer_name in TEMP_TIMERS}

def dir_timers(f='min'):
    print("  Latest run timer info:")
    print()
    for timer_name, time in TEMP_TIMERS.items():
        if f=='sec': pass
        if f=='min': time/=60
        # if f=='auto'
        if time>0.:
            print("    {:_<55}:{:_>20.6f}_{}.".format(timer_name, time, f))

def dir_counters(f='min'):
    print("  Latest run counters info:")
    print()
    for timer_name, count in TEMP_COUNTERS.items():
        if count>0.:
            print("    {:_<55}:{:_>20}_times.".format(timer_name, count))
            
def dir_performance(normalize=False):
    print("  Latest run timer info:")
    print()
    for (timer_name, time), (_,count) in zip(TEMP_TIMERS.items(), TEMP_COUNTERS.items()):
        name=timer_name[:40]
        if count>10**6   : count_f, c_f  =count/10**6, "M"
        elif count>10**3 : count_f, c_f  =count/10**3, "K"
        else             : count_f, c_f  =float(count),"_"  
        if time>60*60    : time_f , t_f  =time/60**2, 'hrs.'
        elif time>60     : time_f , t_f  =time/60   , 'min.'
        else             : time_f , t_f  =time      , 'sec.'
        
        print(f"    {name:_<42}:{count_f:_>10.3f}{c_f}_times__{time_f:_>10.3f}_{t_f}___", end='')
        if normalize!=False:
            print(f"{time/TEMP_TIMERS[normalize]*100:_>6.2f}%___", end='')
        print(f"{time/(1 if count==0 else count):_>10.5f}_sec/time")
    
def timer(timer_name='auto'):
    global TEMP_TIMERS
    global TEMP_COUNTERS

    global DEBUG_LATEST_CALLS
    global DEBUG_LATEST_TIME

    if timer_name=='auto':
        name='timer_'+str(len(TEMP_TIMERS))
    if timer_name not in TEMP_TIMERS:
        TEMP_TIMERS[timer_name]=0.
    if timer_name not in TEMP_COUNTERS:
        TEMP_COUNTERS[timer_name]=0
    def time_it(func):
        global DEBUG_LATEST_CALLS
        global DEBUG_LATEST_TIME
        
        def inner(*args, **kwargs):
            global DEBUG_LATEST_CALLS
            global DEBUG_LATEST_TIME
            
            start=time()
            to_return=func(*args, **kwargs)
            end=time()
            TEMP_TIMERS[timer_name]+=end-start
            TEMP_COUNTERS[timer_name]+=1
            
            DEBUG_LATEST_CALLS=[timer_name]+DEBUG_LATEST_CALLS[:49]
            DEBUG_LATEST_TIME =time()
            
            return to_return
        return inner 
    return time_it            


timer_initialize_distribution          =timer('initialize_reader_or_news_distribution')
timer_initialize_click_behavior        =timer('initialize_click_behavior')
timer_initialize_highlight_distribution=timer('initialize_highlight_distribution')
timer_initialize_run                   =timer('initialize_altogether')
timer_initialize_readers               =timer('initialize_readers')
timer_initialize_news                  =timer('initialize_news')
timer_initialize_perception            =timer('initialize_perception')
timer_initialize_popularity            =timer('initialize_popularity')
timer_run                              =timer('run')
timer_run_clicking_prob                =timer('___clicking_probabilities')
timer_run_highlight_prob               =timer('___highlighting_probabilities')
timer_metrics                          =timer('metrics')



POSSIBLE_STANCES=[i for i in range(-N_CLASSES, N_CLASSES+1)]
s2idx={}
for s in POSSIBLE_STANCES:
    s2idx[s]=s+N_CLASSES


# -------------------------------- distribution 
@timer_initialize_distribution
def normal_distr(dominion, mu, sigma):
    f=1/(sigma * np.sqrt(2 * np.pi)) * np.exp( - (np.array(dominion) - mu)**2 / (2 * sigma**2))
    return np.array(f)/np.sum(f)

@timer_initialize_distribution
def uniform_distr(dominion):
    f=[1]*len(dominion)
    return np.array(f)/np.sum(f)

# DISTRIBUTION_READERS_RK1  =[0.290909, 0.300000, 0.163636, 0.136364, 0.109091]
# DISTRIBUTION_READERS_RK2V1=[0.3194444444444444,0.23842592592592593,0.12962962962962962,0.19212962962962962,0.12037037037037036]
# DISTRIBUTION_READERS_RK2V2=[0.38636363636363635,0.2409090909090909,0.10227272727272728,0.1159090909090909,0.15454545454545454]
# DISTRIBUTION_READERS_RK2V3=[0.34186047, 0.21860465, 0.11395349, 0.16860465, 0.15697674]
# DISTRIBUTION_READERS_RK2V4=[0.31134259, 0.21527778, 0.12384259, 0.15277778, 0.19675926]


# # -------------------------------- perception
# PERCEPTION_RK1=[
# [0.53      , 0.27      , 0.1       , 0.04      , 0.06      ],
# [0.58536585, 0.25609756, 0.13414634, 0.01219512, 0.01219512],
# [0.05185185, 0.07407407, 0.7037037 , 0.14074074, 0.02962963],
# [0.09803922, 0.09803922, 0.25490196, 0.31372549, 0.23529412],
# [0.08      , 0.06      , 0.13      , 0.34      , 0.39      ]]
# PERCEPTION_RK1=np.array(PERCEPTION_RK1).T


# -------------------------------- clicking behavior
@timer_initialize_click_behavior
def generate_click_row_as_continuous(row_idx, rho_confirmatory=0.3, rho_exploratory=0.1):
    row=[rho_exploratory]*len(POSSIBLE_STANCES)
    for n, _ in enumerate(row):
        if np.sign(n-N_CLASSES)==np.sign(row_idx-N_CLASSES):
            row[n]=rho_confirmatory
    row=np.array(row)/np.sum(row)

    return row


# -------------------------------- highlight behavior
def f_bakshy(x, alpha, n_classes):
    f=1-np.exp(-1/(2*alpha)*(np.abs(x)/n_classes*2)**(2*alpha))
    return f    

@timer_initialize_highlight_distribution
def generate_highlighting_row_as_continuous(row_idx, alpha):
    row=[0.0]*len(POSSIBLE_STANCES)
    for n, _ in enumerate(row):
        # if sgn(n-N_CLASSES)==np.sign(row_idx-N_CLASSES):
        if np.abs(row_idx-n)<N_CLASSES/4:
            row[n]=1
    extremism=f_bakshy(row_idx-N_CLASSES, alpha, N_CLASSES)
    return [v*extremism for v in row]

@timer_initialize_run
def Initialize(Number_of_news, Distribution_news, Number_of_readers, Distribution_readers, 
               readers_exact_list=None,
               initial_popularity=None,
               ASSUME_PERFECT_PERCEPTION=True, Perception_matrix=None, 
               news_items_exact_distribution=True):  
#     print(POSSIBLE_STANCES,Number_of_readers,Distribution_readers)
    if readers_exact_list==None:
        Readers=rnd.choices(POSSIBLE_STANCES, k=Number_of_readers, weights=Distribution_readers)
    else:
        Readers=readers_exact_list
        
    if news_items_exact_distribution:
        News_items=[]
        for s in POSSIBLE_STANCES:
            News_items+=[s]*2
    else:
        News_items=rnd.choices(POSSIBLE_STANCES, k=Number_of_news, weights=Distribution_news)

    Perception_matrix_all=[]
    if not ASSUME_PERFECT_PERCEPTION:
        for i_r, reader_stance in enumerate(Readers):
            Perception_matrix_all.append([])
            for i_n, news_stance in enumerate(News_items):
                Perception_matrix_all[i_r].append(rnd.choices(POSSIBLE_STANCES, k=1, 
                                                            weights=Perception_matrix[s2idx[news_stance]])[0]) #there is a faster way to do this
    else:
        for _ in range(len(Readers)):
            Perception_matrix_all.append(News_items)
            
    if initial_popularity==None:
        Initial_popularity=[i/100 for i in range(len(News_items))]
        rnd.shuffle(Initial_popularity)
    else:
        Initial_popularity=initial_popularity
    return News_items, Readers, Perception_matrix_all, Initial_popularity

@timer_initialize_readers
@timer_initialize_news
def Initialize_sample_from_distribution(N, Distr):
    V=rnd.choices(POSSIBLE_STANCES, k=N, weights=Distr)
    return  V

@timer_initialize_readers
@timer_initialize_news
def Initialize_uniform_exact(N_repetition_of_same_stance):
    V=[]
    for s in POSSIBLE_STANCES:
        V+=[s]*N_repetition_of_same_stance
    return V


@timer_initialize_perception
def Initialize_perception(News_items, Readers, Perception_matrix):
    Perception_matrix_all=[]
    for i_r, reader_stance in enumerate(Readers):
        Perception_matrix_all.append([])
        for i_n, news_stance in enumerate(News_items):
            Perception_matrix_all[i_r].append(rnd.choices(POSSIBLE_STANCES, k=1, 
                                                          weights=Perception_matrix[s2idx[news_stance]])[0])
    return Perception_matrix_all

@timer_initialize_popularity
def Initialize_popularity(News_items):
    Initial_popularity=[i/100 for i in range(len(News_items))]
    rnd.shuffle(Initial_popularity)
    return Initial_popularity

def popularity_to_ranking(popularity):
    """
    take the popularity as a vector idx: popularity and returns a vector of idx:ranking
    ranking starts from 1
    """
    Number_of_news=len(popularity)
    popularity_expanded=[(n, pop) for n, pop in enumerate(popularity)] #<--- tuple (id, popularity)
    popularity_expanded=sorted(popularity_expanded, reverse=True, key=lambda x: x[1]) #<--- sorted idx (rank): (id, popularity)
    ranking=['placeholder' for _ in range(Number_of_news)]
    for rank, (n, pop) in enumerate(popularity_expanded):
        ranking[n]=rank+1
    return ranking

@timer_run_clicking_prob
def clicking_probabilities(Behavior_clicking, 
                           Perception_matrix_all, 
                           weight_ranking_bias, 
                           reader_idx, 
                           Readers, News_items, 
                           ranking, 
                           use_beta_powerlow=False):
    phi_row=[Behavior_clicking[s2idx[Readers[reader_idx]]][s2idx[perception_of_news]] #<--- element Clicking[x(m),y(n)] of the matrix, 
             for perception_of_news in Perception_matrix_all[reader_idx]]                 #     iterated over the perception of n news
    phi_row=np.array(phi_row)
    Number_of_news=len(News_items)
    if not use_beta_powerlow: #exponential decay
        rho=weight_ranking_bias**(Number_of_news-np.array(ranking))*phi_row
    else:
        ranking_effect = np.array([r**(weight_ranking_bias) for r in ranking])
        # ranking_effect = ranking_effect / ranking_effect.sum() 
        rho=ranking_effect*phi_row
    return rho/rho.sum()

@timer_run_highlight_prob
def highlighting_probability(Behavior_highlighting, 
                             Perception_matrix_all, 
                             reader_idx, news_idx,
                             Readers):
    return Behavior_highlighting[s2idx[Readers[reader_idx]]][s2idx[Perception_matrix_all[reader_idx][news_idx]]]



from copy import deepcopy

import numpy as np

def warmup(Readers, News_items, 
           Perception_matrix_all, Behavior_clicking, Behavior_highlighting, 
           weight_ranking_bias, weight_popularity_highlight, 
           turns):
    assert 0 # don't want to use this anymore
    Number_of_readers=len(Readers)
    Number_of_news=len(News_items)

    RUN_EVENTS=[]
    FINAL_POPULARITY=[0 for _ in range(len(News_items))]

    for turn in range(turns):
        #randomizes popularity at each turn
        Popularity=Initialize_popularity(News_items) 
        #picks a random reader
        reader_idx=rnd.randint(0,Number_of_readers-1)
        reader_stance=Readers[reader_idx]

        RUN_EVENTS.append({})
        ranking=popularity_to_ranking(Popularity)
        rho=clicking_probabilities(Behavior_clicking, 
                                   Perception_matrix_all,
                                   weight_ranking_bias,
                                  reader_idx, 
                                  Readers, News_items, 
                                  ranking)
        clicked_news_idx=rnd.choices([i for i in range(Number_of_news)], weights=rho, k=1)[0]

        #updates final popularity by click
        FINAL_POPULARITY[clicked_news_idx]+=1
        # ---------- stores inforation
        RUN_EVENTS[-1]['reader_stance']=Readers[reader_idx]
        RUN_EVENTS[-1]['clicked_news_stance']=News_items[clicked_news_idx]
        RUN_EVENTS[-1]['clicked_news_perceived_stance']=Perception_matrix_all[reader_idx][clicked_news_idx]
        RUN_EVENTS[-1]['highlight']=False
        #highlight
        phi=highlighting_probability(Behavior_highlighting, 
                                    Perception_matrix_all, 
                                    reader_idx, clicked_news_idx,
                                    Readers
                                    )
        if phi>=rnd.random():
            FINAL_POPULARITY[clicked_news_idx]+=weight_popularity_highlight
            RUN_EVENTS[-1]['highlight']=True

    return RUN_EVENTS, FINAL_POPULARITY 






@timer_run
def run(Readers, News_items, 
        Initial_popularity, 
        Perception_matrix_all, Behavior_clicking, Behavior_highlighting, 
        weight_ranking_bias, weight_popularity_highlight, weight_other_partition, turns, use_beta_powerlow=False, always_same_readers=False):
    """
    RUN EVENTS: [time-wise {event_name: stat}]
    RUN_POPULARITIES: [time-wise {partition: [idx news item [popularity]]}}
    """
    
    Number_of_readers=len(Readers)
    Number_of_news=len(News_items)

    All_partitions_popularity={}
    for partition in [-1,0,1]: #<----- might need generalization
        All_partitions_popularity[partition]=deepcopy(Initial_popularity)

    RUN_EVENTS=[]  
    RUN_POPULARITIES=[deepcopy(All_partitions_popularity)]
    
    if always_same_readers:
        # shuffle readers list
        rnd.shuffle(Readers)

    for turn in range(turns):
        if always_same_readers:
            reader_idx=turn
        else:
            reader_idx=rnd.randint(0,Number_of_readers-1)
#         print(reader_idx)
        reader_stance=Readers[reader_idx]
            
        RUN_EVENTS.append({})

        ranking=popularity_to_ranking(All_partitions_popularity[np.sign(reader_stance)]) #<---- might need generalization
        
        # ---------- choses news clicked on
        rho=clicking_probabilities(Behavior_clicking, 
                                Perception_matrix_all,
                                weight_ranking_bias,
                                reader_idx, 
                                Readers, News_items, 
                                ranking,
                                use_beta_powerlow=use_beta_powerlow,
                                )
        clicked_news_idx=rnd.choices([i for i in range(Number_of_news)], weights=rho, k=1)[0]
        
        # print(selected_news_idx, ranking[selected_news_idx], rho[selected_news_idx])

        # ---------- update the popularity based on the clicking
        for partition in [-1,0,1]: #<---- might need generalization
            if partition==np.sign(reader_stance):
                All_partitions_popularity[partition][clicked_news_idx]+=1
            if partition!=np.sign(reader_stance):
                All_partitions_popularity[partition][clicked_news_idx]+=weight_other_partition

        # ---------- stores inforation
        RUN_EVENTS[-1]['reader_stance']=Readers[reader_idx]
        RUN_EVENTS[-1]['clicked_news_stance']=News_items[clicked_news_idx]
        RUN_EVENTS[-1]['clicked_news_perceived_stance']=Perception_matrix_all[reader_idx][clicked_news_idx]
        RUN_EVENTS[-1]['highlight']=False

        # ---------- if highlight
        phi=highlighting_probability(Behavior_highlighting, 
                                    Perception_matrix_all, 
                                    reader_idx, clicked_news_idx,
                                    Readers
                                    )
        if phi>=rnd.random():
            for partition in [-1,0,1]:
                if partition==np.sign(reader_stance):
                    All_partitions_popularity[partition][clicked_news_idx]+=weight_popularity_highlight
                if partition!=np.sign(reader_stance):
                    All_partitions_popularity[partition][clicked_news_idx]+=weight_popularity_highlight*weight_other_partition
            RUN_EVENTS[-1]['highlight']=True
            
        RUN_POPULARITIES.append(deepcopy(All_partitions_popularity))

    else:
        return RUN_EVENTS, RUN_POPULARITIES



#<-------------------------- metrics
import matplotlib.pyplot as plt

    
def run_popularities_to_stancewise_avgrank(run_popularities, News_items):
    # NB remember run_popularities are [time {partition: popularity}]
    ##### transforms a series of popularities to a series of ranking
    run_rankings=[]
    for t, partition_popularities in enumerate(run_popularities):
        run_rankings.append({})
        for partition in [-1,0,1]:
            run_rankings[-1][partition]=popularity_to_ranking(partition_popularities[partition])
        
    stancewise_avgrank=[]
    for t, partition_rankings in enumerate(run_rankings):
        stancewise_avgrank.append({})
        for partition in [-1,0,1]:
            tmp_stance_rank={s:[] for s in POSSIBLE_STANCES}
            for s, r in zip(News_items, partition_rankings[partition]):
                tmp_stance_rank[s].append(r)        

            stancewise_avgrank[-1][partition]={s: np.mean(tmp_stance_rank[s]) for s in POSSIBLE_STANCES}
            
    return stancewise_avgrank

@timer_metrics
def populatities_to_stancewise_avgrank(POPULARITIES, News_items, return_data=False, plot=True, final_value_only=False):
    """
    return {partition: {stances: [time value]}}
    """
    RUN_AVGRANKS=[run_popularities_to_stancewise_avgrank(run_popularity, News_items) for run_popularity in POPULARITIES]
    
    STANCEWISE_AVGRANK_AVG={partition: {s: [] for s in POSSIBLE_STANCES} for partition in [-1,0,1]}
    STANCEWISE_AVGRANK_STD={partition: {s: [] for s in POSSIBLE_STANCES} for partition in [-1,0,1]}
    
    N_RUNS=len(RUN_AVGRANKS)
    RUN_LENGTH=len(RUN_AVGRANKS[0])
    for time in range(RUN_LENGTH):
        if final_value_only and time<RUN_LENGTH-1:
            continue
        for partition in [-1,0,1]:
            for stance in POSSIBLE_STANCES:
                r_p_s_data=[RUN_AVGRANKS[run_iter][time][partition][stance] for run_iter in range(N_RUNS)]
                STANCEWISE_AVGRANK_AVG[partition][stance].append(np.mean(r_p_s_data))
                STANCEWISE_AVGRANK_STD[partition][stance].append(np.std(r_p_s_data))
    if plot:
        plt.figure(figsize=(15,5))
        for i, p in enumerate([-1,0,1]):
            plt.subplot(1,3,i+1)
            for s in POSSIBLE_STANCES:
#                 plt.errorbar(range(len(STANCEWISE_AVGRANK_AVG[p][s])), \
#                              -np.array(STANCEWISE_AVGRANK_AVG[p][s]), yerr=STANCEWISE_AVGRANK_STD[p][s], label=s)
                plt.plot(-np.array(STANCEWISE_AVGRANK_AVG[p][s]), label=s)
                
            plt.title(f"Avg stancewise ranking for partition {p}")
            plt.legend(loc="lower left")
            plt.ylim(-10,-1.)
            plt.xlabel("time")
            plt.ylabel("avg rank")
            plt.grid()
    if return_data:
        return STANCEWISE_AVGRANK_AVG, STANCEWISE_AVGRANK_STD
    
def run_popularities_to_stancewise_avgpop(run_popularities, News_items):
    # NB remember run_popularities are [time {partition: popularity}]
    ##### transforms a series of popularities to a series of ranking
    run_rankings=[]
    for t, partition_popularities in enumerate(run_popularities):
        run_rankings.append({})
        for partition in [-1,0,1]:
            run_rankings[-1][partition]=partition_popularities[partition]
        
    stancewise_avgrank=[]
    for t, partition_rankings in enumerate(run_rankings):
        stancewise_avgrank.append({})
        for partition in [-1,0,1]:
            tmp_stance_rank={s:[] for s in POSSIBLE_STANCES}
            for s, r in zip(News_items, partition_rankings[partition]):
                tmp_stance_rank[s].append(r)        

            stancewise_avgrank[-1][partition]={s: np.mean(tmp_stance_rank[s]) for s in POSSIBLE_STANCES}
            
    return stancewise_avgrank

@timer_metrics
def populatities_to_stancewise_avgpop(POPULARITIES, News_items, return_data=False, plot=True, final_value_only=False):
    """
    return {partition: {stances: [time value]}}
    """
    RUN_AVGRANKS=[run_popularities_to_stancewise_avgpop(run_popularity, News_items) for run_popularity in POPULARITIES]
#     RUN_AVGRANKS=POPULARITIES
    
    STANCEWISE_AVGRANK_AVG={partition: {s: [] for s in POSSIBLE_STANCES} for partition in [-1,0,1]}
    STANCEWISE_AVGRANK_STD={partition: {s: [] for s in POSSIBLE_STANCES} for partition in [-1,0,1]}
    
    N_RUNS=len(RUN_AVGRANKS)
    RUN_LENGTH=len(RUN_AVGRANKS[0])
    for time in range(RUN_LENGTH):
        if final_value_only and time<RUN_LENGTH-1:
            continue
        for partition in [-1,0,1]:
            for stance in POSSIBLE_STANCES:
                r_p_s_data=[RUN_AVGRANKS[run_iter][time][partition][stance] for run_iter in range(N_RUNS)]
                STANCEWISE_AVGRANK_AVG[partition][stance].append(np.mean(r_p_s_data))
                STANCEWISE_AVGRANK_STD[partition][stance].append(np.std(r_p_s_data))
    if plot:
        plt.figure(figsize=(15,5))
        for i, p in enumerate([-1,0,1]):
            plt.subplot(1,3,i+1)
            for s in POSSIBLE_STANCES:
                plt.errorbar(range(len(STANCEWISE_AVGRANK_AVG[p][s])), \
                             np.array(STANCEWISE_AVGRANK_AVG[p][s]), yerr=STANCEWISE_AVGRANK_STD[p][s], label=s, alpha=0.1)
#                 plt.plot(np.array(STANCEWISE_AVGRANK_AVG[p][s]))
                
            plt.title(f"Avg stancewise popularity for partition {p}")
            plt.legend(loc="lower left")
#             plt.ylim(-9.5,-1.5)
            plt.xlabel("time")
            plt.ylabel("avg rank")
            plt.grid()
    if return_data:
        return STANCEWISE_AVGRANK_AVG, STANCEWISE_AVGRANK_STD
    
def events_to_n_highlights(EVENTS):
    N_HIGHLIGHTS=[]
    for event_iteration in EVENTS:
        n_highlights=0
        for e in event_iteration:                
            if e['highlight']:
                n_highlights+=1
        N_HIGHLIGHTS.append(n_highlights)
        
    return N_HIGHLIGHTS


def events_to_conf_matrices(EVENTS, plot=True, return_data=False):

    CLICKING_ACTUAL_STANCES=[[0 for _ in range(len(POSSIBLE_STANCES))] for __ in range(len(POSSIBLE_STANCES))]
    CLICKING_PERCEIVED_STANCES=[[0 for _ in range(len(POSSIBLE_STANCES))] for __ in range(len(POSSIBLE_STANCES))]

    HIGHLIGHTS_ACTUAL_STANCES=[[0 for _ in range(len(POSSIBLE_STANCES))] for __ in range(len(POSSIBLE_STANCES))]
    HIGHLIGHTS_PERCEIVED_STANCES=[[0 for _ in range(len(POSSIBLE_STANCES))] for __ in range(len(POSSIBLE_STANCES))]

    for event_iteration in EVENTS:
        for e in event_iteration:
            reader_stance=e['reader_stance']
            news_stance=e['clicked_news_stance']
            perceived_stance=e['clicked_news_perceived_stance']

            CLICKING_ACTUAL_STANCES[s2idx[reader_stance]][s2idx[news_stance]]+=1
            CLICKING_PERCEIVED_STANCES[s2idx[reader_stance]][s2idx[perceived_stance]]+=1

            if e['highlight']:
                HIGHLIGHTS_ACTUAL_STANCES[s2idx[reader_stance]][s2idx[news_stance]]+=1
                HIGHLIGHTS_PERCEIVED_STANCES[s2idx[reader_stance]][s2idx[perceived_stance]]+=1

    if plot:
        plt.figure(figsize=(9,8))
        plt.subplot(2,2,1)
        plt.title("Clicks \n(user stance vs news stance)")
        plt.ylabel("User stance")
        plt.xlabel("News stance")
        plt.imshow(CLICKING_ACTUAL_STANCES)
        plt.subplot(2,2,2)
        plt.title("Highlights \n(user stance vs news stance)")
        plt.ylabel("User stance")
        plt.xlabel("News stance")
        plt.imshow(HIGHLIGHTS_ACTUAL_STANCES)
        plt.subplot(2,2,3)
        plt.title("Clicks \n(user stance vs perceived stance)")
        plt.ylabel("User stance")
        plt.xlabel("Perceived stance")
        plt.imshow(CLICKING_PERCEIVED_STANCES)
        plt.subplot(2,2,4)
        plt.title("Highlights \n(user stance vs perceived stance)")
        plt.ylabel("User stance")
        plt.xlabel("Perceived stance")
        plt.imshow(HIGHLIGHTS_PERCEIVED_STANCES)
        plt.tight_layout()
        
    if return_data:
         return CLICKING_ACTUAL_STANCES, CLICKING_PERCEIVED_STANCES, HIGHLIGHTS_ACTUAL_STANCES, HIGHLIGHTS_PERCEIVED_STANCES
    
def merge_bins(y, merge_by_size=1, apply=np.sum):
    assert N_CLASSES%merge_by_size==0
    y_merged=[]
    for i in range(0, N_CLASSES, merge_by_size):
        y_merged.append([])
        for ii in range(i, i+merge_by_size):
            y_merged[-1].append(y[ii])
        y_merged[-1]=apply(y_merged[-1])
    y_merged.append(y[N_CLASSES])
    for i in range(N_CLASSES+1, N_CLASSES*2+1, merge_by_size):
        y_merged.append([])
        for ii in range(i, i+merge_by_size):
            y_merged[-1].append(y[ii])
        y_merged[-1]=apply(y_merged[-1])
    return y_merged

def events_to_distributions(EVENTS, plot=True, return_data=False, merge_by_size=None):
    CLICK_BY_USERS_STANCE=[0 for __ in range(len(POSSIBLE_STANCES))]
    HIGHLIGH_BY_USER_STANCE=[0 for __ in range(len(POSSIBLE_STANCES))]

    CLICK_BY_NEWS_STANCE=[0 for __ in range(len(POSSIBLE_STANCES))]
    HIGHLIGH_BY_NEWS_STANCE=[0 for __ in range(len(POSSIBLE_STANCES))]

    CLICK_BY_PERCEIVED_STANCE=[0 for __ in range(len(POSSIBLE_STANCES))]
    HIGHLIGH_BY_PERCEIVED_STANCE=[0 for __ in range(len(POSSIBLE_STANCES))]

    for event_iteration in EVENTS:
        for e in event_iteration:
            reader_stance=e['reader_stance']
            news_stance=e['clicked_news_stance']
            perceived_stance=e['clicked_news_perceived_stance']

            CLICK_BY_USERS_STANCE[s2idx[reader_stance]]+=1
            CLICK_BY_NEWS_STANCE[s2idx[news_stance]]+=1
            CLICK_BY_PERCEIVED_STANCE[s2idx[perceived_stance]]+=1

            if e['highlight']:
                HIGHLIGH_BY_USER_STANCE[s2idx[reader_stance]]+=1
                HIGHLIGH_BY_NEWS_STANCE[s2idx[news_stance]]+=1
                HIGHLIGH_BY_PERCEIVED_STANCE[s2idx[perceived_stance]]+=1

    if merge_by_size!=None:
        POSSIBLE_STANCES_ADJ=merge_bins(POSSIBLE_STANCES, merge_by_size=5, apply=np.mean)
        CLICK_BY_USERS_STANCE=merge_bins(CLICK_BY_USERS_STANCE, merge_by_size=5)
        HIGHLIGH_BY_USER_STANCE=merge_bins(HIGHLIGH_BY_USER_STANCE, merge_by_size=5)
        CLICK_BY_NEWS_STANCE=merge_bins(CLICK_BY_NEWS_STANCE, merge_by_size=5)
        HIGHLIGH_BY_NEWS_STANCE=merge_bins(HIGHLIGH_BY_NEWS_STANCE, merge_by_size=5)
        CLICK_BY_PERCEIVED_STANCE=merge_bins(CLICK_BY_PERCEIVED_STANCE, merge_by_size=5)
        HIGHLIGH_BY_PERCEIVED_STANCE=merge_bins(HIGHLIGH_BY_PERCEIVED_STANCE, merge_by_size=5)
    else:
        POSSIBLE_STANCES_ADJ=POSSIBLE_STANCES
    if plot:
        plt.figure(figsize=(14,8))
        plt.subplot(3,2,1)
        plt.title("Clicks by user stance")
        plt.bar(POSSIBLE_STANCES_ADJ, CLICK_BY_USERS_STANCE)
        plt.subplot(3,2,2)
        plt.title("Highlights by user stance")
        plt.bar(POSSIBLE_STANCES_ADJ, HIGHLIGH_BY_USER_STANCE)
        plt.subplot(3,2,3)
        plt.title("Clicks by news stance")
        plt.bar(POSSIBLE_STANCES_ADJ, CLICK_BY_NEWS_STANCE)
        plt.subplot(3,2,4)
        plt.title("Highlights by news stance")
        plt.bar(POSSIBLE_STANCES_ADJ, HIGHLIGH_BY_NEWS_STANCE)
        plt.subplot(3,2,5)
        plt.title("Clicks by perceived stance")
        plt.bar(POSSIBLE_STANCES_ADJ, CLICK_BY_PERCEIVED_STANCE)
        plt.subplot(3,2,6)
        plt.title("Highlights by perceived stance")
        plt.bar(POSSIBLE_STANCES_ADJ, HIGHLIGH_BY_PERCEIVED_STANCE)
        plt.tight_layout()
    if return_data:
        return CLICK_BY_USERS_STANCE, CLICK_BY_NEWS_STANCE, CLICK_BY_PERCEIVED_STANCE, HIGHLIGH_BY_USER_STANCE, HIGHLIGH_BY_NEWS_STANCE, HIGHLIGH_BY_PERCEIVED_STANCE

def mav(values, window=50):
    smoothed_values=[np.nanmean(values[max(0,i-window):i]) for i in range(len(values))]
    return smoothed_values

def mav_centered(values, window=20):
    smoothed_values=[np.nanmean(values[max(0,i-window):i+window]) for i in range(len(values))]
    return smoothed_values

@timer_metrics
def events_to_extremism(EVENTS, window=100, IGNORE_NEUTRAL_READERS=False, Reference_stance=0, plot=True, return_data=False, baseline=None):
#     if IGNORE_NEUTRAL_READERS:
#         print("Not implemented IGNORE_NEUTRAL_READERS=True, switching to False")
#         IGNORE_NEUTRAL_READERS=False
        
    EXTREMISM=[]
    for event_iteration in EVENTS:
        EXTREMISM.append([])
        for n_e, e in enumerate(event_iteration):
            # if n_e%Number_of_readers==0:
            # if n_e==0:
            #     EXTREMISM[-1].append([])
            if IGNORE_NEUTRAL_READERS and e['reader_stance']==0: continue
            EXTREMISM[-1].append(np.abs(e['clicked_news_stance']-Reference_stance))
            # if len(EXTREMISM[-1][-1])==Number_of_readers:
            #     EXTREMISM[-1][-1]=np.mean(EXTREMISM[-1][-1])
    for it, estremism in enumerate(EXTREMISM):
        EXTREMISM[it]=mav(estremism, window=window)

    if plot:
        EXTREMISM_AVG=[]
        EXTREMISM_STD=[]
        SERIES_LENGTH=len(EXTREMISM[0])
        for t in range(SERIES_LENGTH): #<---- assuming all series have the same length
            EXTREMISM_AVG.append(np.mean([ext_iteration[t] for ext_iteration in EXTREMISM]))
            EXTREMISM_STD.append(np.std( [ext_iteration[t] for ext_iteration in EXTREMISM]))

        plt.errorbar(range(SERIES_LENGTH), EXTREMISM_AVG, yerr=EXTREMISM_STD, fmt='o', alpha=0.2, color='k')
        if baseline!=None:
            plt.axhline(baseline, color='r')
        plt.title("Extremism in time")
        plt.xlabel("time")
        # for mis in EXTREMISM:
        #     plt.plot(mis, color='k', alpha=0.1)
        #     if baseline!=None:
        #         plt.axhline(baseline, color='r')
        #     plt.title("Extremism in time")
        #     plt.xlabel("time")
    if return_data:
        return EXTREMISM
    
@timer_metrics
def events_to_extremism_stancewise(EVENTS, window=50, Reference_stance=0, plot=True, return_data=False, baseline=None):
    EXTREMISM=[[] for _ in POSSIBLE_STANCES]
    for event_iteration in EVENTS:
        for s in POSSIBLE_STANCES:        
            EXTREMISM[s2idx[s]].append([])
        for n_e, e in enumerate(event_iteration):
            EXTREMISM[s2idx[e['reader_stance']]][-1].append(np.abs(e['clicked_news_stance']-Reference_stance))

    for s in POSSIBLE_STANCES:
        for it, estremism in enumerate(EXTREMISM[s2idx[s]]):
            EXTREMISM[s2idx[s]][it]=mav(estremism, window=window)

    if plot:
        print("Not implemented")    
    if return_data:
        return EXTREMISM

@timer_metrics
def events_to_polarization(EVENTS, window=100, Reference_stance=0, plot=True, return_data=False, baseline=None):
    POLARIZATION=[]
    for event_iteration in EVENTS:
        POLARIZATION.append([])
        for i in range(len(event_iteration)):
            event_slice=event_iteration[max(0,i-window):i]
            t_left=[]
            t_right=[]
            for e in event_slice:
                if e['reader_stance']<0: # left
                    t_left.append(e['clicked_news_stance'])
                if e['reader_stance']>0: # right
                    t_right.append(e['clicked_news_stance'])
            t_left=np.mean(t_left)
            t_right=np.mean(t_right)
#             POLARIZATION[-1].append(np.abs(t_left-t_right))
            POLARIZATION[-1].append(t_right-t_left)
    if plot:
        POLARIZATION_AVG=[]
        POLARIZATION_STD=[]
        SERIES_LENGTH=len(POLARIZATION[0])
        for t in range(SERIES_LENGTH): #<---- assuming all series have the same length
            POLARIZATION_AVG.append(np.mean([ext_iteration[t] for ext_iteration in POLARIZATION]))
            POLARIZATION_STD.append(np.std( [ext_iteration[t] for ext_iteration in POLARIZATION]))

        plt.errorbar(range(SERIES_LENGTH), POLARIZATION_AVG, yerr=POLARIZATION_STD, fmt='o', alpha=0.2, color='k')
        if baseline!=None:
            plt.axhline(baseline, color='r')
        plt.title("Polarization in time")
        plt.xlabel("time")

        # for pol in POLARIZATION:
        #     plt.plot(pol, color='k', alpha=0.1)
        #     if baseline!=None:
        #         plt.axhline(baseline, color='r')
        #     plt.title("Polarization in time")
        #     plt.xlabel("time")
    if return_data:
        return POLARIZATION
    
@timer_metrics
def events_to_click_density(EVENTS, from_last_event=100, 
                            plot=True, return_data=False, return_data_overall_version=False, 
                            plot_adjust_x_axis=0, merge_by_size=None):
    CLICK_DENSITY=[]
    CLICK_DENSITY_BY_PARTITION=[]
    for event_iteration in EVENTS:
        CLICK_DENSITY.append([0]*len(POSSIBLE_STANCES))
        CLICK_DENSITY_BY_PARTITION.append({p: [0]*len(POSSIBLE_STANCES) for p in [-1,0,1]})
        for n_e, e in enumerate(event_iteration):
            if len(event_iteration)-n_e<from_last_event:
                CLICK_DENSITY[-1][s2idx[e['clicked_news_stance']]]+=1
                CLICK_DENSITY_BY_PARTITION[-1][np.sign(e['reader_stance'])][s2idx[e['clicked_news_stance']]]+=1
                
    # this "overall" means it is aggregated over iterations
    CLICK_DENSITY_OVERALL=[0]*len(POSSIBLE_STANCES)
    CLICK_DENSITY_OVERALL_BY_PARTITION={p: [0]*len(POSSIBLE_STANCES) for p in [-1,0,1]}
    for c_d_iteration in CLICK_DENSITY:
        for s in POSSIBLE_STANCES:
            CLICK_DENSITY_OVERALL[s2idx[s]]+=c_d_iteration[s2idx[s]]
    for c_d_iteration in CLICK_DENSITY_BY_PARTITION:
        for p, data in c_d_iteration.items():
            for s in POSSIBLE_STANCES:
                CLICK_DENSITY_OVERALL_BY_PARTITION[p][s2idx[s]]+=data[s2idx[s]]

    if merge_by_size!=None:
        CLICK_DENSITY_OVERALL=merge_bins(CLICK_DENSITY_OVERALL, merge_by_size=merge_by_size)
        CLICK_DENSITY_OVERALL_BY_PARTITION={p: merge_bins(CLICK_DENSITY_OVERALL_BY_PARTITION[p], merge_by_size=merge_by_size) for p in CLICK_DENSITY_OVERALL_BY_PARTITION.keys()}
        POSSIBLE_STANCES_ADJ=merge_bins(POSSIBLE_STANCES, merge_by_size=merge_by_size, apply=np.mean)
    else:
        POSSIBLE_STANCES_ADJ=POSSIBLE_STANCES

    if plot:
        plt.figure(figsize=(15,4))
        plt.subplot(1,2,1)
        plt.title("Overall click density")
        plt.bar(POSSIBLE_STANCES_ADJ, CLICK_DENSITY_OVERALL)
        plt.subplot(1,2,2)
        plt.title("By partition click density")
        for p, color in zip([-1,0,1], ['blue','grey','red']):
            # if p!=-1: continue
            plt.bar(POSSIBLE_STANCES_ADJ, CLICK_DENSITY_OVERALL_BY_PARTITION[p], alpha=0.8, color=color)
            
    if return_data_overall_version:
            return CLICK_DENSITY_OVERALL, CLICK_DENSITY_OVERALL_BY_PARTITION
        
    if return_data:
        return CLICK_DENSITY, CLICK_DENSITY_BY_PARTITION
   
    
# <---------------------------- simulation with changing parameters (grid)
def simulation_grid(beta, d, C, H, TURNS, REPETITIONS_PER_EXPERIMENT, 
                    use_beta_powerlow=False, 
                    user_stance_list=None,
                    initial_popularity=None,
                    return_all_final_entries=True,
                    return_avgstd_series=True,
                    always_same_readers=False,
                    TEST_LAMBDA=[0,1], TEST_ETA=[0,100], 
                    METRIC_WINDOW=100):
    
#     Final_click_density_partitionwise_avg={}
#     Final_click_density_partitionwise_std={}
    
    N_highlights_avg={}
    N_highlights_std={}

    Final_extremism_avg={}
    Final_extremism_std={}
    Final_extremism_all_avg={}
    Final_extremism_all_std={}
    Final_polarization_avg={}
    Final_polarization_std={}
    Final_extremism_stancewise_avg=[{} for _ in POSSIBLE_STANCES]
    Final_extremism_stancewise_std=[{} for _ in POSSIBLE_STANCES]
    Final_stancewise_avgrank_avg={p:{s: {} for s in POSSIBLE_STANCES} for p in [-1,0,1]}
    Final_stancewise_avgrank_std={p:{s: {} for s in POSSIBLE_STANCES} for p in [-1,0,1]}
    
    if return_all_final_entries:
        N_highlights={}
        
        Final_click_density_partitionwise={}
        
        Final_extremism={}
        Final_extremism_all={}
        Final_polarization={}
        
    if return_avgstd_series:
        Extremism_avg={}
        Extremism_std={}
        Extremism_all_avg={}
        Extremism_all_std={}
        Polarization_avg={}
        Polarization_std={}

    for weight_other_partition in tqdm(TEST_LAMBDA):
#         Final_click_density_avg[weight_other_partition]={}
#         Final_click_density_std[weight_other_partition]={}
        N_highlights_avg[weight_other_partition]={}
        N_highlights_std[weight_other_partition]={}

        Final_extremism_avg[weight_other_partition]={}
        Final_extremism_std[weight_other_partition]={}
        Final_extremism_all_avg[weight_other_partition]={}
        Final_extremism_all_std[weight_other_partition]={}
        Final_polarization_avg[weight_other_partition]={}
        Final_polarization_std[weight_other_partition]={}
        
        if return_all_final_entries:
            N_highlights[weight_other_partition]={}
            
            Final_click_density_partitionwise[weight_other_partition]={}

            Final_extremism[weight_other_partition]={}
            Final_extremism_all[weight_other_partition]={}
            Final_polarization[weight_other_partition]={}
            
        if return_avgstd_series:
            Extremism_avg[weight_other_partition]={}
            Extremism_std[weight_other_partition]={}
            Extremism_all_avg[weight_other_partition]={}
            Extremism_all_std[weight_other_partition]={}
            Polarization_avg[weight_other_partition]={}
            Polarization_std[weight_other_partition]={}

        for s in POSSIBLE_STANCES:
            Final_extremism_stancewise_avg[s2idx[s]][weight_other_partition]={}
            Final_extremism_stancewise_std[s2idx[s]][weight_other_partition]={}
            for p in [-1,0,1]:
#                 Final_click_density_partitionwise_avg[p][s][weight_other_partition]={}
#                 Final_click_density_partitionwise_std[p][s][weight_other_partition]={}
                Final_stancewise_avgrank_avg[p][s][weight_other_partition]={}
                Final_stancewise_avgrank_std[p][s][weight_other_partition]={}


        for weight_popularity_highlight in tqdm(TEST_ETA):
            W_EVENTS=[]
            W_POPULARITIES=[]
            
            # if needs to be always same readers BUT NOT from user_stance_list, it creates the readers list
            if user_stance_list!=None:  
                Readers=user_stance_list
                always_same_readers=True

            else:
                if always_same_readers:
                    _, Readers, __, ___ =\
                    Initialize('dummy', 'dummy', 
                               TURNS, d, 
                               ASSUME_PERFECT_PERCEPTION=True, Perception_matrix=None)

            #starts iterating over rep per experiment
            for iteration in range(REPETITIONS_PER_EXPERIMENT):
                if user_stance_list!=None:
                    always_same_readers=True
                    TURNS=len(Readers)
                    

                # this Readers is either the ones initialized from user_list_stance or from always_same_readers_initialization
                if always_same_readers:
                    readers_exact_list=Readers
                else:
                    readers_exact_list=None
                
                
                News_items, Readers, Perception_matrix_all, Initial_popularity =\
                Initialize('dummy', 'dummy', 
                           TURNS, d, 
                           readers_exact_list=readers_exact_list,
                           initial_popularity=initial_popularity,
                           ASSUME_PERFECT_PERCEPTION=True, Perception_matrix=None
                           )
                
                    
#                 print("always_same_readers", always_same_readers)
#                 print("user_stance_list", user_stance_list)
#                 print("Readers", Readers)
#                 print(TURNS)
                
                events, Popularity= run(
                        Readers, News_items,
                        Initial_popularity, 
                        Perception_matrix_all, C, H,
                        beta, 
                        weight_popularity_highlight, #<----- parameter that changes
                        weight_other_partition, #<----- parameter that changes
                        TURNS, 
                        use_beta_powerlow=use_beta_powerlow,
                        always_same_readers=always_same_readers
                )
                W_EVENTS.append(events)
                W_POPULARITIES.append(Popularity)
                
            N_HIGHLIGHTS=events_to_n_highlights(W_EVENTS)
            N_highlights_avg[weight_other_partition][weight_popularity_highlight]=np.mean(N_HIGHLIGHTS)
            N_highlights_std[weight_other_partition][weight_popularity_highlight]=np.std(N_HIGHLIGHTS)


            W_EXTREMISM=events_to_extremism(W_EVENTS, IGNORE_NEUTRAL_READERS=True, window=METRIC_WINDOW, return_data=True, plot=False)
            Final_extremism_avg[weight_other_partition][weight_popularity_highlight]=np.mean([iteration_extremism[-1] for iteration_extremism in W_EXTREMISM])
            Final_extremism_std[weight_other_partition][weight_popularity_highlight]=np.std([iteration_extremism[-1] for iteration_extremism in W_EXTREMISM])
                

            W_EXTREMISM_ALL=events_to_extremism(W_EVENTS, IGNORE_NEUTRAL_READERS=False, window=METRIC_WINDOW, return_data=True, plot=False)
            Final_extremism_all_avg[weight_other_partition][weight_popularity_highlight]=np.mean([iteration_extremism[-1] for iteration_extremism in W_EXTREMISM_ALL])
            Final_extremism_all_std[weight_other_partition][weight_popularity_highlight]=np.std([iteration_extremism[-1] for iteration_extremism in W_EXTREMISM_ALL])



            W_POLARIZATION=events_to_polarization(W_EVENTS, window=METRIC_WINDOW, return_data=True, plot=False)
            Final_polarization_avg[weight_other_partition][weight_popularity_highlight]=np.mean([iteration_polarization[-1] for iteration_polarization in W_POLARIZATION])
            Final_polarization_std[weight_other_partition][weight_popularity_highlight]=np.std([iteration_polarization[-1] for iteration_polarization in W_POLARIZATION])
            
            if return_all_final_entries:
                N_highlights[weight_other_partition][weight_popularity_highlight]=N_HIGHLIGHTS
                
                Final_extremism[weight_other_partition][weight_popularity_highlight]=[iteration_extremism[-1] for iteration_extremism in W_EXTREMISM]
                Final_extremism_all[weight_other_partition][weight_popularity_highlight]=[iteration_extremism[-1] for iteration_extremism in W_EXTREMISM_ALL]
                Final_polarization[weight_other_partition][weight_popularity_highlight]=[iteration_polarization[-1] for iteration_polarization in W_POLARIZATION]
                
                
            if return_avgstd_series:
#                 print([len(iteration_extremism) for iteration_extremism in W_EXTREMISM])
#                 Extremism_avg[weight_other_partition][weight_popularity_highlight]=[np.mean([iteration_extremism[time] for iteration_extremism in W_EXTREMISM]) for time in range(len(W_EXTREMISM[0]))]
#                 Extremism_std[weight_other_partition][weight_popularity_highlight]=[np.std([iteration_extremism[time] for iteration_extremism in W_EXTREMISM]) for time in range(len(W_EXTREMISM[0]))]
                Extremism_all_avg[weight_other_partition][weight_popularity_highlight]=[np.mean([iteration_extremism[time] for iteration_extremism in W_EXTREMISM_ALL]) for time in range(len(W_EXTREMISM_ALL[0]))]
                Extremism_all_std[weight_other_partition][weight_popularity_highlight]=[np.std([iteration_extremism[time] for iteration_extremism in W_EXTREMISM_ALL]) for time in range(len(W_EXTREMISM_ALL[0]))]
                Polarization_avg[weight_other_partition][weight_popularity_highlight]=[np.mean([iteration_extremism[time] for iteration_extremism in W_POLARIZATION]) for time in range(len(W_POLARIZATION[0]))]
                Polarization_std[weight_other_partition][weight_popularity_highlight]=[np.std([iteration_extremism[time] for iteration_extremism in W_POLARIZATION]) for time in range(len(W_POLARIZATION[0]))]

            W_EXTREMISM_STANCEWISE=events_to_extremism_stancewise(W_EVENTS, window=METRIC_WINDOW, return_data=True, plot=False)
            for s, w_extremism_stancewise in enumerate(W_EXTREMISM_STANCEWISE):
                Final_extremism_stancewise_avg[s][weight_other_partition][weight_popularity_highlight]=\
                    np.nanmean([iteration_extremism_stancewise[-1] for iteration_extremism_stancewise in w_extremism_stancewise])


            W_CLICK_DENSITY, W_CLICK_DENSITY_PARTITIONWISE=events_to_click_density(W_EVENTS, return_data=True, plot=False, from_last_event=METRIC_WINDOW)
            Final_click_density_partitionwise[weight_other_partition][weight_popularity_highlight]=W_CLICK_DENSITY_PARTITIONWISE

            W_STANCEWISE_AVGRANG=populatities_to_stancewise_avgrank(W_POPULARITIES, News_items,
                                                                    final_value_only=True, #<---- to save computation time
                                                                    return_data=True, plot=False)
            for p in [-1,0,1]:
                for s in POSSIBLE_STANCES:
                    Final_stancewise_avgrank_avg[p][s][weight_other_partition][weight_popularity_highlight]=\
                    W_STANCEWISE_AVGRANG[0][p][s][-1]
                    Final_stancewise_avgrank_std[p][s][weight_other_partition][weight_popularity_highlight]=\
                    W_STANCEWISE_AVGRANG[1][p][s][-1]
                    
    to_return= {
        'N_highlights_avg':N_highlights_avg,
        'N_highlights_std':N_highlights_std,
        'Final_extremism_avg':Final_extremism_avg,
        'Final_extremism_std':Final_extremism_std,
        'Final_extremism_all_avg':Final_extremism_all_avg,
        'Final_extremism_all_std':Final_extremism_all_std,
        'Final_polarization_avg':Final_polarization_avg,
        'Final_polarization_std':Final_polarization_std,
#         'Final_click_density_avg':Final_click_density_partitionwise_avg, # not implemented (std neither)
        'Final_extremism_stancewise_avg':Final_extremism_stancewise_avg,
        'Final_extremism_stancewise_std':Final_extremism_stancewise_std,
        'Final_stancewise_avgrank_avg':Final_stancewise_avgrank_avg,
        'Final_stancewise_avgrank_std':Final_stancewise_avgrank_std,
    }
    
    if return_all_final_entries:
        to_return['N_highlights']=N_highlights,
        to_return['Final_click_count_partitionwise']=Final_click_density_partitionwise
        to_return['Final_extremism']=Final_extremism
        to_return['Final_extremism_all']=Final_extremism_all
        to_return['Final_polarization']=Final_polarization

    if return_avgstd_series:
#         to_return['Extremism_avg']=Extremism_avg
#         to_return['Extremism_std']=Extremism_std
        to_return['Extremism_all_avg']=Extremism_all_avg
        to_return['Extremism_all_std']=Extremism_all_std
        to_return['Polarization_avg']=Polarization_avg
        to_return['Polarization_std']=Polarization_std

    return to_return


def final_values_to_avgstd(Final_metric_avg, Final_metric_std):
    M_avg=[]
    M_std=[]

    for eta, data in Final_metric_avg.items():
        M_avg.append([])
        M_std.append([])
        for lmb, metric in data.items():
            M_avg[-1].append(metric)
            M_std[-1].append(Final_metric_std[eta][lmb])
            
    return np.array(M_avg), np.array(M_std)

def plot_grid_avgstd(M_avg, M_std, key_dict, metric_name):
    plt.title(f"{metric_name} values")
    plt.imshow(M_avg)#, cmap='Reds')
    plt.yticks(range(len(key_dict)), [l for l in key_dict.keys()])
    plt.ylabel('$\lambda$')
    plt.xticks(range(len(key_dict[0])), [l for l in key_dict[0].keys()])
    plt.xlabel('$\eta$')
    plt.colorbar()
#     plt.savefig(f'../results/{SAVENAME_PREFIX}_{metric_name}_grid.png')
    
    for i in range(M_avg.shape[0]):
        for j in range(M_avg.shape[1]):
            plt.text(j, i, f'{M_avg[i, j]:.2f}\n+-\n{M_std[i,j]:.2f}', ha='center', va='center', color='white')
            
def plot_scatter_extr_vs_pol(E, P, color='k', label='', only_avgstd=False):
    for lamb, eta2values in E.items():
        for eta, extremism_values in eta2values.items():
            if not only_avgstd:
                plt.scatter(extremism_values, P[lamb][eta], label=f'$\lambda=${lamb:d} $\eta=${eta:d}')
            else:
                E_avg=np.mean(E[lamb][eta])
                E_std=np.std(E[lamb][eta])
                P_avg=np.mean(P[lamb][eta])
                P_std=np.std(P[lamb][eta])
                plt.errorbar(E_avg, P_avg, xerr=E_std, yerr=P_std, label=f'$\lambda=${lamb:d} $\eta=${eta:d}')
    plt.legend()
    
def plot_series_avgstd(avg, std,):
    plt.errorbar(range(len(avg)), avg, yerr=std) 
    
    
   
