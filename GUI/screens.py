from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button


__all__ = ['PalilaScreen', 'WelcomeScreen']


class ContinueButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.locked = True
        self.background_color = [.5, .5, .5, 1.]

    def on_release(self):
        if not self.locked:
            self.parent.manager.navigate_next()
        else:
            self.parent.ids.continue_lbl.text = 'Complete this screen before continuing'

    def unlock(self):
        self.locked = False
        self.background_color = [1., 1., 1., 1.]

    def lock(self):
        self.locked = True
        self.background_color = [.5, .5, .5, 1.]


class PalilaScreen(Screen):
    """
    Subclass of Screen that saves the previous and next screen for the ScreenManager
    """
    def __init__(self, previous_screen: str, next_screen: str, superinit: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.previous_screen = previous_screen
        self.next_screen = next_screen

        if not superinit:
            self.ids.continue_bttn.unlock()


class WelcomeScreen(PalilaScreen):
    def __init__(self, pid_mode: str, welcome_text: str, *args, **kwargs):
        super().__init__(*args, superinit=True, **kwargs)

        if pid_mode == 'auto':
            self.ids.pid_entry.text = 'Your participant ID is set automatically.'
            self.ids.pid_entry.disabled = True
            self.ids.continue_bttn.unlock()

        elif pid_mode == 'input':
            self.ids.pid_entry.text = ''

        else:
            raise SyntaxError('Invalid pid mode in input file.')

        self.ids.welcome.text = welcome_text

    def on_leave(self, *args):
        if not self.ids.pid_entry.disabled:
            pid_set = self.manager.set_pid(self.ids.pid_entry.text)
