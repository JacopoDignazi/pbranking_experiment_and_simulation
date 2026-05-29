############### YOUR PATHS HERE ############################################
pathname_articleinfo=f'../CODE_EXPERIMENT/my_survey_static/article_info.csv'
DATA_FOLDER='../DATA'

############################################################################

REF_COLUMNS=['player_id', 'round', 'topic', 'gender', 'age', 'stance_user',
'stance_user_topicwise', 'click_id', 'click_rank', 'highlight', 'share',
'stance_text_perc', 'stance_text_true', 'perception_distance',
'stance_distance', 'partition_user', 'partition_user_topicwise',
'partition_text_perc', 'partition_text_true', 'click_same_partition',
'time_ranking', 'time_highlight', 'stance_text_error', 'user_avgerror',
'time_decision', 'user_avgtime', 'user_mintime']


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
    if str(ideology)[0]=='D':
        return -1
    if str(ideology)[0]=='R':
        return 1
    return 0

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


def load_results(experiment_versions, drop_incomplete_all=True):
    N_ROUNDS=4
    
    if not isinstance(experiment_versions, list):
        experiment_versions=[experiment_versions]
#     RES=pd.DataFrame()
    for i_ev, ev in enumerate(experiment_versions):
        pathname=f'{DATA_FOLDER}/data_exp_dynamic/{ev}_clean.csv'

        print(ev)
        if i_ev==0:
            RES=pd.read_csv(pathname)
        else:
            RES = pd.concat([RES, pd.read_csv(pathname)], ignore_index=True)


    if drop_incomplete_all:
        RES = RES.dropna(subset=['demographics_and_payment.1.player.age'])
    
    # print("Number of valid entries:", len(RES[~RES['demographics_and_payment.1.player.gender'].isna()]))
    RES=RES[~RES['demographics_and_payment.1.player.gender'].isna()]
    
    A_INFO=pd.read_csv(pathname_articleinfo)
    
    AID2STANCE=A_INFO.set_index('article_id')['stance'].to_dict()
    AID2SOURCE=A_INFO.set_index('article_id')['source'].to_dict()

    for i in range(1, N_ROUNDS+1):
        RES = RES.dropna(subset=[f'my_survey_static.{i}.player.click_id'])
        RES[f'my_survey_static.{i}.player.positioning_true']=\
        RES[f'my_survey_static.{i}.player.click_id'].map(lambda x: AID2STANCE[int(x)] if not x is None else -1000)

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

    SEEN_RANKING=[]
    for i in range(1,N_ROUNDS+1):
        SEEN_RANKING+=RES[f'my_survey_static.{i}.player.tmp_ranking'].tolist()

    SEED=[]
    for i in range(1,N_ROUNDS+1):
        SEED+=RES[f'my_survey_static.{i}.player.seed'].tolist()

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

    user_to_avgtime=RESULTS[['player_id','time_decision']].groupby('player_id').mean()['time_decision'].to_dict()
    RESULTS['user_avgtime']=RESULTS['player_id'].map(lambda x: user_to_avgtime[x])

    user_to_mintime=RESULTS[['player_id','time_decision']].groupby('player_id').min()['time_decision'].to_dict()
    RESULTS['user_mintime']=RESULTS['player_id'].map(lambda x: user_to_mintime[x])

    RESULTS['seed']=SEED

    RESULTS['seen_ranking']=SEEN_RANKING
    RESULTS['seen_ranking']=RESULTS['seen_ranking'].map(str)

    return RESULTS


def load_results_parse(ev):
    df= pd.read_csv(f'{DATA_FOLDER}/data_exp_dynamic/{ev}_parse.csv')


    df=df.dropna(subset='PID')
    mask = df['turn'].isin([1, 2, 3, 4]) & df['participant_label'].isna()
    df = df.drop(index=df[mask].index)  


    df['topic']=df['topic_number']
    # df['player_id']=df['PID'].map(lambda x: x[1:])
    df['player_id']=df['participant_label']
    df['gender']=df['gender'].map(lambda x: gender_to_value(x) if isinstance(x, str) else 0)
    df['age']=df['age'].map(lambda x: age_to_value(x) if isinstance(x, str) else 0)

    # user general stance
    df['stance_user']=df['leaning'].map(ideology_to_value)*df['leaning_strength'].fillna('C').map(strength_to_value)
    mask = df['turn'] == 5
    df.loc[mask, 'center_strength'] = (
        df.loc[mask, 'center_strength']
        .fillna('C')
        .map(center_to_value)
    )
    mask = df['turn'] == 5
    df.loc[mask, 'center_strength'] = (
        df.loc[mask, 'center_strength'] + df.loc[mask, 'stance_user']
    )



    # ------- general attributes
    mask = df['turn'] == 6
    ID2GENDER = df.loc[mask].set_index('PID')['gender'].to_dict()
    ID2AGE    = df.loc[mask].set_index('PID')['age'].to_dict()
    mask = df['turn'] == 5
    ID2STANCE = df.loc[mask].set_index('PID')['stance_user'].to_dict()

    df['gender']=df['PID'].map(lambda x: ID2GENDER[x])
    df['age']=df['PID'].map(lambda x: ID2AGE[x])
    df['stance_user']=df['PID'].map(lambda x: ID2STANCE[x])

    df=df[df['turn'].isin([1,2,3,4])]
    #--------------------------------------

    df['stance_user_topicwise']=df['positioning_user']

    df['share']=df['highlight'].map(lambda x: 1 if x in [1,2] else 0)

    df['stance_text_perc']=df['positioning_text']
    df['stance_text_true']=df['positioning_true']

    df['perception_distance']=np.abs(df['stance_text_perc']-df['stance_text_true'])
    df['stance_distance']=np.abs(df['stance_text_true']-df['stance_user_topicwise'])


    df['partition_user']=df['stance_user'].map(lambda x: np.sign(x))
    df['partition_user_topicwise']=df['stance_user_topicwise'].map(lambda x: np.sign(x))

    df['partition_text_perc']=df['stance_text_perc'].map(lambda x: np.sign(x))
    df['partition_text_true']=df['stance_text_true'].map(lambda x: np.sign(x))

    df['click_same_partition']=np.abs(df['partition_user_topicwise']-df['partition_text_true']).map(lambda x: 1 if x>=1 else 0)

    A_INFO=pd.read_csv(pathname_articleinfo)
    AID2STANCE=A_INFO.set_index('article_id')['stance'].to_dict()
    AID2SOURCE=A_INFO.set_index('article_id')['source'].to_dict()

    df['news_source']=df['click_id'].map(lambda x: AID2SOURCE.get(x))
    # NEWS_SOURCE=[AID2SOURCE[idx] for idx in CLICK_ID]

    df['stance_text_error']=np.abs(df['stance_text_true']-df['stance_text_perc'])

    U2ERROR = {}
    for user in df['player_id'].unique():
        mask = (df['turn'].isin([1, 2, 3, 4])) & (df['player_id'] == user)
        u_res = df.loc[mask, 'stance_text_error']
        U2ERROR[user] = u_res.mean()
    df['user_avgerror']=df['player_id'].map(lambda x: U2ERROR[x])

    df['time_ranking']=df['time_rankig'] # just a typo

    df['time_decision']=0
    for c in ['time_positioning', 'time_ranking', 'time_highlight']:
        df['time_decision']+= df[c]

    user_to_avgtime=df[['player_id','time_decision']].groupby('player_id').mean()['time_decision'].to_dict()
    df['user_avgtime']=df['player_id'].map(lambda x: user_to_avgtime[x])

    user_to_mintime=df[['player_id','time_decision']].groupby('player_id').min()['time_decision'].to_dict()
    df['user_mintime']=df['player_id'].map(lambda x: user_to_mintime[x])
    
    df['round']=df['turn']

    df=df[df['turn'].isin([1,2,3,4])]

    df['seen_ranking']=df['tmp_ranking']
    df['seen_ranking']=df['seen_ranking'].map(str)

    RESULTS=pd.DataFrame()
    for c in REF_COLUMNS+['seed', 'seen_ranking']:
        RESULTS[c]=df[c]



    return RESULTS


def load_all_dyn_results(remove_first_entries=False):
    if remove_first_entries:
        TO_LOAD=['RK3v2p1','RK3v2p2','RK3v3p1','RK3v3p2','RK3v3p3','RK3v3p4']
    else:
        TO_LOAD=['RK3v0p1','RK3v0p2','RK3v0p3','RK3v2p1','RK3v2p2','RK3v3p1','RK3v3p2','RK3v3p3','RK3v3p4']
        
    DYN_RESULTS=load_results(TO_LOAD)

    df=load_results_parse('RK3v4p1')
    DYN_RESULTS=pd.concat([DYN_RESULTS,df], ignore_index=True)
    df=load_results_parse('RK3v4p2')
    DYN_RESULTS=pd.concat([DYN_RESULTS,df], ignore_index=True)

    DYN_RESULTS['seen_ranking']=DYN_RESULTS['seen_ranking'].map(str)
    DYN_RESULTS['seen_ranking']=DYN_RESULTS['seen_ranking'].map(lambda x: x[:-2] if len(x)>10 else x)
    DYN_RESULTS['seen_ranking']=DYN_RESULTS['seen_ranking'].map(lambda x: x+'0' if len(x)<10 else x)
    DYN_RESULTS['seen_ranking']

    DYN_RESULTS=DYN_RESULTS.dropna(subset='click_id')
    return DYN_RESULTS