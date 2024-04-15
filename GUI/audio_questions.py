"""
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
        self.dependant = None
        self.dependant_id = None

        self.answer_temp = ''

    def change_answer(self, answer: str):
        if self.dependant is not None:
            if answer == self.question_dict['dependant condition']:
                self.dependant.dependant_unlock()

            else:
                self.dependant.dependant_lock()

        self.parent.change_answer(self.qid, answer)

    def set_dependant(self):
        if 'dependant' in self.question_dict:
            self.dependant_id = self.question_dict['part-audio'] + self.question_dict['dependant'].zfill(2)
            if 'dependant condition' not in self.question_dict:
                raise SyntaxError(f'{self.qid} does not have a "dependant condition" to unlock its dependant question.')
            else:
                self.dependant: AudioQuestion = self.parent.question_dict[self.dependant_id]
                self.dependant.dependant_lock()

    def dependant_lock(self):
        self.answer_temp = self.parent.answers[self.qid]
        self.change_answer('n/a')
        self.disabled = True

    def dependant_unlock(self):
        self.change_answer(self.answer_temp)
        self.disabled = False


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


class ButtonAQuestion(AudioQuestion):
    def __init__(self, question_dict: dict, **kwargs) -> None:
        super().__init__(question_dict, **kwargs)
        self.buttons = []
        # Add the choices from the input file
        for choice in self.question_dict['choices']:
            button = AudioChoiceButton(choice, font_size=48)
            self.buttons.append(button)
            self.ids.answer_options.add_widget(button)

        self.choice = None
        self.choice_temp = None

    def select_choice(self, choice: AudioChoiceButton):
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
            self.change_answer(choice.text)
            self.choice.select()

    def dependant_lock(self):
        self.choice_temp = self.choice
        self.choice = None
        for button in self.buttons:
            button.background_color = [.7, 1., .7, 1.]
        super().dependant_lock()

    def dependant_unlock(self):
        for button in self.buttons:
            button.deselect()

        self.select_choice(self.choice_temp)
        super().dependant_unlock()


class MultipleChoiceAQuestion(ButtonAQuestion):
    """
    Question type for multiple choice. Subclass of GUI.ButtonAQuestion.
    """
    pass


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
        self.ids.spinner.values = question_dict['choices']

    def spinner_input(self):
        self.change_answer(self.ids.spinner.text)
        self.ids.spinner.background_color = [.5, 1., .5, 1.]

    def dependant_lock(self):
        self.ids.spinner.background_color = [.7, 1., .7, 1.]
        super().dependant_lock()

    def dependant_unlock(self):
        if self.ids.spinner.text:
            self.ids.spinner.background_color = [.5, 1., .5, 1.]
        else:
            self.ids.spinner.background_color = [1., 1., 1., 1.]
        super().dependant_unlock()


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

        question_dict['choices'] = [str(num) for num in range(self.min, self.max + 1)]
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

    def slider_input(self) -> None:
        if self.parent is None:
            return

        self.ids.slider.value = round(self.ids.slider.value, 9)
        self.change_answer(str(self.ids.slider.value))

        self.slider_color = [.9 * .5, .9 * 1., .9 * .5, .9 * 1.]
        self.ids.slider.background_horizontal = 'GUI/assets/Slider_cursor_answered.png'
        self.ids.slider.cursor_image = 'GUI/assets/Slider_cursor_answered.png'


class PointCompassAQuestion(ButtonAQuestion):
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
        question_dict['choices'] = []
        super().__init__(question_dict, **kwargs)
        self.ids.question_text.size_hint_y = .2

        self.buttons = [self.ids[widget_id] for widget_id in self.ids.keys() if 'choice' in widget_id]

    def on_parent(self, *_) -> None:
        """
        When the widget gets a parent QuestionManager, the manager is limited to only one question.
        """
        # When triggered, set the question manager to only accept one question
        if self.parent.n_question > 1:
            raise OverflowError('PointCompass question takes 2 question slots.')

        self.parent.n_max = 1
