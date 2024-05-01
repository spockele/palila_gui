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
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.properties import ColorProperty, NumericProperty

from .numpad_bubble import NumPadBubble


__all__ = ['QuestionnaireQuestion']


class QuestionnaireChoiceButton(Button):
    """
    Button with ability to store a state and interact with QuestionnaireQuestion

    Parameters
    ----------
    text : str, optional
        For setting the Button.text through calling in Python.
    **kwargs
        Keyword arguments. These are passed on to the kivy.uix.button.Button constructor.
    """
    def __init__(self, text: str = '', **kwargs):
        super().__init__(text=text, **kwargs)

    def select(self) -> None:
        """
        Change the color to reflect his button is selected.
        """
        self.background_color = [.5, 1., .5, 1.]

    def deselect(self) -> None:
        """
        Change the color to reflect his button is deselected.
        """
        self.background_color = [1., 1., 1., 1.]

    def on_release(self):
        """
        Select this button on release and communicate this to the QuestionnaireQuestion.
        """
        self.parent.parent.select_choice(self)


class QuestionnaireQuestion(FloatLayout):
    """
    Class to manage the general functions of a question. Subclass of kivy.uix.floatlayout.FloatLayout.

    Parameters
    ----------
    question_dict: dict
        Dictionary with all the information to construct the question. Should include the following keys: 'id', 'text'.
    **kwargs
        Keyword arguments. These are passed on to the kivy.uix.floatlayout.FloatLayout constructor.

    Attributes
    ----------
    question_dict : dict
        Dictionary with all the information to construct the question.
    qid : str
        Question ID for communication with the file system.
    answer
        Currently selected answer. None in case no answer is selected.
    """
    bordercolor = ColorProperty([0., 0., 0., 0.])

    text_width = NumericProperty(.455)
    answer_width = NumericProperty(.545)

    def __init__(self, question_dict: dict, **kwargs):
        super().__init__(**kwargs)
        self.question_dict = question_dict
        self.ids.question_text.text = question_dict['text']
        self.qid = question_dict['id']

        self.dependants: list[QuestionnaireQuestion] = list()
        if 'unlocked by' in question_dict:
            self.unlock_condition = question_dict['unlock condition']
        else:
            self.unlock_condition = None
        # ==============================================================================================================
        # todo: DEPRECATED CODE
        # ---------------------
        self.dependant = None
        # ==============================================================================================================
        self.answer_temp = ''

    def change_answer(self, answer: str) -> None:
        # ==============================================================================================================
        # todo: DEPRECATED CODE
        # ---------------------
        if self.dependant is not None:
            if answer == self.question_dict['dependant condition']:
                self.dependant.dependant_unlock()

            else:
                self.dependant.dependant_lock()
        # ==============================================================================================================

        for question in self.dependants:
            if answer == question.unlock_condition and not self.disabled:
                question.dependant_unlock()
            else:
                question.dependant_lock()

        self.parent.change_answer(self.qid, answer)

    def set_unlock(self):
        if self.unlock_condition is not None:
            self.parent.questions[self.question_dict['unlocked by']].dependants.append(self)
            self.dependant_lock()

    def set_dependant(self):
        # ==============================================================================================================
        # todo: DEPRECATED CODE
        # ---------------------
        if 'dependant' in self.question_dict:
            if 'dependant condition' not in self.question_dict:
                raise SyntaxError(f'{self.qid} does not have a "dependant condition" to unlock its dependant question.')
            else:
                self.dependant: QuestionnaireQuestion = self.parent.questions[self.question_dict['dependant']]
                self.dependant.dependant_lock()
        # ==============================================================================================================

    def dependant_lock(self):
        if not self.answer_temp:
            to_store = self.parent.answers[self.qid]
            self.answer_temp = '' if to_store == 'n/a' else to_store

        self.change_answer('n/a')
        self.disabled = True

    def dependant_unlock(self):
        self.disabled = False
        self.change_answer(self.answer_temp)
        self.answer_temp = ''

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

    def on_touch_down(self, touch):
        """
        Overload of on_touch_down method to trigger the NumPad Bubble.
        """
        if self.collide_point(*touch.pos):
            self.parent.trigger_numpad(self)

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

    def __init__(self, question_dict: dict, **kwargs):
        super().__init__(question_dict, **kwargs)
        self.numpad = NumPadBubble()

    def number_input(self):
        """
        Check the full input of the TextInput before triggering the unlock check.
        """
        if self.ids.number_input.text:
            if self.ids.number_input.text.isnumeric():
                self.ids.number_overlay.text = ''
                self.ids.number_input.background_color = [.5, 1., .5, 1.]

            else:
                self.ids.number_input.text = self.answer_temp

        else:
            self.ids.number_input.background_color = [1., 1., 1., 1.]
            self.ids.number_overlay.text = 'Enter a number here.'

        self.change_answer(self.ids.number_input.text)
        self.answer_temp = self.ids.number_input.text

    def trigger_numpad(self, called_with):
        """
        Open or close the numpad and (de)couple it to the calling widget.
        """
        if self.numpad.parent is None:
            self.parent.parent.add_widget(self.numpad)
            self.numpad.coupled_widget = called_with
        else:
            self.parent.parent.remove_widget(self.numpad)
            self.numpad.coupled_widget = None

    def dependant_lock(self):
        self.ids.number_overlay.text = ''
        self.ids.number_input.background_color = [.7, 1., .7, 1.]
        super().dependant_lock()

    def dependant_unlock(self):
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

    def __init__(self, question_dict: dict, **kwargs):
        super().__init__(question_dict, **kwargs)

    def text_input(self):
        if self.ids.text_input.text:
            if len(self.ids.text_input.text.split('\n')) > 2:
                self.ids.text_input.text = self.answer_temp

            self.ids.text_overlay.text = ''
            self.ids.text_input.background_color = [.5, 1., .5, 1.]

        else:
            self.ids.text_input.background_color = [1., 1., 1., 1.]
            self.ids.text_overlay.text = 'Enter your answer here.'

        self.change_answer(self.ids.text_input.text)
        self.answer_temp = self.ids.text_input.text

    def dependant_lock(self):
        self.ids.text_overlay.text = ''
        self.ids.text_input.background_color = [.7, 1., .7, 1.]
        super().dependant_lock()

    def dependant_unlock(self):
        super().dependant_unlock()
        self.text_input()


class SpinnerQQuestion(QuestionnaireQuestion):
    """
    Multiple choice type question with a dropdown instead of buttons.

    Parameters
    ----------
    question_dict: dict
        Dictionary with all the information to construct the question. Should include the following keys: 'id', 'text'.
    **kwargs
        Keyword arguments. These are passed on to the kivy.uix.floatlayout.FloatLayout constructor.
    """

    def __init__(self, question_dict: dict, **kwargs):
        """

        """
        super().__init__(question_dict, **kwargs)
        self.ids.spinner.values = question_dict['choices']

    def spinner_input(self):
        if self.ids.spinner.text:
            self.ids.spinner.background_color = [.5, 1., .5, 1.]
        else:
            self.ids.spinner.background_color = [1., 1., 1., 1.]

        self.change_answer(self.ids.spinner.text)

    def dependant_lock(self):
        super().dependant_lock()
        self.ids.spinner.background_color = [.7, 1., .7, 1.]

    def dependant_unlock(self):
        self.spinner_input()
        super().dependant_unlock()


class MultipleChoiceQQuestion(QuestionnaireQuestion):
    """
    Question type for multiple choice.

    Parameters
    ----------
    question_dict: dict
        Dictionary with all the information to construct the question. Should include the following keys: 'id', 'text'.
    **kwargs
        Keyword arguments. These are passed on to the kivy.uix.floatlayout.FloatLayout constructor.

    Attributes
    ----------
    choice : QuestionnaireChoiceButton = None
        Currently selected choice button
    """
    def __init__(self, question_dict: dict, **kwargs):
        super().__init__(question_dict, **kwargs)
        self.choice = None
        self.choice_temp = None

        # Add every choice as a button and track their word lengths
        self.choices = []
        lengths = []
        for choice in question_dict['choices']:
            choice_button = QuestionnaireChoiceButton(choice)
            self.choices.append(choice_button)
            self.ids.question_input.add_widget(choice_button)
            lengths.append(len(choice))
        # Resize proportional to the root of the word lengths
        total = sum(lengths)
        for ii, length in enumerate(lengths):
            self.choices[ii].size_hint_x = length ** .5 / total

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
            self.change_answer('')
        else:
            # Set the current answer to the entered button otherwise
            self.choice = choice
            self.choice.select()
            self.change_answer(choice.text)

    def dependant_lock(self):
        if self.choice_temp is None:
            self.choice_temp = self.choice
        self.choice = None

        for choice in self.choices:
            choice.background_color = [.7, 1, .7, 1.]

        super().dependant_lock()

    def dependant_unlock(self):
        for choice in self.choices:
            choice.deselect()

        if self.choice_temp is not None:
            self.select_choice(self.choice_temp)
            self.choice_temp = None

        super().dependant_unlock()

