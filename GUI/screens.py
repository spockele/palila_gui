from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.widget import Widget


__all__ = ['PalilaScreen', 'WelcomeScreen', 'Filler', 'BackButton']


class Filler(Widget):
    """
    Empty widget to be used as a custom filler
    """
    pass


class BackButton(Button):
    pass


class ContinueButton(Button):
    """
    Button subclass with special functionality for the continue function
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Button is always locked initially
        self.disabled = True

    def set_arrow(self):
        print(self.ids)
        self.text = ''
        self.ids.continue_bttn_image.source = 'GUI/assets/arrow.png'
        self.ids.continue_bttn_image.opacity = 1.

    def on_release(self):
        """
        Click action button to do the navigation if the button is unlocked
        """

        # Have the parent screen do its pre-navigation actions (which should return a boolean)
        # The pre-navigation should do any messaging towards the user
        ready = self.parent.pre_navigation()
        # When the screen is ready, navigate
        if ready:
            self.parent.manager.navigate_next()

    def unlock(self):
        """
        Set the button state to unlocked
        """
        self.disabled = False
        self.parent.ids.continue_lbl.text = ''

    def lock(self):
        """
        Set the button state to locked
        """
        self.disabled = True
        self.parent.ids.continue_lbl.text = 'Complete this screen before continuing'


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
        """
        Placeholder for any pre-navigation functionality of the Screen
        """
        return True

    def reset_continue_label(self, *_):
        """
        Function to call for resetting the continue label
        """
        self.ids.continue_lbl.text = ''


class WelcomeScreen(PalilaScreen):
    """
    A screen to welcome participants and set the PID
    """
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
        """
        Function setting the PID before navigating
        """
        if not self.ids.pid_entry.disabled:
            # Set the PID in case the entry box is not disabled
            self.manager.set_pid(self.ids.pid_entry.text)

        return True

    def check_lock(self, input_text: str):
        """
        Function to properly set the lock of the Continue Button with each text entry
        """
        if input_text:
            # Unlock and reset message in case text is in the box
            self.reset_continue_label()
            self.ids.continue_bttn.unlock()
        else:
            # Lock the button in case there is no text in the box
            self.ids.continue_bttn.lock()
