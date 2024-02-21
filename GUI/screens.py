from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.config import Config
from kivy.clock import Clock

from .threaded_tools import ProgressBarThread


__all__ = ['PalilaScreen', 'WelcomeScreen', 'EndScreen', 'FinalScreen', 'TimedTextScreen', 'Filler', 'BackButton']


class Filler(Widget):
    """
    Empty widget to be used as a custom filler
    """
    pass


class BackButton(Button):
    """
    Button subclass with special functionality to go back
    """

    def set_arrow(self):
        """

        """
        self.text = ''
        self.ids.back_bttn_image.source = 'GUI/assets/arrow.png'
        self.ids.back_bttn_image.opacity = 1.


class ContinueButton(Button):
    """
    Button subclass with special functionality to continue
    """
    def __init__(self, **kwargs):
        """

        """
        super().__init__(**kwargs)
        # Button is always locked initially
        self.disabled = True

    def set_arrow(self):
        """

        """
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

    def unlock(self, *_):
        """
        Set the button state to unlocked
        """
        self.disabled = False
        self.parent.ids.continue_lbl.text = ''

    def lock(self, *_):
        """
        Set the button state to locked
        """
        self.disabled = True
        self.parent.ids.continue_lbl.text = 'Complete this screen before continuing'


class PalilaScreen(Screen):
    """
    Subclass of Screen that saves the previous and next screen for the ScreenManager
    """
    def __init__(self, previous_screen: str, next_screen: str, lock: bool = False, **kwargs):
        """

        """
        super().__init__(**kwargs)
        self.previous_screen = previous_screen
        self.next_screen = next_screen

        if not lock:
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

    def set_next_screen(self, next_screen: str):
        """
        Set a new next screen for this screen.

        Parameters
        ----------
        next_screen: str
            The name of the new next screen
        """
        self.next_screen = next_screen


class WelcomeScreen(PalilaScreen):
    """
    A screen to welcome participants and set the PID
    """
    def __init__(self, pid_mode: str, welcome_text: str, *args, **kwargs):
        """

        """
        super().__init__(*args, lock=True, **kwargs)

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


class EndScreen(PalilaScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # First readjust the continue button
        self.ids.continue_bttn.font_size = 32
        self.ids.continue_bttn.text = 'Finish\nExperiment'
        self.ids.continue_bttn.size_hint_x = .145
        self.ids.continue_bttn.pos_hint = {'x': .505, 'y': .015}
        # Create the back button and pass all information to it
        self.back_button = BackButton()
        self.back_button.pos_hint = {'right': .495, 'y': .015}
        self.back_button.size_hint = (.145, .1)
        self.back_button.font_size = 32
        self.back_button.text = 'Back to first\nQuestionnaire'
        # Add the button to the screen
        self.add_widget(self.back_button)

    def back_function(self, *_):
        going_to: PalilaScreen = self.manager.get_screen(self.previous_screen)
        going_to.set_next_screen(self.name)

        self.manager.navigate_previous()

    def on_parent(self, *_):
        self.back_button.on_release = self.back_function


class FinalScreen(PalilaScreen):
    def __init__(self, *args, goodbye: str, **kwargs):
        super().__init__(*args, **kwargs)
        self.ids.continue_bttn.text = ''
        self.ids.continue_bttn.disabled = True
        self.ids.goodbye.text = goodbye

    def on_enter(self, *args):
        if self.manager.experiment.name != 'gui_dev':
            self.manager.answers.stop_timer()
            self.manager.answers.save_to_file()

        Config.set('kivy', 'exit_on_escape', '1')


class TimedTextScreen(PalilaScreen):
    """

    """
    def __init__(self, intro_dict: dict, **kwargs):
        """

        """
        super().__init__(intro_dict['previous'], intro_dict['next'], lock=True, **kwargs)

        self.ids.intro_text.text = intro_dict['text']

        self.ids.timer.max = float(intro_dict['time'])
        self.timing_thread = ProgressBarThread(self.ids.timer)

        self.ids.continue_lbl.text = ''

    def on_enter(self, *_):
        """

        """
        self.timing_thread.start()
        Clock.schedule_once(self.ids.continue_bttn.unlock, self.ids.timer.max)
