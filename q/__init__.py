from otree.api import *
import json
from starlette.responses import RedirectResponse
from pprint import pprint

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
    # Big Five Personality Traits
    big_reserved = models.IntegerField()
    big_trusting = models.IntegerField()
    big_lazy = models.IntegerField()
    big_relaxed = models.IntegerField()
    big_artisticInterests = models.IntegerField()
    big_outgoing = models.IntegerField()
    big_faultFinding = models.IntegerField()
    big_thorough = models.IntegerField()
    big_nervous = models.IntegerField()
    big_imagination = models.IntegerField()

    # Mindful Organizing Scale
    mind_discussWhatToLookFor = models.IntegerField()
    mind_identifyActivities = models.IntegerField()
    mind_discussAlternatives = models.IntegerField()
    mind_goodMapOfTalents = models.IntegerField()
    mind_discussUniqueSkills = models.IntegerField()
    mind_talkAboutMistakes = models.IntegerField()
    mind_discussErrorPrevention = models.IntegerField()
    mind_resolveProblemWithSkills = models.IntegerField()
    mind_poolExpertiseInCrisis = models.IntegerField()


# PAGES
class big5Page(Page):
    def post(self):
        post_data = self._form_data
        raw_data = post_data.get('surveyResults')
        pprint(raw_data)
        if raw_data:
            try:
                survey_data = json.loads(raw_data)

                # Extract Big Five and Mindful Organizing responses
                big5 = survey_data.get('bigFive', {})
                mindful = survey_data.get('mindfulOrganizing', {})

                # Map Big Five responses
                big5_mapping = {
                    "reserved": "big_reserved",
                    "trusting": "big_trusting",
                    "lazy": "big_lazy",
                    "relaxed": "big_relaxed",
                    "artisticInterests": "big_artisticInterests",
                    "outgoing": "big_outgoing",
                    "faultFinding": "big_faultFinding",
                    "thorough": "big_thorough",
                    "nervous": "big_nervous",
                    "imagination": "big_imagination"
                }
                for key, field_name in big5_mapping.items():
                    if key in big5:
                        setattr(self.player, field_name, int(big5[key]))

                # Map Mindful Organizing responses
                mindful_mapping = {
                    "discussWhatToLookFor": "mind_discussWhatToLookFor",
                    "identifyActivities": "mind_identifyActivities",
                    "discussAlternatives": "mind_discussAlternatives",
                    "goodMapOfTalents": "mind_goodMapOfTalents",
                    "discussUniqueSkills": "mind_discussUniqueSkills",
                    "talkAboutMistakes": "mind_talkAboutMistakes",
                    "discussErrorPrevention": "mind_discussErrorPrevention",
                    "resolveProblemWithSkills": "mind_resolveProblemWithSkills",
                    "poolExpertiseInCrisis": "mind_poolExpertiseInCrisis"
                }
                for key, field_name in mindful_mapping.items():
                    if key in mindful:
                        setattr(self.player, field_name, int(mindful[key]))

            except json.JSONDecodeError:
                print("Error: Invalid JSON data received")
            except Exception as e:
                print(f"Unexpected error: {e}")

        return super().post()


class MindfulPage(Page):
    pass


class FinalForProlific(Page):

    def get(self):
        return RedirectResponse(self.session.config.get('prolific_redirect_url'))


page_sequence = [
    # big5Page,
      # MindfulPage,
    FinalForProlific
]
