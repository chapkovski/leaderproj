from otree.api import *
import json

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'q'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass
    big_1 = models.IntegerField()
    big_2 = models.IntegerField()
    big_3 = models.IntegerField()
    big_4 = models.IntegerField()
    big_5 = models.IntegerField()
    big_6 = models.IntegerField()
    big_7 = models.IntegerField()
    big_8 = models.IntegerField()
    big_9 = models.IntegerField()
    big_10 = models.IntegerField()
# # MINDFUL
    mind_1 = models.IntegerField()
    mind_2 = models.IntegerField()
    mind_3 = models.IntegerField()
    mind_4 = models.IntegerField()
    mind_5 = models.IntegerField()
    mind_6 = models.IntegerField()
    mind_7 = models.IntegerField()
    mind_8 = models.IntegerField()
    mind_9 = models.IntegerField()


# PAGES
class big5Page(Page):
    def post(self):
        post_data = self._form_data
        raw_data = post_data.get('surveyholder')
        if raw_data:
            try:
                survey_data = json.loads(raw_data)
                big5 = survey_data.get('big5')
                mindful = survey_data.get('mindful')
                for k,v in big5.items():
                    setattr(self.player, k, int(v))
                    
                for k,v in mindful.items():
                    setattr(self.player, k, int(v))
            except Exception as e:
                print(e)
            
        # raise (Exception)
        return super().post()


class MindfulPage(Page):
    pass


class Results(Page):
    pass


page_sequence = [big5Page,
                #  MindfulPage,
                  Results]
