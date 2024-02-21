"""
Module containing the overall classes for the Audio Question screens.
"""
from kivy.uix.boxlayout import BoxLayout
from kivy.core.audio import SoundLoader

from .threaded_tools import ProgressBarThread
from .screens import PalilaScreen, Filler
from . import audio_questions


__all__ = ['AudioQuestionScreen']


class AudioQuestionScreen(PalilaScreen):
    """
    Class that defines the overall audio question screens. Subclass of .screens.PalilaScreen.

    Parameters
    ----------
    config_dict : dict
        Dictionary that defines the audio and related questions.
    **kwargs
        Keyword arguments. These are passed on to the .screens.PalilaScreen constructor.

    Attributes
    ----------
    config_dict : dict
        Dictionary that defines the audio and related questions.
    audio_manager_left : AudioManagerLeft
        The primary instance of AudioManager linked to this specific screen.
    audio_manager_right : AudioManagerLeft
        The secondary instance of AudioManager linked to this specific screen.
    question_manager : QuestionManager
        The instance of QuestionManager linked to this specific screen.
    audio_block : bool
        Switch indicating that audio replay should be blocked.
    """

    def __init__(self, config_dict: dict, **kwargs) -> None:
        super().__init__(config_dict['previous'], config_dict['next'], lock=True, **kwargs)
        self.config_dict = config_dict

        # Get better references to the audio and question managers
        self.audio_manager_left: AudioManagerLeft = self.ids.audio_manager_left
        self.audio_manager_right: AudioManagerRight = AudioManagerRight()
        self.question_manager: QuestionManager = self.ids.question_manager

        # Initialise the audio managers with the audios defined in the input file
        self.audio_manager_left.initialise_manager(self.config_dict['filepath'],
                                                   int(self.config_dict['max replays']), self)

        # Add the second audio manager if a second audio file is given, otherwise just leave it alone.
        if 'filepath_2' in self.config_dict:
            self.ids.audio_managers.add_widget(self.audio_manager_right)
            self.ids.audio_managers.size_hint_x = 1.
            self.audio_manager_right.initialise_manager(self.config_dict['filepath_2'],
                                                        int(self.config_dict['max replays']), self)
            self.ids.extra_message.text = 'Listen to both samples at least once before answering the question.'

        # Add the questions from the input file to the question manager
        for question in self.config_dict['questions']:
            self.question_manager.add_question(self.config_dict[question])
        # Readjust the question manager after adding all questions
        self.question_manager.readjust(self.config_dict['filler'])

        self.audio_block = False

    def on_pre_leave(self, *_) -> None:
        """
        Store the answers when leaving the screen.
        """
        for qid, question in self.ids.question_manager.question_dict.items():
            # Store the answers, question by question
            if question.answer is not None:
                self.manager.store_answer(qid, question.answer.text)
            else:
                self.manager.store_answer(qid, 'No Answer')

    def unlock_check(self, question_state: bool = None):
        """
        Check whether the continue button can be unlocked.

        Parameters
        ----------
        question_state : bool, optional
            The state of the QuestionManager. Defaults to a check of the QuestionManager state
        """
        audio_state_left = self.audio_manager_left.count >= 1
        audio_state_right = self.audio_manager_right.n_max is None or self.audio_manager_right.count >= 1
        audio_state = audio_state_left and audio_state_right

        if audio_state:
            self.question_manager.unlock()
            self.ids.extra_message.text = ''

            if question_state is None:
                question_state = self.question_manager.get_state()

            # If all questions are answered and the audio is listened to: unlock the continue button
            if question_state:
                self.reset_continue_label()
                self.ids.continue_bttn.unlock()
            # Make sure the continue button is locked if not
            else:
                self.ids.continue_bttn.lock()


class AudioManager(BoxLayout):
    """
    Subclass of kivy.uix.boxlayout.BoxLayout, which manages the audio of the AudioQuestionScreen.

    Parameters
    ----------
    **kwargs
        Keyword arguments. These are passed on to the kivy.uix.boxlayout.BoxLayout constructor.

    Attributes
    ----------
    audio : kivy.core.audio.Sound
        The audio of the AudioQuestionScreen, in the form of a kivy.core.audio.Sound instance. Initialised as None.
    n_max : int
        The maximum number of replays. Initialised as None.
    thread : .threaded_tools.ProgressBarThread
        The threading instance linked to the ProgressBar to make it dynamic. Initialised as None.
    playing : bool
        Boolean that indicates whether audio is currently playing.
    count : int
        Integer that keeps track of the times the audio has been played.
    parent_screen : AudioQuestionScreen
        Screen on which this manager is present.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        # Temporary placeholders
        self.audio = None
        self.n_max = None
        self.thread = None

        # Initial values for the audio playback
        self.playing = False
        self.count = 0

        self.parent_screen = None

    def initialise_manager(self, audio_path: str, n_max: int, parent_screen: AudioQuestionScreen) -> None:
        """
        Set up the AudioManager once the necessary information is available.

        Parameters
        ----------
        audio_path : str
            Full path to the audio file.
        n_max : int
            The maximum number of replays that will be allowed.
        parent_screen : AudioQuestionScreen
            The screen of which this manager is part. To avoid endless .parent.parent chains.
        """
        self.n_max = n_max
        self.audio = SoundLoader.load(audio_path)
        self.audio.on_stop = self._done_playing
        # Set the text next to the play button
        if self.n_max == 1:
            self.ids.txt.text = f'Listen to this audio sample\nYou can play this sample {self.n_max} time'
        else:
            self.ids.txt.text = f'Listen to this audio sample\nYou can play this sample {self.n_max} times'

        self.parent_screen = parent_screen

    def play(self):
        """
        Function that starts the audio.
        """
        # Check the count and if audio is already playing
        if self.count < self.n_max and not self.playing and not self.parent_screen.audio_block:
            # Set up the ProgressBarThread and the corresponding bar
            self.thread = ProgressBarThread(self.ids.progress)
            self.ids.progress.max = self.audio.length
            # Start the thread, audio and set the playing boolean
            self.thread.start()
            self.audio.play()
            self.playing = True
            self.parent_screen.audio_block = True
            # Reflect the audio playing in the play button and text
            self.ids.bttn_image.source = 'GUI/assets/hearing.png'
            self.ids.bttn.background_color = [.5, .5, 1, 1]
            self.ids.txt.text = 'Playing sample ...'
            # Up the count
            self.count += 1

    def _done_playing(self):
        """
        on_stop function for the audio.
        """
        # Terminate and reset the progress bar thread
        self.thread.join()
        self.thread = None
        # Register that no audio is playing
        self.playing = False
        self.parent_screen.audio_block = False
        # Check the remaining replay allowance
        remaining = self.n_max - self.count
        # If there is allowance left
        if remaining > 0:
            # Reset the play button
            self.ids.bttn_image.source = 'GUI/assets/play.png'
            self.ids.bttn.background_color = [1, 1, 1, 1]
            # Set the corresponding text next to the button
            if remaining == 1:
                self.ids.txt.text = f'You can replay this sample\n {remaining} more time'
            else:
                self.ids.txt.text = f'You can replay this sample\n {remaining} more times'
        # Otherwise reflect running out of replays in the button and text
        else:
            self.ids.bttn_image.source = 'GUI/assets/done.png'
            self.ids.bttn.background_color = [.5, 1, .5, 1]
            self.ids.txt.text = ''

        # Unlock the rest of the screen when the audio has been played once
        if self.count == 1:
            self.parent_screen.unlock_check()


class AudioManagerRight(AudioManager):
    pass


class AudioManagerLeft(AudioManager):
    pass


class QuestionManager(BoxLayout):
    """
    Subclass of kivy.uix.boxlayout.BoxLayout that defines and manages the question part of an AudioQuestionScreen.

    Parameters
    ----------
    **kwargs
        Keyword arguments. These are passed on to the kivy.uix.boxlayout.BoxLayout constructor.

    Attributes
    ----------
    n_max : int = 2
        Maximum number of questions that will fit this manager.
    n_question : int
        Number of questions in this manager.
    answered : dict of str:bool
        Dictionary that tracks which questions have been answered.
    """

    n_max = 2

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.n_question = 0
        self.question_dict = {}
        self.answered = {}
        self.disabled = True

    def add_question(self, question_dict: dict) -> None:
        """
        Adds a question to the allocated space.

        Parameters
        ----------
        question_dict : dict
            Dictionary which defines the question to be added.

        Raises
        ------
        OverflowError:
            If the question that is passed makes the question count go over the limit.
        """
        # Check if the space is full
        if self.n_question < self.n_max:
            # Add the question according to the input file
            question_type = getattr(audio_questions, f'{question_dict["type"]}AQuestion')
            question = question_type(question_dict)

            self.question_dict[question_dict['id']] = question
            self.answered[question_dict['id']] = False
            # Add the question to the widgets
            self.add_widget(question)
            # Update the counter
            self.n_question += 1

        # Throw hands if the space is full
        else:
            raise OverflowError(f'Audio contains more than {self.n_max} questions.')

    def readjust(self, filler: bool) -> None:
        """
        Fill the empty space to avoid weird sizing of the questions.

        Parameters
        ----------
        filler : bool
            Indicate whether to fill the empty space or not.
        """
        if filler:
            # Add filler widgets in the leftover space
            for ii in range(self.n_max - self.n_question):
                self.add_widget(Filler())

    def unlock(self) -> None:
        """
        Unlock this question manager.
        """
        self.disabled = False

    def get_state(self) -> None:
        """
        Get an indication if all questions have been answered in this manager.

        Returns
        -------
        bool
            Indication if all questions have been answered in this manager.
        """
        # Start a variable to store the total state
        total_state = True
        for state in self.answered.values():
            # Update the total state via the boolean "and" operator
            total_state = total_state and state

        return total_state

    def question_answered(self, question_id: str, answered: bool) -> None:
        """
        Function to set and check the state of the questions.

        Parameters
        ----------
        question_id : str
            Question ID of the question to set the state of.
        answered : bool
            Indication if the question linked to the ID has been answered.
        """
        # Firstly set the state of the question
        self.answered[question_id] = answered
        # Have the AudioQuestionScreen check the state
        self.parent.parent.unlock_check(question_state=self.get_state() and not self.disabled)

