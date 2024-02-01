from kivy.lang import Builder
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager

from .answer_system import PalilaAnswers
from .audio_question_screen import *
from .file_system import *
from .screens import *
from .screens import *

Builder.load_file('GUI/setup.kv')


class PalilaScreenManager(ScreenManager):
    """
    Subclass of kivy ScreenManager which handles the connection between the GUI and the input file system.
    """
    def __init__(self, experiment: PalilaExperiment, answers: PalilaAnswers, **kwargs):
        """
        :param experiment: An instance of PalilaExperiment containing the configuration for the ScreenManager.
        """
        super().__init__(**kwargs)
        self.experiment = experiment
        self.answers = answers

        self.add_widget(WelcomeScreen(self.experiment['pid'], self.experiment['welcome'], '', 'questionnaire',
                                      name='welcome'))

        # Go about initialising the Screens based on the input file
        self._initialise_screens()

    def _initialise_screens(self):
        """
        Internal function to initialise the Screens from the PalilaExperiment instance
        """
        prev, nxt = self.experiment['questionnaire']['previous'], self.experiment['questionnaire']['next']
        self.add_widget(PalilaScreen(prev, nxt, name='questionnaire'))

        # Loop over the experiment parts
        for part in self.experiment['parts']:
            # Within each part, loop over the audios
            for ia, audio in enumerate(self.experiment[part]['audios']):
                # Gather the corresponding configuration dictionary and add the general audio path of the experiment
                audio_config_dict = self.experiment[part][audio]

                # Create the screen
                new_screen = AudioQuestionScreen(audio_config_dict, name=f'{part}-{audio}')

                self.add_widget(new_screen)

            # End the final questionnaire if it is present
            prev, nxt = self.experiment[part]['questionnaire']['previous'], self.experiment[part]['questionnaire']['next']
            self.add_widget(PalilaScreen(prev, nxt, name=f'{part}-questionnaire'))

        self.add_widget(PalilaScreen('', '', name='end'))

    def navigate_next(self):
        self.current = self.current_screen.next_screen

    def navigate_previous(self):
        self.current = self.current_screen.previous_screen

    def set_pid(self, pid: str):
        return self.answers.set_pid(pid)

    def store_answer(self, key: str, value):
        self.answers.out.loc['response', key] = value
        print(self.answers.out)


class PalilaApp(App):
    """
    Subclass of kivy App for the customisation needed for the GUI
    """
    def __init__(self, experiment_name: str, **kwargs):
        """
        :param experiment_name: name of the experiment configuration file (without the .palila extension
        """
        super().__init__(**kwargs)

        # Load the experiment from the file
        self.experiment = PalilaExperiment(experiment_name)
        self.answers = PalilaAnswers(self.experiment)

    def build(self):
        """
        Builds the App (default App function)
        """
        # Set the screen color to a very light grey
        Window.clearcolor = (.95, .95, .95, 1)
        # Set the screen to a fixed resolution
        Window.fullscreen = 'auto'

        # Create the ScreenManager and pass the experiment along
        manager = PalilaScreenManager(self.experiment, self.answers)

        # Required return of the ScreenManager
        return manager

    def on_stop(self):
        self.answers.out.to_csv(self.answers.out_path)
