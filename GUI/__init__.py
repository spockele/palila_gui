"""
Main module of the GUI package.

Pulls in all functions from the modules in the package. It also defines the custom ScreenManager and App classes, which
form the core of this package. Loads all the relevant kivy files for this package.
"""
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.config import Config
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
    **kwargs
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

        # Go about initialising the Screens based on the input file
        self._initialise_screens()

    def _initialise_screens(self) -> None:
        """
        Internal function to initialise the Screens from the PalilaExperiment instance
        """
        # Add the welcome screen and set it as the current screen.
        self.add_widget(WelcomeScreen(self.experiment['pid mode'], self.experiment['welcome'],
                                      '', 'main-questionnaire', name='welcome'))
        self.current = 'welcome'
        # Add the first questionnaire
        self.add_widget(QuestionnaireScreen(self.experiment['questionnaire'], self, name='main-questionnaire'))

        # Loop over the experiment parts
        for part in self.experiment['parts']:
            # Add the introductions
            self.add_widget(TimedTextScreen(self.experiment[part]['intro'], name=f'{part}-intro'))
            # Within each part, loop over the audios
            for ia, audio in enumerate(self.experiment[part]['audios']):
                # Create the AudioQuestionScreen and add it to the manager
                self.add_widget(AudioQuestionScreen(self.experiment[part][audio], name=f'{part}-{audio}'))

                # Check if a break should be added.
                if 'break' in self.experiment[part][audio]['next']:
                    break_name = self.experiment[part][audio]["next"]
                    # Create the screen name for the break
                    self.add_widget(TimedTextScreen(self.experiment[part][break_name],
                                                    name=break_name))

            # Add the final questionnaire if it is present
            if 'questionnaire' in self.experiment[part].sections:
                self.add_widget(QuestionnaireScreen(self.experiment[part]['questionnaire'],
                                                    manager=self, name=f'{part}-questionnaire'))

        self.add_widget(EndScreen('main-questionnaire', 'final', name='end'))
        self.add_widget(FinalScreen('end', '', goodbye=self.experiment['goodbye'], name='final'))

    def navigate_next(self) -> None:
        """
        Navigate to the next screen, based on the string defined in the current screen.
        """
        # Set the transition direction and the new current screen
        self.transition.direction = 'left'
        self.current = self.current_screen.next_screen
        # Start the timer when leaving the main questionnaire
        if 'main-questionnaire' in self.current_screen.previous_screen and 'main-questionnaire' not in self.current:
            self.answers.start_timer()
        elif self.current == 'final':
            self.answers.stop_timer()

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
    **kwargs
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
        Config.set('kivy', 'exit_on_escape', '0')

        # Required return of the ScreenManager
        return manager
