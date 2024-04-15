from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.properties import ColorProperty

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

    def __init__(self, question_dict: dict, **kwargs):
        super().__init__(**kwargs)
        self.question_dict = question_dict
        self.ids.question_text.text = question_dict['text']
        self.qid = question_dict['id']
        self.answer = None

        self.dependant = None
        self.dependant_answer_temp = None

    def set_dependant(self):
        if 'dependant' in self.question_dict:
            if 'dependant condition' not in self.question_dict:
                raise SyntaxError(f'{self.qid} does not have a "dependant condition" to unlock its dependant question.')
            else:
                self.dependant: QuestionnaireQuestion = self.parent.parent.all_questions[self.question_dict['dependant']]
                self.dependant.dependant_lock()

    def check_input(self):
        """
        Have the QuestionnaireScreen check the unlock condition.
        """
        if self.dependant is not None and self.answer == self.question_dict['dependant condition']:
            self.dependant.dependant_unlock(self.dependant_answer_temp)

        elif self.dependant is not None:
            self.dependant_answer_temp = self.dependant.answer
            self.dependant.dependant_lock()
            self.parent.answered[self.dependant.qid] = True

        self.parent.answered[self.qid] = self.answer is not None
        self.parent.parent.unlock_check()

    def border(self):
        """
        Add the top borderline to the question.
        """
        self.bordercolor = [.8, .8, .8, 1.]

    def dependant_lock(self):
        self.answer = 'n/a'
        self.disabled = True

    def dependant_unlock(self, previous_answer):
        self.answer = previous_answer
        self.check_input()
        self.disabled = False


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

    def check_input(self):
        """
        Check the full input of the TextInput before triggering the unlock check.
        """
        if self.ids.question_input.text:
            if self.ids.question_input.text.isnumeric():
                self.answer = self.ids.question_input.text
                self.ids.question_input_overlay.text = ''
                self.ids.question_input_overlay.color = [.7, .7, .7, 1.]
                self.ids.question_input.background_color = [.5, 1., .5, 1.]

            else:
                if self.answer is not None:
                    self.ids.question_input.text = self.answer
                else:
                    self.ids.question_input.text = ''
                    self.ids.question_input_overlay.color = [1., .2, .2, 1.]
                    self.ids.question_input.background_color = [1., .7, .7, 1.]

        else:
            self.answer = None
            self.ids.question_input.background_color = [1., 1., 1., 1.]
            self.ids.question_input_overlay.color = [.7, .7, .7, 1.]
            self.ids.question_input_overlay.text = 'Enter a number here.'

        super().check_input()

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
        super().dependant_lock()
        self.ids.question_input_overlay.text = ''
        self.ids.question_input_overlay.color = [.7, .7, .7, 1.]
        self.ids.question_input.background_color = [.7, 1., .7, 1.]

    def dependant_unlock(self, previous_answer):
        super().dependant_unlock(previous_answer)
        self.check_input()


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

    def check_input(self):
        """
        Check the full input of the TextInput before triggering the unlock check.
        """
        if self.ids.question_input.text:
            if len(self.ids.question_input.text.split('\n')) > 2:
                self.ids.question_input.text = self.answer

            self.answer = self.ids.question_input.text
            self.ids.question_input_overlay.text = ''
            self.ids.question_input_overlay.color = [.7, .7, .7, 1.]
            self.ids.question_input.background_color = [.5, 1., .5, 1.]

        else:
            self.answer = None
            self.ids.question_input.background_color = [1., 1., 1., 1.]
            self.ids.question_input_overlay.color = [.7, .7, .7, 1.]
            self.ids.question_input_overlay.text = 'Enter your answer here.'

        super().check_input()

    def dependant_lock(self):
        super().dependant_lock()
        self.ids.question_input_overlay.text = ''
        self.ids.question_input_overlay.color = [.7, .7, .7, 1.]
        self.ids.question_input.background_color = [.7, 1., .7, 1.]

    def dependant_unlock(self, previous_answer):
        super().dependant_unlock(previous_answer)
        self.check_input()


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
        self.ids.question_input.values = question_dict['choices']

    def check_input(self):
        """

        """
        if self.ids.question_input.text:
            self.answer = self.ids.question_input.text
            self.ids.question_input.background_color = [.5, 1., .5, 1.]
        else:
            self.answer = None
            self.ids.question_input.background_color = [1., 1., 1., 1.]

        super().check_input()

    def dependant_lock(self):
        super().dependant_lock()
        self.ids.question_input.background_color = [.7, 1., .7, 1.]

    def dependant_unlock(self, previous_answer):
        super().dependant_unlock(previous_answer)
        self.check_input()


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
            self.answer = None
        else:
            # Set the current answer to the entered button otherwise
            self.choice = choice
            self.choice.select()
            self.answer = choice.text

        super().check_input()

    def dependant_lock(self):
        super().dependant_lock()
        self.choice_temp = self.choice
        self.choice = None
        for choice in self.choices:
            choice.background_color = [.7, 1, .7, 1.]

    def dependant_unlock(self, previous_answer):
        super().dependant_unlock(previous_answer)
        for choice in self.choices:
            choice.deselect()

        self.select_choice(self.choice_temp)

