"""
Module with all the code for the modular audio questions.
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

from kivy.properties import NumericProperty, ListProperty, StringProperty

from .questions import *


class AudioQuestion(Question):
    """
    Class to manage the general functions of a question. Subclass of GUI.questions.Question.
    """
    value = NumericProperty(0.)
    text = StringProperty('')


class TextAQuestion(AudioQuestion):
    """
    Question type which only displays text. Subclass of GUI.AudioQuestion.

    Parameters
    ----------
    question_dict: dict
        Dictionary with all the information to construct the question. Should include the following keys: 'id', 'text'.
    **kwargs
        Keyword arguments. These are passed on to the kivy.uix.boxlayout.BoxLayout constructor.
    """
    def __init__(self, question_dict: dict, **kwargs) -> None:
        super().__init__(question_dict, **kwargs)
        self.ids.question_text.valign = 'center'


class ButtonAQuestion(ButtonQuestion, AudioQuestion):
    """
    General class for questions involving buttons. Subclass of GUI.ButtonQuestion and GUI.AudioQuestion.
    """
    def __init__(self, question_dict: dict, **kwargs):
        super().__init__(question_dict, **kwargs)

        # Increase the button text font size.
        for button in self.buttons:
            button.font_size = 42


class MultipleChoiceAQuestion(ButtonAQuestion):
    """
    Question type for multiple choice. Subclass of GUI.ButtonAQuestion.
    """
    pass


class IntegerScaleAQuestion(ButtonAQuestion):
    """
    Numerical scale question type. Subclass of GUI.AudioQuestion.

    Parameters
    ----------
    question_dict: dict
        Dictionary with all the information to construct the question.
        Should include the following keys: 'id', 'text', 'min', 'max'. Optional keys: 'left note', 'right note'.
    **kwargs
        Keyword arguments. These are passed on to the kivy.uix.boxlayout.BoxLayout constructor.
    """
    def __init__(self, question_dict: dict, **kwargs) -> None:
        # Make the min and max values into integers
        self.min = int(question_dict['min'])
        self.max = int(question_dict['max'])

        # Make the question dict compatible with the superclass requirements
        question_dict['choices'] = [str(num) for num in range(self.min, self.max + 1)]
        super().__init__(question_dict, **kwargs)

        # Create variable to detect the presence of the edge notes
        no_notes = True
        # Add the left side note if there is one
        if 'left note' in question_dict.keys():
            if '\n' in question_dict['left note']:
                question_dict['left note'] = question_dict['left note'].replace('\t', '')
            self.ids.left_note.text = question_dict['left note']
            no_notes = False
        # Add the right side note if there is one
        if 'right note' in question_dict.keys():
            if '\n' in question_dict['right note']:
                question_dict['right note'] = question_dict['right note'].replace('\t', '')
            self.ids.right_note.text = question_dict['right note']
            no_notes = False

        # Set up the scale size, according to the presence of edge notes
        if no_notes:
            scale_width = .95
            scale_start = .025
            self.ids.scale_bar.size_hint = (.96, .2)
        else:
            scale_width = .64
            scale_start = .18

        # Determine the number of buttons and their width
        n_button = self.max - self.min + 1
        button_width = scale_width / n_button

        # Add buttons at integer intervals
        for bi, button in enumerate(self.buttons):
            # Set the x and y size of the buttons (specific to 16:10 aspect ratio)
            button.size_hint_x = .75 * (button_width ** .95)
            button.size_hint_y = .75 * (button_width ** .95) * 9
            # Determine their positions
            button.pos_hint = {'center_x': (scale_start + button_width / 2) + (bi * button_width), 'center_y': .5}


class SpinnerAQuestion(SpinnerQuestion, AudioQuestion):
    pass


class SliderAQuestion(AudioQuestion):
    """
    Numerical scale type question with a slider instead of buttons for a more granular answer.

    Parameters
    ----------
    question_dict: dict
        Dictionary with all the information to construct the question.
        Should include the following keys: 'id', 'text', 'min', 'max'. 'step'. Optional keys: 'left note', 'right note'.
    **kwargs
        Keyword arguments. These are passed on to the kivy.uix.boxlayout.BoxLayout constructor.

    Attributes
    ----------
    min : NumericProperty
        Minimum value of the slider.
    max : NumericProperty
        Maximum value of the slider.
    step : NumericProperty
        Step size of the slider.
    slider_color : ListProperty
        Color of the slider to indicate its answer state.
    answered : bool
        Indication of the slider state.
    """

    min = NumericProperty(0.)
    max = NumericProperty(0.)
    step = NumericProperty(0.)

    slider_color = ListProperty([.8, .8, .8, 1.])

    def __init__(self, question_dict: dict, **kwargs) -> None:
        super().__init__(question_dict, **kwargs)
        # Create variable to detect the presence of the edge notes
        no_notes = True
        # Add the left side note if there is one
        if 'left note' in question_dict.keys():
            if '\n' in question_dict['left note']:
                question_dict['left note'] = question_dict['left note'].replace('\t', '')
            self.ids.left_note.text = question_dict['left note']
            no_notes = False
        # Add the right side note if there is one
        if 'right note' in question_dict.keys():
            if '\n' in question_dict['right note']:
                question_dict['right note'] = question_dict['right note'].replace('\t', '')
            self.ids.right_note.text = question_dict['right note']
            no_notes = False

        # Adjust the slider size when no side notes are present.
        if no_notes:
            self.ids.slider_holder.size_hint_x = .95
            self.ids.left_note.size_hint_x = 0.05
            self.ids.right_note.size_hint_x = 0.05

        # Make the min and max values into integers
        self.min = float(question_dict['min'])
        self.max = float(question_dict['max'])
        self.step = float(question_dict['step'])

        # Adjust the initial position of the slider according to the input file
        if 'initial' in question_dict:
            # Extract the initial value
            initial = float(question_dict['initial'])
            # Check if the value is valid for the slider setup
            if self.min > initial or self.max < initial:
                raise SyntaxError(f'Initial Slider value of {question_dict["id"]} '
                                  f'outside the range [{self.min}, {self.max}].')
            elif initial % self.step:
                raise SyntaxError(f'Initial Slider value of {question_dict["id"]} '
                                  f'not compatible with step size {self.step}.')

            # In case it is valid, set it
            else:
                self.value = initial

        else:
            # If no initial value is given, set the slider to the middle
            self.value = (self.max + self.min) / 2.

        # Initialise the answer state to False
        self.answered = False

    def slider_input(self) -> None:
        """
        Function to be triggered when the slider is changed.
        """
        # Avoid issues during the initialisation of the GUI
        if self.parent is None:
            return

        # Round the value on the slider to be workable
        self.ids.slider.value = round(self.ids.slider.value, 9)
        # Communicate the value to the backend
        self.change_answer(str(self.ids.slider.value))

        # Change the slider look to indicate it has been answered.
        self.slider_color = [.9 * .5, .9 * 1., .9 * .5, .9 * 1.]
        self.ids.slider.background_horizontal = 'GUI/assets/Slider_cursor_answered.png'
        self.ids.slider.cursor_image = 'GUI/assets/Slider_cursor_answered.png'

        self.answered = True

    def dependant_lock(self) -> None:
        """
        Lock this question when it is locked by another question.
        """
        self.slider_color = [.9 * .5, .9 * 1., .9 * .5, .9 * 1.]
        # Change the slider look
        self.ids.slider.background_disabled_horizontal = 'GUI/assets/Slider_background_locked.png'
        self.ids.slider.cursor_disabled_image = 'GUI/assets/Slider_cursor_locked.png'

        super().dependant_lock()

    def dependant_unlock(self) -> None:
        """
        Lock this question when it is locked by another question.
        """
        # Change the slider look to indicate if it has been answered.
        if self.answered:
            self.slider_color = [.9 * .5, .9 * 1., .9 * .5, .9 * 1.]
        else:
            self.slider_color = [1., 1., 1., 1.]

        # Reset the slider look
        self.ids.slider.background_disabled_horizontal = 'GUI/assets/Slider_background_disabled.png'
        self.ids.slider.cursor_disabled_image = 'GUI/assets/Slider_cursor_disabled.png'

        super().dependant_unlock()
