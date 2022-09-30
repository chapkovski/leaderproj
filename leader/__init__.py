from otree.api import *

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'leader'
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS = 1
    LEADER_ROLE = 'Leader'
    P1_ROLE = 'Participant 1'
    P2_ROLE = 'Participant 2'


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    prediction = models.IntegerField()


class Player(BasePlayer):
    pass


# PAGES
class MyPage(Page):
    form_model = 'group'
    timeout_seconds = 1000

    @staticmethod
    def get_form_fields(player: Player):
        if player.role == C.LEADER_ROLE:
            return ['prediction']


class ResultsWaitPage(WaitPage):
    pass


class Results(Page):
    pass


page_sequence = [MyPage, ResultsWaitPage, Results]
