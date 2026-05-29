from otree.api import *
import random
import time

class C(BaseConstants):
    NAME_IN_URL = 'my_survey_static'
    PLAYERS_PER_GROUP = 20
    NUM_ROUNDS = 5


class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass
    
class Player(BasePlayer):
    click_rank = models.IntegerField(label ='Feed',widget = widgets.RadioSelect, choices = range(20))
    click_id = models.IntegerField(label ='Feed')
    positioning = models.IntegerField(label ='Feed', widget = widgets.RadioSelectHorizontal, choices = [[+2,'Strongly Pro'],[+1,'Pro'],[0,'Neither Pro or Against'],[-1,'Against'],[-2,'Strongly Against']])
    highlight = models.BooleanField(choices=[[1,'Yes'],[0,'No']],blank= True, label = 'Would you give a like to this content on your personal social media platforms (e.g. Facebook, Twitter...)?')
    post_social_media = models.BooleanField(choices=[[1,'Yes'],[0,'No']],blank= True, label = 'Would you re-share this content on your personal social media platforms (e.g. Facebook, Twitter...)?')
    t_ranking = models.StringField()
    t_read = models.StringField()

class Article(ExtraModel):
    group = models.Link(Group)
    article_id = models.IntegerField()
    topic = models.StringField()
    clean_url = models.StringField()
    domain = models.StringField()
    first_post_time = models.StringField()
    id_estimation = models.StringField()
    quality = models.StringField()
    title = models.StringField()
    abstract = models.StringField() 
    id_bucket = models.IntegerField()  
    quality_bucket = models.IntegerField() 
    selected = models.IntegerField() 
    
                  
# CUSTOM FUNCTIONS:

def time_spent_in_text_format(initial_time):
    return str(round(time.time()-initial_time, 2))    
    
# FUNCTIONS
def creating_session(subsession: Subsession):
    rows = read_csv('my_survey_static/selected_news.csv', Article)
    for group in subsession.get_groups():
        for row in rows:
            #this generates the article instances
            Article.create(
                group = group,
                article_id = row['article_id'],
                topic = row['topic'],
                clean_url = row['clean_url'],
                title = row['title'],
                abstract = row['abstract'],
                domain = row['domain'],
                first_post_time = row['first_post_time'],
                id_estimation = row['id_estimation'],
                id_bucket = row['id_bucket'],
                quality = row['quality'],
                quality_bucket = row['quality_bucket'],
                selected = row['selected'],
                )  
        
# PAGES

class Positioning(Page):
    form_model = 'player'
    form_fields = ['positioning']
    
    # this is in case we want more than one round with the same topic
    #@staticmethod
    #def is_displayed(player):
    #   return player.round_number % 2 != 0
    
    @staticmethod
    def vars_for_template(player):
        group = player.group
        if (group.round_number == 1):
            topic = 'Climate Change legislation'
        if (group.round_number == 2):
            topic = 'Abortion and reproductive laws'
        if (group.round_number == 3):
            topic = 'Gun control or fire-arms regulation'
        if (group.round_number == 4):
            topic = 'Covid-19 vaccination effectiveness'
        if (group.round_number == 5):
            topic = 'Immigration policy of the Joe Biden administration'
            
        return dict(
            topic = topic,round_number = player.round_number)
    

class Ranking_1(Page):
    
    form_model = 'player'
    form_fields = ['click_rank']
   
    
    #here I select the titles to show
    def vars_for_template(player):

        player.participant.vars["time_holder"] = time.time()
        
        group = player.group
        if (group.round_number == 1):
            topic = 'climate'   
            topic_name = 'Climate Change legislation'
        if (group.round_number == 2):
            topic = 'abortion'
            topic_name = 'Abortion and reproductive laws'
        if (group.round_number == 3):
            topic = 'guncontrol'
            topic_name = 'Gun control or fire-arms regulation'
        if (group.round_number == 4):
            topic = 'vaccines'
            topic_name = 'Covid-19 vaccination effectiveness'
        if (group.round_number == 5):
            topic = 'migration'
            topic_name = 'Immigration in the US'
            
        titles = []
        sources = []    
        articles_selected = Article.filter(group=group,topic = topic, selected = 1)
    
        for i,a in enumerate(articles_selected):
            titles.append([a.title,])
            sources.append([a.domain,])
    
        ind = [i for i in range(10)]
        random.seed(player.id_in_group)
        random.shuffle(ind)
        
        titles_new =[]
        sources_new = []
        for i,j in enumerate(ind):
            titles_new.append(titles[j][0])
            sources_new.append(sources[j][0])

        variables = [f'title_{i}' for i in range(10)]
        vars_dict = dict(zip(variables,titles_new))
        
        variables_source = [f'source_{i}' for i in range(10)]
        dict_source = dict(zip(variables_source,sources_new))
        
        vars_dict.update({'round_number' : player.round_number})
        vars_dict.update(dict_source)
        vars_dict.update({'topic' : topic_name})

        return vars_dict


    #here I save the article id that belongs to that click
    def before_next_page(player,timeout_happened):
        group = player.group
        if (group.round_number == 1):
            topic = 'climate'   
        if (group.round_number == 2):
            topic = 'abortion'
        if (group.round_number == 3):
            topic = 'guncontrol'
        if (group.round_number == 4):
            topic = 'vaccines'
        if (group.round_number == 5):
            topic = 'migration'
            
        article_ids = []    
        articles_selected = Article.filter(group=group,topic = topic, selected = 1)
    
        for i,a in enumerate(articles_selected):
            article_ids.append([a.article_id,])
    
        ind = [i for i in range(10)]
        random.seed(player.id_in_group)
        random.shuffle(ind)
        
        article_ids_new =[]
        for i,j in enumerate(ind):
            article_ids_new.append(article_ids[j][0])
        
        click_rank = int(player.click_rank)
        
        #assign article id to selected news
        player.click_id = article_ids_new[click_rank]

        #assign time ranking
        player.t_ranking = time_spent_in_text_format(player.participant.vars["time_holder"])

        
class Show_content(Page):
    form_model = 'player'
    @staticmethod
    def vars_for_template(player):

        player.participant.vars["time_holder"] = time.time()
        click_id = int(player.click_id)
        group = player.group
        article_selected = Article.filter(group = group ,article_id = click_id)
        for a in article_selected:
            title = a.title
            abstract = a.abstract
            source = a.domain
            clean_url = a.clean_url
            print(clean_url)
        return dict(
            text = abstract,
            title = title,
            source = source,
            clean_url = clean_url,
            round_number = player.round_number)

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.t_read = time_spent_in_text_format(player.participant.vars["time_holder"])
    
class Highlight(Page):
    form_model = 'player'
    form_fields = ['highlight','post_social_media']
    @staticmethod
    def vars_for_template(player):
        click_id = int(player.click_id)
        group = player.group
        article_selected = Article.filter(group = group ,article_id = click_id)
        for a in article_selected:
            title = a.title
            abstract = a.abstract
            source = a.domain
            clean_url = a.clean_url
        return dict(
            text = abstract,
            title = title,
            source = source,
            clean_url = clean_url,
            round_number = player.round_number)



page_sequence = [Positioning, Ranking_1, Show_content, Highlight]
