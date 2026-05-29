from os import environ


SESSION_CONFIGS = [
    dict(
        name='My_survey_static',
        display_name="Ranking experiment static",
        # app_sequence=['introduction','my_survey_static','ideology', 'demographics_and_payment'], num_demo_participants=20, #introduction is on qualtrics
        app_sequence=['my_survey_static','ideology', 'demographics_and_payment'], num_demo_participants=200,
        completionlink='https://app.prolific.com/submissions/complete?cc=PLACEHOLDER', #<--- "use a placeholder link, and replace once you have a study created in prolific"
        ),
#    dict(
#         name='My_survey_updates',
#         display_name="Ranking experiment with updates",
#         app_sequence=['introduction','my_survey_dynamic','ideology', 'demographics_and_payment'], num_demo_participants=6,
#     ),    
]


# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

PARTICIPANT_FIELDS = []

# in the experiments, these are stored FOR EACH participants
# which made experiment data redundantly big
# I am keeping because it was here during the experiment
# but you are free to leave it as empty list
SESSION_FIELDS = [
    '_events_loaded',
    '_SEED2POP_INITIAL',
    'SEED2POP',
    'SEED2PARAM',
    "players_queue", 
    "seed2open", "seed2interactions",
    "EVENTS",
    'DIAGNOSTIC_CORRECTED_TIMEOUTS',
    "start_time"
]

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True

ROOMS = [
    dict(
        name='test',
        display_name='Test',
        #participant_label_file='_rooms/test.txt',
    ),
]

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """
Here are some oTree games.
"""


SECRET_KEY = 'YOUR_SECRET_KEY_HERE'

INSTALLED_APPS = ['otree']
