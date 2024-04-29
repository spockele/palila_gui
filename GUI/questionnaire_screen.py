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
"""
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.boxlayout import BoxLayout

from .screens import PalilaScreen, BackButton, Filler
from . import questionnaire_questions


__all__ = ['QuestionnaireScreen', 'questionnaire_setup']


# class QuestionnaireScreen(PalilaScreen):
#     """
#     Class that defines the overall audio question screens. Subclass of GUI.screens.PalilaScreen.
#
#     Parameters
#     ----------
#     questionnaire_dict : dict
#         Dictionary that defines the questionnaire and its questions.
#     manager : ScreenManager
#         Underlying ScreenManager to be used for adding multiple screens of this questionnaire.
#     extra_screen_start : int, optional
#         Place to start a new screen in the questions list.
#     all_screens : list, optional
#         List with all the questionnaire screens.
#     **kwargs
#         Keyword arguments. These are passed on to the GUI.screens.PalilaScreen constructor.
#
#     Attributes
#     ----------
#     questionnaire_dict : dict
#         Dictionary that defines the questionnaire and its questions.
#     all_screens : list
#         List with all the questionnaire screens.
#     questions : list
#         List of all the questions in this singular screen.
#     """
#     def __init__(self, questionnaire_dict: dict, manager: ScreenManager,
#                  extra_screen_start: int = 0, state_override: bool = False, **kwargs):
#         super().__init__(questionnaire_dict['previous'], questionnaire_dict['next'], lock=True, **kwargs)
#
#         self.questionnaire_dict = questionnaire_dict
#         self.state_override = state_override
#         self.question_manager: QQuestionManager = self.ids.question_manager
#
#         # Keep a count of the number of screens in this questionnaire
#         if 'screen_count' not in self.questionnaire_dict.keys():
#             # In case it's the first screen, set the count to 1
#             self.questionnaire_dict['screen_count'] = 1
#         else:
#             # In case it's not the first screen, set up the back button
#             # First readjust the continue button
#             self.ids.continue_bttn.size_hint_x -= .065
#             self.ids.continue_bttn.pos_hint = {'x': .415, 'y': .015}
#             # Create the back button and pass all information to it
#             back_button = BackButton()
#             back_button.pos_hint = {'x': .35, 'y': .015}
#             back_button.size_hint = (.0625, .1)
#             back_button.on_release = manager.navigate_previous
#             back_button.set_arrow()
#             # Add the button to the screen
#             self.add_widget(back_button)
#             # Up the screen count
#             self.questionnaire_dict['screen_count'] += 1
#
#         # Split the questions according to the input file
#         if self.questionnaire_dict['manual split']:
#             self._manual_splitting(manager, extra_screen_start)
#         else:
#             self._automatic_splitting(manager, extra_screen_start)
#
#         self.unlock_check()
#         [question.border() for question in self.question_manager.questions.values()]
#         [question.set_dependant() for question in self.question_manager.questions.values()]
#
#     def _manual_splitting(self, manager: ScreenManager, extra_screen_start: int):
#         """
#         Split the questionnaire into screens based on a manual assignment.
#
#         Parameters
#         ----------
#         manager : ScreenManager
#             Underlying ScreenManager to be used for adding multiple screens of this questionnaire.
#         extra_screen_start : int, optional
#             Place to start a new screen in the questions list.
#
#         Raises
#         ------
#         SyntaxError
#             If more than 7 questions are manually assigned to this screen.
#         """
#         # Determine which questions to put on this screen
#         to_add = [question for question in self.questionnaire_dict['questions']
#                   if int(self.questionnaire_dict[question]['manual screen']) == self.questionnaire_dict['screen_count']]
#         # Determine the questions that have not yet been assigned
#         remaining = [question for question in self.questionnaire_dict['questions']
#                      if int(self.questionnaire_dict[question]['manual screen']) > self.questionnaire_dict['screen_count']]
#
#         # Error in case there are too many questions assigned to this screen
#         if len(to_add) > 7:
#             raise SyntaxError(f'In case of manual splitting, ensure no more than 7 questions per questionnaire screen.'
#                               f'Currently attempting to add {len(to_add)}.')
#         # Loop over 7 indices
#         for qi in range(7):
#             # If the end of the to_add list is passed, just fill the space
#             if qi >= len(to_add):
#                 self.question_manager.add_widget(Filler())
#             # Otherwise
#             else:
#                 # Gather the question, type and create the actual instance of the question
#                 question = to_add[qi]
#                 self.question_manager.add_question(self.questionnaire_dict[question])
#
#         # If there are any questions remaining, add an extra screen
#         if remaining:
#             self._add_extra_screen(manager, extra_screen_start)
#
#     def _automatic_splitting(self, manager: ScreenManager, extra_screen_start: int):
#         """
#         Split the questionnaire into screens based on automatic assignment.
#
#         Parameters
#         ----------
#         manager : ScreenManager
#             Underlying ScreenManager to be used for adding multiple screens of this questionnaire.
#         extra_screen_start : int, optional
#             Place to start a new screen in the questions list.
#         """
#         # Loop over 7 indices
#         for qi in range(7):
#             # If the end of the questions input list is passed, just fill the space
#             if qi >= len(self.questionnaire_dict['questions'][extra_screen_start:]):
#                 self.question_manager.add_widget(Filler())
#             # Otherwise
#             else:
#                 # Gather the question, type and create the actual instance of the question
#                 question = self.questionnaire_dict['questions'][extra_screen_start:][qi]
#                 self.question_manager.add_question(self.questionnaire_dict[question])
#
#         # If there are any questions remaining, add an extra screen
#         if len(self.questionnaire_dict['questions'][extra_screen_start:]) > 7:
#             self._add_extra_screen(manager, extra_screen_start)
#
#     def _add_extra_screen(self, manager: ScreenManager, extra_screen_start: int):
#         """
#         Add an extra questionnaire screen to this questionnaire.
#
#         Parameters
#         ----------
#         manager : ScreenManager
#             Underlying ScreenManager to be used for adding multiple screens of this questionnaire.
#         extra_screen_start : int, optional
#             Place to start a new screen in the questions list.
#         """
#         # Create the extra screen and let it do its thing
#         extra_screen = QuestionnaireScreen(self.questionnaire_dict, manager,
#                                            extra_screen_start=extra_screen_start + 7,
#                                            state_override=self.state_override,
#                                            name=self.name + f'-{self.questionnaire_dict["screen_count"]}')
#
#         # Add it to the ScreenManager
#         manager.add_widget(extra_screen)
#
#         # Set the 'previous' of the new screen
#         extra_screen.previous_screen = self.name
#         # Set the 'next' of this screen
#         self.next_screen = extra_screen.name
#         # Set up the continue button for the multiscreen questionnaire
#         self.ids.continue_bttn.set_arrow()
#         self.ids.continue_bttn.unlock()
#
#     def unlock_check(self, question_state: bool = None):
#         """
#         Check for unlocking the continue button.
#         """
#         if question_state is None:
#             question_state = self.question_manager.get_state()
#
#         # If all questions are answered and the audio is listened to: unlock the continue button
#         if question_state or self.state_override:
#             self.reset_continue_label()
#             self.ids.continue_bttn.unlock()
#         # Make sure the continue button is locked if not
#         else:
#             self.ids.continue_bttn.lock()
#
#     def on_pre_leave(self, *_):
#         """
#         Store all answers before leaving the screen.
#         """
#         for qid, answer in self.question_manager.answers.items():
#             self.manager.store_answer(qid, answer)
#
#     def on_pre_enter(self, *args):
#         """
#         Unlock the continue button if appropriate.
#         """
#         self.unlock_check()
#         super().on_pre_enter(*args)
#
#     def set_next_screen(self, next_screen: str):
#         """
#         Set a new next screen for this screen.
#
#         Parameters
#         ----------
#         next_screen: str
#             The name of the new next screen
#         """
#         if self.all_screens is None:
#             self.next_screen = next_screen
#         else:
#             self.all_screens[-1].next_screen = next_screen


class QuestionnaireScreen(PalilaScreen):
    """
    Class that defines the overall audio question screens. Subclass of GUI.screens.PalilaScreen.

    Parameters
    ----------
    questionnaire_dict : dict
        Dictionary that defines the questionnaire and its questions.
    **kwargs
        Keyword arguments. These are passed on to the GUI.screens.PalilaScreen constructor.

    Attributes
        ----------
        questionnaire_dict : dict
            Dictionary that defines the questionnaire and its questions.
    """

    def __init__(self, questionnaire_dict: dict, questions: list, back_function: callable = None, *args,
                 state_override: bool = False, **kwargs):

        super().__init__(*args, lock=True, **kwargs)

        self.questionnaire_dict = questionnaire_dict
        self.questions = questions

        self.state_override = state_override
        self.question_manager: QQuestionManager = self.ids.question_manager

        for question in self.questions:
            self.question_manager.add_question(self.questionnaire_dict[question])

        for _ in range(7 - len(self.questions)):
            self.question_manager.add_widget(Filler())

        if back_function is not None:
            # In case it's not the first screen, set up the back button
            # First readjust the continue button
            self.ids.continue_bttn.size_hint_x -= .065
            self.ids.continue_bttn.pos_hint = {'x': .415, 'y': .015}
            # Create the back button and pass all information to it
            back_button = BackButton()
            back_button.pos_hint = {'x': .35, 'y': .015}
            back_button.size_hint = (.0625, .1)
            back_button.on_release = back_function
            back_button.set_arrow()
            # Add the button to the screen
            self.add_widget(back_button)

        self.unlock_check()
        [question.border() for question in self.question_manager.questions.values()]
        [question.set_dependant() for question in self.question_manager.questions.values()]

    def unlock_check(self, question_state: bool = None):
        """
        Check for unlocking the continue button.
        """
        if question_state is None:
            question_state = self.question_manager.get_state()

        # If all questions are answered and the audio is listened to: unlock the continue button
        if question_state or self.state_override:
            self.reset_continue_label()
            self.ids.continue_bttn.unlock()
        # Make sure the continue button is locked if not
        else:
            self.ids.continue_bttn.lock()

    def on_pre_leave(self, *_):
        """
        Store all answers before leaving the screen.
        """
        for qid, answer in self.question_manager.answers.items():
            self.manager.store_answer(qid, answer)

    def on_pre_enter(self, *args):
        """
        Unlock the continue button if appropriate.
        """
        self.unlock_check()
        super().on_pre_enter(*args)


class QQuestionManager(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.questions = {}
        self.answers = {}

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

        self.questions[question_dict['id']] = question_instance
        self.answers[question_dict['id']] = ''

    def get_state(self):
        """
        Get the completion state of this questionnaire.
        """
        # Start a variable to store the total state
        total_state = True

        # Loop over all questions
        for qid, answer in self.answers.items():
            total_state = total_state and bool(answer)

        # Return the final state
        return total_state

    def change_answer(self, question_id: str, answer: str) -> None:
        self.answers[question_id] = answer
        self.parent.unlock_check(question_state=self.get_state() and not self.disabled)


def questionnaire_setup(questionnaire_dict: dict, manager: ScreenManager, state_override: bool,
                        part: str = 'main', ) -> None:
    """

    Parameters
    ----------
    questionnaire_dict : dict

    manager : PalilaScreenManager

    state_override : bool

    part : str

    """
    if not questionnaire_dict['screen dict']:
        manager.get_screen(questionnaire_dict['previous']).next_screen = questionnaire_dict['next']

    else:
        screen_nums = sorted(questionnaire_dict['screen dict'].keys())
        for ii, screen_num in enumerate(screen_nums):
            if ii:
                previous_screen = f'{part}-questionnaire-{ii}'
            else:
                previous_screen = questionnaire_dict['previous']

            if screen_num < max(screen_nums):
                next_screen = f'{part}-questionnaire-{ii + 2}'
            else:
                next_screen = questionnaire_dict['next']

            new_screen = QuestionnaireScreen(questionnaire_dict, questionnaire_dict['screen dict'][screen_num],
                                             manager.navigate_previous, previous_screen, next_screen,
                                             state_override=state_override,
                                             name=f'{part}-questionnaire-{ii + 1}')

            manager.add_widget(new_screen)

