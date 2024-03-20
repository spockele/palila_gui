from kivy.uix.screenmanager import ScreenManager
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.properties import ColorProperty

from .screens import PalilaScreen, Filler, BackButton
from .numpad_bubble import NumPadBubble


__all__ = ['QuestionnaireScreen', ]


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

    def set_dependant(self, *_):
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


class QuestionnaireScreen(PalilaScreen):
    """
    Class that defines the overall audio question screens. Subclass of GUI.screens.PalilaScreen.

    Parameters
    ----------
    questionnaire_dict : dict
        Dictionary that defines the questionnaire and its questions.
    manager : ScreenManager
        Underlying ScreenManager to be used for adding multiple screens of this questionnaire.
    extra_screen_start : int, optional
        Place to start a new screen in the questions list.
    all_screens : list, optional
        List with all the questionnaire screens.
    **kwargs
        Keyword arguments. These are passed on to the GUI.screens.PalilaScreen constructor.

    Attributes
    ----------
    questionnaire_dict : dict
        Dictionary that defines the questionnaire and its questions.
    state_override : bool
        Override of the answering state to allow navigation between questionnaire screens.
    all_screens : list
        List with all the questionnaire screens.
    questions : list
        List of all the questions in this singular screen.
    """
    def __init__(self, questionnaire_dict: dict, manager: ScreenManager, all_questions: dict = None,
                 extra_screen_start: int = 0, all_screens: list = None, state_override: bool = False, **kwargs):
        super().__init__(questionnaire_dict['previous'], questionnaire_dict['next'], lock=True, **kwargs)

        self.questionnaire_dict = questionnaire_dict
        self.state_override = state_override
        self.all_screens = all_screens
        # Set up the dict with all questionnaire questions, in order to handle conditional questions
        self.all_questions = {} if all_questions is None else all_questions

        # Keep a count of the number of screens in this questionnaire
        if 'screen_count' not in self.questionnaire_dict.keys():
            # In case it's the first screen, set the count to 1
            self.questionnaire_dict['screen_count'] = 1
        else:
            # In case it's not the first screen, set up the back button
            # First readjust the continue button
            self.ids.continue_bttn.size_hint_x -= .065
            self.ids.continue_bttn.pos_hint = {'x': .415, 'y': .015}
            # Create the back button and pass all information to it
            back_button = BackButton()
            back_button.pos_hint = {'x': .35, 'y': .015}
            back_button.size_hint = (.0625, .1)
            back_button.on_release = manager.navigate_previous
            back_button.set_arrow()
            # Add the button to the screen
            self.add_widget(back_button)
            # Up the screen count
            self.questionnaire_dict['screen_count'] += 1

        # Start a list to store all questions in this screen
        self.questions = []
        # Split the questions according to the input file
        if self.questionnaire_dict['manual split']:
            self._manual_splitting(manager, extra_screen_start)
        else:
            self._automatic_splitting(manager, extra_screen_start)

        [question.border() for question in self.questions[:-1]]

        self.unlock_check()
        if not extra_screen_start:
            for qid, question in self.all_questions.items():
                question: QuestionnaireQuestion
                question.set_dependant()

    def _manual_splitting(self, manager: ScreenManager, extra_screen_start: int):
        """
        Split the questionnaire into screens based on a manual assignment.

        Parameters
        ----------
        manager : ScreenManager
            Underlying ScreenManager to be used for adding multiple screens of this questionnaire.
        extra_screen_start : int, optional
            Place to start a new screen in the questions list.

        Raises
        ------
        SyntaxError
            If more than 7 questions are manually assigned to this screen.
        """
        # Determine which questions to put on this screen
        to_add = [question for question in self.questionnaire_dict['questions']
                  if int(self.questionnaire_dict[question]['manual screen']) == self.questionnaire_dict['screen_count']]
        # Determine the questions that have not yet been assigned
        remaining = [question for question in self.questionnaire_dict['questions']
                     if int(self.questionnaire_dict[question]['manual screen']) > self.questionnaire_dict['screen_count']]

        # Error in case there are too many questions assigned to this screen
        if len(to_add) > 7:
            raise SyntaxError(f'In case of manual splitting, ensure no more than 7 questions per questionnaire screen.'
                              f'Currently attempting to add {len(to_add)}.')
        # Loop over 7 indices
        for qi in range(7):
            # If the end of the to_add list is passed, just fill the space
            if qi >= len(to_add):
                self.ids.questions.add_widget(Filler())
            # Otherwise
            else:
                # Gather the question, type and create the actual instance of the question
                question = to_add[qi]
                question_type = globals()[f'{self.questionnaire_dict[question]["type"]}QQuestion']
                question_instance: QuestionnaireQuestion = question_type(self.questionnaire_dict[question])
                # Add the instance to the screen and the list
                self.ids.questions.add_widget(question_instance)
                self.questions.append(question_instance)
                self.all_questions[self.questionnaire_dict[question]['id']] = question_instance

        # If there are any questions remaining, add an extra screen
        if remaining:
            self._add_extra_screen(manager, extra_screen_start)

    def _automatic_splitting(self, manager: ScreenManager, extra_screen_start: int):
        """
        Split the questionnaire into screens based on automatic assignment.

        Parameters
        ----------
        manager : ScreenManager
            Underlying ScreenManager to be used for adding multiple screens of this questionnaire.
        extra_screen_start : int, optional
            Place to start a new screen in the questions list.
        """
        # Loop over 7 indices
        for qi in range(7):
            # If the end of the questions input list is passed, just fill the space
            if qi >= len(self.questionnaire_dict['questions'][extra_screen_start:]):
                self.ids.questions.add_widget(Filler())
            # Otherwise
            else:
                # Gather the question, type and create the actual instance of the question
                question = self.questionnaire_dict['questions'][extra_screen_start:][qi]
                question_type = globals()[f'{self.questionnaire_dict[question]["type"]}QQuestion']
                question_instance: QuestionnaireQuestion = question_type(self.questionnaire_dict[question])
                # Add the instance to the screen and the list
                self.ids.questions.add_widget(question_instance)
                self.questions.append(question_instance)
                self.all_questions[self.questionnaire_dict[question]['id']] = question_instance

        # If there are any questions remaining, add an extra screen
        if len(self.questionnaire_dict['questions'][extra_screen_start:]) > 7:
            self._add_extra_screen(manager, extra_screen_start)

    def _add_extra_screen(self, manager: ScreenManager, extra_screen_start: int):
        """
        Add an extra questionnaire screen to this questionnaire.

        Parameters
        ----------
        manager : ScreenManager
            Underlying ScreenManager to be used for adding multiple screens of this questionnaire.
        extra_screen_start : int, optional
            Place to start a new screen in the questions list.
        """
        # Create the extra screen and let it do its thing
        extra_screen = QuestionnaireScreen(self.questionnaire_dict, manager, all_questions=self.all_questions,
                                           extra_screen_start=extra_screen_start + 7, all_screens=self.all_screens,
                                           state_override=self.state_override,
                                           name=self.name + f'-{self.questionnaire_dict["screen_count"]}')

        # Add it to the ScreenManager
        manager.add_widget(extra_screen)

        # Set the 'previous' of the new screen
        extra_screen.previous_screen = self.name
        # Set the 'next' of this screen
        self.next_screen = extra_screen.name
        # Set up the continue button for the multiscreen questionnaire
        self.ids.continue_bttn.set_arrow()
        self.ids.continue_bttn.unlock()
        # Override the state to allow for navigation before this screen is complete.
        self.state_override = True

    def get_state(self):
        """
        Get the completion state of this questionnaire.
        """
        # Start a variable to store the total state
        total_state = True

        # Loop over all questions
        for question_instance in self.all_questions.values():
            state = question_instance.answer is not None
            # Update the total state via the boolean "and" operator
            total_state = total_state and state

        # Return the final state or the override
        return total_state or self.state_override

    def unlock_check(self):
        """
        Check for unlocking the continue button.
        """
        if self.get_state():
            # If all questions are answered: unlock the continue button
            self.reset_continue_label()
            self.ids.continue_bttn.unlock()
        else:
            # Make sure the continue button is locked if not
            self.ids.continue_bttn.lock()

    def on_pre_leave(self, *_):
        """
        Store all answers before leaving the screen.
        """
        for question_instance in self.questions:
            if question_instance.answer is not None:
                self.manager.store_answer(question_instance.qid, question_instance.answer)

    def on_pre_enter(self, *args):
        """
        Unlock the continue button if appropriate.
        """
        self.unlock_check()
        super().on_pre_enter(*args)

    def set_next_screen(self, next_screen: str):
        """
        Set a new next screen for this screen.

        Parameters
        ----------
        next_screen: str
            The name of the new next screen
        """
        if self.all_screens is None:
            self.next_screen = next_screen
        else:
            self.all_screens[-1].next_screen = next_screen
