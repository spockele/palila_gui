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

from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.config import Config
from kivy.clock import Clock

from .questions import QuestionManager
from .tools import ProgressBarThread


__all__ = ['PalilaScreen', 'WelcomeScreen', 'EndScreen', 'FinalScreen', 'TimedTextScreen', 'QuestionScreen',
           'Filler', 'BackButton']


class Filler(Widget):
    """
    Empty widget to be used as a custom filler
    """
    pass


class BackButton(Button):
    """
    Button subclass with special functionality to go back
    """

    def set_arrow(self) -> None:
        """
        Set an arrow in the BackButton using the Image Widget.
        """
        self.text = ''
        self.ids.back_bttn_image.source = 'GUI/assets/arrow.png'
        self.ids.back_bttn_image.opacity = 1.


class ContinueButton(Button):
    """
    Button subclass with special functionality to continue.

    Parameters
    ----------
    **kwargs
        Keyword arguments. These are passed on to the kivy.uix.button.Button constructor.
    """
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        # Button is always locked initially
        self.disabled = True

    def set_arrow(self) -> None:
        """
        Set an arrow in the ContinueButton using the Image Widget.
        """
        self.text = ''
        self.ids.continue_bttn_image.source = 'GUI/assets/arrow.png'
        self.ids.continue_bttn_image.opacity = 1.

    def on_release(self) -> None:
        """
        Click action button to do the navigation if the button is unlocked
        """
        self.parent.manager.navigate_next()

    def unlock(self, *_) -> None:
        """
        Set the button state to unlocked
        """
        self.disabled = False
        self.parent.ids.continue_lbl.text = ''

    def lock(self, *_) -> None:
        """
        Set the button state to locked
        """
        self.disabled = True
        self.parent.ids.continue_lbl.text = 'Complete this screen before continuing'


class PalilaScreen(Screen):
    """
    Subclass of Screen that saves the previous and next screen for the ScreenManager.

    Parameters
    ----------
    previous_screen : str
        Name of the previous screen in the ScreenManager.
    next_screen : str
        Name of the next screen in the ScreenManager.
    lock : bool, optional
        Optional boolean to keep the PalilaScreen locked.
    **kwargs
        Keyword arguments. These are passed on to the kivy.uix.screenmanager.Screen constructor.

    Attributes
    ----------
    previous_screen : str
        Name of the previous screen in the ScreenManager.
    next_screen : str
        Name of the next screen in the ScreenManager.
    """
    def __init__(self, previous_screen: str, next_screen: str, lock: bool = False, **kwargs) -> None:
        super().__init__(**kwargs)
        self.previous_screen = previous_screen
        self.next_screen = next_screen

        if not lock:
            self.ids.continue_bttn.unlock()

    def reset_continue_label(self, *_) -> None:
        """
        Function to call for resetting the continue label
        """
        self.ids.continue_lbl.text = ''

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
        super().__init__(*args, lock=True, **kwargs)

        if pid_mode == 'auto':
            self.ids.pid_entry.text = 'Your participant ID is set automatically.'
            self.ids.pid_entry.disabled = True
            self.ids.continue_bttn.unlock()

        elif pid_mode == 'input':
            self.ids.pid_entry.text = ''

        else:
            raise SyntaxError('Invalid pid mode in input file.')

        self.ids.welcome.text = welcome_text

    def on_pre_leave(self) -> None:
        """
        Function setting the PID before navigating
        """
        if not self.ids.pid_entry.disabled:
            # Set the PID in case the entry box is not disabled
            self.manager.set_pid(self.ids.pid_entry.text)

    def check_lock(self, input_text: str) -> None:
        """
        Function to properly set the lock of the Continue Button with each text entry
        """
        if input_text:
            # Unlock and reset message in case text is in the box
            self.reset_continue_label()
            self.ids.continue_bttn.unlock()
        else:
            # Lock the button in case there is no text in the box
            self.ids.continue_bttn.lock()


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
        super().__init__(*args, **kwargs)
        # First readjust the continue button
        self.ids.continue_bttn.font_size = 32
        self.ids.continue_bttn.text = 'Finish\nExperiment'
        self.ids.continue_bttn.size_hint_x = .145
        self.ids.continue_bttn.pos_hint = {'x': .505, 'y': .015}
        # Create the back button and pass all information to it
        self.back_button = BackButton()
        self.back_button.pos_hint = {'right': .495, 'y': .015}
        self.back_button.size_hint = (.145, .1)
        self.back_button.text = 'Back to first\nQuestionnaire'
        # Add the button to the screen
        self.add_widget(self.back_button)

    def back_function(self, *_) -> None:
        """
        Function for the on_release of the BackButton.
        """
        # Set up the screen where this button navigates to,
        #  in order to come back without going through the whole experiment.
        going_to: PalilaScreen = self.manager.get_screen(self.previous_screen)
        going_to.set_next_screen(self.name)
        self.manager.tracker.track(self.name, back_to_main_questionnaire=True)
        # Actually navigate using the PalilaScreenManager
        self.manager.navigate_previous()

    def on_parent(self, *_) -> None:
        """
        Assigns the BackButton's on_release when this screen gets a parent.
        This is needed, because the current screen requires a parent which is not always the case.
        """
        self.back_button.on_release = self.back_function


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
        self.ids.continue_bttn.text = ''
        self.ids.continue_bttn.disabled = True
        self.ids.goodbye.text = goodbye

    def on_enter(self, *args) -> None:
        """
        Stop the timer and save results when entering this screen.
        """
        self.manager.answers.save_to_file()
        # Don't forget to unlock the escape button
        Config.set('kivy', 'exit_on_escape', '1')


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
        super().__init__(config_dict['previous'], config_dict['next'], lock=True, **kwargs)

        self.ids.intro_text.text = config_dict['text']
        if '\n' not in config_dict['text']:
            self.ids.intro_text.halign = 'center'

        self.ids.timer.max = float(config_dict['time'])
        self.timing_thread = ProgressBarThread(self.ids.timer)

        self.ids.continue_lbl.text = ''

    def on_enter(self, *_) -> None:
        """
        Start the timer and ProgressBar when entering the screen.
        """
        self.timing_thread.start()
        Clock.schedule_once(self.ids.continue_bttn.unlock, self.ids.timer.max)


class QuestionScreen(PalilaScreen):
    """
    Class that defines the question screens. Subclass of GUI.screens.PalilaScreen.

    Parameters
    ----------
    config_dict: dict

    questions: list

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
                 questions: list,
                 n_max: int,
                 state_override: bool = False,
                 **kwargs
                 ) -> None:

        self.config_dict = config_dict
        self.questions = questions

        super().__init__(self.config_dict['previous'], self.config_dict['next'], **kwargs)

        # Store the state override variable.
        self.state_override = state_override

        # Create a link to the question manager from the Kivy code.
        self.question_manager: QuestionManager = self.ids.question_manager

        # Add the questions from the list to this screen.
        for question in self.questions:
            self.question_manager.add_question(self.config_dict[question])

        # Fill up the empty space.
        for _ in range(n_max - len(self.questions)):
            self.question_manager.add_widget(Filler())

    def unlock_check(self):
        """
        Check for unlocking the continue button.
        """
        question_state = self.question_manager.get_state()

        # If all questions are answered and the audio is listened to: unlock the continue button.
        if question_state or self.state_override:
            self.reset_continue_label()
            self.ids.continue_bttn.unlock()

        else:
            # Otherwise, make sure the continue button is locked.
            self.ids.continue_bttn.lock()

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
