"""
Module with all the code for the modular questions.
"""
from kivy.properties import NumericProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button


__all__ = ['AudioChoiceButton', 'AudioQuestion', 'TextQuestion', 'MultipleChoiceQuestion',
           'IntegerScaleQuestion', 'PointCompassQuestion'
           ]


class AudioChoiceButton(Button):
    """
    Button with ability to store a state and interact with AudioQuestion. Subclass of kivy.uix.button.Button.

    Parameters
    ----------
    text : str
        Text to be displayed on the button.
    font_size : int, optional
        Optional font size of the text. Defaults to 72.
    **kwargs : dict
        Keyword arguments. These are passed on to the kivy.uix.button.Button constructor.
    """
    def __init__(self, text: str = '', font_size: int = 72, **kwargs) -> None:
        super().__init__(text=text, **kwargs)
        self.font_size = font_size

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
    **kwargs : dict
        Keyword arguments. These are passed on to the kivy.uix.boxlayout.BoxLayout constructor.

    Attributes
    ----------
    question_dict : dict
        Dictionary with all the information to construct the question.
    qid : str
        Question ID for communication with the file system.
    answer : AudioChoiceButton = None
        Button of the currently selected answer. None in case no answer is selected.
    """
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

    def select_choice(self, choice: AudioChoiceButton) -> None:
        """
        Sets the current answer in this manager, based on the selected choice.

        Parameters
        ----------
        choice : AudioChoiceButton
            The AudioChoiceButton instance which has triggered the answer selection
        """
        # Deselect the current answer if there is one
        if self.answer is not None:
            self.answer.deselect()

        # Remove the current answer if the current answer is pressed again
        if self.answer == choice:
            self.answer = None
            # Communicate to the question manager that the question is unanswered.
            self.parent.question_answered(self.qid, False)
        # Set the current answer to the selected button otherwise
        else:
            self.answer = choice
            self.answer.select()
            # Communicate to the question manager that the question is answered.
            self.parent.question_answered(self.qid, True)


class TextQuestion(AudioQuestion):
    """
    Question type which only displays text. Subclass of GUI.AudioQuestion.

    Parameters
    ----------
    question_dict: dict
        Dictionary with all the information to construct the question. Should include the following keys: 'id', 'text'.
    **kwargs : dict
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


class MultipleChoiceQuestion(AudioQuestion):
    """
    Question type for multiple choice. Subclass of GUI.AudioQuestion.

    Parameters
    ----------
    question_dict: dict
        Dictionary with all the information to construct the question.
        Should include the following keys: 'id', 'text', 'choices'.
    **kwargs : dict
        Keyword arguments. These are passed on to the kivy.uix.boxlayout.BoxLayout constructor.
    """
    def __init__(self, question_dict: dict, **kwargs) -> None:
        super().__init__(question_dict, **kwargs)
        # Add the choices from the input file
        for choice in self.question_dict['choices']:
            button = AudioChoiceButton(choice, font_size=48)
            # self.options.append(button)
            self.ids.answer_options.add_widget(button)


class IntegerScaleQuestion(AudioQuestion):
    """
    Numerical scale question type. Subclass of GUI.AudioQuestion.

    Parameters
    ----------
    question_dict: dict
        Dictionary with all the information to construct the question.
        Should include the following keys: 'id', 'text', 'min', 'max'. Optional keys: 'left note', 'right note'.
    **kwargs : dict
        Keyword arguments. These are passed on to the kivy.uix.boxlayout.BoxLayout constructor.
    """
    def __init__(self, question_dict: dict, **kwargs) -> None:
        super().__init__(question_dict, **kwargs)
        # Add the left side note if there is one
        if 'left note' in question_dict.keys():
            self.ids.left_note.text = question_dict['left note']
        # Add the right side note if there is one
        if 'right note' in question_dict.keys():
            self.ids.right_note.text = question_dict['right note']

        # Make the min and max values into integers
        self.min = int(question_dict['min'])
        self.max = int(question_dict['max'])
        # Determine the number of buttons and their width
        n_button = self.max - self.min + 1
        button_width = .65 / n_button

        # Add buttons at integer intervals
        for bi, bv in enumerate(range(self.min, self.max + 1)):
            # Create the button and add it to the Layout
            button = AudioChoiceButton(str(bv))
            self.ids.answer_options.add_widget(button)
            # Set the x and y size of the buttons (specific to 16:10 aspect ratio)
            button.size_hint_x = .65 * (button_width ** .95)
            button.size_hint_y = .65 * (button_width ** .95) * 9
            # Determine their positions
            button.pos_hint = {'center_x': (.175 + button_width / 2) + (bi * button_width), 'center_y': .5}


class PointCompassQuestion(AudioQuestion):
    """
    The compass question type. Subclass of GUI.AudioQuestion.

    Parameters
    ----------
    question_dict: dict
        Dictionary with all the information to construct the question. Should include the following keys: 'id', 'text'.
    **kwargs : dict
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


class AnswerHolder:
    """


    Attributes
    ----------
    text : str
        Holds the answer text
    """
    def __init__(self):
        self.text: str = ''


class SliderQuestion(AudioQuestion):
    """

    Parameters
    ----------
    question_dict: dict
        Dictionary with all the information to construct the question.
        Should include the following keys: 'id', 'text', 'min', 'max'. 'step'. Optional keys: 'left note', 'right note'.

    Attributes
    ----------

    """

    value = NumericProperty(0.)
    value_normalized = NumericProperty(0.)

    min = NumericProperty(0.)
    max = NumericProperty(0.)
    step = NumericProperty(0.)

    slider_color = ListProperty([.8, .8, .8, 1.])

    def __init__(self, question_dict: dict, **kwargs) -> None:
        super().__init__(question_dict, **kwargs)
        # Add the left side note if there is one
        if 'left note' in question_dict.keys():
            self.ids.left_note.text = question_dict['left note']
        # Add the right side note if there is one
        if 'right note' in question_dict.keys():
            self.ids.right_note.text = question_dict['right note']

        # Make the min and max values into integers
        self.min = float(question_dict['min'])
        self.max = float(question_dict['max'])
        self.step = float(question_dict['step'])

        self.value = (self.max + self.min) / 2.
        self.value_normalized = self.ids.slider.value_normalized

        self.answer = AnswerHolder()

    def set_value(self, value: float, value_normalized: float) -> None:
        """

        Parameters
        ----------
        value : float
            The value passed from the slider
        value_normalized : float

        """
        if self.answer is not None:
            if not self.answer.text:
                self.parent.question_answered(self.qid, True)
                self.ids.slider.background_color = (.5, 1., .5, 1)

            value = round(value, 9)
            self.answer.text = str(value)
            self.value = value
            self.value_normalized = value_normalized

            self.slider_color = [.9 * .5, .9 * 1., .9 * .5, .9 * 1.]
            self.ids.slider.background_horizontal = 'GUI/assets/Slider_cursor_answered.png'
            self.ids.slider.cursor_image = 'GUI/assets/Slider_cursor_answered.png'
