"""
Module containing the overall classes and functions for the Questionnaire screens.
"""

# Copyright (c) 2025 Josephine Siebert Pockelé
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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

    def __init__(self, questionnaire_dict: dict, questions: list, *args,
                 back_function: callable = None, state_override: bool = False, **kwargs):
        super().__init__(*args, lock=True, **kwargs)

        # Store the overall questionnaire dict.
        self.questionnaire_dict = questionnaire_dict
        # Store the list of questions specific to this screen.
        self.questions = questions
        # Store the state override variable.
        self.state_override = state_override

        # In case it's not the first screen (indicated by the presence of a back_function), set up the back button
        if back_function is not None:
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

        # Create a link to the question manager from the Kivy code.
        self.question_manager: QQuestionManager = self.ids.question_manager

        # Add the questions from the list to this screen.
        for question in self.questions:
            self.question_manager.add_question(self.questionnaire_dict[question])

        # Fill up the empty space.
        for _ in range(7 - len(self.questions)):
            self.question_manager.add_widget(Filler())

        # Do the unlock check
        self.unlock_check()
        # Add the borders to all questions
        [question.border() for question in self.question_manager.questions.values()]
        # Set the dependency locks for all questions, now that they are part of this screen.
        [question.set_unlock() for question in self.question_manager.questions.values()]

    def unlock_check(self, question_state: bool = None):
        """
        Check for unlocking the continue button.
        """
        if question_state is None:
            question_state = self.question_manager.get_state()

        # If all questions are answered and the audio is listened to: unlock the continue button.
        if question_state or self.state_override:
            self.reset_continue_label()
            self.ids.continue_bttn.unlock()

        else:
            # Otherwise, make sure the continue button is locked.
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

    def set_next_screen(self, next_screen: str) -> None:
        """
        Set a new next screen for this questionnaire.

        Parameters
        ----------
        next_screen: str
            The name of the new next screen
        """
        if 'questionnaire' in self.next_screen:
            self.manager.get_screen(self.next_screen).set_next_screen(next_screen)
        else:
            self.next_screen = next_screen


class QQuestionManager(BoxLayout):
    """
    Subclass of kivy.uix.boxlayout.BoxLayout that defines and manages the question part of an AudioQuestionScreen.

    Parameters
    ----------
    **kwargs
        Keyword arguments. These are passed on to the kivy.uix.boxlayout.BoxLayout constructor.

    Attributes
    ----------
    questions : dict[str, QQuestion]
        Dictionary that links the question IDs to the questions.
    answers : dict[str, str]
        Dictionary that stores the answers linked to question IDs.
    """
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
        # TODO: see how to merge this with AQuestionManager
        # Get the question type class.
        question_type = getattr(questionnaire_questions, f'{question_dict["type"]}QQuestion')
        # Create the instance of it.
        question_instance: questionnaire_questions.QuestionnaireQuestion = question_type(question_dict)

        # Add the instance to the screen and the list.
        self.add_widget(question_instance)

        # Link the ID to the instance
        self.questions[question_dict['id']] = question_instance
        # Create a spot in the answer dictionary
        self.answers[question_dict['id']] = ''

    def get_state(self) -> bool:
        """
        Get an indication if all questions have been answered in this manager.

        Returns
        -------
        bool
            Indication if all questions have been answered in this manager.
        """
        total_state = True

        for qid, answer in self.answers.items():
            total_state = total_state and bool(answer)

        return total_state

    def change_answer(self, question_id: str, answer: str) -> None:
        """
        Update the answer of the question with the given ID.

        Parameters
        ----------
        question_id : str
            ID of the question for which to change the answer.
        answer : str
            The answer string to update to.
        """
        # TODO: Check if parent level can be equalised with AQuestionManager
        self.answers[question_id] = answer
        # Have the QuestionnaireScreen check the state
        self.parent.unlock_check(question_state=self.get_state() and not self.disabled)


def questionnaire_setup(questionnaire_dict: dict, manager: ScreenManager, state_override: bool,
                        part: str = 'main', ) -> None:
    """
    Set up a questionnaire based on the questionnaire dictionary.

    Parameters
    ----------
    questionnaire_dict : dict
        Dictionary that defines the questionnaire and its questions.
    manager : PalilaScreenManager
        ScreenManager to add the questionnaire to.
    state_override : bool
        Override variable to be passed to the questionnaire screens.
    part : str
        String defining the experiment block of which this questionnaire is a part.
    """
    # If the dictionary with the question distribution over the screens is empty, make the GUI skip the questionnaire.
    if not questionnaire_dict['screen dict']:
        manager.get_screen(questionnaire_dict['previous']).next_screen = questionnaire_dict['next']

    else:
        # Extract the screen numbers from the question distribution
        screen_nums = sorted(questionnaire_dict['screen dict'].keys())
        # Loop over those numbers
        for ii, screen_num in enumerate(screen_nums):
            if ii:
                # When this is not the last screen, define the previous indexed screen as previous to this one
                previous_screen = f'{part}-questionnaire {ii}'
            else:
                # In case this is the first questionnaire screen, set the previous screen to the one defined
                # in the setup dictionary
                previous_screen = questionnaire_dict['previous']

            # Check if this is the last questionnaire screen.
            if screen_num < max(screen_nums):
                # If not, define the next one by the index + 2
                next_screen = f'{part}-questionnaire {ii + 2}'
            else:
                # The last screen continues into the defined next screen.
                next_screen = questionnaire_dict['next']

            if ii:
                # Create a new questionnaire screen with the necessary parameters
                new_screen = QuestionnaireScreen(questionnaire_dict, questionnaire_dict['screen dict'][screen_num],
                                                 previous_screen, next_screen,
                                                 back_function=manager.navigate_previous, state_override=state_override,
                                                 name=f'{part}-questionnaire {ii + 1}',
                                                 )
            else:
                # Special case for the first questionnaire screen
                new_screen = QuestionnaireScreen(questionnaire_dict, questionnaire_dict['screen dict'][screen_num],
                                                 previous_screen, next_screen,
                                                 state_override=state_override, name=f'{part}-questionnaire {ii + 1}',
                                                 )
            # Add the questionnaire screen to the ScreenManager
            manager.add_widget(new_screen)
