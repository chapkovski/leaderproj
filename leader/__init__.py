from otree.api import *
from video import WaitPage as MWP
import csv
from otree.models import Participant
from typing import List
from otree.database import dbq
from video.methods import wpmethod
with open('leader/data/graph.csv') as csvfile:
    graph_data = [int(i[0]) for i in csv.reader(csvfile)]

doc = """
Leader proj. by Philipp Chapkovski (UBonn)
"""


def vars_for_wp(player):
    return wpmethod(player, Player, Participant, dbq, C)


def creating_session(subsession):
    subsession.true_value = C.TO_PREDICT[subsession.round_number-1]


class C(BaseConstants):
    NAME_IN_URL = 'leader'
    PLAYERS_PER_GROUP = 3

    LEADER_ROLE = 'Leader'
    P1_ROLE = 'Participant 1'
    P2_ROLE = 'Participant 2'
    MAX_OLD_VALUES = 48
    TO_PREDICT = graph_data[MAX_OLD_VALUES:]
    GRAPHS_DATA = graph_data[:MAX_OLD_VALUES]
    LAST_ITEM = GRAPHS_DATA[-1]
    NUM_ROUNDS = 6
    WRONG_ANSWER = 'Please re-read the instructions and check the answer'


class Subsession(BaseSubsession):
    true_value = models.IntegerField()


class Group(BaseGroup):

    final_prediction = models.IntegerField(label='Look at the predictions made by you at the discussion stage and make the final prediction for this round:')

    @property
    def prognosis_data(self):

        p = dbq(Group).filter(
            Group.session == self.session,
            Group.round_number < self.round_number
        ).order_by('round_number').with_entities(Group.final_prediction)
        ready_prognosis = [i for [i] in list(p)]

        empty = [None for i in range(len(C.GRAPHS_DATA))]
        return empty + ready_prognosis

    @property
    def true_values(self):
        empty = [None for i in range(len(C.GRAPHS_DATA)-1)]
        return empty + [C.LAST_ITEM] + C.TO_PREDICT[:self.round_number-1]


class Player(BasePlayer):
    prediction = models.IntegerField()
    q1 = models.StringField(label='Who should submit each group’s forecast?',
                            choices=["Any participant",
                                     "All team members",
                                     "The leader",
                                     ],
                            widget=widgets.RadioSelect)
    q2 = models.StringField(label='How many forecasts should the group produce?',
                            choices=["3",
                                     "4",
                                     "6",
                                     ],
                            widget=widgets.RadioSelect)
    q3 = models.StringField(label='A MAPE score of > 50% is considered:',
                            choices=["Accurate",
                                     "Inaccurate",
                                     "Acceptable", ],
                            widget=widgets.RadioSelect)


def q1_error_message(player, value):
    if value != "The leader":
        return C.WRONG_ANSWER


def q2_error_message(player, value):
    if value != "6":
        return C.WRONG_ANSWER


def q3_error_message(player, value):
    if value != "Inaccurate":
        return C.WRONG_ANSWER


# PAGES
def firstround(player: Player):
    return player.round_number == 1


class Instructions(Page):
    is_displayed = firstround


class Q(Page):
    is_displayed = firstround
    form_model: str = 'player'
    form_fields: List[str] = ['q1', 'q2', 'q3']


class IntroRound(Page):
    pass


class BeforeDecisionWP(MWP):
    template_name = 'video/templates/WaitPage.html'
    vars_for_template = vars_for_wp


def live_method(player, data):
    print('DATA RECIEVED', data)
    return {0: 'Done'}


class DecisionPage(Page):
    @staticmethod
    def get_timeout_seconds(player: Player):
        MINUTE = 60
        if player.round_number == 1:
            return player.session.config.get('round_one_minutes')*MINUTE
        return player.session.config.get('other_round_minutes')*MINUTE

    live_method = live_method


    def post(self):
        if self._form_data.get('prediction'):
            try:
                self.player.prediction = int(self._form_data.get('prediction'))
            except Exception as E:
                print(E)
                return super().post()
        return super().post()


class BeforeLeaderDecisionWP(MWP):
    body_text = 'Please wait while leader makes the final prediction!'
    template_name = 'video/templates/WaitPage.html'
    vars_for_template = vars_for_wp



class LeaderDecisionPage(Page):
    form_fields = ['final_prediction']
    form_model = 'group'

    @staticmethod
    def is_displayed(player: Player):
        return player.role == C.LEADER_ROLE


class ResultsWaitPage(MWP):
    pass


class Results(Page):
    pass


page_sequence = [
    Instructions,
    Q,
    IntroRound,
    BeforeDecisionWP,
    DecisionPage,
    BeforeLeaderDecisionWP,
    LeaderDecisionPage,
    ResultsWaitPage,
    Results
]
