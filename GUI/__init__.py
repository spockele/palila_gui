from kivy.lang import Builder
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager

from .audio_question_screen import *
from .input_system import *


Builder.load_file('GUI/setup.kv')


class PalilaScreenManager(ScreenManager):
    """
    Subclass of kivy ScreenManager which handles the connection between the GUI and the input file system.
    """
    def __init__(self, experiment: PalilaExperiment, **kwargs):
        """
        :param experiment: An instance of PalilaExperiment containing the configuration for the ScreenManager.
        """
        super().__init__(**kwargs)
        self.experiment = experiment

        # Extract the experiment sections
        self.sections = [section for section in self.experiment.sections if 'section' in section]
        # Go about initialising the Screens based on the input file
        self._initialise_screens()

    def _initialise_screens(self):
        """
        Internal function to initialise the Screens from the PalilaExperiment instance
        """
        # Loop over the experiment sections
        for section in self.sections:
            audios = [audio for audio in self.experiment[section].sections if 'audio' in audio]
            # Within each section, loop over the audios
            for audio in audios:
                # Gather the corresponding configuration dictionary and add the general audio path of the experiment
                audio_config_dict = self.experiment[section][audio]
                audio_config_dict['filepath'] = self.experiment.audio_path
                # Create the screen and add to the Manager
                self.add_widget(AudioQuestionScreen(audio_config_dict))


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

    def build(self):
        """
        Builds the App (default App function)
        """
        # Set the screen color to a very light grey
        Window.clearcolor = (.95, .95, .95, 1)
        # Set the screen to a fixed resolution
        Window.size = (1600, 900)

        manager = PalilaScreenManager(self.experiment)

        return manager
