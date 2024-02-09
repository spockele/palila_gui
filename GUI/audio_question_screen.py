from kivy.uix.boxlayout import BoxLayout
from kivy.uix.progressbar import ProgressBar
from kivy.core.audio import SoundLoader
from kivy.lang import Builder

import threading
import time

from .screens import PalilaScreen, Filler
from . import audio_questions


__all__ = ['AudioQuestionScreen']
Builder.load_file('GUI/audio_question_screen.kv')


class ProgressBarThread(threading.Thread):
    """
    Thread subclass to manage the ProgressBar that times audio
    """
    def __init__(self, progress_bar: ProgressBar, **kwargs):
        """
        @param progress_bar: The ProgressBar object to be timed
        """
        super().__init__(**kwargs)
        self.progress_bar = progress_bar

    def run(self):
        # Set initial time
        t0 = time.time()
        dt = .1
        # Do while the time is below the max of the progress bar
        while time.time() - t0 <= self.progress_bar.max + dt:
            # Update the progress bar value
            self.progress_bar.value = time.time() - t0
            # # Hold to not overload the system
            time.sleep(dt)


class AudioManager(BoxLayout):
    """
    Class with the audio stuff for the question screen
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Temporary placeholders
        self.audio = None
        self.n_max = None
        self.thread = None

        # Initial values for the audio playback
        self.playing = False
        self.count: int = 0

    def initialise_audio(self, audio_path: str, n_max: int):
        """
        Setup audio when the file path is set in kivy
        """
        self.n_max = n_max
        self.audio = SoundLoader.load(audio_path)
        self.audio.on_stop = self.done_playing
        if self.n_max == 1:
            self.ids.txt.text = f'Listen to the audio sample\nYou can play the sample {self.n_max} time'
        else:
            self.ids.txt.text = f'Listen to the audio sample\nYou can play the sample {self.n_max} times'

    def play(self):
        """
        Function that starts the audio
        """
        if self.count < self.n_max and not self.playing:
            self.thread = ProgressBarThread(self.ids.progress)
            self.ids.progress.max = self.audio.length

            self.thread.start()
            self.audio.play()
            self.playing = True

            self.ids.bttn_image.source = 'GUI/assets/hearing.png'
            self.ids.bttn.background_color = [.5, .5, 1, 1]
            self.ids.txt.text = 'Playing sample ...'

            self.count += 1

    def done_playing(self):
        """
        on_stop function for the audio
        """
        # Terminate and reset the progress bar thread
        self.thread.join()
        self.thread = None
        # Register that no audio is playing
        self.playing = False

        remaining = self.n_max - self.count
        if remaining > 0:
            self.ids.bttn_image.source = 'GUI/assets/play.png'
            self.ids.bttn.background_color = [1, 1, 1, 1]
            if remaining == 1:
                self.ids.txt.text = f'You can replay {remaining} more time'
            else:
                self.ids.txt.text = f'You can replay {remaining} more times'
        else:
            self.ids.bttn_image.source = 'GUI/assets/done.png'
            self.ids.bttn.background_color = [.5, 1, .5, 1]
            self.ids.txt.text = ''

        if self.count == 1:
            self.parent.parent.ids.question_manager.unlock()
            self.parent.parent.unlock_check(audio_state=True, )


class QuestionManager(BoxLayout):
    """
    Class that defines and manages the question part of an audio question screen.
    """
    n_max = 2

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.n_question = 0
        self.question_dict = {}
        self.answered = {}
        self.locked = True

    def add_question(self, question_dict: dict) -> None:
        """
        Adds a question to the allocated space.
        """
        # Check if the space is full
        if self.n_question < self.n_max:
            # Add the question according to the input file
            question_type = getattr(audio_questions, f'{question_dict["type"]}Question')
            question = question_type(question_dict)

            self.question_dict[question_dict['id']] = question
            self.answered[question_dict['id']] = False
            # Add the question to the widgets
            self.add_widget(question)
            # Update the counter
            self.n_question += 1

        # Throw hands if the space is full
        else:
            raise OverflowError(f'Audio contains more than {self.n_max} questions.')

    def readjust(self, filler: bool) -> None:
        """
        Fill the empty space to avoid weird sizing of the questions.
        """
        if filler:
            # Add filler widgets in the leftover space
            for ii in range(self.n_max - self.n_question):
                self.add_widget(Filler())

    def unlock(self):
        for question in self.question_dict.values():
            question.unlock()
        self.locked = False

    def get_state(self):
        # Start a variable to store the total state
        total_state = True
        for state in self.answered.values():
            # Update the total state via the boolean "and" operator
            total_state = total_state and state

        return total_state

    def question_answered(self, question_id: str, answered: bool):
        """
        Function to set and check the state of the questions
        """
        # Firstly set the state of the question
        self.answered[question_id] = answered
        self.parent.parent.unlock_check(question_state=self.get_state() and not self.locked)


class AudioQuestionScreen(PalilaScreen):
    """
    Class that defines the overall audio question screens
    """
    def __init__(self, config_dict: dict, **kwargs):
        super().__init__(config_dict['previous'], config_dict['next'], superinit=True, **kwargs)
        self.config_dict = config_dict

        # Initialise the audio manager with the audio defined in the input file
        self.ids.audio_manager.initialise_audio(self.config_dict['filepath'], int(self.config_dict['max replays']))

        # Add the questions from the input file to the question manager
        for question in self.config_dict['questions']:
            self.ids.question_manager.add_question(self.config_dict[question])
        # Readjust the question manager after adding all questions
        self.ids.question_manager.readjust(self.config_dict['filler'])

    def on_pre_leave(self, *args):
        """
        Store the answers on leaving the screen
        """
        for qid, question in self.ids.question_manager.question_dict.items():
            # Store the answers, question by question
            self.manager.store_answer(qid, question.return_answer())

    def unlock_check(self, audio_state: bool = None, question_state: bool = None):
        """

        """
        if audio_state is None:
            audio_state = self.ids.audio_manager.count >= 1

        if question_state is None:
            question_state = self.ids.question_manager.get_state()

        if audio_state and question_state:
            # If all questions are answered and the audio is listened to: unlock the continue button
            self.reset_continue_label()
            self.ids.continue_bttn.unlock()
        else:
            # Make sure the continue button is locked if not
            self.ids.continue_bttn.lock()

