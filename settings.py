from os import environ

SESSION_CONFIGS = [
   

    dict(
        name='leader_baseline',
        app_sequence=[
            'video',
            'leader',
             'q',
            ],
        treatment='control',
        num_demo_participants=3,
    ),
    dict(
        name='leader_treatment',
        app_sequence=[
            'video',
            'leader',
             'q',
            ],
        treatment='manipulation',
        num_demo_participants=3,
    ),
    #  dict(
    #     name='q_only',
    #     display_name='Final questionnaire only',
    #     app_sequence=[
    #         'q',
    #
    #         ],
    #     num_demo_participants=1,
    # ),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc="",
    round_one_minutes=10,
    other_round_minutes=3,
    endowment=5,
    prolific_redirect_url='https://app.prolific.co/submissions/complete?cc=C1N6GE6V',
    prolific_timeout_url='https://app.prolific.co/submissions/complete?cc=SKIPPED'
)

PARTICIPANT_FIELDS = []
SESSION_FIELDS = []

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'GBP'
USE_POINTS = False

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = '2327454921041'
ROOMS = [

    dict(
        name='prolific',
        display_name='Prolific'
    ),
]