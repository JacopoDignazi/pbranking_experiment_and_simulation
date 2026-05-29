from otree.api import *

class C(BaseConstants):
    NAME_IN_URL = 'ideology'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass
    
class Player(BasePlayer):
    leaning = models.StringField(
        choices=[['Democrat', 'Democrat'], ['Republican', 'Republican'], ['Independent','Independent'],['None', 'None of the options']],
        label='How do you consider yourself?',
        widget=widgets.RadioSelect,
    )
    leaning_strength = models.StringField(
        choices=[['Strong', 'Strong'], ['Moderate', 'Moderate']],
        label='Within the leaning you selected, how strong to you consider your ideology orientation to be?',
        widget=widgets.RadioSelect,
    )
    center_strength = models.StringField(
        choices=[['Democrat Party', 'Democrat Party'], ['Republican Party', 'Republican Party'],['Center', 'Completely in the middle']],
        label='do you consider yourself closer to the:',
        widget=widgets.RadioSelect,
    )
        
        
# PAGES
class Leaning(Page):
    form_model = 'player'
    form_fields = ['leaning']
    
class Leaning_strength(Page):
    form_model = 'player'
    form_fields = ['leaning_strength']  
    @staticmethod
    def vars_for_template(player: Player):
        return dict(leaning=player.leaning)  
    @staticmethod
    def is_displayed(player):
    	return (player.leaning == 'Democrat') or (player.leaning == 'Republican')
    	
class Center(Page):
    form_model = 'player'
    form_fields = ['center_strength']  
    @staticmethod
    def vars_for_template(player: Player):
        return dict(leaning=player.leaning)  
    @staticmethod
    def is_displayed(player):
    	return (player.leaning == 'Independent') or (player.leaning == 'None')
 


page_sequence = [Leaning, Leaning_strength, Center]
