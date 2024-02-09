from kivy.uix.floatlayout import FloatLayout
from kivy.lang import Builder

from .screens import PalilaScreen, Filler


__all__ = ['QuestionnaireScreen']
Builder.load_file('GUI/questionnaire.kv')


class QuestionnaireQuestion(FloatLayout):
    def __init__(self, question_dict: dict, **kwargs):
        super().__init__(**kwargs)
        self.question_dict = question_dict
        self.ids.question_text.text = question_dict["text"]
        print(self.ids.question_text.text)


class FreeNumQuestion(QuestionnaireQuestion):
    def __init__(self, question_dict: dict, **kwargs):
        super().__init__(question_dict, **kwargs)


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

        for ii in range(8 - len(self.questions)):
            self.ids.questions.add_widget(Filler())

    def _default_setup(self):
        pass
