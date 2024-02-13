from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.lang import Builder

Builder.load_file('GUI/audio_questions.kv')


class AudioChoiceButton(Button):
    """
    Button with ability to store a state and interact with AudioQuestion
    """
    def __init__(self, text: str = '', font_size: int = 72, **kwargs):
        super().__init__(text=text, **kwargs)
        self.font_size = font_size

    def select(self) -> None:
        self.background_color = [.5, 1., .5, 1.]

    def deselect(self) -> None:
        self.background_color = [1., 1., 1., 1.]

    def on_release(self):
        self.select()
        self.parent.parent.select_choice(self)


class AudioQuestion(BoxLayout):
    """
    Class to manage the general functions of a question
    """
    def __init__(self, question_dict: dict, **kwargs):
        super().__init__(**kwargs)
        self.disabled = True
        # Store the input information
        self.question_dict = question_dict
        self.qid = question_dict['id']
        self.ids.question_text.text = question_dict['text']
        if '\n' in question_dict['text']:
            self.ids.question_text.font_size = 42
        # Initialise variable to store current answer
        self.answer = None
        self.options = []

    def select_choice(self, choice: AudioChoiceButton):
        """
        Sets the current answer, based on the input ChoiceButton
        """
        if self.answer is not None:
            # Deselect the current answer if there is one
            self.answer.deselect()

        if self.answer == choice:
            # Remove the current answer if the same button is pressed
            self.answer = None
            # Don't forget to communicate with the QuestionManager
            self.parent.question_answered(self.qid, False)
        else:
            # Set the current answer to the entered button otherwhise
            self.answer = choice
            # Don't forget to communicate with the QuestionManager
            self.parent.question_answered(self.qid, True)

    def unlock(self):
        self.disabled = False


class TextQuestion(AudioQuestion):
    """
    Question type to just display text
    """
    def __init__(self, question_dict: dict, **kwargs):
        super().__init__(question_dict, **kwargs)
        self.ids.question_text.valign = 'center'

    def on_size(self, *_):
        # Upon getting triggered, communicate to QuestionManager this one is answered
        self.parent.question_answered(self.qid, True)


class AudioMCQuestion(AudioQuestion):
    """
    Question type for multiple choice
    """
    def __init__(self, question_dict: dict, **kwargs):
        super().__init__(question_dict, **kwargs)
        # Add the choices from the input file
        for choice in self.question_dict['choices']:
            button = AudioChoiceButton(choice, font_size=48)
            self.options.append(button)
            self.ids.answer_options.add_widget(button)


class NumScaleQuestion(AudioQuestion):
    """
    Numerical scale question type
    """
    def __init__(self, question_dict: dict, **kwargs):
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
            self.options.append(button)
            self.ids.answer_options.add_widget(button)
            # Set the x and y size of the buttons (specific to 16:10 aspect ratio)
            button.size_hint_x = .65 * (button_width ** .95)
            button.size_hint_y = .65 * (button_width ** .95) * 9
            # Determine their positions
            button.pos_hint = {'center_x': (.175 + button_width / 2) + (bi * button_width), 'center_y': .5}


class PointCompassQuestion(AudioQuestion):
    """
    The compass type question
    """
    def __init__(self, question_dict: dict, **kwargs):
        super().__init__(question_dict, **kwargs)
        self.ids.question_text.size_hint_y = .2

        for widget_id in self.ids:
            if 'choice' in widget_id:
                self.options.append(self.ids[widget_id])

    def on_size(self, *_):
        # When triggered, set the question manager to only accept one question
        if self.parent.n_question > 1:
            raise OverflowError('PointCompass question takes 2 question slots.')

        self.parent.n_max = 1
