from otree.api import *
import random
import time

import numpy as np

import datetime

from copy import deepcopy

class C(BaseConstants):
    NAME_IN_URL = 'my_survey_static'

    RAKING_RANDOMIZED=True

    TIME_REFRESH=3

    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 4

    NUM_EXP_PARAM=2
    NUM_EXP_REP=3

    # debugging only
    PRINT_START_SESSION=False
    PRINT_EVENT=False
    PRINT_SEED_MATCHING=False
    PRINT_SEED_PICK_BEST=False
    PRINT_QUEUE=False
    PRINT_RANKING=False
    PRINT_POP=False

    TIMEOUT_ROUND=900



class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass
    
class Player(BasePlayer):
    participant_label = models.StringField(default=str(" "))

    initialized_round=models.IntegerField(initial=0)
    time_start_round=models.StringField()
    assigned_seed=models.IntegerField(initial=0)
    seed=models.StringField(initial=str(""))

    #<-------------- timeout management
    round_time_left=models.IntegerField()
    round_timed_out=models.IntegerField(initial=0)

    #<-------------- waiting 
    waited_n_refresh=models.IntegerField()

    #<-------------- round specific vars
    topic_number=models.IntegerField()
    # here I store the order of occurrences of topics
    interacted_topics=models.StringField(initial=str(""))

    #<-------------- user positioning vars
    positioning_user = models.IntegerField(widget = widgets.RadioSelect, label = '')
    time_positioning=models.StringField()

    partition_user=models.IntegerField()

    #<-------------- task explaination vars
    # I_understand = models.BooleanField(label = '')
    I_understand = models.BooleanField(choices=[[1, 'I understand']], widget=widgets.RadioSelect, label = '')
    time_taskexplaination=models.StringField()

    #<-------------- ranking vars
    # here I store the ranking that occurred for a specific player
    tmp_ranking=models.StringField()
    click_rank = models.IntegerField(label ='Feed',widget = widgets.RadioSelect, choices = range(20))
    click_id = models.IntegerField(label ='Feed')
    positioning_true=models.IntegerField()
    time_rankig = models.StringField()

    #<-------------- highlight vars
    #positioning = models.IntegerField(widget = widgets.RadioSelectHorizontal)
    highlight = models.IntegerField(choices=[[0,'Like'],[1,'Share'],[2,'Like and Share'],[3,'Do nothing']],widget=widgets.RadioSelect, label = '')
    read_more_highlight=models.IntegerField()
    time_highlight=models.StringField()

    #<-------------- text positioning vars
    positioning_text = models.IntegerField(widget = widgets.RadioSelect, label = '')
    read_more_positioning = models.IntegerField()
    time_positioning_text = models.StringField()
    
# # CUSTOM DATA EXPORT
# somewhy not working
# def custom_export(players):
#     events=player.session.vars['EVENTS']
#     # header row
#     yield [field_name for field_name in events[-1].keys()]

#     for ev in events:
#         yield [field_value for field_value in ev.values()]

class Topic(ExtraModel):
    group=models.Link(Group)
    topic_number=models.IntegerField()
    topic = models.StringField() 
    topic_name_short=models.StringField() 
    topic_spec =models.StringField() 
    topic_description=models.StringField()
    topic_description_left   =models.StringField()
    topic_description_right  =models.StringField()
    topic_description_neutral=models.StringField()

class Article(ExtraModel):
    # round_number,article_id,topic,stance,label,source,link,title,text
    group = models.Link(Group)
    topic_number=models.IntegerField()
    article_id = models.IntegerField()
    topic = models.StringField()
    stance = models.IntegerField() 
    label = models.StringField() 
    source = models.StringField() 
    abstract_cut=models.IntegerField()
    link = models.StringField() 
    title = models.StringField() 
    text = models.StringField()    

class InitialPopularity(ExtraModel):
    group = models.Link(Group)
    seed= models.IntegerField()
    partition=models.IntegerField()
    num_news=models.IntegerField()
    popularity=models.FloatField()

class PreviousEvents(ExtraModel):
    group = models.Link(Group)
    time= models.FloatField()
    seed=models.StringField()
    event=models.StringField()
    user_id=models.IntegerField()
    user_stance=models.IntegerField()
    user_partition=models.IntegerField()
    ranking=models.StringField()
    num_rank=models.IntegerField()
    num_news=models.IntegerField()
    news_stance=models.IntegerField()
    highlight=models.BooleanField()
    in_this_session=models.BooleanField()


# CUSTOM FUNCTIONS:

def positioning_user_choices(player):
    #here I select the articles to show to each player+round combination
    import numpy
    
    group = player.group
    choices_t = [[-2,'Strongly Left'],
                 [-1,'Leaning Left'],
                 [0,'Neutral'],
                 [+1,'Leaning Right'],
                 [+2,'Strongly Right']]    
    return choices_t

def positioning_text_choices(player):
    #here I select the articles to show to each player+round combination
    import numpy
    
    group = player.group
    choices_t = [[-2,'Strongly Left'],
                 [-1,'Leaning Left'],
                 [0,'Neutral'],
                 [+1,'Leaning Right'],
                 [+2,'Strongly Right']]   
    return choices_t

def time_spent_in_text_format(initial_time):
    return str(round(time.time()-initial_time, 2))    

def popularity_to_ranking(popularity):
    """
    take the popularity as a vector idx: popularity and returns a vector of idx:ranking
    ranking starts from 0
    """
    Number_of_news=len(popularity)
    popularity_expanded=[(n, pop) for n, pop in enumerate(popularity)] #<--- tuple (id, popularity)
    popularity_expanded=sorted(popularity_expanded, reverse=True, key=lambda x: x[1]) #<--- sorted idx (rank): (id, popularity)
    ranking=['placeholder' for _ in range(Number_of_news)]
    for rank, (n, pop) in enumerate(popularity_expanded):
        ranking[n]=rank
    return ranking


def player_waiting_priority(player, players_queue, open_topics):
    player_waiting_info=players_queue[player.id_in_subsession]
    player_topics=player_waiting_info['topics']
    player_time=player_waiting_info['time']

    priority_on_topic={str(t):True for t in open_topics}
    for t in player_topics:
        for p in players_queue:
            if p==player.id_in_subsession: pass
            if t in players_queue[p]['topics']:
                if players_queue[p]['time']>player_time:
                    priority_on_topic[t]=False
                if players_queue[p]['time']==player_time and int(p)<player.id_in_subsession:
                    priority_on_topic[t]=False
    
    priority_topics=""
    priority=False
    for t, t_priority in priority_on_topic.items():
        if t_priority:
            priority_topics+=t
            priority=True

    return {
        'priority': priority,
        'priority_topics': priority_topics
    }

def pet2seed(p,e,t):
    return str(p)+str(e)+str(t)              

def _get_topic_open_seeds(t, seed2open):
    open_seeds=[]
    for seed,open in seed2open.items():
        if seed[2]==t and open==1:
            open_seeds.append(seed)

    return open_seeds

def get_topics_open_seeds(topics, seed2open):
    open_seeds=[]
    for t in topics:
        open_seeds+=_get_topic_open_seeds(t, seed2open)

    return open_seeds

def pick_best_seed(player, seeds):
    """
    this function assumes that seeds in these parameters are already OPENED and MATCHING the player requirements
    """
    ############################## chooses the topic(s) that have most opened seeds
    #---- counts number of opened seeds per topic
    topic2nopens={}
    for s in seeds:
        t=s[2]
        if t not in topic2nopens: topic2nopens[t]=0 #---- initializes with topics that are matching the seeds passed
        topic2nopens[t]+=1

    #---- check which topics have the most opened spaces (can be more than one if same amount)
    max_opened=0
    most_opened_topics=[]
    for t, nopen in topic2nopens.items():
        if nopen>max_opened:
            most_opened_topics=[t]
            max_opened=nopen
        elif nopen==max_opened:
            most_opened_topics.append(t)
    
    #---- looks at the seeds corresponding to one of the most opened topic(s)
    seeds_to_choose_from=[]
    for s in seeds:
        for t in most_opened_topics:
            if s[2]==t:
                seeds_to_choose_from.append(s)
                break
    if C.PRINT_SEED_PICK_BEST:
        print("matching topics:", topic2nopens)
        print("most opened topics:", most_opened_topics)
    
    ############################### chooses the seed (among these topics) that have the least amount of updates
    #----- checks number of interactions per seed
    s2n={s:player.session.vars['seed2interactions'][s] for s in seeds_to_choose_from}
    if C.PRINT_SEED_PICK_BEST:
        print("corresponding seeds:", s2n)

    #----- finds the seed(s) that have least amount of interactions
    min_interactions=1000000
    least_interacted_seeds=[]
    for s, n in s2n.items():
        if n <min_interactions:
            least_interacted_seeds=[s]
            min_interactions=n
        elif n==min_interactions:
            least_interacted_seeds.append(s)
    if C.PRINT_SEED_PICK_BEST:
        print("least interacted seeds:", least_interacted_seeds)

    #---- if more seeds have least amount of interactions, pick one at random between the two
    return random.choice(least_interacted_seeds)        

def update_event_memory(player, seed, event, 
                        user_partition='', user_stance='', 
                        ranking='',
                        num_rank='', num_news='', news_stance='', 
                        highlight=''):
    player.session.vars['EVENTS'].append({
        'time': time.time(),
        'seed': seed,
        'event': event,
        'user_id': player.id_in_subsession,
        'user_stance': user_stance,
        'user_partition': user_partition,
        'ranking':ranking,
        'num_rank':num_rank,
        'num_news':num_news,
        'news_stance': news_stance,
        'highlight': highlight,
        'in_this_session': True,
    })

def timestamp_to_datetime(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime('%c')[4:-5] 

def event_list_to_table(subsession, event_list):
    TABLE_EVENTS='<table><tr>'
    for field in event_list[-1].keys():
        TABLE_EVENTS+='<th>{s:{c}<{n}}</th>'.format(s=str(field),n=12,c='_')
    TABLE_EVENTS+='</tr>'
    for ev in event_list[::-1]:
        TABLE_EVENTS+='<tr>'
        for field_name, field_value in ev.items():
            if field_name=='time':
                to_print=int(field_value-subsession.session.vars['start_time'])
                to_print=timestamp_to_datetime(field_value)
            else:
                to_print=field_value
            TABLE_EVENTS+=f'<td>{to_print}</td>'
        TABLE_EVENTS+='</tr>'
    TABLE_EVENTS+='</table>'

    return TABLE_EVENTS

# DOWNLOADABLES
def make_event_csv(event_list):
    if len(event_list)==0:
        return "No event of this type registered"
    csv_file=''
    for column,field_name in enumerate(event_list[-1].keys()):
        if column!=0: csv_file+=','
        csv_file+=field_name
    csv_file+='\\n'
    for ev in event_list:
        for column, (field_name, field_value) in enumerate(ev.items()):
            if column!=0: csv_file+=','
            if field_name=='time':
                csv_file+=str(int(field_value))
            else:
                csv_file+=str(field_value)
        csv_file+='\\n'
    
    return csv_file

def make_pop_csv(seed2pop):
    csv_file=''
    for column,field_name in enumerate(['seed','partition','num_news','popularity']):
        if column!=0: csv_file+=','
        csv_file+=field_name
    csv_file+='\\n'
    for seed in seed2pop.keys():
        for partition in seed2pop[seed].keys():
            for num_news, pop in seed2pop[seed][partition].items():
                for column, field_value in enumerate([seed,partition, num_news, pop]):
                    if column!=0: csv_file+=','
                    csv_file+=str(field_value)
                csv_file+='\\n'
    return csv_file

# SAFETY CHECKS
def check_pop_match(obj):
    seed2pop_initial=deepcopy(obj.session.vars['_SEED2POP_INITIAL'])
    seed2pop=deepcopy(obj.session.vars['SEED2POP'])
    events=[ev for ev in obj.session.vars['EVENTS'] if ev['in_this_session'] and ev['event']=='Interaction']
    
    #--------- re-calculate popularities
    for ev in events:
        seed=ev['seed']
        num_news=ev['num_news']
        highlight=ev['highlight']
        user_partition=ev['user_partition']

        #---- retrieves eta and lambda for this seed
        eta=obj.session.vars['SEED2PARAM'][seed]['eta']
        lam=obj.session.vars['SEED2PARAM'][seed]['lambda']

        AMOUNT_POP_INCREASE=1
        if highlight:
            AMOUNT_POP_INCREASE+=eta
        for partition in [-1,0,1]:
            if partition==user_partition:
                seed2pop_initial[seed][partition][num_news]+=AMOUNT_POP_INCREASE
            if partition!=user_partition:
                seed2pop_initial[seed][partition][num_news]+=AMOUNT_POP_INCREASE*lam

    #--------- compare with registered popularities
    POP_MATCH=True
    ERRORS_ON=[]
    for s in seed2pop:
        for p in seed2pop[s]:
            for n, pop in seed2pop[s][p].items():
                if not pop==seed2pop_initial[s][p][n]:
                    POP_MATCH=False
                    ERRORS_ON.append((s,p,n, pop, seed2pop_initial[s][p][n]))
    return POP_MATCH, ERRORS_ON

# REPORT
def vars_for_admin_report(subsession):
    import time
    current_time=time.time()
    seed2open=subsession.session.vars['seed2open']

    #################################### checking popularity match
    try:
        pop_match, errors=check_pop_match(subsession)
        if pop_match:
            CHECK_POP='Good'
        else:
            CHECK_POP='Bad<br>Errors found on:'
            for error in errors:
                CHECK_POP+='<br>'+str(error)
    except:
        CHECK_POP='Error occurred while evaluating'

    #################################### COMPUTING EXTREMISM AND POLARIZATION
    try:
        WINDOW_INTERACTIONS=100
        
        SEED2EXTREMISM={s:[] for s in seed2open.keys()}
        SEED2POL={s: {part:[] for part in [-1,0,1]} for s in seed2open.keys()}
        seed2countinteractions={seed: 0 for seed in seed2open.keys()}


        interaction_events=[ev for ev in subsession.session.vars['EVENTS'][::-1] if ev['event']=='Interaction']
        for ev in interaction_events:
            seed=ev['seed']
            #---- stops the count after the LAST WINDOW_INTERACTIONS interactions (see [::-1] in interaction_events definition)
            if seed2countinteractions[seed]>=WINDOW_INTERACTIONS:
                continue
            partition=ev['user_partition']
            click_stance=ev['news_stance']
            SEED2EXTREMISM[seed].append(click_stance)
            SEED2POL[seed][partition].append(click_stance)

            seed2countinteractions[seed]+=1

        for s, values in SEED2EXTREMISM.items():
            if len(values):
                SEED2EXTREMISM[s]=np.mean(np.abs(values))
            else:
                SEED2EXTREMISM[s]=0
        for s, p2v in SEED2POL.items():
            left_values=p2v[-1]
            right_values=p2v[1]
            if len(left_values) and len(right_values):
                SEED2POL[s]=sum(right_values)/len(right_values)-sum(left_values)/len(left_values)
            else:
                SEED2POL[s]=0


        #----- computing extremism and polarization averaging on repeated experiments
        PT2EXTR={}
        PT2POL={}
        for p in range(1, C.NUM_EXP_PARAM+1):
            for t in range(1, C.NUM_ROUNDS+1):
                extr_values=[SEED2EXTREMISM[pet2seed(p,e,t)] for e in range(1, C.NUM_EXP_REP+1)]
                pol_values=[SEED2POL[pet2seed(p,e,t)] for e in range(1, C.NUM_EXP_REP+1)]

                PT2EXTR[str(p)+str(t)]=sum(extr_values)/len(extr_values)
                PT2POL[str(p)+str(t)]=sum(pol_values)/len(pol_values)
    except:
        pass


    #################################### SEED 2 STATES TABLE
    try:
        s2tu={}
        for event in subsession.session.vars['EVENTS'][::-1]:
            if event['event'] not in ['Opened','Closed']: continue
            seed=event['seed']
            if seed not in s2tu:
                user_id=event['user_id']
                time_passed=current_time-event['time']
                if event['event']=='Opened':
                    open=1
                if event['event']=='Closed':
                    open=0
                s2tu[seed]={
                    'open':open,
                    'time': time_passed,
                    'user_id':user_id,
                }

        SEEDS=[s for s in seed2open.keys()]
        OPEN=[o for o in seed2open.values()]
        USER=[s2tu[s]['user_id'] for s in seed2open.keys()]
        _open_check=[s2tu[s]['open'] for s in seed2open.keys()]
        for o1,o2 in zip(OPEN, _open_check):
            assert o1==o2
        #-------- compute total interactions, including previous sessions
        seed2totinteractions={seed: 0 for seed in seed2open.keys()}
        seed2itsinteractions={seed: 0 for seed in seed2open.keys()}
        for event in subsession.session.vars['EVENTS']:
            if event['event']=='Interaction':
                seed2totinteractions[event['seed']]+=1
                if event['in_this_session']:
                    seed2itsinteractions[event['seed']]+=1
        INTERACTIONS_TOT=[seed2totinteractions[s] for s in seed2open.keys()]
        INTERACTIONS_ITS=[seed2itsinteractions[s] for s in seed2open.keys()]

        TIME=[s2tu[s]['time'] for s in seed2open.keys()]
        EXT=[SEED2EXTREMISM[s] for s in seed2open.keys()]
        POL=[SEED2POL[s] for s in seed2open.keys()]


        TABLE_SEEDS_STATE="<table>"
        TABLE_SEEDS_STATE+='  <tr>\
        <th>Seed______</th>\
        <th>Open___</th>\
        <th>User____</th>\
        <th>Interact.TOT___</th>\
        <th>Interact.ITS___</th>\
        <th>Extremism____</th>\
        <th>Polarization____</th>\
        <th>Time__(sec)___</th>\
        </tr>'

        for s, o, u, i, i_its, e, p, t in zip(SEEDS, OPEN, USER, INTERACTIONS_TOT, INTERACTIONS_ITS, EXT, POL, TIME):
            TABLE_SEEDS_STATE+= f""" <tr>
            <td><b>{s}</b></td>
            <td>{o}</td>
            <td>{u}</td>
            <td>{i}</td>
            <td>{i_its}</td>
            <td>{e:.4f}</td>
            <td>{p:.4f}</td>
            <td>{round(t)}</td>
            </tr>"""
        TABLE_SEEDS_STATE+='</table>'          
    except:
        TABLE_SEEDS_STATE='Error occurred while evaluating'

    #################################### TOPIC # OPEN TABLE
    try:
        topic2pe2open={t:{} for t in range(1,4+1)}
        topic2open_tot={t:0 for t in range(1,4+1)}
        param2open_tot={p:0 for p in range(1,C.NUM_EXP_PARAM+1)}
        total_overall=0
        for s, i in subsession.session.vars['seed2open'].items():
            topic2pe2open[int(s[2])][s[:2]]=i
            topic2open_tot[int(s[2])]+=i
            param2open_tot[int(s[0])]+=i
            total_overall+=i

        TABLE_TOPIC_OPEN='<table>'
        TABLE_TOPIC_OPEN+='<tr><th>Topic______________</th>'
        #---- headers
        for p in range(1, C.NUM_EXP_PARAM+1):
            for e in range(1, C.NUM_EXP_REP+1):
                TABLE_TOPIC_OPEN+=f'<th>p={p}_e={e}____</th>'
        TABLE_TOPIC_OPEN+='<th>Total</th>'
        TABLE_TOPIC_OPEN+='</tr>'
        #---- one row per each topic
        for t in range(1, C.NUM_ROUNDS+1):
            TABLE_TOPIC_OPEN+=f'<tr><td><b>{t}</b></td>'
            for p in range(1, C.NUM_EXP_PARAM+1):
                for e in range(1, C.NUM_EXP_REP+1):        
                    TABLE_TOPIC_OPEN+=f'<td>{topic2pe2open[t][str(p)+str(e)]}</td>'
            TABLE_TOPIC_OPEN+=f'<td>{topic2open_tot[t]}</td>'
        TABLE_TOPIC_OPEN+='</tr>'
        #--- row for total by parametrization
        TABLE_TOPIC_OPEN+='<tr><td>Total by param_____</td>'
        for p in range(1, C.NUM_EXP_PARAM+1):
            for e in range(1, C.NUM_EXP_REP+1):  
                if e==1:
                    TABLE_TOPIC_OPEN+=f'<td>{param2open_tot[p]}</td>'
                else:
                    TABLE_TOPIC_OPEN+='<td></td>'
        TABLE_TOPIC_OPEN+=f'<td>{total_overall}</td>'
        TABLE_TOPIC_OPEN+='</tr>'
        TABLE_TOPIC_OPEN+='</table>'
    except:
        TABLE_TOPIC_OPEN='Error occurred while evaluating'

    #################################### TOPIC # INTERACTIONS TABLE
    try:
        topic2pe2interactions={t:{} for t in range(1,4+1)}
        topic2interactions_tot={t:0 for t in range(1,4+1)}
        param2interactions_tot={p:0 for p in range(1,C.NUM_EXP_PARAM+1)}
        total_overall=0
        for s, i in subsession.session.vars['seed2interactions'].items():
            topic2pe2interactions[int(s[2])][s[:2]]=i
            topic2interactions_tot[int(s[2])]+=i
            param2interactions_tot[int(s[0])]+=i
            total_overall+=i

        TABLE_TOPIC_INTERACTIONS='<table>'
        TABLE_TOPIC_INTERACTIONS+='<tr><th>Topic______________</th>'
        #---- headers
        for p in range(1, C.NUM_EXP_PARAM+1):
            for e in range(1, C.NUM_EXP_REP+1):
                TABLE_TOPIC_INTERACTIONS+=f'<th>p={p}_e={e}____</th>'
        TABLE_TOPIC_INTERACTIONS+='<th>Total</th>'
        TABLE_TOPIC_INTERACTIONS+='</tr>'
        #---- one row per each topic
        for t in range(1, C.NUM_ROUNDS+1):
            TABLE_TOPIC_INTERACTIONS+=f'<tr><td><b>{t}</b></td>'
            for p in range(1, C.NUM_EXP_PARAM+1):
                for e in range(1, C.NUM_EXP_REP+1):        
                    TABLE_TOPIC_INTERACTIONS+=f'<td>{topic2pe2interactions[t][str(p)+str(e)]}</td>'
            TABLE_TOPIC_INTERACTIONS+=f'<td>{topic2interactions_tot[t]}</td>'
            TABLE_TOPIC_INTERACTIONS+='</tr>'
        #--- row for total by parametrization
        TABLE_TOPIC_INTERACTIONS+='<tr><td>Total by param_____</td>'
        for p in range(1, C.NUM_EXP_PARAM+1):
            for e in range(1, C.NUM_EXP_REP+1):  
                if e==1:
                    TABLE_TOPIC_INTERACTIONS+=f'<td>{param2interactions_tot[p]}</td>'
                else:
                    TABLE_TOPIC_INTERACTIONS+='<td></td>'
        TABLE_TOPIC_INTERACTIONS+=f'<td>{total_overall}</td>'
        TABLE_TOPIC_INTERACTIONS+='</tr>'
        TABLE_TOPIC_INTERACTIONS+='</table>'
    except:
        TABLE_TOPIC_INTERACTIONS='Error occurred while evaluating'

    ################################################## PT 2 METRICS TABLE
    try:
        TABLE_METRICS='<table>'
        TABLE_METRICS+='<tr><th>Parametrization_and_topic_____</th><th>Avg_Extremism_____</th><th>Avg_Polarization_____</th><th>Delta_Extremism____</th><th>Delta_Polarization____</th></tr>'
        for pt, extr in PT2EXTR.items():
            TABLE_METRICS+='<tr>'
            TABLE_METRICS+=f'<td>Param={pt[0]}_Topic={pt[1]}</td>'
            TABLE_METRICS+=f'<td>{extr:.4f}</td>'
            TABLE_METRICS+=f'<td>{PT2POL[pt]:.4f}</td>'
            if pt[0]=='1':
                TABLE_METRICS+=f'<td></td>'
                TABLE_METRICS+=f'<td></td>'
            else:
                TABLE_METRICS+=f'<td>{PT2EXTR[pt]-PT2EXTR["1"+pt[1]]:.5f}</td>'
                TABLE_METRICS+=f'<td>{PT2POL[pt]-PT2POL["1"+pt[1]]:.5f}</td>'
            TABLE_METRICS+='</tr>'
        TABLE_METRICS+='</table>'
    except:
        TABLE_METRICS='Error occurred while evaluating'

    #################################### CURRENT QUEUE REPORT
    try:
        queue=subsession.session.vars['players_queue']
        TABLE_QUEUE=""
        if len(queue)==0:
            TABLE_QUEUE+="No player currently in queue"
        else:
            TABLE_QUEUE+='<table>'
            TABLE_QUEUE+='<tr><th>user_id___</th><th>time_(sec)_____</th><th>topics____</th></tr>'
            for user, queue_row in queue.items():
                TABLE_QUEUE+='<tr>'
                TABLE_QUEUE+=f'<td>{user}</td>'
                TABLE_QUEUE+=f'<td>{queue_row["time"]*C.TIME_REFRESH}</td>'
                TABLE_QUEUE+=f'<td>{queue_row["topics"]}</td>'
                TABLE_QUEUE+='</tr>'
            TABLE_QUEUE+='</table>'
    except:
        TABLE_QUEUE='Error occurred while evaluating'

    #################################### WAITING OVERALL REPORT
    try:
        waiting_info=[]
        for p in subsession.get_players():
            for round_info in p.in_previous_rounds():
                wn=round_info.field_maybe_none('waited_n_refresh')
                if wn==None: continue
                if wn!=0:
                    waiting_info.append({
                        'user_id':round_info.id_in_subsession,
                        'waited_for': wn*C.TIME_REFRESH,
                        'round': round_info.round_number
                    })
        if len(waiting_info)==0:
            TABLE_WAITING='Nobody ever waited in this session'
        else:
            waiting_info=sorted(waiting_info, key=lambda x: x['waited_for'], reverse=True)
            TABLE_WAITING='<table>'
            TABLE_WAITING+='<tr><th>user_id____</th><th>waited_for_(sec)____</th><th>at_round_____</th></tr>'
            for waiting_row in waiting_info:
                TABLE_WAITING+='<tr>'
                TABLE_WAITING+=f'<td>{waiting_row["user_id"]}</td>'
                TABLE_WAITING+=f'<td>{waiting_row["waited_for"]}</td>'
                TABLE_WAITING+=f'<td>{waiting_row["round"]}</td>'
                TABLE_WAITING+='</tr>'
            TABLE_WAITING+='</table>'
    except:
        TABLE_WAITING='Error occurred while evaluating'


    #################################### TIMEOUT REPORT
    try:
        timeout_events=[]
        # for p in subsession.get_players():
        #     for round_info in p.in_previous_rounds():
        #         timed_out=round_info.round_timed_out
        #         if timed_out==1:
        #             timeout_events.append({
        #                 'user_id':round_info.id_in_subsession,
        #                 'time': int(float(round_info.time_start_round)+float(round_info.waited_n_refresh*C.TIME_REFRESH) +float(C.TIMEOUT_ROUND)  ),
        #                 'round':round_info.round_number,
        #             })
        for ev in subsession.session.vars['EVENTS'][::-1]:
            if 'Timeout' in ev['event']:
                timeout_events.append({
                    'seed':ev['seed'],
                    'user_id':ev['user_id'],
                    'time': ev['time'],
                })

        if len(timeout_events)==0:
            TABLE_TIMEOUT='Nobody ever got timed out in this session'
        else:
            timeout_events=sorted(timeout_events, key=lambda x: x['time'], reverse=True)
            TABLE_TIMEOUT='<table>'
            TABLE_TIMEOUT+='<tr><th>on_seed_____</th><th>user_id____</th><th>at_time____(sec)____</th></tr>'
            for timeout_event in timeout_events:
                TABLE_TIMEOUT+='<tr>'
                TABLE_TIMEOUT+=f'<td>{timeout_event["seed"]}</td>'
                TABLE_TIMEOUT+=f'<td>{timeout_event["user_id"]}</td>'
                TABLE_TIMEOUT+=f'<td>{timestamp_to_datetime(timeout_event["time"])}</td>'
                TABLE_TIMEOUT+='</tr>'
            TABLE_TIMEOUT+='</table>'
    except:
        TABLE_TIMEOUT='Error occurred while evaluating'


    ################################## TABLE OF RANKINGS
    try:
        sp2rnk={s:{} for s in subsession.session.vars['SEED2POP'].keys()}
        for s, p2pop in subsession.session.vars['SEED2POP'].items():
            for p in [-1,0,1]:
                news_pop=[p2pop[p][num_news] for num_news in range(10)]
                news_ranking=popularity_to_ranking(news_pop)
                ind=[ nr[0] for nr in sorted([(n, r) for n, r in enumerate(news_ranking)], reverse=False, key=lambda x: x[1]) ]
                rnk=''.join([str(k) for k in ind])
                sp2rnk[s][p]=rnk

        TABLE_RANKINGS='<table>'
        TABLE_RANKINGS+='<tr><th>seed____</th><th>partition_left_______</th><th>partition_center_____</th><th>partition_right______</th></tr>'
        for s, p2rnk in sp2rnk.items():
            TABLE_RANKINGS+=f'<tr><td>{s}</td>'
            for p, rnk in p2rnk.items():
                TABLE_RANKINGS+=f'<td>{rnk}</td>'
            TABLE_RANKINGS+='</tr>'
        TABLE_RANKINGS+='</table>'

    except:
        TABLE_RANKINGS='Error occurred while evaluating'
    
    ################################## TABLE ALL EVENTS
    try:
        all_events=subsession.session.vars['EVENTS']
        if len(all_events)==0:
            TABLE_ALL_EVENTS='No event yet'
        else:
            TABLE_ALL_EVENTS=event_list_to_table(subsession, all_events)
    except:
        TABLE_ALL_EVENTS='Error occurred while evaluating'

    ################################### TABLE INTERACTION EVENTS
    try:
        interaction_events=[ev for ev in all_events if ev['event']=='Interaction']
        if len(interaction_events)==0:
            TABLE_EVENTS_INTERACTIONS='No event yet'
        else:
            TABLE_EVENTS_INTERACTIONS=event_list_to_table(subsession, interaction_events)
    except:
        TABLE_EVENTS_INTERACTIONS='Error occurred while evaluating'

    ################################### TABLE SEED MANAGEMENT EVENTS
    try:
        seed_management_events=[ev for ev in all_events if ev['event']!='Interaction']
        if len(seed_management_events)==0:
            TABLE_EVENTS_SEEDS='No event yet'
        else:
            TABLE_EVENTS_SEEDS=event_list_to_table(subsession, seed_management_events)
    except:
        TABLE_EVENTS_SEEDS='Error occurred while evaluating'

    ################################# downloadables
    try:
        csv_all_events=make_event_csv(all_events)
    except:
        csv_all_events='Error occurred while evaluating'

    try:
        csv_interaction_events=make_event_csv(interaction_events)
    except:
        csv_interaction_events='Error occurred while evaluating'

    try:
        csv_popularities=make_pop_csv(subsession.session.vars['SEED2POP'])
    except:
        csv_popularities='Error occurred while evaluating'

    ################################# seed state closed for too long
    closed_state_good=True
    errors=[]
    for s,o,t in zip(SEEDS,OPEN,TIME):
        if o==0 and t>C.TIMEOUT_ROUND*1:
            closed_state_good=False
            errors.append((s,o,t))
    if closed_state_good:
        CHECK_CLOSED_STATE='Good'
    else:
        CHECK_CLOSED_STATE='Bad<br>'
        for error in errors:
            CHECK_CLOSED_STATE+=str(error)+'<br>'
    



    return {
        'CHECK_POP':CHECK_POP,
        'CHECK_CLOSED_STATE':CHECK_CLOSED_STATE,
        'TABLE_SEEDS_STATE':TABLE_SEEDS_STATE,
        'TABLE_QUEUE':TABLE_QUEUE,
        'TABLE_WAITING':TABLE_WAITING,
        'TABLE_TOPIC_OPEN':TABLE_TOPIC_OPEN,
        'TABLE_TOPIC_INTERACTIONS':TABLE_TOPIC_INTERACTIONS,
        'TABLE_METRICS':TABLE_METRICS,
        'TABLE_TIMEOUT':TABLE_TIMEOUT,
        'TABLE_RANKINGS':TABLE_RANKINGS,
        'TABLE_ALL_EVENTS':TABLE_ALL_EVENTS,
        'TABLE_EVENTS_INTERACTIONS':TABLE_EVENTS_INTERACTIONS,
        'TABLE_EVENTS_SEEDS':TABLE_EVENTS_SEEDS,
        'csv_all_events':csv_all_events,
        'csv_interaction_events':csv_interaction_events,
        'csv_popularities':csv_popularities,
    }

# # CUSTOM DATA EXPORT
# def custom_export(players):
#     events=player.session.vars['EVENTS']
#     # header row
#     yield [field_name for field_name in events[-1].keys()]

#     for ev in events:
#         yield [field_value for field_value in ev.values()]


# FUNCTIONS
def creating_session(subsession: Subsession):
    rows = read_csv('my_survey_static/article_info.csv', Article)
    for group in subsession.get_groups():
        for row in rows:
            #this generates the article instances
            Article.create(
                group = group,
                topic_number=row['topic_number'],
                article_id = row['article_id'],

                topic = row['topic'],
                stance = row['stance'],         
                label = row['label'], 

                source = row['source'],
                abstract_cut=row['abstract_cut'],
                link=row['link'],

                title = row['title'],
                text = row['text'],
                )  
            
    rows = read_csv('my_survey_static/topic_info.csv', Topic)
    for group in subsession.get_groups(): 
        for row in rows:
            #this generates the topic instances
            Topic.create(
                group = group,
                topic_number=row['topic_number'],

                topic=row['topic'],                 
                topic_name_short=row['topic_name_short'],
                topic_spec =row['topic_spec'],

                topic_description=row['topic_description'],                
                topic_description_left   =row['topic_description_left'],
                topic_description_right  =row['topic_description_right'],
                topic_description_neutral=row['topic_description_neutral']
                

                )
            
    ############################################### Loading previus popularities
    SEED2POP={}
    InitialPopularityRows= read_csv('my_survey_static/initial_popularity.csv', InitialPopularity)
    for group in subsession.get_groups():
        for row in InitialPopularityRows:
            InitialPopularity.create(
                group=group,
                seed=row['seed'],
                partition=row['partition'],
                num_news=row['num_news'],
                popularity=row['popularity']
            )

    for group in subsession.get_groups():
        for parm in range(1,1+C.NUM_EXP_PARAM):
            for nexp in range(1,1+C.NUM_EXP_REP):
                for t in range(1,1+C.NUM_ROUNDS):
                    seed=pet2seed(parm,nexp,t)
                    SEED2POP[seed]={}
                    for partition in [-1,0,1]:
                        SEED2POP[seed][partition]={}
                        this_pop=InitialPopularity.filter(group=group, seed=seed, partition=partition)
                        # ------------- to avoid loading a file with missing data
                        if not len(this_pop):
                            assert 0
                        # -------------------------------------------------------
                        for n2pop in this_pop:
                            SEED2POP[seed][partition][n2pop.num_news]=n2pop.popularity
        break
        #loading data from csv with otree using builtin read_csv requires filtering by group
        #but data here is the same for all groups so we do not need to create one file per group

    subsession.session.vars['SEED2POP']=deepcopy(SEED2POP)
    subsession.session.vars['_SEED2POP_INITIAL']=deepcopy(SEED2POP)

    #---- assigning parameters (eta, lambda) to each seed
    SEED2PARAM={}
    for seed in SEED2POP.keys():
        SEED2PARAM[seed]={}
        if seed[0]=='1':
            SEED2PARAM[seed]['lambda']=1
            SEED2PARAM[seed]['eta']=0
        if seed[0]=='2': 
            SEED2PARAM[seed]['lambda']=0
            SEED2PARAM[seed]['eta']=100
    subsession.session.vars['SEED2PARAM']=deepcopy(SEED2PARAM)          
            
    #---- initializing queue
    subsession.session.vars['players_queue']={}

    #---- initializing seed2open
    seed2open={}
    for parm in range(1,1+C.NUM_EXP_PARAM):
        for nexp in range(1,1+C.NUM_EXP_REP):
            for t in range(1,1+C.NUM_ROUNDS):
                seed2open[pet2seed(parm,nexp,t)]=1
    subsession.session.vars['seed2open']=deepcopy(seed2open)

    #---- saving start time
    subsession.session.vars['start_time']=time.time()

    ############################################### Loading previous events
    try:
        assert subsession.session.vars['_events_loaded']
        assert POPULARITY_FILE_STATE_GOOD

    except:
        EVENTS=[]
        PreviousEventsRows= read_csv('my_survey_static/previous_events.csv', PreviousEvents)
        for group in subsession.get_groups():
            for row in PreviousEventsRows:
                row['in_this_session']=False
                EVENTS.append(row)
            break


        #---- Updating current event memory (starting with dummy opening of the seeds)
        for seed in subsession.session.vars['seed2open'].keys():
            EVENTS.append({
                'time': time.time(),
                'seed': seed,
                'event': 'Opened',
                'user_id': 0,
                'user_stance': '',
                'user_partition': '',
                'ranking':'',
                'num_rank':'',
                'num_news':'',
                'news_stance': '',
                'highlight': '',  
                'in_this_session':True,
            })

        subsession.session.vars['EVENTS']=deepcopy(EVENTS)
        subsession.session.vars['_events_loaded']=True

        #---- to know how many times timeout failed (you can see when by events open with user_id=0)
        subsession.session.vars['DIAGNOSTIC_CORRECTED_TIMEOUTS']=0

        ################################################################### compares popularity and previous events file to see if they match
        POPULARITY_FILE_STATE_GOOD=True

        #---- creates a popularity dict that starts from 0
        _pop_check={}
        for s in SEED2POP.keys():
            _pop_check[s]={}
            for p in SEED2POP[s].keys():
                _pop_check[s][p]={}
                for n in SEED2POP[s][p].keys():
                    _pop_check[s][p][n]=0

        #---- elaborates it with interactions loaded from file of previous sessions
        for ev in EVENTS:
            if ev['event']=='Interaction':
                seed=ev['seed']
                num_news=ev['num_news']
                highlight=ev['highlight']
                user_partition=ev['user_partition']

                #---- retrieves eta and lambda for this seed
                eta=SEED2PARAM[seed]['eta']
                lam=SEED2PARAM[seed]['lambda']

                #---- add corresponding value
                AMOUNT_POP_INCREASE=1
                if highlight:
                    AMOUNT_POP_INCREASE+=eta
                for partition in [-1,0,1]:
                    if partition==user_partition:
                        _pop_check[seed][partition][num_news]+=AMOUNT_POP_INCREASE
                    if partition!=user_partition:
                        _pop_check[seed][partition][num_news]+=AMOUNT_POP_INCREASE*lam
        
        #--------- compare with popularity loaded from file of initial popularity for this session
        for s in SEED2POP:
            for p in SEED2POP[s]:
                for n, pop in SEED2POP[s][p].items():
                    if not np.abs(pop-_pop_check[s][p][n])<=0.1:
                        POPULARITY_FILE_STATE_GOOD=False
                    if C.PRINT_START_SESSION:
                        print(POPULARITY_FILE_STATE_GOOD, s,p,n, pop, _pop_check[s][p][n])
        if C.PRINT_START_SESSION:
            print("POPULARITY_FILE_STATE_GOOD:", POPULARITY_FILE_STATE_GOOD)
        assert POPULARITY_FILE_STATE_GOOD

        #---- initializing seed2interactions
        seed2interactions={seed: 0 for seed in seed2open.keys()}
        for ev in EVENTS:
            if ev['event']=='Interaction':
                seed2interactions[ev['seed']]+=1
        subsession.session.vars['seed2interactions']=deepcopy(seed2interactions)


        if C.PRINT_START_SESSION:
            # print(subsession.session.vars['EVENTS'])
            print("-----====[ SESSION STARTED ]====------")


def run_seed_diagnostic_and_correct(player):
    s2tu={}
    for event in player.session.vars['EVENTS'][::-1]:
        if event['event'] not in ['Opened','Closed']: continue
        seed=event['seed']
        if seed not in s2tu:
            user_id=event['user_id']
            time_passed=time.time()-event['time']
            if event['event']=='Opened':
                open=1
            if event['event']=='Closed':
                open=0
            s2tu[seed]={
                'open':open,
                'time': time_passed,
                'user_id':user_id,
            }
        if len(s2tu)==len(player.session.vars['seed2open']):
            break
        
    for s, s_info in s2tu.items():
        if s_info['open']==0 and s_info['time']>C.TIMEOUT_ROUND*1.2:
            player.session.vars['DIAGNOSTIC_CORRECTED_TIMEOUTS']+=1
            player.session.vars['seed2open'][s]=1
            player.session.vars['EVENTS'].append({
                'time': time.time(),
                'seed': s,
                'event': 'Timeout_admin',
                'user_id': '0',
                'user_stance': '',
                'user_partition': '',
                'ranking':'',
                'num_rank':'',
                'num_news':'',
                'news_stance': '',
                'highlight': '',
                'in_this_session': True,
            })
            player.session.vars['EVENTS'].append({
                'time': time.time(),
                'seed': s,
                'event': 'Opened',
                'user_id': '0',
                'user_stance': '',
                'user_partition': '',
                'ranking':'',
                'num_rank':'',
                'num_news':'',
                'news_stance': '',
                'highlight': '',
                'in_this_session': True,
            })

# PAGES
class Wait_until_seed_assigned(Page):

    @staticmethod
    def is_displayed(player):
        if player.assigned_seed==1:
            return False
        
        if player.initialized_round==0 and player.round_number==1:
            run_seed_diagnostic_and_correct(player)            

        if player.initialized_round==0:
            #---- this is for label managemen, should be put as soon as possible
            player.participant_label = player.participant.label
            
            #---- keeps track of round starting time 
            player.time_start_round=time_spent_in_text_format(0)
            player.waited_n_refresh=0
            
            if C.PRINT_EVENT:
                print(f"EVENT PLAYER {player.id_in_subsession} enters round {player.round_number}---------------------------------------")
            if C.PRINT_QUEUE:
                print(f"Queue seen by player {player.id_in_subsession}:", player.session.vars['players_queue'])

            #---- so this block of code does not get executed twice
            player.initialized_round=1

        if C.PRINT_QUEUE:
            print("is_displayed called by", player.id_in_subsession)

        #---- retrieve topic occurred in previous tasks
        if player.round_number==1:
            player.interacted_topics=""
        else:
            player.interacted_topics=player.in_previous_rounds()[-1].interacted_topics
        player_unseen_topics='1234'
        for t in player.interacted_topics:
            player_unseen_topics=player_unseen_topics.replace(t,'')

        #---- adds player to (local copy of) players queue
        players_queue=deepcopy(player.session.vars['players_queue'])
        #it's unclear when session variables are updated, so I'll create a local version
        players_queue[player.id_in_subsession]={
                'time':player.waited_n_refresh, 
                'topics': player_unseen_topics
            }
        
        #---- data about which seed is open
        seed2open=player.session.vars['seed2open']

        #---- finds open seeds on topics that player still has to answer to
        matching_open_seeds=get_topics_open_seeds(player_unseen_topics, seed2open)
        
        #---- if there are open seeds for these topics, then check if player has queue priority on those topics
        if len(matching_open_seeds)>0:
            #---- check if player has priority on any topic
            player_priority=player_waiting_priority(player, players_queue, player_unseen_topics)
            if C.PRINT_SEED_MATCHING:
                print("EVENT LOOKING FOR SEED--------------------------------------------------")
                print("matching open seeds available:", matching_open_seeds)
                print(f"player queue priotity: Player {player.id_in_subsession} priorities:", player_priority)

            #---- if player has priority on any topic, it checks if there are seed available on those
            if player_priority['priority']:
                priority_matching_open_seeds=get_topics_open_seeds(player_priority['priority_topics'], seed2open)

                #---- if there are open seeds for topic on which player has priority, 
                #---- then proceeds assigning a seed
                if len(priority_matching_open_seeds)>0:
                    if C.PRINT_SEED_MATCHING:
                        print("priority matching open seeds:", priority_matching_open_seeds)
                        # use this code if blank page is needed for this calculation
                        # player.participant.vars['seeds_to_choose_from']=priority_matching_open_seeds
                        # player.participant.vars['assigned_seed']=pick_best_seed(player.participant.vars['seeds_to_choose_from'])

                        ##################### SEED FOUND MANAGEMENT:
                        #---- assigns seed
                        print("CHOOSING BEST SEED")

                    chosen_seed=pick_best_seed(player, priority_matching_open_seeds)
                    player.participant.vars['assigned_seed']=chosen_seed

                    #---- closes the assigned seed
                    player.session.vars['seed2open'][ chosen_seed ] = 0

                    #---- keeps memory of the event
                    update_event_memory(player, chosen_seed, 'Closed')
                    
                    #---- removes player from the queue
                    if player.id_in_subsession in player.session.vars['players_queue']:
                        player.session.vars['players_queue'].pop(player.id_in_subsession)

                    #####################
                    if C.PRINT_EVENT:
                        print("EVENT SEED CLOSED--------------------------------------------------------")
                        print(f"Player {player.id_in_subsession} assigned seed",player.participant.vars['assigned_seed'] )
                        print("seed state:")
                        print(player.session.vars['seed2open'])
                        print("last event memorized:")
                        print(player.session.vars['EVENTS'][-1])
                        print("-------------------------------------------------------------------------")
                    player.assigned_seed=1

                    return False
                
        if player.waited_n_refresh==0: #meaning it starts waiting now
            update_event_memory(player, '000', 'Waiting')
        player.waited_n_refresh+=1
        players_queue[player.id_in_subsession]['time']+=1
        player.session.vars['players_queue']=deepcopy(players_queue)
        
        if C.PRINT_QUEUE:
            print("EVENT PLAYER SENT TO QUEUE")
            print(f"Queue seen by player {player.id_in_subsession}:", player.session.vars['players_queue'])

        return True

    @staticmethod
    def vars_for_template(player):
        return dict(
            TIME_REFRESH=C.TIME_REFRESH,
            round_number=player.round_number,
        )

# class Blank_assign_seed(Page):
#     # we need this page because not sure why is_displayed is running twice thus assigning more seeds to each participant
#     timeout_seconds =0.0
    
#     @staticmethod
#     def vars_for_template(player):
#         return dict(
#             round_number=player.round_number,
#         )
    
#     @staticmethod
#     def before_next_page(player, timeout_happened):
             #here goes the code for assigning seed if needed

def get_timeout_seconds(player):
    return player.round_time_left


class Positioning(Page):
    form_model = 'player'
    form_fields = ['positioning_user']
    
    # Initializes round timer with setting var
    timeout_seconds=C.TIMEOUT_ROUND 
    
    @staticmethod
    def vars_for_template(player):
        # player.time_wait=time_spent_in_text_format(player.participant.vars["time_holder"])

        player.participant.vars["time_holder"] = time.time()
        group = player.group

        # player.interacted_topics=player.interacted_topics
        
        player.seed=player.participant.vars['assigned_seed']
        topic_number=int(player.seed[2])
        # stores this info of this topic occurring for next tasks
        player.interacted_topics=player.interacted_topics+str(topic_number)
        # label this round with this topic
        player.topic_number=topic_number

        t_topic=Topic.filter(group=group, topic_number=topic_number)[0]
        topic=t_topic.topic
        topic_name_short=t_topic.topic_name_short      
        topic_spec =t_topic.topic_spec

        topic_description=t_topic.topic_description

        topic_description_left=t_topic.topic_description_left
        topic_description_right=t_topic.topic_description_right
        topic_description_neutral=t_topic.topic_description_neutral
            
        return dict(
            topic = topic, 
            topic_name_short = topic_name_short, 
            topic_spec  = topic_spec,
            round_number = player.round_number,
            topic_number = player.topic_number,
            interacted_topics=player.interacted_topics,
            topic_description=topic_description,
            topic_description_left=topic_description_left,
            topic_description_right=topic_description_right,
            topic_description_neutral=topic_description_neutral
            )
    
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.round_timed_out=1

            #---- keeps memory of the event
            update_event_memory(player, player.seed, 'Timeout')

            #---- reopens the seed
            player.session.vars['seed2open'][player.seed]=1
            update_event_memory(player, player.seed, 'Opened')
            
        else:
            time_spent_on_this_page=time_spent_in_text_format(player.participant.vars["time_holder"])

            player.time_positioning = time_spent_on_this_page

            player.round_time_left = C.TIMEOUT_ROUND - int(float(time_spent_on_this_page))

            if player.positioning_user <0:
                player.partition_user=-1
            if player.positioning_user==0:
                player.partition_user=0
            if player.positioning_user>0:
                player.partition_user=1
    

class Task_explaination(Page):
    form_model ='player'
    form_fields=['I_understand']

    get_timeout_seconds=get_timeout_seconds

    @staticmethod
    def is_displayed(player):
        return player.round_timed_out==0

    @staticmethod
    def vars_for_template(player):
        player.participant.vars["time_holder"] = time.time()
        group = player.group

        t_topic=Topic.filter(group=group, topic_number=player.topic_number)[0]
        topic=t_topic.topic
        topic_name_short=t_topic.topic_name_short
        topic_spec =t_topic.topic_spec
            
        return dict(
            topic = topic, 
            topic_name_short = topic_name_short, 
            topic_spec  = topic_spec,
            round_number = player.round_number,
            topic_number = player.topic_number
            )
    
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.round_timed_out=1

            #---- keeps memory of the event
            update_event_memory(player, player.seed, 'Timeout')

            #---- reopens the seed
            player.session.vars['seed2open'][player.seed]=1
            update_event_memory(player, player.seed, 'Opened')

        else:
            time_spent_on_this_page=time_spent_in_text_format(player.participant.vars["time_holder"])

            #assign time ranking
            player.time_taskexplaination = time_spent_on_this_page
            player.round_time_left=player.round_time_left-int(float(time_spent_on_this_page))


class Ranking_1(Page):
    
    form_model = 'player'
    form_fields = ['click_rank']

    get_timeout_seconds=get_timeout_seconds

    def is_displayed(player):
        return player.round_timed_out==0
   
    
    #here I select the titles to show
    def vars_for_template(player):

        player.participant.vars["time_holder"] = time.time()
        
        group = player.group
        t_topic=Topic.filter(group=group, topic_number=player.topic_number)[0]
        topic=t_topic.topic
        topic_name_short=t_topic.topic_name_short
        topic_spec=t_topic.topic_spec
            
        titles = []
        labels = []    
        articles_selected = Article.filter(group=group,topic = topic)
    
        for i,a in enumerate(articles_selected):
            titles.append([a.title,])
            labels.append([a.label,]) #<--------- here it's decided what's used as label under the title during ranked titles selection
    

        if C.RAKING_RANDOMIZED:
        # ################### randomizing ranking
            ind = [i for i in range(10)]
            # random.seed(player.id_in_subsession)
            random.shuffle(ind)
        #######################################################################
        else:
            news_pop=[player.session.vars['SEED2POP'][player.seed][player.partition_user][num_news] for num_news in range(10)]
            news_ranking=popularity_to_ranking(news_pop)#is fed a list [popularity] and returns a list ordered by num news [ranking]
            ind=[ nr[0] for nr in sorted([(n, r) for n, r in enumerate(news_ranking)], reverse=False, key=lambda x: x[1]) ]
        
        if C.PRINT_RANKING:
            print("News items popularities:", news_pop)
            # print(news_ranking)
            print("News items ordered by popularity:", ind)

        titles_new =[]
        labels_new = []
        for _,j in enumerate(ind):
            titles_new.append(titles[j][0])
            labels_new.append(labels[j][0])
            

        variables = [f'title_{i}' for i in range(10)]
        vars_dict = dict(zip(variables,titles_new))
        
        variables_source = [f'source_{i}' for i in range(10)]
        dict_source = dict(zip(variables_source,labels_new))
        
        vars_dict.update({'round_number' : player.round_number})
        vars_dict.update({'topic_number' : player.topic_number})
        vars_dict.update(dict_source)
        vars_dict.update({'topic_spec' : topic_spec})
        vars_dict.update({'topic_name_short' : topic_name_short})


        # I store this here to pass to the next page
        # it is a string containing digit from 0-9 
        # indicating the ranking the player was exposed to 
        player.tmp_ranking=''.join([str(k) for k in ind])

        return vars_dict

    #NB this is indide ranking_1 page class
    #here I save the article id that belongs to that click
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.round_timed_out=1

            #---- keeps memory of the event
            update_event_memory(player, player.seed, 'Timeout')

            #---- reopens the seed
            player.session.vars['seed2open'][player.seed]=1
            update_event_memory(player, player.seed, 'Opened')

        else:
            time_spent_on_this_page=time_spent_in_text_format(player.participant.vars["time_holder"])

            #assign time ranking
            player.time_rankig = time_spent_on_this_page
            player.round_time_left=player.round_time_left-int(float(time_spent_on_this_page))

            group = player.group
            t_topic=Topic.filter(group=group, topic_number=player.topic_number)[0]
            topic=t_topic.topic
            article_ids = []    
            articles_selected = Article.filter(group=group,topic = topic, )
        
            for i,a in enumerate(articles_selected):
                article_ids.append([a.article_id,])
        
            # ind = [i for i in range(10)]
            # random.seed(player.id_in_subsession)
            # random.shuffle(ind)
            # here I extract the info about the ranking the player was exposed to
            # which I stored as a string of digits 0-9 ordered accordingly
            ind=[int(k) for k in player.tmp_ranking]
            
            article_ids_new =[]
            for i,j in enumerate(ind):
                article_ids_new.append(article_ids[j][0])
            
            click_rank = int(player.click_rank)
            
            #assign article id to selected news
            player.click_id = article_ids_new[click_rank]

            # #memorizing stance of clicked news item
            player.positioning_true= Article.filter(group=group,topic = topic, article_id=article_ids_new[click_rank])[0].stance




    
    
class Highlight(Page):
    form_model = 'player'
    form_fields = ['highlight','read_more_highlight']

    get_timeout_seconds=get_timeout_seconds

    @staticmethod
    def is_displayed(player):
        return player.round_timed_out==0

    @staticmethod
    def vars_for_template(player):
        player.participant.vars["time_holder"] = time.time()

        click_id = int(player.click_id)
        group = player.group
        t_topic=Topic.filter(group=group, topic_number=player.topic_number)[0]
        topic=t_topic.topic
        topic_name_short=t_topic.topic_name_short
        topic_spec =t_topic.topic_spec

        article_selected = Article.filter(group = group ,article_id = click_id)[0]
        title = article_selected.title
        text = article_selected.text
        source = article_selected.source
        abstract_cut=article_selected.abstract_cut
        return dict(
            topic = topic,
            topic_name_short = topic_name_short,
            topic_spec  = topic_spec,

            text = text,
            abstract=text[:abstract_cut],
            title = title,
            source = source,
            round_number = player.round_number,
            topic_number = player.topic_number,

            )
    
    # @staticmethod
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.round_timed_out=1

            #---- keeps memory of the event
            update_event_memory(player, player.seed, 'Timeout')

            #---- reopens the seed
            player.session.vars['seed2open'][player.seed]=1
            update_event_memory(player, player.seed, 'Opened')

        else:
            time_spent_on_this_page=time_spent_in_text_format(player.participant.vars["time_holder"])

            #assign time ranking
            player.time_highlight = time_spent_on_this_page
            player.round_time_left=player.round_time_left-int(float(time_spent_on_this_page))


            ######################################## updates the popularities
            #---- retrieves eta and lambda for this seed
            eta=player.session.vars['SEED2PARAM'][player.seed]['eta']
            lam=player.session.vars['SEED2PARAM'][player.seed]['lambda']
            
            #---- extract num news (second character of news_id) (because SEED2POP is indexed by that instead of full id)
            num_news=int(str(player.click_id)[1])

            #---- calculates amount of increase
            AMOUNT_POP_INCREASE=1
            if player.highlight<3:
                highlight=True
            else:
                highlight=False
            if highlight:
                AMOUNT_POP_INCREASE+=eta

            #---- performs the update on all partitions
            if C.PRINT_POP:
                print("EVENT POP INCREASE------------------------------------------------------")
            for partition in [-1,0,1]:
                if partition==player.partition_user:
                    player.session.vars['SEED2POP'][player.seed][partition][num_news]+=AMOUNT_POP_INCREASE
                if partition!=player.partition_user:
                    player.session.vars['SEED2POP'][player.seed][partition][num_news]+=AMOUNT_POP_INCREASE*lam

                if C.PRINT_POP:
                    print(f"Seed {player.seed}, partition {partition},\
                        new pop of item {player.click_id}:", player.session.vars['SEED2POP'][player.seed][partition][num_news])
            if C.PRINT_EVENT:
                print("last event memorized:")
                print(player.session.vars['EVENTS'][-1])

            #---- keeps track of number of total interactions
            player.session.vars['seed2interactions'][player.participant.vars['assigned_seed']] +=1

            #---- keeps memory of the event
            update_event_memory(player, player.seed, 'Interaction', 
                                user_partition=player.partition_user, user_stance=player.positioning_user,
                                ranking=player.tmp_ranking,
                                num_rank=player.click_rank, num_news=num_news, news_stance=player.positioning_true, 
                                highlight=highlight)
            

            ######################################## reopens the seed

            #---- reopens the seed
            player.session.vars['seed2open'][player.participant.vars['assigned_seed']] = 1

            #---- keeps memory of the event 
            update_event_memory(player, player.seed, 'Opened')
            if C.PRINT_EVENT:
                print("EVENT SEED OPENED--------------------------------------------------------")
                print("seed state:")
                print(player.session.vars['seed2open'])
                print("seed interactions:")
                print(player.session.vars['seed2interactions'])
                print("last event memorized:")
                print(player.session.vars['EVENTS'][-1])
                print("-------------------------------------------------------------------------")
            

class Positioning_text(Page):
    form_model = 'player'
    form_fields = ['positioning_text','read_more_positioning']

    @staticmethod
    def is_displayed(player):
        return player.round_timed_out==0

    @staticmethod
    def vars_for_template(player):
        player.participant.vars["time_holder"] = time.time()

        click_id = int(player.click_id)
        group = player.group
        t_topic=Topic.filter(group=group, topic_number=player.topic_number)[0]
        topic=t_topic.topic
        topic_name_short=t_topic.topic_name_short
        topic_spec =t_topic.topic_spec

        article_selected = Article.filter(group = group ,article_id = click_id)[0]
        title = article_selected.title
        text = article_selected.text
        source = article_selected.source
        abstract_cut=article_selected.abstract_cut
        return dict(
            topic = topic,
            topic_name_short = topic_name_short,
            topic_spec  = topic_spec,

            text = text,
            abstract=text[:abstract_cut],
            title = title,
            source = source,
            round_number = player.round_number,
            topic_number = player.topic_number,

            )
    
    # @staticmethod
    def before_next_page(player, timeout_happened):
       player.time_positioning_text = time_spent_in_text_format(player.participant.vars["time_holder"])
    


# page_sequence = [Wait_until_seed_found, Blank_assign_seed, Positioning, Task_explaination, Ranking_1, Highlight, Positioning_text]

page_sequence = [Wait_until_seed_assigned, Positioning, Task_explaination, Ranking_1, Highlight, Positioning_text]
