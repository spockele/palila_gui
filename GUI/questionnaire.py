from kivy.uix.floatlayout import FloatLayout
from kivy.lang import Builder

from .screens import PalilaScreen


__all__ = ['QuestionnaireScreen']
Builder.load_file('GUI/questionnaire.kv')


class QuestionnaireQuestion(FloatLayout):
    def __init__(self, question_dict: dict, **kwargs):
        super().__init__(**kwargs)
        self.question_dict = question_dict
        self.ids.question_text.text = question_dict['text']

        if len(question_dict['text'].split('\n')) > 1:
            self.ids.question_text.font_size = 36


class FreeNumQuestion(QuestionnaireQuestion):
    def __init__(self, question_dict: dict, **kwargs):
        super().__init__(question_dict, **kwargs)
        self.answer = None

    def check_answer(self, answer: str):
        if answer:
            try:
                self.answer = int(answer)
                self.ids.question_input_overlay.text = ''
                self.ids.question_input.background_color = (1., 1., 1., 1.)
                self.ids.question_input_overlay.color = (.7, .7, .7, 1.)
                return True
            except ValueError:
                self.ids.question_input.text = str(self.answer) if self.answer is not None else ''
                self.ids.question_input_overlay.color = (1., .2, .2, 1.)
                self.ids.question_input.background_color = (1., .7, .7, 1.)
                return False

        else:
            self.answer = None
            self.ids.question_input_overlay.text = 'Enter a number here.'


class QuestionnaireScreen(PalilaScreen):
    """

    """
    def __init__(self, questionnaire_dict: dict, **kwargs):
        super().__init__(questionnaire_dict['previous'], questionnaire_dict['next'], **kwargs)

        self.questionnaire_dict = questionnaire_dict
        if self.questionnaire_dict['default']:
            self._default_setup()

        self.questions = []
        for question in self.questionnaire_dict['questions']:
            question_type = globals()[f'{questionnaire_dict[question]["type"]}Question']
            question_instance = question_type(questionnaire_dict[question])

            self.ids.questions.add_widget(question_instance)
            self.questions.append(question_instance)

        for ii in range(7 - len(self.questions)):
            self.ids.questions.add_widget(QuestionnaireQuestion({'text': ''}))

    def _default_setup(self):
        pass
