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

------------------------------------------------------------------------------------------------------------------------

Module with all the code for the modular questionnaire questions.

------------------------------------------------------------------------------------------------------------------------
"""
from kivy.properties import ColorProperty, NumericProperty
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

from .numpad_bubble import NumPadBubble
from .questions import *


__all__ = ['QuestionnaireQuestion']


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


class FreeNumberTextInput(TextInput):
    """
    Subclass of the TextInput to accommodate the NumPad Bubble for entering text with touchscreens.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_touch_down(self, touch) -> None:
        """
        Overload of on_touch_down method to trigger the NumPad Bubble.
        """
        if self.collide_point(*touch.pos):
            self.parent.parent.trigger_numpad(self)

        super().on_touch_down(touch)


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
