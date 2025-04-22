"""
Module containing all code for the Audio Question screens.
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

from kivy.properties import NumericProperty, ListProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.core.audio import SoundLoader
import os

from .tools import ProgressBarThread
from .screens import QuestionScreen
from .questions import *


__all__ = ['AudioQuestionScreen', ]


class AudioQuestionScreen(QuestionScreen):
    """
    Class that defines the overall audio question screens. Subclass of GUI.screens.QuestionScreen.

    Parameters
    ----------
    config_dict : dict
        Dictionary that defines the audio and related questions.
    demo : bool, optional
        Set this screen up as the demonstration to show participants. Defaults to False.
    state_override: bool, optional (default=False)

    **kwargs
        Keyword arguments. These are passed on to the .screens.PalilaScreen constructor.

    Attributes
    ----------
    config_dict : dict
        Dictionary that defines the audio and related questions.
    audio_manager_left : AudioManagerLeft
        The primary instance of AudioManager linked to this specific screen.
    audio_manager_right : AudioManagerLeft
        The secondary instance of AudioManager linked to this specific screen.
    question_manager : AQuestionManager
        The instance of QuestionManager linked to this specific screen.
    audio_playing : bool
        Switch indicating that audio replay should be blocked.
    """

    demo_dict = {'previous': '',
                 'next': 'welcome',
                 'filepath': os.path.abspath('GUI/assets/tone500Hz.wav'),
                 'max replays': '1',
                 'questions': ['question 1', ],
                 'question 1': {'type': 'IntegerScale', 'multi': False,
                                'text': 'This screen is a demonstration.\nSelect a number on the scale:',
                                'min': '0', 'max': '7', 'id': 'demo'},
                 }

    def __init__(self,
                 config_dict: dict,
                 demo: bool = False,
                 state_override: bool = False,
                 **kwargs
                 ) -> None:

        self.demo = demo
        config_dict = config_dict if not self.demo else self.demo_dict

        super().__init__(config_dict, config_dict['questions'], 2, state_override=state_override, lock=True, **kwargs)

        # Get better references to the audio and question managers
        self.audio_manager_left: AudioManagerLeft = self.ids.audio_manager_left
        self.audio_manager_right: AudioManagerRight = AudioManagerRight()

        # Initialise the audio managers with the audios defined in the input file
        self.audio_manager_left.initialise_manager(self.config_dict['filepath'],
                                                   int(self.config_dict['max replays']), self)

        # Add the second audio manager if a second audio file is given, otherwise just leave it alone.
        if 'filepath_2' in self.config_dict:
            self.ids.audio_managers.add_widget(self.audio_manager_right)
            self.ids.audio_managers.size_hint_x = 1.
            self.audio_manager_right.initialise_manager(self.config_dict['filepath_2'],
                                                        int(self.config_dict['max replays']), self)
            self.audio_manager_right.active = True
            self.ids.extra_message.text = 'Listen to both samples at least once before answering the question.'

        self.audio_playing = False

    def on_pre_leave(self, *args) -> None:
        """
        Store the answers when leaving the screen.
        """
        # Do not store answers if this screen is in demo mode
        if self.demo:
            return

        else:
            super().on_pre_leave(*args)

            if int(self.config_dict['max replays']) > 1:
                if self.audio_manager_right.active:
                    self.manager.store_answer(f'{self.config_dict["part-audio"]}-replays-left',
                                              str(self.audio_manager_left.count))
                    self.manager.store_answer(f'{self.config_dict["part-audio"]}-replays-right',
                                              str(self.audio_manager_right.count))
                else:
                    self.manager.store_answer(f'{self.config_dict["part-audio"]}-replays',
                                              self.audio_manager_left.count)

    def unlock_check(self) -> None:
        """
        Check whether the continue button can be unlocked.
        """
        audio_state_left = self.audio_manager_left.count >= 1
        audio_state_right = not self.audio_manager_right.active or self.audio_manager_right.count >= 1
        audio_state = audio_state_left and audio_state_right

        if (audio_state or self.state_override) and not self.audio_playing:
            self.question_manager.unlock()
            self.ids.extra_message.text = ''

            super().unlock_check()

        else:
            self.ids.continue_bttn.lock()


class AudioManager(BoxLayout):
    """
    Subclass of kivy.uix.boxlayout.BoxLayout, which manages the audio of the AudioQuestionScreen.

    Parameters
    ----------
    **kwargs
        Keyword arguments. These are passed on to the kivy.uix.boxlayout.BoxLayout constructor.

    Attributes
    ----------
    audio : kivy.core.audio.Sound
        The audio of the AudioQuestionScreen, in the form of a kivy.core.audio.Sound instance. Initialised as None.
    n_max : int
        The maximum number of replays. Initialised as None.
    thread : .threaded_tools.ProgressBarThread
        The threading instance linked to the ProgressBar to make it dynamic. Initialised as None.
    count : int
        Integer that keeps track of the times the audio has been played.
    parent_screen : AudioQuestionScreen
        Screen on which this manager is present.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        # Temporary placeholders
        self.audio = None
        self.n_max = None
        self.thread = None

        # Initial values for the audio playback
        self.count = 0

        self.parent_screen = None

    def initialise_manager(self, audio_path: str, n_max: int, parent_screen: AudioQuestionScreen) -> None:
        """
        Set up the AudioManager once the necessary information is available.

        Parameters
        ----------
        audio_path : str
            Full path to the audio file.
        n_max : int
            The maximum number of replays that will be allowed.
        parent_screen : AudioQuestionScreen
            The screen of which this manager is part. To avoid endless .parent.parent chains.
        """
        self.n_max = n_max
        self.audio = SoundLoader.load(audio_path)
        self.audio.on_stop = self._done_playing
        # Set the text next to the play button
        if self.n_max == 1:
            self.ids.txt.text = f'Listen to this audio sample\nYou can play this sample {self.n_max} time'
        else:
            self.ids.txt.text = f'Listen to this audio sample\nYou can play this sample {self.n_max} times'

        self.parent_screen = parent_screen

    def play(self) -> None:
        """
        Function that starts the audio.
        """
        # Check the count and if audio is already playing
        if self.count < self.n_max and not self.parent_screen.audio_playing:
            # Set up the ProgressBarThread and the corresponding bar
            self.thread = ProgressBarThread(self.ids.progress)
            self.ids.progress.max = self.audio.length
            # Start the thread, audio and set the playing boolean
            self.thread.start()
            self.audio.play()
            self.parent_screen.audio_playing = True
            self.parent_screen.unlock_check()
            # Reflect the audio playing in the play button and text
            self.ids.bttn_image.source = 'GUI/assets/hearing.png'
            self.ids.bttn.background_color = [.5, .5, 1, 1]
            self.ids.txt.text = 'Playing sample ...'
            # Up the count
            self.count += 1

    def _done_playing(self) -> None:
        """
        on_stop function for the audio.
        """
        # Terminate and reset the progress bar thread
        self.thread.join()
        self.thread = None
        # Register that no audio is playing
        self.parent_screen.audio_playing = False
        # Check the remaining replay allowance
        remaining = self.n_max - self.count
        # If there is allowance left
        if remaining > 0:
            # Reset the play button
            self.ids.bttn_image.source = 'GUI/assets/play.png'
            self.ids.bttn.background_color = [1, 1, 1, 1]
            # Set the corresponding text next to the button
            if remaining == 1:
                self.ids.txt.text = f'You can replay this sample {remaining} time'
            else:
                self.ids.txt.text = f'You can replay this sample {remaining} times'
        # Otherwise reflect running out of replays in the button and text
        else:
            self.ids.bttn_image.source = 'GUI/assets/done.png'
            self.ids.bttn.background_color = [.5, 1, .5, 1]
            self.ids.txt.text = ''

        # Unlock the rest of the screen when the audio has been played
        self.parent_screen.unlock_check()


class AudioManagerLeft(AudioManager):
    """
    Subclass of GUI.AudioManager for the default one on the left side of the AudioQuestionScreen.
    """
    pass


class AudioManagerRight(AudioManager):
    """
    Subclass of GUI.AudioManager for the optional second one on the right side of the AudioQuestionScreen.
    """
    active = False
    pass


class AQuestionManager(QuestionManager):
    """
    Subclass of kivy.uix.boxlayout.BoxLayout that defines and manages the question part of an AudioQuestionScreen.

    Parameters
    ----------
    **kwargs
        Keyword arguments. These are passed on to the kivy.uix.boxlayout.BoxLayout constructor.

    Attributes
    ----------
    questions : dict[str, QQuestion]
        Dictionary that links the question IDs to the questions.
    answers : dict[str, str]
        Dictionary that stores the answers linked to question IDs.
    """
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        # By default, disable this widget in Kivy
        self.disabled = True

    @staticmethod
    def question_class_from_type(question_type: str) -> type:
        """
        Obtain the type definition of a question type for the add_question function.

        Parameters
        ----------
        question_type: str
            Name of the question type from a question_dict.
        """
        return globals()[f'{question_type}AQuestion']


class AudioQuestion(Question):
    """
    Class to manage the general functions of a question. Subclass of GUI.questions.Question.
    """
    value = NumericProperty(0.)
    text = StringProperty('')


class TextAQuestion(AudioQuestion):
    """
    Question type which only displays text. Subclass of GUI.AudioQuestion.

    Parameters
    ----------
    question_dict: dict
        Dictionary with all the information to construct the question. Should include the following keys: 'id', 'text'.
    **kwargs
        Keyword arguments. These are passed on to the kivy.uix.boxlayout.BoxLayout constructor.
    """
    def __init__(self, question_dict: dict, **kwargs) -> None:
        super().__init__(question_dict, **kwargs)
        self.ids.question_text.valign = 'center'


class ButtonAQuestion(ButtonQuestion, AudioQuestion):
    """
    General class for questions involving buttons. Subclass of GUI.ButtonQuestion and GUI.AudioQuestion.
    """
    def __init__(self, question_dict: dict, **kwargs):
        super().__init__(question_dict, **kwargs)

        # Increase the button text font size.
        for button in self.buttons:
            button.font_size = 42


class MultipleChoiceAQuestion(ButtonAQuestion):
    """
    Question type for multiple choice. Subclass of GUI.ButtonAQuestion.
    """
    pass


class IntegerScaleAQuestion(ButtonAQuestion):
    """
    Numerical scale question type. Subclass of GUI.AudioQuestion.

    Parameters
    ----------
    question_dict: dict
        Dictionary with all the information to construct the question.
        Should include the following keys: 'id', 'text', 'min', 'max'. Optional keys: 'left note', 'right note'.
    **kwargs
        Keyword arguments. These are passed on to the kivy.uix.boxlayout.BoxLayout constructor.
    """
    def __init__(self, question_dict: dict, **kwargs) -> None:
        # Make the min and max values into integers
        self.min = int(question_dict['min'])
        self.max = int(question_dict['max'])

        # Make the question dict compatible with the superclass requirements
        question_dict['choices'] = [str(num) for num in range(self.min, self.max + 1)]
        super().__init__(question_dict, **kwargs)

        # Create variable to detect the presence of the edge notes
        no_notes = True
        # Add the left side note if there is one
        if 'left note' in question_dict.keys():
            if '\n' in question_dict['left note']:
                question_dict['left note'] = question_dict['left note'].replace('\t', '')
            self.ids.left_note.text = question_dict['left note']
            no_notes = False
        # Add the right side note if there is one
        if 'right note' in question_dict.keys():
            if '\n' in question_dict['right note']:
                question_dict['right note'] = question_dict['right note'].replace('\t', '')
            self.ids.right_note.text = question_dict['right note']
            no_notes = False

        # Set up the scale size, according to the presence of edge notes
        if no_notes:
            scale_width = .95
            scale_start = .025
            self.ids.scale_bar.size_hint = (.95, .2)
        else:
            scale_width = .81
            scale_start = .095

        # Determine the number of buttons and their width
        n_button = self.max - self.min + 1
        button_width = scale_width / n_button

        # Add buttons at integer intervals
        for bi, button in enumerate(self.buttons):
            # Set the x and y size of the buttons (specific to 16:10 aspect ratio)
            button.size_hint_x = .75 * (button_width ** .95)
            button.size_hint_y = .75 * (button_width ** .95) * 9
            # Determine their positions
            button.pos_hint = {'center_x': (scale_start + button_width / 2) + (bi * button_width), 'center_y': .5}


class AnnoyanceAQuestion(IntegerScaleAQuestion):
    """
    Question with an 11-point annoyance scale. Subclass of GUI.audio_screen.IntegerScaleAQuestion.

    Parameters
    ----------
    question_dict: dict
        Dictionary with all the information to construct the question.
        Should include the following keys: 'id'
    **kwargs
        Keyword arguments. These are passed on to the kivy.uix.boxlayout.BoxLayout constructor.

    """
    def __init__(self, question_dict: dict, **kwargs) -> None:
        if not question_dict['text']:
            question_dict['text'] = 'What number from 0 to 10 best describes how much you are\n'\
                                    'bothered, disturbed or annoyed by the presented noise?'
        question_dict['min'] = 0
        question_dict['max'] = 10
        question_dict['left note'] = 'Not at all'
        question_dict['right note'] = 'Extremely'

        super().__init__(question_dict, **kwargs)


class SpinnerAQuestion(SpinnerQuestion, AudioQuestion):
    pass


class SliderAQuestion(AudioQuestion):
    """
    Numerical scale type question with a slider instead of buttons for a more granular answer.

    Parameters
    ----------
    question_dict: dict
        Dictionary with all the information to construct the question.
        Should include the following keys: 'id', 'text', 'min', 'max'. 'step'. Optional keys: 'left note', 'right note'.
    **kwargs
        Keyword arguments. These are passed on to the kivy.uix.boxlayout.BoxLayout constructor.

    Attributes
    ----------
    min : NumericProperty
        Minimum value of the slider.
    max : NumericProperty
        Maximum value of the slider.
    step : NumericProperty
        Step size of the slider.
    slider_color : ListProperty
        Color of the slider to indicate its answer state.
    answered : bool
        Indication of the slider state.
    """

    min = NumericProperty(0.)
    max = NumericProperty(0.)
    step = NumericProperty(0.)

    slider_color = ListProperty([.8, .8, .8, 1.])

    def __init__(self, question_dict: dict, **kwargs) -> None:
        super().__init__(question_dict, **kwargs)
        # Create variable to detect the presence of the edge notes
        no_notes = True
        # Add the left side note if there is one
        if 'left note' in question_dict.keys():
            if '\n' in question_dict['left note']:
                question_dict['left note'] = question_dict['left note'].replace('\t', '')
            self.ids.left_note.text = question_dict['left note']
            no_notes = False
        # Add the right side note if there is one
        if 'right note' in question_dict.keys():
            if '\n' in question_dict['right note']:
                question_dict['right note'] = question_dict['right note'].replace('\t', '')
            self.ids.right_note.text = question_dict['right note']
            no_notes = False

        # Adjust the slider size when no side notes are present.
        if no_notes:
            self.ids.slider_holder.size_hint_x = .95
            self.ids.left_note.size_hint_x = 0.05
            self.ids.right_note.size_hint_x = 0.05

        # Make the min and max values into integers
        self.min = float(question_dict['min'])
        self.max = float(question_dict['max'])
        self.step = float(question_dict['step'])

        # Adjust the initial position of the slider according to the input file
        if 'initial' in question_dict:
            # Extract the initial value
            initial = float(question_dict['initial'])
            # Check if the value is valid for the slider setup
            if self.min > initial or self.max < initial:
                raise SyntaxError(f'Initial Slider value of {question_dict["id"]} '
                                  f'outside the range [{self.min}, {self.max}].')
            elif initial % self.step:
                raise SyntaxError(f'Initial Slider value of {question_dict["id"]} '
                                  f'not compatible with step size {self.step}.')

            # In case it is valid, set it
            else:
                self.value = initial

        else:
            # If no initial value is given, set the slider to the middle
            self.value = (self.max + self.min) / 2.

        # Initialise the answer state to False
        self.answered = False

    def slider_input(self) -> None:
        """
        Function to be triggered when the slider is changed.
        """
        # Avoid issues during the initialisation of the GUI
        if self.parent is None:
            return

        # Round the value on the slider to be workable
        self.ids.slider.value = round(self.ids.slider.value, 9)
        # Communicate the value to the backend
        self.change_answer(str(self.ids.slider.value))

        # Change the slider look to indicate it has been answered.
        self.slider_color = [.9 * .5, .9 * 1., .9 * .5, .9 * 1.]
        self.ids.slider.background_horizontal = 'GUI/assets/Slider_cursor_answered.png'
        self.ids.slider.cursor_image = 'GUI/assets/Slider_cursor_answered.png'

        self.answered = True

    def dependant_lock(self) -> None:
        """
        Lock this question when it is locked by another question.
        """
        self.slider_color = [.9 * .5, .9 * 1., .9 * .5, .9 * 1.]
        # Change the slider look
        self.ids.slider.background_disabled_horizontal = 'GUI/assets/Slider_background_locked.png'
        self.ids.slider.cursor_disabled_image = 'GUI/assets/Slider_cursor_locked.png'

        super().dependant_lock()

    def dependant_unlock(self) -> None:
        """
        Lock this question when it is locked by another question.
        """
        # Change the slider look to indicate if it has been answered.
        if self.answered:
            self.slider_color = [.9 * .5, .9 * 1., .9 * .5, .9 * 1.]
        else:
            self.slider_color = [1., 1., 1., 1.]

        # Reset the slider look
        self.ids.slider.background_disabled_horizontal = 'GUI/assets/Slider_background_disabled.png'
        self.ids.slider.cursor_disabled_image = 'GUI/assets/Slider_cursor_disabled.png'

        super().dependant_unlock()
