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
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget

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
    """

    bordercolor = ColorProperty([0., 0., 0., 0.])

    text_width = NumericProperty(.455)
    answer_width = NumericProperty(.545)

    def __init__(self, question_dict: dict, **kwargs) -> None:
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
        """
        Change the answer related to this question.

        Parameters
        ----------
        answer : str
            String form of the answer to store in the answering system.
        """
        # ==============================================================================================================
        # Code for the original dependency system to check if the dependent question should be unlocked
        # todo: DEPRECATED CODE
        # ---------------------
        if self.dependant is not None:
            if answer == self.question_dict['dependant condition']:
                self.dependant.dependant_unlock()

            else:
                self.dependant.dependant_lock()
        # ==============================================================================================================

        # Code for the new dependency system to check if the dependent question(s) should be unlocked
        # Loop over all dependent questions
        for question in self.dependants:
            # Check if the unlock condition of this dependent question is met.
            # Also ensure this does not happen with this question disabled. Otherwise, undesired unlocks will happen.
            if any(a in question.unlock_condition.split(';') for a in answer.split(';')) and not self.disabled:
                # Unlock the dependant question.
                question.dependant_unlock()
            else:
                # Under all other conditions, lock the dependent question again.
                question.dependant_lock()

        # Communicate with the question manager
        self.parent.change_answer(self.qid, answer)

    def set_unlock(self) -> None:
        """
        Add this question to the dependents list of the 'unlocked by' question.
        """
        if self.unlock_condition is not None:
            # Add this question to that question's dependents list
            self.parent.questions[self.question_dict['unlocked by']].assign_dependant(self)
            # Lock this question
            self.dependant_lock()

    def assign_dependant(self, question) -> None:
        """
        Assign the given question as a dependent.

        Parameters
        ----------
        question : AudioQuestion
            The question to add to the list of dependant questions.
        """
        self.dependants.append(question)

    # ==================================================================================================================
    # todo: DEPRECATED CODE
    # ---------------------
    def set_dependant(self) -> None:
        """
        Add the dependent question to the variable to manage it.
        """
        if 'dependant' in self.question_dict:
            if 'dependant condition' not in self.question_dict:
                raise SyntaxError(f'{self.qid} does not have a "dependant condition" to unlock its dependant question.')
            else:
                self.dependant: QuestionnaireQuestion = self.parent.questions[self.question_dict['dependant']]
                self.dependant.dependant_lock()
    # ==================================================================================================================

    def dependant_lock(self) -> None:
        """
        Lock this question when it is locked by another question.
        """
        # Check if there is already a temporary answer
        if not self.answer_temp:
            # If not, set the current answer as the temporary stored one
            to_store = self.parent.answers[self.qid]
            self.answer_temp = '' if to_store == 'n/a' else to_store

        # Change the answer for this question to 'n/a' to indicate it does not have to be answered.
        self.change_answer('n/a')
        # Disable this question in Kivy
        self.disabled = True

    def dependant_unlock(self) -> None:
        """
        Unlock this question when it is locked by another question.
        """
        # Enable this question in Kivy
        self.disabled = False
        # Change the answer for this question to the one that is temporarily stored.
        self.change_answer(self.answer_temp)
        # Change the temporary answer back to empty
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

    def on_touch_down(self, touch) -> None:
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

    def __init__(self, question_dict: dict, **kwargs) -> None:
        super().__init__(question_dict, **kwargs)
        self.ids.spinner.values = question_dict['choices']

    def spinner_input(self) -> None:
        """
        Function triggered by input in the Spinner widget.
        Checks the full input before changing the answer.
        """
        # Make the spinner green.
        self.ids.spinner.background_color = [.5, 1., .5, 1.]
        # Store the answer.
        self.change_answer(self.ids.spinner.text)

    def dependant_lock(self) -> None:
        """
        Lock this question when it is locked by another question.
        """
        super().dependant_lock()
        self.ids.spinner.background_color = [.7, 1., .7, 1.]

    def dependant_unlock(self) -> None:
        """
        Unlock this question when it is locked by another question.
        """
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
    buttons : list[QuestionnaireChoiceButton]
        List of the available choice buttons
    choice : QuestionnaireChoiceButton = None
        Currently selected choice button
    """

    def __init__(self, question_dict: dict, **kwargs) -> None:
        super().__init__(question_dict, **kwargs)
        self.choice = None
        self.choice_temp = None

        # Add every choice as a button and track their word lengths
        self.buttons = []
        lengths = []
        for choice in question_dict['choices']:
            choice_button = QuestionnaireChoiceButton(choice)
            self.buttons.append(choice_button)
            self.ids.question_input.add_widget(choice_button)
            lengths.append(len(choice))

        # Resize the buttons proportional to the square root of the word lengths.
        total = sum(lengths)
        for ii, length in enumerate(lengths):
            self.buttons[ii].size_hint_x = length ** .5 / total

    def select_choice(self, choice: QuestionnaireChoiceButton) -> None:
        """
        Sets the current answer, based on the input ChoiceButton.

        Parameters
        ----------
        choice : QuestionnaireChoiceButton
            The button that has been selected.
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

    def dependant_lock(self) -> None:
        """
        Lock this question when it is locked by another question.
        """
        if self.choice_temp is None:
            self.choice_temp = self.choice
        self.choice = None

        for choice in self.buttons:
            choice.background_color = [.7, 1, .7, 1.]

        super().dependant_lock()

    def dependant_unlock(self) -> None:
        """
        Unlock this question when it is locked by another question.
        """
        for choice in self.buttons:
            choice.deselect()

        if self.choice_temp is not None:
            self.select_choice(self.choice_temp)
            self.choice_temp = None

        super().dependant_unlock()


class MultiMultipleChoiceQQuestion(QuestionnaireQuestion):
    """
    Question type for multiple choice, multiple answer.
    TODO: figure out a way to merge this with MultipleChoiceQQuestion.

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
        self.choices = []
        self.choice_temp = None

        # Add every choice as a button and track their word lengths
        self.buttons = []
        lengths = []
        for choice in question_dict['choices']:
            choice_button = QuestionnaireChoiceButton(choice)
            self.buttons.append(choice_button)
            self.ids.question_input.add_widget(choice_button)
            lengths.append(len(choice))

        # Resize proportional to the root of the word lengths
        total = sum(lengths)
        for ii, length in enumerate(lengths):
            self.buttons[ii].size_hint_x = length ** .5 / total

    def select_choice(self, choice: QuestionnaireChoiceButton) -> None:
        """
        Question triggered by pressing a QuestionnaireChoiceButton.

        Parameters
        ----------
        choice : QuestionnaireChoiceButton
        """
        if choice in self.choices:
            # Deselect the currently selected button if it has already been chosen
            choice.deselect()
            self.choices.remove(choice)

        else:
            # Set the current answer to the entered button otherwise
            choice.select()
            self.choices.append(choice)

        # Fill out the answer string again.
        answer_str = ''
        for button in self.choices:
            answer_str += f'{button.text};'

        # Store this change in answer
        self.change_answer(answer_str[:-1])

    def dependant_lock(self) -> None:
        """
        Lock this question when it is locked by another question.
        """
        # Store the currently selected answers
        if self.choice_temp is None:
            self.choice_temp = self.choices

        # Reset the choices variable
        self.choices = None

        # Make all the choice buttons green
        for choice in self.buttons:
            choice.background_color = [.7, 1, .7, 1.]

        # Do the superclass actions
        super().dependant_lock()

    def dependant_unlock(self) -> None:
        """
        Unlock this question when it is locked by another question.
        """
        # Reset all choice buttons
        for choice in self.buttons:
            choice.deselect()

        # Start with a fresh choices list
        self.choices = []
        # Only fill it in case there were answers previously
        if self.choice_temp is not None:
            # Loop over the temp answers store
            for choice in self.choice_temp:
                # Select the choice button
                self.select_choice(choice)

            # Clear the temp variable
            self.choice_temp = None

        # Do the superclass actions
        super().dependant_unlock()
