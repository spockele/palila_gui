from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.progressbar import ProgressBar
from kivy.core.audio import SoundLoader
from kivy.lang import Builder

import threading
import time
import os


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

        if self.count < self.n_max:
            self.ids.bttn_image.source = 'GUI/assets/play.png'
            self.ids.bttn.background_color = [1, 1, 1, 1]
            self.ids.txt.text = 'Press play to restart sample'
        else:
            self.ids.bttn_image.source = 'GUI/assets/done.png'
            self.ids.bttn.background_color = [.5, 1, .5, 1]
            self.ids.txt.text = 'Cannot restart sample.'


class AudioQuestionScreen(Screen):
    def __init__(self, config_dict: dict, **kwargs):
        super().__init__(**kwargs)
        self.config_dict = config_dict
        self.audio_path = os.path.join(self.config_dict['filepath'], self.config_dict['filename'])

        self.ids.audio_manager.initialise_audio(self.audio_path, int(self.config_dict['max replays']))
