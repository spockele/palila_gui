"""
Main module of the GUI package.

Pulls in all functions from the modules in the package. It also defines the custom ScreenManager and App classes, which
form the core of this package. Loads all the relevant kivy files for this package.
"""
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.app import App

from .audio_question_screen import *
from .questionnaire import *
from .file_system import *
from .screens import *


__all__ = ['PalilaApp', ]

Builder.load_file('GUI/audio_question_screen.kv')
Builder.load_file('GUI/audio_questions.kv')
Builder.load_file('GUI/numpad_bubble.kv')
Builder.load_file('GUI/questionnaire.kv')
Builder.load_file('GUI/setup.kv')


class PalilaScreenManager(ScreenManager):
    """
    Subclass of kivy.uix.screenmanager.ScreenManager which handles the connection between the GUI and the input file system.

    Parameters
    ----------
    experiment : PalilaExperiment
        PalilaExperiment instance to link this screen manager to.
    answers : PalilaAnswers
        PalilaAnswers instance to link this screen manager to.
    **kwargs : dict
        Keyword arguments. These are passed on to the kivy.uix.screenmanager.ScreenManager constructor.

    Attributes
    ----------
    experiment : PalilaExperiment
        The linked PalilaExperiment instance.
    answers : PalilaAnswers
        The linked PalilaAnswers instance.
    """

    def __init__(self, experiment: PalilaExperiment, answers: PalilaAnswers, **kwargs) -> None:
        super().__init__(**kwargs)
        self.experiment = experiment
        self.answers = answers

        self.add_widget(WelcomeScreen(self.experiment['pid'], self.experiment['welcome'],
                                      '', 'main-questionnaire', name='welcome'))
        self.current = 'welcome'

        # Go about initialising the Screens based on the input file
        self._initialise_screens()

    def _initialise_screens(self) -> None:
        """
        Internal function to initialise the Screens from the PalilaExperiment instance
        """
        # Add the initial questionnaire
        self.add_widget(QuestionnaireScreen(self.experiment['questionnaire'], self, name='main-questionnaire'))

        # Loop over the experiment parts
        for part in self.experiment['parts']:
            self.add_widget(PartIntroScreen(self.experiment[part]['intro'], name=f'{part}-intro'))
            # Within each part, loop over the audios
            for ia, audio in enumerate(self.experiment[part]['audios']):
                # Gather the corresponding configuration dictionary and add the general audio path of the experiment
                audio_config_dict = self.experiment[part][audio]

                # Create the screen
                self.add_widget(AudioQuestionScreen(audio_config_dict, name=f'{part}-{audio}'))

            # Add the final questionnaire if it is present
            if 'questionnaire' in self.experiment[part].sections:
                self.add_widget(QuestionnaireScreen(self.experiment[part]['questionnaire'],
                                                    manager=self, name=f'{part}-questionnaire'))

        self.add_widget(PalilaScreen('', '', name='end'))

    def navigate_next(self) -> None:
        """
        Navigate to the next screen, based on the string defined in the current screen.
        """
        self.transition.direction = 'left'
        self.current = self.current_screen.next_screen

    def navigate_previous(self) -> None:
        """
        Navigate to the previous screen, based on the string defined in the current screen.
        """
        self.transition.direction = 'right'
        self.current = self.current_screen.previous_screen

    def set_pid(self, pid: str) -> None:
        """
        Pass-through function to set the participant ID in the linked PalilaAnswers instance.

        Parameters
        ----------
        pid : str
            The participant ID to be set.
        """
        self.answers.set_pid(pid)

    def store_answer(self, key: str, value: str) -> None:
        """
        Store an answer in the pandas.DataFrame in the linked PalilaAnswers instance.

        Parameters
        ----------
        key : str
            Column key in the answers DataFrame. Should be the Question ID of the requesting question.
        value : str
            The answer value to be stored in the DataFrame. Should be a string to avoid issues with pandas.
        """
        self.answers.out.loc['response', key] = value


class PalilaApp(App):
    """
    Subclass of kivy.app.App for the customisation needed for the GUI.

    Parameters
    ----------
    experiment_name : str
        Name of the listening experiment config file (<name>.palila) and directory.
    **kwargs : dict
        Keyword arguments. These are passed on to the kivy.app.App constructor.

    Attributes
    ----------
    experiment : PalilaExperiment
        The linked PalilaExperiment instance.
    answers : PalilaAnswers
        The linked PalilaAnswers instance.
    """

    def __init__(self, experiment_name: str, **kwargs) -> None:
        super().__init__(**kwargs)

        # Load the experiment from the file
        self.experiment = PalilaExperiment(experiment_name)
        self.answers = PalilaAnswers(self.experiment)

    def build(self) -> PalilaScreenManager:
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

    def on_stop(self) -> None:
        """
        Actions to be taken when the app is stopped.
        """
        if self.experiment.name != 'gui_dev':
            self.answers.save_to_file()
