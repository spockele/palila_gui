from kivy.lang import Builder
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager

from .audio_question_screen import *
from .input_system import *


Builder.load_file('GUI/setup.kv')


class PalilaScreenManager(ScreenManager):
    def __init__(self, experiment: PalilaExperiment, **kwargs):
        super().__init__(**kwargs)

        self.experiment = experiment
        self.sections = [section for section in self.experiment.sections if 'section' in section]

        self._organise()

    def _organise(self):
        for section in self.sections:
            audios = [audio for audio in self.experiment[section].sections if 'audio' in audio]
            for audio in audios:
                audio_config_dict = self.experiment[section][audio]
                audio_config_dict['filepath'] = self.experiment.audio_path

                self.add_widget(AudioQuestionScreen(audio_config_dict))


class PalilaApp(App):
    def __init__(self, experiment_name, **kwargs):
        super().__init__(**kwargs)

        self.experiment = PalilaExperiment(experiment_name)

    def build(self):
        Window.clearcolor = (.9, .9, .9, 1)
        Window.size = (1600, 900)

        manager = PalilaScreenManager(self.experiment)

        return manager
