from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager

from GUI import AudioQuestionScreen


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


if __name__ == '__main__':
    PalilaApp().run()
