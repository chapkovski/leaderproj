from otree.chat import chat_template_tag
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
    for p in subsession.get_players():
        p.participant.vars['treatment'] =  subsession.session.config.get('treatment', C.CONTROL)
        p.endowment = subsession.session.config.get('endowment', 1)
    subsession.true_value = C.TO_PREDICT[subsession.round_number-1]


class C(BaseConstants):
    NAME_IN_URL = 'leader'
    PLAYERS_PER_GROUP = 3
    CONTROL = 'control'
    MANIPULATION = 'manipulation'
    LEADER_MSG_CONTROL = ' Remember, good leaders are decisive, show the way, and take risks.'
    LEADER_MSG_MANIPULATION = 'Remember,  good leaders facilitate discussions, learn from previous mistakes, and defer decisions to expert team members.'
    LEADER = 'Leader'
    P1 = 'Participant 1'
    P2 = 'Participant 2'
    ROLES = [LEADER, P1, P2]
    MAX_OLD_VALUES = 48
    TO_PREDICT = graph_data[MAX_OLD_VALUES:]
    GRAPHS_DATA = graph_data[:MAX_OLD_VALUES]
    LAST_ITEM = GRAPHS_DATA[-1]
    NUM_ROUNDS = 6
    WRONG_ANSWER = 'Please re-read the instructions and check the answer'


class Subsession(BaseSubsession):
    true_value = models.IntegerField()


class Group(BaseGroup):
    def mape(self):
        allrels = [i.rel_deviation for i in self.in_all_rounds()]
        return sum(allrels)/len(allrels)

    def mape_formatted(self):
        return f'{self.mape():.0%}'

    @property
    def deviation(self):
        return self.final_prediction-self.subsession.true_value

    @property
    def rel_deviation(self):
        return self.abs_deviation/self.subsession.true_value

    @property
    def rel_deviation_formatted(self):
        return f'{self.rel_deviation:.0%}'

    @property
    def abs_deviation(self):
        return abs(self.deviation)

    final_prediction = models.IntegerField(
        label='Look at the predictions made by you at the discussion stage and make the final prediction for this round:')

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
    endowment = models.CurrencyField()
    inner_role = models.StringField()

    @property
    def role(self):
        return self.inner_role

    @property
    def example_payoff(self):
        return self.endowment*(1-0.083)
    prediction = models.IntegerField()


class IntroRound(Page):
    timeout_seconds = 60


class BeforeDecisionWP(MWP):
    template_name = 'video/templates/WaitPage.html'
    vars_for_template = vars_for_wp


def live_method(player, data):
    print(
        f'Prediction submitted by {player.participant.code}; round {player.round_number}; group {player.group.id_in_subsession} ', data)
    try:
        player.prediction = int(data.get('prediction'))
        predictions = [p.field_maybe_none(
            'prediction') is not None for p in player.group.get_players()]
        group_done = all(predictions)
        return {0: dict(
            msg=f'{player.role} submitted prediction {player.prediction}',
            group_done=group_done
        )}
    except Exception as E:
        print(E)
        print(
            f'Something went wrong with prediction registration for participant {player.participant.code}')


class DecisionPage(Page):
    @staticmethod
    def get_timeout_seconds(player: Player):
        MINUTE = 60
        if player.round_number == 1:
            return player.session.config.get('round_one_minutes')*MINUTE
        return player.session.config.get('other_round_minutes')*MINUTE

    live_method = live_method

    @staticmethod
    def vars_for_template(player: Player):
        context = dict(player=player,
                       group=player.group,
                       Constants=C,
                       participant=player.participant,
                       session=player.session)
        chat_context = chat_template_tag(context, nickname=player.role)
        return dict(chat_vars_for_js=chat_context)

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
    timeout_seconds = 120
    form_fields = ['final_prediction']
    form_model = 'group'

    @staticmethod
    def is_displayed(player: Player):
        return player.role == C.LEADER


class ResultsWaitPage(MWP):
    body_text = '<h2>Please wait while the <span class="text-danger">leader</span> of your group submits the final prediction for this round...</h2>'
    template_name = 'video/templates/WaitPage.html'
    vars_for_template = vars_for_wp


class Results(Page):
    timeout_seconds = 120


class BeforeFinalResultsWP(WaitPage):
    template_name = 'video/templates/WaitPage.html'
    vars_for_template = vars_for_wp

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS
    after_all_players_arrive = 'set_payoffs'


class FinalResults(Page):
    pass

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS


def set_payoffs(group):
    mape = group.mape()
    for p in group.get_players():
        p.payoff = p.endowment*(1-mape)


class FirstWP(WaitPage):
    body_text = """<h2>Please be patient: it may take up to <span class="text-danger">5 minutes</span>
    till your partners reach this page and you will be able to proceed further.</h2> 
    <h3>If you have any questions, please communicate with us via Prolific or email: <a href="mailto:chapkovski@uni-bonn.de">chapkovski@uni-bonn.de</a></h3>"""
    group_by_arrival_time = True
    template_name = 'video/templates/WaitPage.html'
    vars_for_template = vars_for_wp

    @staticmethod
    def is_displayed(player):
        return player.round_number == 1

    @ staticmethod
    def after_all_players_arrive(group: Group):
        for p in group.get_players():
            inner_role = C.ROLES[p.id_in_group-1]
            for i in range(1, C.NUM_ROUNDS+1):
                p.in_round(i).inner_role = inner_role
            p.participant.vars['role'] = inner_role


page_sequence = [
    FirstWP,
    IntroRound,
    BeforeDecisionWP,
    DecisionPage,
    BeforeLeaderDecisionWP,
    LeaderDecisionPage,
    ResultsWaitPage,
    Results,
    BeforeFinalResultsWP,
    FinalResults
]
