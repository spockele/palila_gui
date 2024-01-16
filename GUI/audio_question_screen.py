from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.progressbar import ProgressBar
from kivy.properties import NumericProperty, StringProperty
from kivy.core.audio import SoundLoader
from kivy.lang import Builder

import threading
import time


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
    # Some variables to be set through kivy
    audio_path = StringProperty('')
    n_max = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Temporary placeholders
        self.audio = None
        self.thread = None

        # Initial values for the audio playback
        self.playing = False
        self.count: int = 0

    def on_audio_path(self, *_):
        """
        Setup audio when the file path is set in kivy
        """
        self.audio = SoundLoader.load(self.audio_path)
        self.audio.on_stop = self.done_playing

    def play(self):
        """
        Function that starts the audio
        """
        if self.count < self.n_max and not self.playing:
            print(f'{self.audio_path}, {self.count}')

            self.thread = ProgressBarThread(self.ids.progress)
            self.ids.progress.max = self.audio.length

            self.thread.start()
            self.audio.play()

            self.playing = True
            self.count += 1

            if self.count == self.n_max:
                self.ids.txt.text = 'Maximum number of replays reached.'

    def done_playing(self):
        """
        on_stop function for the audio
        """
        # Terminate and reset the progress bar thread
        self.thread.join()
        self.thread = None
        # Register that no audio is playing
        self.playing = False


class AudioQuestionScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)