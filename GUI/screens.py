from kivy.uix.screenmanager import Screen


__all__ = ['PalilaScreen', 'WelcomeScreen']


class PalilaScreen(Screen):
    """
    Subclass of Screen that saves the previous and next screen for the ScreenManager
    """
    def __init__(self, previous_screen: str, next_screen: str, **kwargs):
        super().__init__(**kwargs)
        self.previous_screen = previous_screen
        self.next_screen = next_screen


class WelcomeScreen(PalilaScreen):
    def __init__(self, pid_mode: str, welcome_text: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if pid_mode == 'auto':
            self.ids.pid_entry.text = 'Your participant ID is set automatically.'
            self.ids.pid_entry.disabled = True

        elif pid_mode == 'input':
            self.ids.pid_entry.text = ''

        else:
            raise SyntaxError('Invalid pid mode in input file.')

        self.ids.welcome.text = welcome_text

    def on_leave(self, *args):
        if not self.ids.pid_entry.disabled:
            pid_set = self.manager.set_pid(self.ids.pid_entry.text)
