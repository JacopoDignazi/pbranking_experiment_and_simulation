from otree.api import *

class C(BaseConstants):
    NAME_IN_URL = 'demographics'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1



class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass
    
class Player(BasePlayer):
    age = models.StringField(
        choices=[['18-24', '18-24'], ['25-34', '25-34'], ['35-44','35-44'],['45-54', '45-54'],['55-64', '55-64'],['65+', '65 or older'],['Prefer_not_to_say', 'Prefer not to say']],
        label='What is your age group?',
        widget=widgets.RadioSelect,
    )
    gender = models.StringField(
        choices=[['Male', 'Male'], ['Female', 'Female'], ['Other','Other'],['Prefer_not_to_say', 'Prefer not to say']],
        label='What gender do you identify with?',
        widget=widgets.RadioSelect,
    )
    gender_open = models.StringField(label='If you answered "Other" in the previous question, you can type below and specify your gender identity:', blank=True)
    
    comment=models.StringField(label='', blank=True)
        
# PAGES
class Demographics_1(Page):
    form_model = 'player'
    form_fields = ['age', 'gender','gender_open']

class Comment(Page):
    form_model= 'player'
    form_fields = ['comment']
 
class PaymentInfo(Page):

    # @staticmethod
    # def vars_for_template(player: Player):
    #     participant = player.participant
    #     return dict(redemption_code=participant.label or participant.code)

    
    from_model= 'player'  #<---- WIP

    @staticmethod              
    def js_vars(player):
        return dict(
            completionlink=
              player.subsession.session.config['completionlink']
        )


page_sequence = [Demographics_1, Comment, PaymentInfo]

