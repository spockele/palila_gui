from kivy.uix.screenmanager import Screen


class PalilaScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.next = None
        self.previous = None

    def set_next(self, next_screen: Screen):
        self.next = next_screen

    def set_previous(self, previous_screen: Screen):
        self.previous = previous_screen
