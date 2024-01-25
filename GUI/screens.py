from kivy.uix.screenmanager import Screen


__all__ = ['PalilaScreen']


class PalilaScreen(Screen):
    def __init__(self, previous_screen: str, next_screen: str, **kwargs):
        super().__init__(**kwargs)
        self.previous_screen = previous_screen
        self.next_screen = next_screen
