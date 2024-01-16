from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout

from kivy.properties import NumericProperty, StringProperty

from kivy.core.audio import SoundLoader

from kivy.lang import Builder


__all__ = ['AudioQuestionScreen']
Builder.load_file('GUI/audio_question_screen.kv')


class AudioManager(BoxLayout):
    audio_path = StringProperty('')
    n_max = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.audio = None
        self.count: int = 0

    def play(self):
        if not self.count:
            self.audio = SoundLoader.load(self.audio_path)

        if self.count < self.n_max:
            print(f'{self.audio_path}, {self.count}')
            self.audio.play()
            self.count += 1

            if self.count == self.n_max:
                self.ids.txt.text = 'Maximum number of replays reached.'


class AudioQuestionScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
