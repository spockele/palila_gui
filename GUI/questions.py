"""
Module with all the code for the modular questions.
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

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button


__all__ = ['QuestionManager', 'Question', 'SpinnerQuestion', 'ButtonQuestion']


class QuestionManager(BoxLayout):
    """
    Subclass of kivy.uix.boxlayout.BoxLayout that defines and manages the interaction of question front-end with the
        file systems.

    Parameters
    ----------
    **kwargs
        Keyword arguments. These are passed on to the kivy.uix.boxlayout.BoxLayout constructor.

    Attributes
    ----------
    questions : dict[str, Question]
        Dictionary that links the question IDs to the questions.
    answers : dict[str, str]
        Dictionary that stores the answers linked to question IDs.
    """
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.questions = {}
        self.answers = {}

    @staticmethod
    def question_class_from_type(question_type: str) -> type:
        """
        Obtain the type definition of a question type for the add_question function.
        OVERLOAD REQUIRED TO WORK!!

        Parameters
        ----------
        question_type: str
            Name of the question type from a question_dict.
        """
        pass

    def add_question(self, question_dict: dict) -> None:
        """
        Adds a question to the allocated space.

        Parameters
        ----------
        question_dict : dict
            Dictionary which defines the question to be added.
        """
        # Get the question type class.
        question_type = self.question_class_from_type(question_dict['type'])
        # Create the instance of it.
        question: Question = question_type(question_dict)

        # Add the question to the widgets
        self.add_widget(question)

        # Link the ID to the instance
        self.questions[question_dict['id']] = question
        # Create a spot in the answer dictionary
        self.answers[question_dict['id']] = 'n/a' if question_dict['type'] == 'Text' else ''

    def unlock(self) -> None:
        """
        Unlock this question manager.
        """
        self.disabled = False

    def get_state(self) -> bool:
        """
        Get an indication if all questions have been answered in this manager.

        Returns
        -------
        bool
            Indication if all questions have been answered in this manager.
        """
        total_state = True

        for qid, answer in self.answers.items():
            total_state = total_state and bool(answer)

        return total_state

    def change_answer(self, question_id: str, answer: str) -> None:
        """
        Update the answer of the question with the given ID.

        Parameters
        ----------
        question_id : str
            ID of the question for which to change the answer.
        answer : str
            The answer string to update to.
        """
        self.answers[question_id] = answer
        # Have the AudioQuestionScreen check the state
        self.parent.unlock_check(question_state=self.get_state() and not self.disabled)


class ChoiceButton(Button):
    """
    Button with ability to store a state and interact with Question. Subclass of kivy.uix.button.Button.

    Parameters
    ----------
    text : str
        Text to be displayed on the button.
        Optional font size of the text. Defaults to 72.
    **kwargs
        Keyword arguments. These are passed on to the kivy.uix.button.Button constructor.
    """
    def __init__(self, text: str = '', **kwargs) -> None:
        super().__init__(text=text, **kwargs)

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


class Question(BoxLayout):
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
    dependants : list[AudioQuestion]
        List of all the questions that unlock from an answer in this one.
    answer_temp : str
        Variable to temporarily store the last answer when this question is locked.
    """
    def __init__(self, question_dict: dict, **kwargs) -> None:
        super().__init__(**kwargs)
        # Store the input information
        self.question_dict = question_dict
        self.ids.question_text.text = question_dict['text']
        self.qid = question_dict['id']

        # Initialise the list of dependent questions
        # TODO: Change the spelling of 'dependants' to 'dependents'
        self.dependants: list[Question] = list()
        # If this question gets unlocked by another, set up the unlock condition
        if 'unlocked by' in question_dict:
            self.unlock_condition = question_dict['unlock condition']
        else:
            self.unlock_condition = None

        # Initialise a variable to temporarily store answers.
        self.answer_temp = ''

    def change_answer(self, answer: str) -> None:
        """
        Change the answer related to this question.

        Parameters
        ----------
        answer : str
            String form of the answer to store in the answering system.
        """
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
            # Determine the id of the question that unlocks this one
            unlocked_by_id = self.question_dict['part-audio'] + self.question_dict['unlocked by'].zfill(2)
            # Add this question to that question's dependents list
            self.parent.questions[unlocked_by_id].assign_dependant(self)
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


class SpinnerQuestion(Question):
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
        # Change the look back to its previous state, based on whether there is an answer
        if self.ids.spinner.text:
            self.ids.spinner.background_color = [.5, 1., .5, 1.]
        else:
            self.ids.spinner.background_color = [1., 1., 1., 1.]
        # Do the superclass actions
        super().dependant_unlock()


class ButtonQuestion(Question):
    """
    General class for questions involving buttons. Subclass of GUI.Question.

    Parameters
    ----------
    question_dict: dict
        Dictionary with all the information to construct the question. Should include the following keys: 'id', 'text'.
    **kwargs
        Keyword arguments. These are passed on to the kivy.uix.boxlayout.BoxLayout constructor.

    Attributes
    ----------
    buttons : list[ChoiceButton]
        List of all the buttons in this question.
    choices : list[ChoiceButton]
        Currently selected button(s).
    choice_temp : list[ChoiceButton]
        Variable to temporarily store the last selected button when this question is locked.
    """

    def __init__(self, question_dict: dict, **kwargs) -> None:
        super().__init__(question_dict, **kwargs)
        self.choices: list[ChoiceButton] = []
        self.choice_temp = None
        self.multi = question_dict['multi']

        # Add every choice as a button.
        self.buttons = []
        for choice in question_dict['choices']:
            choice_button = ChoiceButton(choice)
            self.buttons.append(choice_button)
            self.ids.answer_options.add_widget(choice_button)

    def select_choice(self, choice: ChoiceButton) -> None:
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
            if not self.multi:
                [chc.deselect() for chc in self.choices]
                self.choices = []

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
            # Store the current choice to the temporary variable, if not
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
