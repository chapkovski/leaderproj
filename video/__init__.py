from otree.models import Participant
from .methods import wpmethod
from typing import Any
from jinja2 import Environment, FileSystemLoader
from otree.forms.widgets import BaseWidget
from otree.templating import render
from wtforms.widgets import CheckboxInput
from otree.api import *
from otree.api import WaitPage as OWaitPage, Page as OPage
from otree.database import dbq
from starlette.templating import Jinja2Templates
import jinja2
import json
from starlette.datastructures import FormData as StarletteFormData
from markupsafe import escape, Markup
from starlette.responses import RedirectResponse
from otree.constants import timeout_happened

# from leader import live_method
templates = Jinja2Templates(directory='video/templates')
doc = """
Intro (video) to leader proj.
"""
# DEBUG
templateLoader = jinja2.FileSystemLoader(searchpath="video/templates")
templateEnv = jinja2.Environment(loader=templateLoader)


# ENDDEBUG
class Page(OPage):
    @staticmethod
    def before_next_page(player, timeout_happened):
        player.skipped = timeout_happened

def creating_session(subsession):
    for p in subsession.get_players():
        p.endowment = subsession.session.config.get('endowment', 1)
        treatment = subsession.session.config['treatment']

        p.treatment = treatment
        p.participant.vars['treatment'] = treatment
        i = p
        if treatment == C.CONTROL:
            i.video = C.VIDEOS_CONTROL[i.round_number - 1].get('video')
            i.video_duration = C.VIDEOS_CONTROL[i.round_number - 1].get(
                'length')
        else:
            i.video = C.VIDEOS_TREATMENT[i.round_number - 1].get('video')
            i.video_duration = C.VIDEOS_TREATMENT[i.round_number - 1].get(
                'length')


def vars_for_wp(player):
    return wpmethod(player, Player, Participant, dbq, C)


class WaitPage(OWaitPage):
    countdown=False
    template_name = 'video/templates/WaitPage.html'
    # live_method = wpmethod

    vars_for_template = vars_for_wp


class MyValidator:
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        raise ValueError('jopa')


class MyWidget(BaseWidget):
    has_value = True
    TEMPLATE_FILE = "checkbox.html"

    def __init__(self, choices) -> None:
        self.choices = choices
        super().__init__()

    def __call__(self, field, **render_kw):
        self.field = field
        render_kw.setdefault('id', field.id)
        if self.has_value and 'value' not in render_kw:
            render_kw['value'] = field._value()

        self.render_kw = render_kw
        return Markup(''.join(self.get_html_fragments()))

    def get_html_fragments(self):
        self.render_kw['name'] = self.field.name
        template = templateEnv.get_template(self.TEMPLATE_FILE)
        yield (template.render(choices=self.choices, render_kw=self.render_kw))


class C(BaseConstants):
    NAME_IN_URL = 'video'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 4
    CONTROL = 'control'
    MANIPULATION = 'manipulation'
    TREATMENTS = [MANIPULATION, CONTROL]
    VIDEOS_CONTROL = [dict(video='ddt_IGMMOrI', length=200)
                      ] * NUM_ROUNDS
    VIDEOS_TREATMENT = [
        dict(video='xNk-98TIW8s', length=60),
        dict(video='ZZeGJs6A_wQ', length=60),
        dict(video='dPX2sdl-j4g', length=60),
        dict(video='zAsAHTb9thQ', length=60),
    ]
    ERR_MSG = 'Please, re-read instructions'
    WRONG_ANSWER = 'Please re-read the instructions and check the answer'


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


def control_q1_error_message(player, value):
    if value != '...to meet strict deadlines':
        return C.ERR_MSG


def control_q2_error_message(player, value):
    if value != 'Inspires and motivates':
        return C.ERR_MSG


def treatment_q1_error_message(player, value):
    # pvalue = set(json.loads(value))
    check = 'Facilitator'
    if value != check:
        return C.ERR_MSG


def treatment_q2_error_message(player, value):
    pvalue = set(json.loads(value))
    check = set(["Ensure participation",
                 "Connect current task to previous performance.",
                 ])
    if pvalue != check:
        return C.ERR_MSG


def treatment_q3_error_message(player, value):
    pvalue = set(json.loads(value))
    check = set([
        "They focus on error and what could go wrong.",
        "They could defer decisions to team members.",
    ])
    if pvalue != check:
        return C.ERR_MSG


class Player(BasePlayer):
    skipped = models.BooleanField(initial=False)

    @property
    def example_payoff(self):
        return self.endowment * (1 - 0.083)

    endowment = models.CurrencyField()
    treatment = models.StringField()
    video = models.StringField()
    video_duration = models.IntegerField()
    treatment_q1 = models.StringField(label='What role could a team leader play to improve team task results? ',
                                      choices=["Supervisor",
                                               "Bold leader",
                                               "Visionary leader",
                                               "Facilitator"],
                                      widget=widgets.RadioSelect
                                      )
    treatment_q2 = models.StringField(
        label='What constitutes effective facilitation strategies? <br><b>(select TWO choices)</b>',
        widget=MyWidget(choices=["Ensure participation",
                                 "Assigning tasks effectively.",
                                 "Connect current task to previous performance.",
                                 "Being assertive and clear in providing direction.",
                                 ]))
    treatment_q3 = models.StringField(
        label="How aircraft carriers' crews conduct discussions? <br><b>(select TWO choices)</b>",
        widget=MyWidget(choices=["They focus on their successes and reassure each other.",
                                 "They focus on error and what could go wrong.",
                                 "They are confident in their leader’s decisions and follow suit.",
                                 "They could defer decisions to team members.",
                                 ], ))
    control_q1 = models.StringField(label='When is a transactional leader effective? When there is a need... ',
                                    choices=[
                                        '...for creative work',
                                        '...to meet strict deadlines',
                                        '...to foster collaboration',
                                        '...to listen and empathize'
                                    ],
                                    widget=widgets.RadioSelect
                                    )
    control_q2 = models.StringField(label='What do transformational leaders do? ',

                                    choices=[
                                        'Use carrot and stick',
                                        'Try to control',
                                        'React to present concerns',
                                        'Inspires and motivates'
                                    ],
                                    widget=widgets.RadioSelect)

    q1 = models.StringField(label='Who decides the team final forecast in each round?   ',
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


# PAGES


def treatment_sorter(player):
    if player.skipped:
        return False
    if player.treatment == C.CONTROL:
        return player.round_number == 1
    else:
        return True


# CONDITIONS AND HELPERS


def firstround(player: Player):
    return player.round_number == 1


def is_skipped(player: Player):
    return player.skipped




# PAGES
class NonSkippedPage(Page):
    @staticmethod
    def is_displayed(player): return not player.skipped


class Video(OPage):
    @staticmethod
    def get_timeout_seconds(player):
        return player.video_duration

    is_displayed = treatment_sorter


class Q(NonSkippedPage):

    @staticmethod
    def get_timeout_seconds(player):
        return 180

    form_model = 'player'
    checkboxes = [
        'treatment_q2',
        'treatment_q3',
    ]

    def post(self):
        data = dict(self._form_data)
        for i in self.checkboxes:
            if self._form_data.getlist(i):
                data[i] = json.dumps(self._form_data.getlist(i))
        self._form_data = StarletteFormData(data)
        return super().post()

    @staticmethod
    def is_displayed(player: Player):
        if player.skipped:
            return False
        if player.treatment == C.CONTROL:
            return player.round_number == 1
        return player.round_number < C.NUM_ROUNDS

    @staticmethod
    def get_form_fields(player):
        if player.treatment == C.CONTROL:
            return ['control_q1', 'control_q2']
        else:
            if player.round_number == C.NUM_ROUNDS:
                return []
            return [f'treatment_q{player.round_number}']


class GameInstructions(Page):
    @staticmethod
    def get_timeout_seconds(player):
        return 300

    is_displayed = firstround


class GameQ(Page):
    @staticmethod
    def get_timeout_seconds(player):
        return 240

    is_displayed = firstround
    form_model: str = 'player'
    form_fields = ['q1', 'q2', 'q3']

    def post(self):
        post_data = self._form_data

        auto_submitted = post_data.get(timeout_happened)
        if auto_submitted:
            self.player.skipped = True
        return super().post()


class Skipped(Page):
    is_displayed = is_skipped

    # def get(self):
    #     return RedirectResponse(self.session.config.get('prolific_timeout_url'))


class AfterQWP(WaitPage):
    is_displayed = treatment_sorter
    body_text = 'Please wait while other participants watch the video and answer the questions'


# PAGES


def q1_error_message(player, value):
    if value != "The leader":
        return C.WRONG_ANSWER


def q2_error_message(player, value):
    if value != "6":
        return C.WRONG_ANSWER


def q3_error_message(player, value):
    if value != "Inaccurate":
        return C.WRONG_ANSWER


class Consent(Page):
    timeout_seconds = 60

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1


page_sequence = [
    Consent,
    GameInstructions,
    GameQ,
    Video,
    Q,
    Skipped
]
