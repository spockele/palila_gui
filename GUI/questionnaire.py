from kivy.uix.screenmanager import ScreenManager
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.lang import Builder

from .screens import PalilaScreen, Filler, BackButton


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

    def check_input(self):
        self.parent.parent.unlock_check()


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

        super().check_input()


class SpinnerQuestion(QuestionnaireQuestion):
    def __init__(self, question_dict: dict, **kwargs):
        super().__init__(question_dict, **kwargs)
        self.ids.question_input.values = question_dict['choices']

    def check_input(self):
        if self.ids.question_input.text:
            self.answer = self.ids.question_input.text
        else:
            self.answer = None

        super().check_input()


class QuestionnaireChoiceButton(Button):
    """
    Button with ability to store a state and interact with QuestionnaireQuestion
    """
    def __init__(self, text: str = '', **kwargs):
        super().__init__(text=text, **kwargs)

    def select(self) -> None:
        self.background_color = [.5, 1., .5, 1.]

    def deselect(self) -> None:
        self.background_color = [1., 1., 1., 1.]

    def on_release(self):
        self.select()
        self.parent.parent.select_choice(self)


class QuestionnaireMCQuestion(QuestionnaireQuestion):
    def __init__(self, question_dict: dict, **kwargs):
        super().__init__(question_dict, **kwargs)
        self.choice = None

        # Add every choice as a button and track their word lengths
        choices = []
        lengths = []
        for choice in question_dict['choices']:
            choice_button = QuestionnaireChoiceButton(choice)
            choices.append(choice_button)
            self.ids.question_input.add_widget(choice_button)
            lengths.append(len(choice))
        # Resize proportional to the root of the word lengths
        total = sum(lengths)
        for ii, length in enumerate(lengths):
            choices[ii].size_hint_x = length ** .5 / total

    def select_choice(self, choice: QuestionnaireChoiceButton):
        """
        Sets the current answer, based on the input ChoiceButton
        """
        if self.choice is not None:
            # Deselect the current answer if there is one
            self.choice.deselect()

        if self.choice == choice:
            # Remove the current answer if the same button is pressed
            self.choice = None
            self.answer = None
        else:
            # Set the current answer to the entered button otherwhise
            self.choice = choice
            self.answer = choice.text

        super().check_input()


class QuestionnaireScreen(PalilaScreen):
    """

    """
    def __init__(self, questionnaire_dict: dict, manager: ScreenManager, extra_screen_start: int = 0, **kwargs):
        super().__init__(questionnaire_dict['previous'], questionnaire_dict['next'], superinit=False, **kwargs)

        self.questionnaire_dict = questionnaire_dict

        # Keep a count of the number of screens in this questionnaire
        if 'screen_count' not in self.questionnaire_dict.keys():
            self.questionnaire_dict['screen_count'] = 1
        else:
            self.ids.continue_bttn.size_hint_x -= .065
            self.ids.continue_bttn.pos_hint = {'x': .415, 'y': .015}

            back_button = BackButton()
            back_button.pos_hint = {'x': .35, 'y': .015}
            back_button.size_hint = (.0625, .1)
            back_button.on_release = manager.navigate_previous
            self.add_widget(back_button)

            self.questionnaire_dict['screen_count'] += 1

        self.questions = []

        for qi in range(7):
            if qi >= len(self.questionnaire_dict['questions'][extra_screen_start:]):
                self.ids.questions.add_widget(Filler())

            else:
                question = self.questionnaire_dict['questions'][extra_screen_start:][qi]
                question_type = globals()[f'{questionnaire_dict[question]["type"]}Question']
                question_instance: QuestionnaireQuestion = question_type(questionnaire_dict[question])

                self.ids.questions.add_widget(question_instance)
                self.questions.append(question_instance)

        if len(self.questionnaire_dict['questions'][extra_screen_start:]) > 7:
            extra_screen = QuestionnaireScreen(self.questionnaire_dict, manager,
                                               extra_screen_start=extra_screen_start + 7,
                                               name=self.name + f'-{self.questionnaire_dict["screen_count"]}')
            manager.add_widget(extra_screen)

            extra_screen.previous_screen = self.name
            extra_screen.next_screen = self.next_screen
            self.next_screen = extra_screen.name

        # self.unlock_check()

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

    def on_pre_leave(self, *args):
        for question_instance in self.questions:
            if question_instance.answer is not None:
                self.manager.store_answer(question_instance.qid, question_instance.answer)
                # print(question_instance.qid, question_instance.answer)
