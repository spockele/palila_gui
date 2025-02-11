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

from .screens import QuestionScreen, BackButton, Filler
from .questions import QuestionManager
from . import questionnaire_questions


__all__ = ['questionnaire_setup']


class QuestionnaireScreen(QuestionScreen):
    """
    Class that defines the overall audio question screens. Subclass of GUI.screens.QuestionScreen.

    Parameters
    ----------
    questionnaire_dict : dict
        Dictionary that defines the questionnaire and its questions.

    questions: list

    state_override: bool, optional (default=False)

    back_function: callable, optional

    **kwargs
        Keyword arguments. These are passed on to the GUI.screens.PalilaScreen constructor.

    Attributes
    ----------
    config_dict : dict
        Dictionary that defines the questionnaire and its questions.
    """

    def __init__(self,
                 questionnaire_dict: dict,
                 questions: list,
                 state_override: bool = False,
                 back_function: callable = None,
                 **kwargs
                 ) -> None:

        super().__init__(questionnaire_dict, questions, 7, state_override=state_override, lock=True, **kwargs)

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

        # Add the borders to all questions
        [question.border() for question in self.question_manager.questions.values()]

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


class QQuestionManager(QuestionManager):
    """
    Subclass of GUI.questions.QuestionManager.
    """
    @staticmethod
    def question_class_from_type(question_type: str) -> type:
        """
        Obtain the type definition of a question type for the add_question function.

        Parameters
        ----------
        question_type: str
            Name of the question type from a question_dict.
        """
        return getattr(questionnaire_questions, f'{question_type}QQuestion')


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
                questionnaire_dict['previous'] = f'{part}-questionnaire {ii}'

            # Check if this is the last questionnaire screen.
            if screen_num < max(screen_nums):
                # If not, define the next one by the index + 2
                questionnaire_dict['next'] = f'{part}-questionnaire {ii + 2}'

            if ii:
                # Create a new questionnaire screen with the necessary parameters
                new_screen = QuestionnaireScreen(questionnaire_dict, questionnaire_dict['screen dict'][screen_num],
                                                 state_override=state_override, back_function=manager.navigate_previous,
                                                 name=f'{part}-questionnaire {ii + 1}',
                                                 )
            else:
                # Special case for the first questionnaire screen
                new_screen = QuestionnaireScreen(questionnaire_dict, questionnaire_dict['screen dict'][screen_num],
                                                 state_override=state_override, name=f'{part}-questionnaire {ii + 1}',
                                                 )
            # Add the questionnaire screen to the ScreenManager
            manager.add_widget(new_screen)
