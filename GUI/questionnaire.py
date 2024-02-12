from kivy.uix.floatlayout import FloatLayout
from kivy.lang import Builder

from .screens import PalilaScreen, Filler


__all__ = ['QuestionnaireScreen']
Builder.load_file('GUI/questionnaire.kv')


class QuestionnaireQuestion(FloatLayout):
    def __init__(self, question_dict: dict, **kwargs):
        super().__init__(**kwargs)
        self.question_dict = question_dict
        self.ids.question_text.text = question_dict['text']
        self.qid = question_dict['id']
        self.answer = None

        if len(question_dict['text'].split('\n')) > 1:
            self.ids.question_text.font_size = 36


class FreeNumQuestion(QuestionnaireQuestion):
    def __init__(self, question_dict: dict, **kwargs):
        super().__init__(question_dict, **kwargs)

    def check_input(self):
        if self.ids.question_input.text:
            try:
                self.answer = int(self.ids.question_input.text)
                self.ids.question_input_overlay.text = ''
                self.ids.question_input.background_color = (1., 1., 1., 1.)
                self.ids.question_input_overlay.color = (.7, .7, .7, 1.)

            except ValueError:
                self.ids.question_input.text = str(self.answer) if self.answer is not None else ''
                self.ids.question_input_overlay.color = (1., .2, .2, 1.)
                self.ids.question_input.background_color = (1., .7, .7, 1.)

        else:
            self.answer = None
            self.ids.question_input_overlay.text = 'Enter a number here.'

        self.parent.parent.unlock_check()


class QuestionnaireScreen(PalilaScreen):
    """

    """
    def __init__(self, questionnaire_dict: dict, **kwargs):
        super().__init__(questionnaire_dict['previous'], questionnaire_dict['next'], superinit=True, **kwargs)

        self.questionnaire_dict = questionnaire_dict
        self.questions = []

        for question in self.questionnaire_dict['questions']:
            question_type = globals()[f'{questionnaire_dict[question]["type"]}Question']
            question_instance: QuestionnaireQuestion = question_type(questionnaire_dict[question])

            self.ids.questions.add_widget(question_instance)
            self.questions.append(question_instance)

        for ii in range(7 - len(self.questions)):
            self.ids.questions.add_widget(Filler())

    def get_state(self):
        # Start a variable to store the total state
        total_state = True
        for question_instance in self.questions:
            state = question_instance.answer is not None
            # Update the total state via the boolean "and" operator
            total_state = total_state and state

        return total_state

    def unlock_check(self):
        if self.get_state():
            # If all questions are answered: unlock the continue button
            self.reset_continue_label()
            self.ids.continue_bttn.unlock()
        else:
            # Make sure the continue button is locked if not
            self.ids.continue_bttn.lock()
