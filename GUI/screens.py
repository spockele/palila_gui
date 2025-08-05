"""
Module containing some fundamental Kivy GUI elements for the PALILA GUI.
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

from kivy.uix.screenmanager import Screen, ScreenManagerException
from kivy.uix.widget import Widget
from kivy.config import Config
from kivy.clock import Clock

from .questions import QuestionManager
from .tools import ProgressBarThread


__all__ = ['PalilaScreen', 'WelcomeScreen', 'EndScreen', 'FinalScreen', 'TimedTextScreen', 'QuestionScreen', 'Filler']


class Filler(Widget):
    """
    Empty widget to be used as a custom filler
    """
    pass


class PalilaScreen(Screen):
    """
    Subclass of Screen that saves the previous and next screen for the ScreenManager.

    Parameters
    ----------
    previous_screen : str
        Name of the previous screen in the ScreenManager.
    next_screen : str
        Name of the next screen in the ScreenManager.
    **kwargs
        Keyword arguments. These are passed on to the kivy.uix.screenmanager.Screen constructor.

    Attributes
    ----------
    previous_screen : str
        Name of the previous screen in the ScreenManager.
    next_screen : str
        Name of the next screen in the ScreenManager.
    """
    def __init__(self,
                 previous_screen: str,
                 next_screen: str,
                 back_button: bool = False,
                 **kwargs
                 ) -> None:

        super().__init__(**kwargs)
        self.previous_screen = previous_screen
        self.next_screen = next_screen

        self.back_button = back_button

    def set_next_screen(self, next_screen: str) -> None:
        """
        Set a new next screen for this screen.

        Parameters
        ----------
        next_screen: str
            The name of the new next screen
        """
        self.next_screen = next_screen


class WelcomeScreen(PalilaScreen):
    """
    A screen to welcome participants and set the PID.

    Parameters
    ----------
    pid_mode : str
        Mode for setting the Participant ID. Can be 'auto' or 'input'.
    welcome_text : str
        Text to be displayed on the welcome screen.
    *args
        Arguments for the PalilaScreen class.
    **kwargs
        Keyword arguments. These are passed on to the PalilaScreen constructor.

    Raises
    ------
    SyntaxError
        If an invalid string is passed for the PID mode.
    """

    def __init__(self, pid_mode: str, welcome_text: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        if pid_mode == 'auto':
            self.ids.pid_entry.text = 'Your participant ID is set automatically.'
            self.ids.pid_entry.disabled = True

        elif pid_mode == 'input':
            self.ids.pid_entry.text = ''
            self.ids.pid_entry.on_text = self.check_lock

        else:
            raise SyntaxError(f'Participant ID mode "pid mode = {pid_mode}" not supported!')

        self.ids.welcome.text = welcome_text

    def on_pre_leave(self) -> None:
        """
        Function setting the PID before navigating
        """
        self.manager.set_pid(self.ids.pid_entry.text)

    def on_pre_enter(self, *args):
        self.check_lock()

    def check_lock(self) -> None:
        """
        Function to properly set the lock of the Continue Button with each text entry
        """
        if self.ids.pid_entry.text:
            # Unlock in case text is in the box
            self.manager.navigation.unlock()
        else:
            # Lock the button in case there is no text in the box
            self.manager.navigation.lock()


class EndScreen(PalilaScreen):
    """
    Screen to show at the end and allow a return to the Questionnaire

    Parameters
    ----------
    *args
        Arguments for the PalilaScreen class.
    **kwargs
        Keyword arguments. These are passed on to the PalilaScreen constructor.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, back_button=True, **kwargs)

    def on_pre_enter(self, *_):
        try:
            self.manager.get_screen(self.previous_screen).set_next_screen(self.name)

            self.manager.navigation.back_button.arrow_opacity = 0
            self.manager.navigation.back_button.text = 'Back to first\nQuestionnaire'
            self.manager.navigation.back_button.pos_hint = {'right': .495}
            self.manager.navigation.back_button.size_hint_x = .145
            self.manager.navigation.back_button.font_size = 32

            self.manager.navigation.ids.continue_button.text = 'Finish\nExperiment'
            self.manager.navigation.ids.continue_button.pos_hint = {'x': .505}
            self.manager.navigation.ids.continue_button.size_hint_x = .145
            self.manager.navigation.ids.continue_button.font_size = 32

        except ScreenManagerException:
            self.back_button = False
            self.manager.navigation.reset(self.name)
            self.manager.navigation.ids.continue_button.text = 'Finish Experiment'

    def on_pre_leave(self, *_):
        self.manager.navigation.back_button.arrow_opacity = 1
        self.manager.navigation.back_button.text = ''
        self.manager.navigation.back_button.font_size = 42

        self.manager.navigation.ids.continue_button.text = 'Continue'
        self.manager.navigation.ids.continue_button.font_size = 42


class FinalScreen(PalilaScreen):
    """
    Screen to show after finishing the full experiment. This one is always locked to avoid unwanted navigation.

    Parameters
    ----------
    *args
        Arguments for the PalilaScreen class.
    goodbye : str
        Message to say goodbye to a participant.
    **kwargs
        Keyword arguments. These are passed on to the PalilaScreen constructor.
    """

    def __init__(self, *args, goodbye: str, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.ids.goodbye.text = goodbye

    def on_enter(self, *args) -> None:
        """
        Stop the timer and save results when entering this screen.
        """
        self.manager.answers.save_to_file()
        # Don't forget to unlock the escape button
        Config.set('kivy', 'exit_on_escape', '1')

    def on_pre_enter(self, *args):
        self.manager.navigation.hide()


class TimedTextScreen(PalilaScreen):
    """
    Screen for breaks and intros, which require free text and a timer.

    Parameters
    ----------
    config_dict : dict
        Dictionary with all the information to set up the screen.
    **kwargs
        Keyword arguments. These are passed on to the PalilaScreen constructor.
    """
    def __init__(self, config_dict: dict, **kwargs) -> None:
        super().__init__(config_dict['previous'], config_dict['next'], **kwargs)

        self.ids.intro_text.text = config_dict['text']
        if '\n' not in config_dict['text']:
            self.ids.intro_text.halign = 'center'

        self.ids.timer.max = float(config_dict['time'])
        self.timing_thread = ProgressBarThread(self.ids.timer)

    def on_pre_enter(self, *_):
        self.manager.navigation.lock()
        self.manager.navigation.message = 'Please wait for the timer.'

    def on_enter(self, *_) -> None:
        """
        Start the timer and ProgressBar when entering the screen.
        """
        self.timing_thread.start()
        Clock.schedule_once(self._after_timer, self.ids.timer.max)

    def _after_timer(self, *_):
        self.manager.navigation.unlock()
        self.ids.timer.opacity = 0


class QuestionScreen(PalilaScreen):
    """
    Class that defines the question screens. Subclass of GUI.screens.PalilaScreen.

    Parameters
    ----------
    config_dict: dict

    state_override: bool, optional (default=False)

    **kwargs
        Keyword arguments. These are passed on to the GUI.screens.PalilaScreen constructor.

    Attributes
    ----------
    config_dict : dict
        Dictionary that defines the elements of the QuestionScreen.
    """

    def __init__(self,
                 config_dict: dict,
                 n_max: int,
                 state_override: bool = False,
                 **kwargs
                 ) -> None:

        self.config_dict = config_dict

        super().__init__(self.config_dict['previous'], self.config_dict['next'], **kwargs)

        # Store the state override variable.
        self.state_override = state_override

        # Create a link to the question manager from the Kivy code.
        self.question_manager: QuestionManager = self.ids.question_manager

        # Add the questions from the list to this screen.
        for question in self.config_dict['questions']:
            self.question_manager.add_question(self.config_dict[question])

        # Fill up the empty space.
        for _ in range(n_max - len(self.config_dict['questions'])):
            self.question_manager.add_widget(Filler())

    def unlock_check(self):
        """
        Check for unlocking the continue button.
        """
        question_state = self.question_manager.get_state()

        # If all questions are answered and the audio is listened to: unlock the continue button.
        if question_state or self.state_override:
            self.manager.navigation.unlock()

        else:
            # Otherwise, make sure the continue button is locked.
            self.manager.navigation.lock()

    def on_pre_leave(self, *_):
        """
        Store all answers before leaving the screen.
        """
        for qid, answer in self.question_manager.answers.items():
            self.manager.store_answer(qid, answer)

    def on_pre_enter(self, *_):
        """
        Set up the dependency unlocks and do the unlock check
        """
        # Set the dependency locks for all questions, now that they are part of this screen.
        [question.set_unlock() for question in self.question_manager.questions.values()]
        self.unlock_check()
