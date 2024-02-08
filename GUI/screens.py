from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.clock import Clock


__all__ = ['PalilaScreen', 'WelcomeScreen']


class ContinueButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.locked = True
        self.background_color = [.5, .5, .5, 1.]

    def on_release(self):
        if not self.locked:
            ready = self.parent.pre_navigation()
            if ready:
                self.parent.manager.navigate_next()
        else:
            self.parent.ids.continue_lbl.text = 'Complete this screen before continuing'
            Clock.schedule_once(self.parent.reset_continue_label, 5)

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

    def pre_navigation(self):
        return True

    def reset_continue_label(self, *_):
        self.ids.continue_lbl.text = ''


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

    def pre_navigation(self):
        if not self.ids.pid_entry.disabled:
            self.manager.set_pid(self.ids.pid_entry.text)

        return True

    def check_lock(self, input_text: str):
        if input_text:
            self.reset_continue_label()
            self.ids.continue_bttn.unlock()
        else:
            self.ids.continue_bttn.lock()
