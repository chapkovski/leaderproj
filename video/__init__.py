from otree.api import *
from otree.database import dbq

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'video'
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS = 4
    CONTROL = 'control'
    MANIPULATION = 'manipulation'
    TREATMENTS = [ MANIPULATION,CONTROL]
    VIDEOS_CONTROL = ['ddt_IGMMOrI'] * NUM_ROUNDS
    VIDEOS_TREATMENT = [
        'xNk-98TIW8s',
        'ZZeGJs6A_wQ',
        'dPX2sdl-j4g',
        'zAsAHTb9thQ'
    ]


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    treatment = models.StringField()
    video = models.StringField()
    treatment_q1 = models.StringField(label='What role could a team leader play to improve team task results? ',
                                      choices=["Supervisor",
                                               "Bold leader",
                                               "Visionary leader",
                                               "Facilitator"],  widget=widgets.RadioSelect)
    treatment_q2 = models.StringField(label='What constitutes effective facilitation strategies?',
                                      choices=["Ensure participation",
                                               "Assigning tasks effectively.",
                                               "Connect current task to previous performance.",
                                               "Being assertive and clear in providing direction.",
                                               ],  widget=widgets.RadioSelect)
    treatment_q3 = models.StringField(label="How aircraft carriers' crews conduct discussions? ",
                                      choices=["They focus on their successes and reassure each other.",
                                               "They focus on error and what could go wrong.",
                                               "They are confident in their leader’s decisions and follow suit.",
                                               "They could defer decisions to team members.",
                                               ],  widget=widgets.RadioSelect)
    control_q1 = models.StringField(label='When is a transactional leader effective? When there is a need... ',
                                    choices=[
                                        '...for creative work',
                                        '...to meet strict deadlines',
                                        '...to foster collaboration',
                                        '...to listen and empathize'
                                    ],
                                    widget=widgets.RadioSelect)
    control_q2 = models.StringField(label='What do transformational leaders do? ',
                                    choices=[
                                        'Use carrot and stick',
                                        'Try to control',
                                        'React to present concerns',
                                        'Inspires and motivates'
                                    ],
                                    widget=widgets.RadioSelect)
# PAGES


class FirstWP(WaitPage):
    group_by_arrival_time = True

    @staticmethod
    def is_displayed(player):
        return player.round_number == 1

    @staticmethod
    def after_all_players_arrive(group: Group):
        for p in group.get_players():
            participant = p.participant
            treatment = C.TREATMENTS[group.id_in_subsession % 2]
            p.participant.vars['treatment'] = treatment
            dbq(Player).filter(Player.participant ==
                               participant,).update({"treatment": treatment, })
            ps = dbq(Player).filter(Player.participant == participant)
            for i in ps:
                if treatment == C.CONTROL:
                    i.video = C.VIDEOS_CONTROL[i.round_number-1]
                else:
                    i.video = C.VIDEOS_TREATMENT[i.round_number-1]


def treatment_sorter(player):
    if player.treatment == C.CONTROL:
        return player.round_number == 1
    else:
        return True


class Video(Page):
    is_displayed = treatment_sorter


class Q(Page):
    form_model = 'player'
    

    @staticmethod
    def is_displayed(player: Player):
        return  player.round_number<C.NUM_ROUNDS
                

    @staticmethod
    def get_form_fields(player):
        if player.treatment == C.CONTROL:
            return ['control_q1', 'control_q2']
        else:
            if player.round_number==C.NUM_ROUNDS: 
                return []
            return [f'treatment_q{player.round_number}']


class AfterQWP(WaitPage):
    is_displayed = treatment_sorter
    body_text = 'Please wait while other participants watch the video and answer the questions'


page_sequence = [
    FirstWP,
    Video,
    Q,
    AfterQWP,
]
