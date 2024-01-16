from kivy.app import App

from GUI import AudioQuestionScreen


class PalilaApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self):
        return AudioQuestionScreen()


if __name__ == '__main__':
    PalilaApp().run()
