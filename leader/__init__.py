from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'leader'
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS = 1
    LEADER_ROLE='Leader'
    P1_ROLE='Participant 1'
    P2_ROLE='Participant 2'

class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass


# PAGES
class MyPage(Page):
    timeout_seconds = 1000


class ResultsWaitPage(WaitPage):
    pass


class Results(Page):
    pass


page_sequence = [MyPage, ResultsWaitPage, Results]
