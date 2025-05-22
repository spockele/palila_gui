"""
Main module of the GUI package.

Pulls in all functions from the modules in the package. It also defines the custom ScreenManager and App classes, which
form the core of this package. Loads all the relevant kivy files for this package.
"""

# Copyright (c) 2025 Josephine Siebert Pockelé
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from kivy.uix.screenmanager import ScreenManager
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.config import Config
from kivy.lang import Builder
from kivy.app import App

import datetime
import warnings

from .questionnaire_screen import *
from .audio_screen import *
from .file_system import *
from .screens import *
from .tools import *


__all__ = ['main', ]

from .tools import NavigationBar

Builder.load_file('GUI/audio_screen.kv')
Builder.load_file('GUI/audio_questions.kv')
Builder.load_file('GUI/tools.kv')
Builder.load_file('GUI/questionnaire_questions.kv')
Builder.load_file('GUI/questionnaire_screen.kv')


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

        self.size_hint = (1., 1. - .015 - .15)
        self.navigation = NavigationBar(self)

        # Go about initialising the Screens based on the input file
        self._initialise_screens()

        self.tracker = ProgressTracker(self.screen_names, size_hint=(1., .015, ))

    def _initialise_screens(self) -> None:
        """
        Internal function to initialise the Screens from the PalilaExperiment instance
        """
        # Little shortcut for the purpose of testing stuff
        override = self.experiment.as_bool('override')

        # Add the welcome screen
        self.add_widget(WelcomeScreen(self.experiment['pid mode'], self.experiment['welcome'],
                                      '', 'main-questionnaire 1', name='welcome'))

        # Add the demo screen if that is required and set the correct screen as current
        if self.experiment.as_bool('demo'):
            screen = AudioQuestionScreen(self.experiment['demo dict'], demo=True, name='demo')
            self.add_widget(screen)
            self.current = 'demo'
        else:
            self.current = 'welcome'

        # Set up the first questionnaire
        questionnaire_setup(self.experiment['questionnaire'], self, override)

        # Initialise the counter for the progress bar
        progress = 0
        # Loop over the experiment parts
        for part in self.experiment['parts']:
            # Add the introductions
            self.add_widget(TimedTextScreen(self.experiment[part]['intro'], name=f'{part}-intro'))
            # Within each part, loop over the audios
            for ia, audio in enumerate(self.experiment[part]['audios']):
                # Up the progress counter by 1
                progress += 1
                # Create the AudioQuestionScreen and add it to the manager
                screen = AudioQuestionScreen(self.experiment[part][audio],
                                             name=f'{part}-{audio}', state_override=override)
                self.add_widget(screen)

                # Check if a break should be added.
                if 'break' in self.experiment[part][audio]['next']:
                    break_name = self.experiment[part][audio]["next"]
                    # Create the screen name for the break
                    self.add_widget(TimedTextScreen(self.experiment[part][break_name],
                                                    name=break_name))

            # Add the final questionnaire if it is present
            if 'questionnaire' in self.experiment[part].sections:
                # Setup the questionnaire screens
                questionnaire_setup(self.experiment[part]['questionnaire'], self, override, part=part)

                # Check if a break should be added.
                if 'break' in self.experiment[part]['questionnaire']['next']:
                    break_name = self.experiment[part]['questionnaire']["next"]
                    # Create the screen name for the break
                    self.add_widget(TimedTextScreen(self.experiment[part][break_name],
                                                    name=break_name))

        # Add the Final two screens
        self.add_widget(EndScreen('main-questionnaire 1', 'final', name='end'))
        self.add_widget(FinalScreen('end', '', goodbye=self.experiment['goodbye'], name='final'))

    def navigate_next(self) -> None:
        """
        Navigate to the next screen, based on the string defined in the current screen.
        """
        # Start the timer when leaving the welcome screen
        if self.current == 'welcome':
            self.answers.start_timer()
        elif self.current_screen.next_screen == 'final':
            self.answers.stop_timer()

        self.tracker.track(self.current)

        # Set the transition direction and the new current screen
        self.transition.direction = 'left'
        self.current = self.current_screen.next_screen

    def navigate_previous(self) -> None:
        """
        Navigate to the previous screen, based on the string defined in the current screen.
        """
        # Set the transition direction and the new current screen
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
        if self.experiment['pid mode'] == 'auto':
            self.answers.set_pid(datetime.datetime.now().strftime('%y%m%d-%H%M'))
        elif self.experiment['pid mode'] == 'input':
            self.answers.set_pid(pid)
        else:
            raise SyntaxError(f'Participant ID mode "pid mode = {self.experiment["pid mode"]}" not supported!')

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

    def build(self) -> GridLayout:
        """
        Builds the App (default App function)
        """
        # Set the screen color to a very light grey
        Window.clearcolor = (.95, .95, .95, 1)
        # Set the screen to a fixed resolution
        Window.fullscreen = 'auto'

        main_layout = GridLayout(cols=1, )
        # Create the ScreenManager and pass the experiment along
        manager = PalilaScreenManager(self.experiment, self.answers)
        Config.set('kivy', 'exit_on_escape', '0')

        main_layout.add_widget(manager)
        main_layout.add_widget(manager.navigation)
        main_layout.add_widget(manager.tracker)

        # Required return of the ScreenManager
        return main_layout


def main(experiment: str) -> None:
    """
    Main run function of the GUI.
    """
    warnings.simplefilter('always', DeprecationWarning)
    PalilaApp(experiment).run()
