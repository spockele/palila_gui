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

Module with all the code for the modular questions.
"""
from kivy.properties import NumericProperty, ListProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button


class AudioChoiceButton(Button):
    """
    Button with ability to store a state and interact with AudioQuestion. Subclass of kivy.uix.button.Button.

    Parameters
    ----------
    text : str
        Text to be displayed on the button.
    font_size : int, optional
        Optional font size of the text. Defaults to 72.
    **kwargs
        Keyword arguments. These are passed on to the kivy.uix.button.Button constructor.
    """
    def __init__(self, text: str = '', font_size: int = 72, **kwargs) -> None:
        super().__init__(text=text, **kwargs)
        self.font_size = font_size
        self.dependant_lock = False

    def select(self) -> None:
        """
        Make the background color green to indicate this button is selected.
        """
        self.background_color = [.5, 1., .5, 1.]

    def deselect(self) -> None:
        """
        Reset the background color to indicate this button is not selected.
        """
        self.background_color = [1., 1., 1., 1.]

    def on_release(self) -> None:
        """
        Use the AudioQuestion class to do the selection.
        """
        self.parent.parent.select_choice(self)


class AnswerHolder:
    """
    Placeholder for the ChoiceButton for those question types that do not use buttons to answer.

    Attributes
    ----------
    text : str
        Holds the answer text
    """
    def __init__(self, dependant_lock: bool = False):
        self.text: str = 'n/a' if dependant_lock else ''
        self.dependant_lock = dependant_lock


class AudioQuestion(BoxLayout):
    """
    Class to manage the general functions of a question. Subclass of kivy.uix.boxlayout.BoxLayout.

    Parameters
    ----------
    question_dict: dict
        Dictionary with all the information to construct the question. Should include the following keys: 'id', 'text'.
    **kwargs
        Keyword arguments. These are passed on to the kivy.uix.boxlayout.BoxLayout constructor.

    Attributes
    ----------
    question_dict : dict
        Dictionary with all the information to construct the question.
    qid : str
        Question ID for communication with the file system.
    answer
        AudioChoiceButton or AnswerHolder with the currently selected answer. None in case no answer is selected.
    """

    value = NumericProperty(0.)
    text = StringProperty('')

    def __init__(self, question_dict: dict, **kwargs) -> None:
        super().__init__(**kwargs)
        # Store the input information
        self.question_dict = question_dict
        self.qid = question_dict['id']
        self.ids.question_text.text = question_dict['text']
        if '\n' in question_dict['text']:
            self.ids.question_text.font_size = 38
        # Initialise variable to store current answer
        self.answer = None

        self.dependant = None
        self.dependant_id = None
        self.dependant_answer_temp = None

    def select_choice(self, choice: AudioChoiceButton, dependant_unlock: bool = False) -> None:
        """
        Sets the current answer in this manager, based on the selected ChoiceButton.

        Parameters
        ----------
        choice : AudioChoiceButton
            The AudioChoiceButton instance which has triggered the answer selection.
        dependant_unlock : bool, optional

        """
        # Deselect the current answer if there is one
        if self.answer is not None:
            self.answer.deselect()

        # Remove the current answer if the current answer is pressed again
        if self.answer == choice and not dependant_unlock:
            self.answer = None
            # Communicate to the question manager that the question is unanswered.
            self.parent.question_answered(self.qid, False)
        # Set the current answer to the selected button otherwise
        else:
            self.answer = choice
            self.answer.select()
            # Communicate to the question manager that the question is answered.
            self.parent.question_answered(self.qid, True)

        if self.dependant is not None:
            self.check_dependant()

    def set_value(self):
        """
        Sets the current answer in this manager, based on the selected numerical value.
        """
        # Set the string equivalent of the numerical value
        self.text = str(self.value)
        self.set_text()

    def set_text(self):
        """
        Sets the current answer in this manager, based on the selected text.
        """
        # Create an AnswerHolder if there is None
        if self.answer is None:
            self.answer = AnswerHolder()

        # In case this is the first answer
        if not self.answer.text:
            # Indicate to the parent that this question is answered
            self.parent.question_answered(self.qid, True)
            # Change the background color of the answer option
            self.ids.answer_options.background_color = (.5, 1., .5, 1)

        # Set the text in the answer instance
        self.answer.text = self.text

        if self.dependant is not None:
            self.check_dependant()

    def check_dependant(self):
        if self.answer is not None and self.answer.text == self.question_dict['dependant condition']:
            self.dependant.dependant_unlock(self.dependant_answer_temp)
        else:
            if self.dependant.answer is not None and not self.dependant.answer.dependant_lock:
                self.dependant_answer_temp = self.dependant.answer
            self.dependant.dependant_lock()

    def set_dependant(self):
        if 'dependant' in self.question_dict:
            self.dependant_id = self.question_dict['part-audio'] + self.question_dict['dependant'].zfill(2)
            if 'dependant condition' not in self.question_dict:
                raise SyntaxError(f'{self.qid} does not have a "dependant condition" to unlock its dependant question.')
            else:
                self.dependant: AudioQuestion = self.parent.question_dict[self.dependant_id]
                self.dependant.dependant_lock()

    def dependant_lock(self):
        self.answer = AnswerHolder(dependant_lock=True)
        self.parent.question_answered(self.qid, True)
        self.disabled = True

    def dependant_unlock(self, previous_answer):
        self.answer = None
        self.parent.question_answered(self.qid, False)
        self.disabled = False

        if isinstance(previous_answer, AnswerHolder):
            self.set_text()
        elif previous_answer is not None:
            self.select_choice(previous_answer, dependant_unlock=True)


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
    def __init__(self, question_dict: dict, **kwargs):
        super().__init__(question_dict, **kwargs)
        self.ids.question_text.valign = 'center'

    def on_parent(self, *_):
        """
        When the widget gets a parent QuestionManager, this function notifies it that no answer is required here.
        """
        self.parent.question_answered(self.qid, True)


class MultipleChoiceAQuestion(AudioQuestion):
    """
    Question type for multiple choice. Subclass of GUI.AudioQuestion.

    Parameters
    ----------
    question_dict: dict
        Dictionary with all the information to construct the question.
        Should include the following keys: 'id', 'text', 'choices'.
    **kwargs
        Keyword arguments. These are passed on to the kivy.uix.boxlayout.BoxLayout constructor.
    """
    def __init__(self, question_dict: dict, **kwargs) -> None:
        super().__init__(question_dict, **kwargs)
        self.buttons = []
        # Add the choices from the input file
        for choice in self.question_dict['choices']:
            button = AudioChoiceButton(choice, font_size=48)
            self.buttons.append(button)
            # self.options.append(button)
            self.ids.answer_options.add_widget(button)

    def dependant_lock(self):
        for button in self.buttons:
            button.background_color = [.7, 1., .7, 1.]
        super().dependant_lock()

    def dependant_unlock(self, previous_answer):
        for button in self.buttons:
            button.background_color = [1, 1, 1, 1]
        super().dependant_unlock(previous_answer)


class SpinnerAQuestion(AudioQuestion):
    """
    Multiple choice type question with a dropdown instead of buttons.

    Parameters
    ----------
    question_dict: dict
        Dictionary with all the information to construct the question.
        Should include the following keys: 'id', 'text', 'choices'.
    **kwargs
        Keyword arguments. These are passed on to the kivy.uix.boxlayout.BoxLayout constructor.
    """

    def __init__(self, question_dict: dict, **kwargs) -> None:
        super().__init__(question_dict, **kwargs)
        self.ids.answer_options.values = question_dict['choices']


class IntegerScaleAQuestion(AudioQuestion):
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
        super().__init__(question_dict, **kwargs)
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

        scale_width = .64
        scale_start = .18
        if no_notes:
            scale_width = .95
            scale_start = .025
            self.ids.scale_bar.size_hint = (.96, .2)

        # Make the min and max values into integers
        self.min = int(question_dict['min'])
        self.max = int(question_dict['max'])
        # Determine the number of buttons and their width
        n_button = self.max - self.min + 1
        button_width = scale_width / n_button

        # Add buttons at integer intervals
        for bi, bv in enumerate(range(self.min, self.max + 1)):
            # Create the button and add it to the Layout
            button = AudioChoiceButton(str(bv))
            self.ids.answer_options.add_widget(button)
            # Set the x and y size of the buttons (specific to 16:10 aspect ratio)
            button.size_hint_x = .75 * (button_width ** .95)
            button.size_hint_y = .75 * (button_width ** .95) * 9
            # Determine their positions
            button.pos_hint = {'center_x': (scale_start + button_width / 2) + (bi * button_width), 'center_y': .5}


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
    """

    min = NumericProperty(0.)
    max = NumericProperty(0.)
    step = NumericProperty(0.)

    slider_color = ListProperty([.8, .8, .8, 1.])

    def __init__(self, question_dict: dict, **kwargs) -> None:
        super().__init__(question_dict, **kwargs)
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

        if no_notes:
            self.ids.slider_holder.size_hint_x = .95
            self.ids.left_note.size_hint_x = 0.05
            self.ids.right_note.size_hint_x = 0.05

        # Make the min and max values into integers
        self.min = float(question_dict['min'])
        self.max = float(question_dict['max'])
        self.step = float(question_dict['step'])

        if 'initial' in question_dict:
            initial = float(question_dict['initial'])
            if self.min > initial or self.max < initial:
                raise SyntaxError(f'Initial Slider value of {question_dict["id"]} '
                                  f'outside the range [{self.min}, {self.max}].')
            elif initial % self.step:
                raise SyntaxError(f'Initial Slider value of {question_dict["id"]} '
                                  f'not compatible with step size {self.step}.')

            else:
                self.value = initial
        else:
            self.value = (self.max + self.min) / 2.

    def set_value(self) -> None:
        """
        Overwrite of the set_value method to set the slider look and block when the parent is not assigned yet.
        """
        if self.parent is not None:
            self.ids.slider.value = round(self.ids.slider.value, 9)
            self.value = self.ids.slider.value
            super().set_value()

            self.slider_color = [.9 * .5, .9 * 1., .9 * .5, .9 * 1.]
            self.ids.slider.background_horizontal = 'GUI/assets/Slider_cursor_answered.png'
            self.ids.slider.cursor_image = 'GUI/assets/Slider_cursor_answered.png'


class PointCompassAQuestion(AudioQuestion):
    """
    The compass question type. Subclass of GUI.AudioQuestion.

    Parameters
    ----------
    question_dict: dict
        Dictionary with all the information to construct the question. Should include the following keys: 'id', 'text'.
    **kwargs
        Keyword arguments. These are passed on to the kivy.uix.boxlayout.BoxLayout constructor.
    """
    def __init__(self, question_dict: dict, **kwargs) -> None:
        super().__init__(question_dict, **kwargs)
        self.ids.question_text.size_hint_y = .2

    def on_parent(self, *_) -> None:
        """
        When the widget gets a parent QuestionManager, the manager is limited to only one question.
        """
        # When triggered, set the question manager to only accept one question
        if self.parent.n_question > 1:
            raise OverflowError('PointCompass question takes 2 question slots.')

        self.parent.n_max = 1
