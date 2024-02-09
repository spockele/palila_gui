from kivy.lang import Builder

from .screens import PalilaScreen


__all__ = ['QuestionnaireScreen']
Builder.load_file('GUI/questionnaire.kv')


class QuestionnaireScreen(PalilaScreen):
    """

    """
    def __init__(self, questionnaire_dict: dict, **kwargs):
        super().__init__(questionnaire_dict['previous'], questionnaire_dict['next'], **kwargs)
        print(questionnaire_dict)

        self.questionnaire_dict = questionnaire_dict
        if self.questionnaire_dict['default']:
            self._default_setup()

    def _default_setup(self):
        pass
