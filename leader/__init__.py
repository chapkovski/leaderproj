from otree.api import *
import csv

from otree.database import dbq
with open('leader/data/graph.csv') as csvfile:
    graph_data =  [int(i[0]) for i in csv.reader(csvfile)]

doc = """
Leader proj. by Philipp Chapkovski (UBonn)
"""


class C(BaseConstants):
    NAME_IN_URL = 'leader'
    PLAYERS_PER_GROUP = 3
    
    LEADER_ROLE = 'Leader'
    P1_ROLE = 'Participant 1' 
    P2_ROLE = 'Participant 2'
    MAX_OLD_VALUES=3
    TO_PREDICT=graph_data[MAX_OLD_VALUES:]
    GRAPHS_DATA= graph_data[:MAX_OLD_VALUES]
    LAST_ITEM=GRAPHS_DATA[-1]
    NUM_ROUNDS = len(graph_data)-MAX_OLD_VALUES

class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    prediction = models.IntegerField()
    @property
    def prognosis_data(self):

        p = dbq(Group).filter(
            Group.session == self.session, 
            Group.round_number<self.round_number
        ).order_by('round_number').with_entities(Group.prediction)
        ready_prognosis = [i for [i] in list(p)]
        
        empty = [None for i in range(len(C.GRAPHS_DATA))]
        return  empty+ ready_prognosis
    @property
    def true_values(self):
        empty = [None for i in range(len(C.GRAPHS_DATA)-1)]
        return empty + [C.LAST_ITEM] +  C.TO_PREDICT[:self.round_number-1]

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


page_sequence = [
    MyPage,
    #  ResultsWaitPage, 
    #  Results
     ]
