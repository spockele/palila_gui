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

from kivy.properties import ColorProperty, NumericProperty
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.widget import Widget

from .screens import QuestionScreen
from .tools import NumPadBubble
from .questions import *


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
                 state_override: bool = False,
                 **kwargs
                 ) -> None:

        super().__init__(questionnaire_dict, 7, state_override=state_override, **kwargs)

        # Add the borders to all questions
        [question.border() for question in list(self.question_manager.questions.values())[:-1]]

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
        return globals()[f'{question_type}QQuestion']


class QuestionnaireQuestion(Question):
    """
    Class to manage the general functions of a question. Subclass of GUI.questions.Question.
    """
    bordercolor = ColorProperty([0., 0., 0., 0.])
    text_width = NumericProperty(.455)
    answer_width = NumericProperty(.545)

    def border(self):
        """
        Add the top borderline to the question.
        """
        self.bordercolor = [.8, .8, .8, 1.]


class FreeNumberQQuestion(QuestionnaireQuestion):
    """
    Question type that allows for a number to be entered by the participant.

    Parameters
    ----------
    question_dict: dict
        Dictionary with all the information to construct the question. Should include the following keys: 'id', 'text'.
    **kwargs
        Keyword arguments. These are passed on to the kivy.uix.floatlayout.FloatLayout constructor.

    Attributes
    ----------
    numpad : NumPadBubble
        Numpad coupled to this Question
    """

    def __init__(self, question_dict: dict, **kwargs) -> None:
        super().__init__(question_dict, **kwargs)
        self.numpad = NumPadBubble()

    def number_input(self) -> None:
        """
        Function triggered by input in the TextInput bar.
        Checks the full input of the TextInput before changing the answer.
        """
        # Check if there is text left after the input
        if self.ids.number_input.text:
            # Check if this text is actually a number.
            if self.ids.number_input.text.isnumeric():
                # If so, remove the overlay text and change the color to green.
                self.ids.number_overlay.text = ''
                self.ids.number_input.background_color = [.5, 1., .5, 1.]

            else:
                # In case it's not a number, revert to the last valid state
                self.ids.number_input.text = self.answer_temp

        else:
            # If the input bar is empty again, change the color back to white and reset the overlay text.
            self.ids.number_input.background_color = [1., 1., 1., 1.]
            self.ids.number_overlay.text = 'Enter a number here.'

        # After checking everything, change the answer of this question and store it in the temp variable.
        self.change_answer(self.ids.number_input.text)
        self.answer_temp = self.ids.number_input.text

    def trigger_numpad(self, called_with: Widget) -> None:
        """
        Open or close the numpad and (de)couple it to/from the calling widget.

        Parameters
        ----------
        called_with : Widget
            The widget that called for the numpad to be opened.
        """
        # In case the numpad is not yet coupled and on the screen:
        if self.numpad.parent is None:
            # Put it on the screen and couple it.
            self.parent.parent.add_widget(self.numpad)
            self.numpad.coupled_widget = called_with
        else:
            # Otherwise, remove and decouple.
            self.parent.parent.remove_widget(self.numpad)
            self.numpad.coupled_widget = None

    def dependant_lock(self) -> None:
        """
        Lock this question when it is locked by another question.
        """
        self.ids.number_overlay.text = ''
        self.ids.number_input.background_color = [.7, 1., .7, 1.]
        super().dependant_lock()

    def dependant_unlock(self) -> None:
        """
        Unlock this question when it is locked by another question.
        """
        self.number_input()
        super().dependant_unlock()


class FreeTextQQuestion(QuestionnaireQuestion):
    """
    Question type that allows for text to be entered by the participant.

    Parameters
    ----------
    question_dict: dict
        Dictionary with all the information to construct the question. Should include the following keys: 'id', 'text'.
    **kwargs
        Keyword arguments. These are passed on to the kivy.uix.floatlayout.FloatLayout constructor.
    """

    def __init__(self, question_dict: dict, **kwargs) -> None:
        super().__init__(question_dict, **kwargs)

    def text_input(self) -> None:
        """
        Function triggered by input in the TextInput bar.
        Checks the full input of the TextInput before changing the answer.
        """
        # Check if there is text left after the latest input.
        if self.ids.text_input.text:
            # Check that the text is no more than the supported 2 lines.
            if len(self.ids.text_input.text.split('\n')) > 2:
                # If the input results in >2 lines, ignore.
                self.ids.text_input.text = self.answer_temp
            # Remove the overlay text and change the bar color to green.
            self.ids.text_overlay.text = ''
            self.ids.text_input.background_color = [.5, 1., .5, 1.]

        else:
            # Otherwise, change the color back to white and reset the overlay message.
            self.ids.text_input.background_color = [1., 1., 1., 1.]
            self.ids.text_overlay.text = 'Enter your answer here.'

        # Finally, change the stored answer and store it in the temp variable as well.
        self.change_answer(self.ids.text_input.text)
        self.answer_temp = self.ids.text_input.text

    def dependant_lock(self) -> None:
        """
        Lock this question when it is locked by another question.
        """
        self.ids.text_overlay.text = ''
        self.ids.text_input.background_color = [.7, 1., .7, 1.]
        super().dependant_lock()

    def dependant_unlock(self) -> None:
        """
        Unlock this question when it is locked by another question.
        """
        super().dependant_unlock()
        self.text_input()


class SpinnerQQuestion(SpinnerQuestion, QuestionnaireQuestion):
    pass


class MultipleChoiceQQuestion(ButtonQuestion, QuestionnaireQuestion):
    """
    Question type for multiple choice, multiple answer.

    Parameters
    ----------
    question_dict: dict
        Dictionary with all the information to construct the question. Should include the following keys: 'id', 'text'.
    **kwargs
        Keyword arguments. These are passed on to the kivy.uix.floatlayout.FloatLayout constructor.

    Attributes
    ----------
    buttons : list[QuestionnaireChoiceButton]
        List of the available choice buttons
    choices : list[QuestionnaireChoiceButton] = []
        Currently selected choice button(s)
    """

    def __init__(self, question_dict: dict, **kwargs) -> None:
        super().__init__(question_dict, **kwargs)

        # Resize proportional to the root of the word lengths
        lengths = [len(choice.text) for choice in self.buttons]
        total = sum(lengths)
        for ii, length in enumerate(lengths):
            self.buttons[ii].size_hint_x = length ** .5 / total


# ======================================================================================================================
# todo: DEPRECATED CODE
# ---------------------
class MultiMultipleChoiceQQuestion(MultipleChoiceQQuestion):
    """
    Class to maintain compatibility with previous versions.
    """
    def __init__(self, question_dict: dict, **kwargs) -> None:
        question_dict['multi'] = True
        super().__init__(question_dict, **kwargs)
# ======================================================================================================================


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
            screen_dict = dict()

            if ii:
                # When this is not the last screen, define the previous indexed screen as previous to this one
                screen_dict['previous'] = f'{part}-questionnaire {ii}'
            else:
                screen_dict['previous'] = questionnaire_dict['previous']

            # Check if this is the last questionnaire screen.
            if screen_num < max(screen_nums):
                # If not, define the next one by the index + 2
                screen_dict['next'] = f'{part}-questionnaire {ii + 2}'

            else:
                screen_dict['next'] = questionnaire_dict['next']

            screen_dict['questions'] = questionnaire_dict['screen dict'][screen_num]
            for question in screen_dict['questions']:
                screen_dict[question] = questionnaire_dict[question]

            if ii:
                # Create a new questionnaire screen with the necessary parameters
                new_screen = QuestionnaireScreen(screen_dict,
                                                 state_override=state_override,
                                                 name=f'{part}-questionnaire {ii + 1}',
                                                 )
            else:
                # Special case for the first questionnaire screen
                new_screen = QuestionnaireScreen(screen_dict,
                                                 state_override=state_override, name=f'{part}-questionnaire {ii + 1}',
                                                 )
            # Add the questionnaire screen to the ScreenManager
            manager.add_widget(new_screen)
