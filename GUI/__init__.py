from kivy.lang import Builder
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager

from .audio_question_screen import *
from .input_system import *


Builder.load_file('GUI/setup.kv')


class PalilaScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class PalilaApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self):
        Window.clearcolor = (.9, .9, .9, 1)
        Window.size = (1600, 900)

        manager = PalilaScreenManager()
        manager.add_widget(AudioQuestionScreen())

        return manager
