from kivy.uix.screenmanager import ScreenManager
from kivy.uix.boxlayout import BoxLayout

from .screens import PalilaScreen, BackButton, Filler
from . import questionnaire_questions


__all__ = ['QuestionnaireScreen', ]


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
        if all_screens is not None:
            self.all_screens.append(self)
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
                question: questionnaire_questions.QuestionnaireQuestion
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
                self.ids.question_manager.add_widget(Filler())
            # Otherwise
            else:
                # Gather the question, type and create the actual instance of the question
                question = to_add[qi]
                self.ids.question_manager.add_question(self.questionnaire_dict[question])

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
                self.ids.question_manager.add_widget(Filler())
            # Otherwise
            else:
                # Gather the question, type and create the actual instance of the question
                question = self.questionnaire_dict['questions'][extra_screen_start:][qi]
                self.ids.question_manager.add_question(self.questionnaire_dict[question])

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
        if self.all_screens is None:
            self.all_screens = [self, ]
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

    def get_state(self):
        """
        Get the completion state of this questionnaire.
        """
        # Start a variable to store the total state
        total_state = True

        # Loop over all questions
        for qid, state in self.ids.question_manager.answered.items():
            print(qid, state)
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
        print(self.all_screens)
        if self.all_screens is None:
            self.next_screen = next_screen
        else:
            self.all_screens[-1].next_screen = next_screen


class QQuestionManager(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.question_dict = {}
        self.answered = {}

    def add_question(self, question_dict: dict) -> None:
        """
        Add a questionnaire question to this question manager.
        Parameters
        ----------
        question_dict : dict
            Dictionary with all the information to construct the question.
        """
        question_type = getattr(questionnaire_questions,
                                f'{question_dict["type"]}QQuestion')
        question_instance: questionnaire_questions.QuestionnaireQuestion = question_type(question_dict)
        # Add the instance to the screen and the list
        self.add_widget(question_instance)
        self.parent.questions.append(question_instance)
        self.parent.all_questions[question_dict['id']] = question_instance

        self.question_dict[question_dict['id']] = question_instance
        self.answered[question_dict['id']] = False
