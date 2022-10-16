
from typing import Any
from jinja2 import Environment, FileSystemLoader
from otree.forms.widgets import BaseWidget
from otree.templating import render
from wtforms.widgets import CheckboxInput
from otree.api import *
from otree.api import WaitPage as OWaitPage
from otree.database import dbq
from starlette.templating import Jinja2Templates
import jinja2
import json
from starlette.datastructures import FormData as StarletteFormData
from markupsafe import escape, Markup

from leader import live_method
templates = Jinja2Templates(directory='video/templates')
doc = """
Intro (video) to leader proj.
"""
# DEBUG
templateLoader = jinja2.FileSystemLoader(searchpath="video/templates")
templateEnv = jinja2.Environment(loader=templateLoader)
# ENDDEBUG

from otree.models import Participant
def wpmethod(player, data):
    fk_field=Player.group_id
    my_page_index = player.participant._index_in_pages
    
    ps =dbq(Player).join(Participant).filter(fk_field == player.group.id,
    ).with_entities(Participant)
    num_left=ps.filter(Participant._index_in_pages<my_page_index).count()
    num_here=ps.filter(Participant._index_in_pages==my_page_index).count()
    
    return {0:dict(num_left=num_left, num_here=num_here)}

class WaitPage(OWaitPage):
    template_name = 'video/templates/WaitPage.html'
    live_method = wpmethod

    def get(self):

        return super().get()


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
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS = 4
    CONTROL = 'control'
    MANIPULATION = 'manipulation'
    TREATMENTS = [MANIPULATION, CONTROL]
    VIDEOS_CONTROL = ['ddt_IGMMOrI'] * NUM_ROUNDS
    VIDEOS_TREATMENT = [
        'xNk-98TIW8s',
        'ZZeGJs6A_wQ',
        'dPX2sdl-j4g',
        'zAsAHTb9thQ'
    ]
    ERR_MSG = 'Please, re-read instructions'


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
    pvalue = set(json.loads(value))
    check = set(['Facilitator'])
    if pvalue != check:
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
    treatment = models.StringField()
    video = models.StringField()
    treatment_q1 = models.StringField(label='What role could a team leader play to improve team task results? ',
                                      widget=MyWidget(choices=["Supervisor",
                                                               "Bold leader",
                                                               "Visionary leader",
                                                               "Facilitator"])
                                      )
    treatment_q2 = models.StringField(label='What constitutes effective facilitation strategies?',
                                      widget=MyWidget(choices=["Ensure participation",
                                                               "Assigning tasks effectively.",
                                                               "Connect current task to previous performance.",
                                                               "Being assertive and clear in providing direction.",
                                                               ]))
    treatment_q3 = models.StringField(label="How aircraft carriers' crews conduct discussions? ",
                                      widget=MyWidget(choices=["They focus on their successes and reassure each other.",
                                                               "They focus on error and what could go wrong.",
                                                               "They are confident in their leader’s decisions and follow suit.",
                                                               "They could defer decisions to team members.",
                                                               ],))
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

# PAGES


class FirstWP(WaitPage):
    group_by_arrival_time = True

    def get_context_data(self):
        ps = self._get_participants_for_this_waitpage(
            self._group_or_subsession
        )
        print(list(ps))
        return super().get_context_data()

    @ staticmethod
    def is_displayed(player):
        return player.round_number == 1

    @ staticmethod
    def after_all_players_arrive(group: Group):
        for p in group.get_players():
            participant = p.participant
            if group.session.config.get('treatment'):
                treatment = group.session.config.get('treatment')
            else:
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
    return True
    if player.treatment == C.CONTROL:
        return player.round_number == 1
    else:
        return True


class Video(Page):
    is_displayed = treatment_sorter


class Q(Page):
    form_model = 'player'
    checkboxes = [

        'treatment_q1',
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

    @ staticmethod
    def is_displayed(player: Player):
        return player.round_number < C.NUM_ROUNDS

    @ staticmethod
    def get_form_fields(player):
        if player.treatment == C.CONTROL:
            return ['control_q1', 'control_q2']
        else:
            if player.round_number == C.NUM_ROUNDS:
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
 