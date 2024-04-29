"""
Copyright (c) 2024 Josephine Siebert Pockelé

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.boxlayout import BoxLayout

from .screens import PalilaScreen, BackButton, Filler
from . import questionnaire_questions


__all__ = ['questionnaire_setup']


class QuestionnaireScreen(PalilaScreen):
    """
    Class that defines the overall audio question screens. Subclass of GUI.screens.PalilaScreen.

    Parameters
    ----------
    questionnaire_dict : dict
        Dictionary that defines the questionnaire and its questions.
    **kwargs
        Keyword arguments. These are passed on to the GUI.screens.PalilaScreen constructor.

    Attributes
        ----------
        questionnaire_dict : dict
            Dictionary that defines the questionnaire and its questions.
    """

    def __init__(self, questionnaire_dict: dict, questions: list, back_function: callable = None, *args,
                 state_override: bool = False, **kwargs):

        super().__init__(*args, lock=True, **kwargs)

        self.questionnaire_dict = questionnaire_dict
        self.questions = questions

        self.state_override = state_override
        self.question_manager: QQuestionManager = self.ids.question_manager

        for question in self.questions:
            self.question_manager.add_question(self.questionnaire_dict[question])

        for _ in range(7 - len(self.questions)):
            self.question_manager.add_widget(Filler())

        if back_function is not None:
            # In case it's not the first screen, set up the back button
            # First readjust the continue button
            self.ids.continue_bttn.size_hint_x -= .065
            self.ids.continue_bttn.pos_hint = {'x': .415, 'y': .015}
            # Create the back button and pass all information to it
            back_button = BackButton()
            back_button.pos_hint = {'x': .35, 'y': .015}
            back_button.size_hint = (.0625, .1)
            back_button.on_release = back_function
            back_button.set_arrow()
            # Add the button to the screen
            self.add_widget(back_button)

        self.unlock_check()
        [question.border() for question in self.question_manager.questions.values()]
        [question.set_dependant() for question in self.question_manager.questions.values()]

    def unlock_check(self, question_state: bool = None):
        """
        Check for unlocking the continue button.
        """
        if question_state is None:
            question_state = self.question_manager.get_state()

        # If all questions are answered and the audio is listened to: unlock the continue button
        if question_state or self.state_override:
            self.reset_continue_label()
            self.ids.continue_bttn.unlock()
        # Make sure the continue button is locked if not
        else:
            self.ids.continue_bttn.lock()

    def on_pre_leave(self, *_):
        """
        Store all answers before leaving the screen.
        """
        for qid, answer in self.question_manager.answers.items():
            self.manager.store_answer(qid, answer)

    def on_pre_enter(self, *args):
        """
        Unlock the continue button if appropriate.
        """
        self.unlock_check()
        super().on_pre_enter(*args)


class QQuestionManager(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.questions = {}
        self.answers = {}

    def add_question(self, question_dict: dict) -> None:
        """
        Add a questionnaire question to this question manager.
        Parameters
        ----------
        question_dict : dict
            Dictionary with all the information to construct the question.
        """
        question_type = getattr(questionnaire_questions,
                                f'{question_dict["type"]}QQuestion')
        question_instance: questionnaire_questions.QuestionnaireQuestion = question_type(question_dict)
        # Add the instance to the screen and the list
        self.add_widget(question_instance)

        self.questions[question_dict['id']] = question_instance
        self.answers[question_dict['id']] = ''

    def get_state(self):
        """
        Get the completion state of this questionnaire.
        """
        # Start a variable to store the total state
        total_state = True

        # Loop over all questions
        for qid, answer in self.answers.items():
            total_state = total_state and bool(answer)

        # Return the final state
        return total_state

    def change_answer(self, question_id: str, answer: str) -> None:
        self.answers[question_id] = answer
        self.parent.unlock_check(question_state=self.get_state() and not self.disabled)


def questionnaire_setup(questionnaire_dict: dict, manager: ScreenManager, state_override: bool,
                        part: str = 'main', ) -> None:
    """

    Parameters
    ----------
    questionnaire_dict : dict

    manager : PalilaScreenManager

    state_override : bool

    part : str

    """
    if not questionnaire_dict['screen dict']:
        manager.get_screen(questionnaire_dict['previous']).next_screen = questionnaire_dict['next']

    else:
        screen_nums = sorted(questionnaire_dict['screen dict'].keys())
        for ii, screen_num in enumerate(screen_nums):
            if ii:
                previous_screen = f'{part}-questionnaire-{ii}'
            else:
                previous_screen = questionnaire_dict['previous']

            if screen_num < max(screen_nums):
                next_screen = f'{part}-questionnaire-{ii + 2}'
            else:
                next_screen = questionnaire_dict['next']

            new_screen = QuestionnaireScreen(questionnaire_dict, questionnaire_dict['screen dict'][screen_num],
                                             manager.navigate_previous, previous_screen, next_screen,
                                             state_override=state_override,
                                             name=f'{part}-questionnaire-{ii + 1}')

            manager.add_widget(new_screen)

