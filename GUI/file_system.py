"""
Module containing the classes that manage the interactions with files during the experiment.
"""
from configobj import ConfigObj
import pandas as pd
import datetime
import random
import time
import copy
import os


__all__ = ['PalilaExperiment', 'PalilaAnswers']


class PalilaExperiment(ConfigObj):
    """
    Subclass of ConfigObj. Stores the full configuration of the experiment. Responsible for verification and
    pre-processing of the config file information.

    Parameters
    ----------
    name : str
        Name of the listening experiment config file (<name>.palila) and directory.

    Attributes
    ----------
    name : str
        Name of the listening experiment config file (<name>.palila).
    path : str
        Path to the listening experiment directory with all the files.
    question_id_list : list of str
        List of question IDs present in the experiment.
    """

    def __init__(self, name: str) -> None:
        super().__init__(os.path.abspath(f'{name}.palila'))
        self.name = name
        self.path = os.path.abspath(f'{name}')
        self.response_path = os.path.join(self.path, 'responses')

        # Create a directory to store the experiment responses to
        if not os.path.isdir(self.response_path):
            os.mkdir(self.response_path)

        # Initialise the list for question ids
        self.question_id_list = []
        # Create list of parts in the overall dict
        self['parts'] = [part for part in self.sections if 'part' in part]
        # Create a list of the questionnaire questions in the questionnaire dict
        self['questionnaire']['questions'] = [question for question in self['questionnaire'].sections
                                              if 'question' in question]

        # Create a list of audios in each part dict
        for part in self['parts']:
            self[part]['audios'] = []
            # Go over all the sections to find audios
            for audio in self[part]:
                if 'audio ' in audio:
                    # In case a repeat is requested, add the required number of repeating audios
                    if 'repeat' in self[part][audio].keys():
                        # Get the number of repeats.
                        repeat = int(self[part][audio]['repeat'])
                        # For each repeat
                        for ri in range(repeat):
                            # Create a new name and add to the list of audios
                            new_name = audio + '_' + str(ri).zfill(2)
                            self[part]['audios'].append(new_name)
                            # Copy this audio as a repeat
                            self[part][new_name] = {}
                            for key, value in self[part][audio].items():
                                if 'question ' in key:
                                    self[part][new_name][key] = {}
                                    for subkey, subvalue in value.items():
                                        self[part][new_name][key][subkey] = copy.deepcopy(subvalue)
                                else:
                                    self[part][new_name][key] = copy.deepcopy(value)

                        # Remove the original audio from the dict to save space.
                        del self[part][audio]
                    # Otherwise, just add the audio name to the list of audios
                    else:
                        self[part]['audios'].append(audio)

            # Create a list of questions in each audio dict
            for audio in self[part]['audios']:
                self[part][audio]['questions'] = [question for question in self[part][audio].sections]

        print(f'Successfully loaded "{self.name}.palila".\nVerifying experiment setup...')
        # Verify and prepare for the GUI
        self._verify_experiment()
        print(f'Successfully verified experiment setup.\nPreparing experiment setup for GUI...')
        self._prepare_experiment()
        print(f'Successfully prepared experiment.\nStarting GUI...')

    def _verify_part(self, part: str) -> None:
        """
        Verification of the experiment part from the input file to check if everything is present.

        Raises
        ------
        SyntaxError :
            If anything in the config file is wrong.

        FileNotFoundError :
            If an audio file from the config file is not found.
        """
        # Check that the part is not completely empty
        if not self[part].sections:
            raise SyntaxError(f'Empty experiment part ("{part}") found in input file {self.name}.palila')

        # Check that the part contains audio questions.
        if not self[part]['audios']:
            raise SyntaxError(f'Experiment {part} does not contain any audio questions.')

        # Check the intro section if it exists
        if 'intro' in self[part].sections:
            if 'text' not in self[part]['intro']:
                raise SyntaxError(f'Experiment {part} intro does not contain "text" variable.')

            if 'time' not in self[part]['intro']:
                raise SyntaxError(f'Experiment {part} intro does not contain "time" variable.')
            elif not self[part]['intro']['time'].isnumeric():
                raise SyntaxError(f'Experiment {part} intro "time" is not a number.')

        if 'breaks' in self[part].sections:
            if 'interval' not in self[part]['breaks']:
                raise SyntaxError(f'Experiment {part} breaks does not contain "interval" variable.')
            elif (not self[part]['breaks']['interval'].startswith('-') and
                  not self[part]['breaks']['interval'].isnumeric()):
                raise SyntaxError(f'Experiment {part} breaks "interval" is not a number.')
            elif (self[part]['breaks']['interval'].startswith('-') and
                  not self[part]['breaks']['interval'][1:].isnumeric()):
                raise SyntaxError(f'Experiment {part} breaks "interval" is not a number.')

            if 'time' not in self[part]['breaks']:
                raise SyntaxError(f'Experiment {part} breaks does not contain "time" variable.')
            elif not self[part]['breaks']['time'].isnumeric():
                raise SyntaxError(f'Experiment {part} breaks "time" is not a number.')

        # Check if the questionnaire is split properly
        if 'questionnaire' in self[part].sections:
            if 'manual split' in self[part]['questionnaire']:
                self[part]['questionnaire']['manual split'] = self[part]['questionnaire'].as_bool('manual split')
                if self[part]['questionnaire']['manual split']:
                    for question in self[part]['questionnaire'].sections:
                        if 'manual screen' not in self[part]['questionnaire'][question]:
                            raise SyntaxError(f'Experiment {part} questionnaire {question} does not contain '
                                              f'"manual screen" variable.')
                        elif self[part]['questionnaire'][question]['manual screen'].isnumeric():
                            raise SyntaxError(f'Experiment {part} questionnaire {question} "manual screen" '
                                              f'is not a number.')
            else:
                self[part]['questionnaire']['manual split'] = False

        # Check the individual audios in the experiment part
        for audio in self[part]['audios']:
            if 'filename' not in self[part][audio].keys():
                raise SyntaxError(f'No filename found for {part}: {audio}.')

            if not os.path.isfile(os.path.join(self.path, self[part][audio]['filename'])):
                raise FileNotFoundError(f'Audio file {self[part][audio]["filename"]} not found for {part}: {audio}.')

    def _verify_experiment(self) -> None:
        """
        Verification of the experiment input file to check if everything is present.

        Raises
        ------
        SyntaxError :
            If anything in the config file is wrong.
        """
        # Check that the experiment is not completely empty
        if not self.sections:
            raise SyntaxError(f'Empty experiment in input file {self.name}.palila')

        # Check for the presence of a startup questionnaire.
        if 'questionnaire' not in self.sections:
            raise SyntaxError(f'Experiment does not contain a startup questionnaire.')

        # Check if the questionnaire is split properly
        if 'manual split' in self['questionnaire']:
            self['questionnaire']['manual split'] = self['questionnaire'].as_bool('manual split')
            if self['questionnaire']['manual split']:
                for question in self['questionnaire'].sections:
                    if 'manual screen' not in self['questionnaire'][question]:
                        raise SyntaxError('If manual split is set, each questionnaire question requires '
                                          'an assigned screen.')
        else:
            self['questionnaire']['manual split'] = False

        # Check for the presence of experiment parts
        if not self['parts']:
            raise SyntaxError(f'Experiment does not contain any parts.')

        # Verify the individual experiment parts
        for part in self['parts']:
            self._verify_part(part)

    def _prepare_main_questionnaire(self) -> None:
        """
        Sets up the main questionnaire dictionary based on the config file.
        """
        # Check for the default keyword in the main questionnaire
        if 'default' in self['questionnaire'].keys():
            self['questionnaire']['default'] = self['questionnaire'].as_bool('default')
        else:
            self['questionnaire']['default'] = False

        # Get the default questionnaire setup if that is set
        if self['questionnaire']['default']:
            # Load the configfile
            self['questionnaire'].update(
                ConfigObj(os.path.join(os.path.abspath('GUI'), 'default_questionnaire.palila'))
            )
            # Create a list of the questionnaire questions in the questionnaire dict
            self['questionnaire']['questions'] = [question for question in self['questionnaire'].sections
                                                  if 'question' in question]

        # Set the questionnaire's 'previous' to the welcome screen
        self['questionnaire']['previous'] = 'welcome'

        # Loop over the questionnaire questions
        for iq, question in enumerate(self['questionnaire']['questions']):
            # Replace tab characters in the question text
            self['questionnaire'][question]['text'] = self['questionnaire'][question]['text'].replace('\t', '')

            # Extract the id to the overall question id list
            if 'id' in self['questionnaire'][question]:
                self.question_id_list.append(self['questionnaire'][question]['id'])
            # Generate a not-so-nice (but standardised) id when it's not defined explicitly
            else:
                # Extract the user input part, audio and question names from the brackets
                question_id = question.replace('question ', '')
                # Put those together and add to the list
                qid = f'main-questionnaire-{question_id.zfill(2)}'
                self.question_id_list.append(qid)
                self['questionnaire'][question]['id'] = qid

    def _prepare_part_audio(self, part: str, audio: str, question_overwrite: bool = False):
        """
        Prepares a specific audio's dictionary.

        Parameters
        ----------
        part : str
            Index of the part dictionary inside the overall dictionary.
        audio : str
            Index of the audio dictionary inside the part dictionary.
        question_overwrite : bool, optional
            If set to True, questions will be obtained from self[part]['questions'] instead of the audio dictionary.
            Defaults to False.
        """
        # Define the full filepath of the audio
        self[part][audio]['filepath'] = os.path.join(self.path, self[part][audio]['filename'])
        if 'filename_2' in self[part][audio].keys():
            self[part][audio]['filepath_2'] = os.path.join(self.path, self[part][audio]['filename_2'])
        # Define the max number of replays
        if 'max replays' not in self[part][audio].keys():
            self[part][audio]['max replays'] = '1'
        # Extract the filler option
        if 'filler' not in self[part][audio].keys():
            self[part][audio]['filler'] = True
        else:
            self[part][audio]['filler'] = self[part][audio].as_bool('filler')

        # Obtain the questions in case of question overwrite from the part
        if question_overwrite:
            # First remove the ones that may be in the audio dictionary
            for question in self[part][audio]['questions']:
                del self[part][audio][question]
            # Deep copy the part questions redo the questions list
            for key, value in self[part]['questions'].items():
                self[part][audio][key] = {}
                for subkey, sub_value in value.items():
                    self[part][audio][key][subkey] = copy.deepcopy(sub_value)

            self[part][audio]['questions'] = self[part]['questions'].keys()

        # Loop over the questions
        for question in self[part][audio]['questions']:
            # Remove tabs from the input file in the question text
            self[part][audio][question]['text'] = self[part][audio][question]['text'].replace('\t', '')
            # Generate a standardised question id
            # Extract the part, audio and question names
            part_id = part.replace('part ', '')
            audio_id = audio.replace('audio ', '')
            question_id = question.replace('question ', '')

            # Put everything together and add to the list
            qid = f'{part_id.zfill(2)}-{audio_id.zfill(2)}-{question_id.zfill(2)}'
            self.question_id_list.append(qid)
            self[part][audio][question]['id'] = qid

    def _prepare_part_questionnaire(self, part):
        """
        Prepares the dictionary of the given part's questionnaire.

        Parameters
        ----------
        part : str
            Index of the part dictionary inside the overall dictionary.
        """
        # Create a list of the questionnaire questions in the questionnaire dict
        self[part]['questionnaire']['questions'] = [question for question in
                                                    self[part]['questionnaire'].sections
                                                    if 'question' in question]
        # Set up the part questionnaire questions
        for iq, question in enumerate(self[part]['questionnaire']['questions']):
            # Make sure the text is nice.
            text_mod = self[part]['questionnaire'][question]['text'].replace('\t', '')
            self[part]['questionnaire'][question]['text'] = text_mod

            # Extract the id to the overall question id list
            if 'id' in self[part]['questionnaire'][question]:
                self.question_id_list.append(self[part]['questionnaire'][question]['id'])
            # Generate a not-so-nice (but standardised) id when it's not defined explicitly
            else:
                # Extract the user input part, audio and question names from the brackets
                part_id = part.replace('part ', '')
                question_id = question.replace('question ', '')
                # Put those together and add to the list
                qid = f'{part_id.zfill(2)}-questionnaire-{question_id.zfill(2)}'
                self.question_id_list.append(qid)
                self[part]['questionnaire'][question]['id'] = qid

    def _prepare_part(self, ip: int, part: str, previous_part: str, previous_audio: str, previous_name: str, ):
        """
        Prepares the full dictionary of a part of the experiment.

        Parameters
        ----------
        ip : int
            Index number of the current part inside the preparation loop
        part : str
            Index of the part dictionary inside the overall dictionary.
        previous_part : str
            Index of the previous part's dictionary inside the overall dictionary.
        previous_audio : str
            Index of the last audio (or questionnaire) dictionary inside the previous part's dictionary.
        previous_name : str
            Formatted name of the last audio (or questionnaire) of the previous part.

        Returns
        -------
        audio : str
            The index of the last audio (or questionnaire) of this part.
        current_name: str
            The formatted name of the last audio (or questionnaire) of this part.
        """

        # Set the intro as the current added screen
        audio = 'intro'
        current_name = f'{part}-intro'
        # Add the default intro if it's not in the config file
        if 'intro' not in self[part].sections:
            self[part]['intro'] = {'text': f'You have reached part {ip + 1} of the experiment.\n'
                                           f'Press "Continue" below to resume the experiment.',
                                   'time': '3.'}
        # Fix up the introduction text
        self[part]['intro']['text'] = self[part]['intro']['text'].replace('\t', '')
        # Set the intro screen's 'previous'
        self[part]['intro']['previous'] = previous_name
        # In case this is the first part, set the intro as the 'next' of the questionnaire
        if not ip:
            self['questionnaire']['next'] = current_name
        # Otherwise, set the intro as the 'next' of the last part's questionnaire
        else:
            self[previous_part][previous_audio]['next'] = current_name
        # And set the intro as the previously added screen
        previous_name = current_name
        previous_audio = audio

        # ==========================================================================================================
        # PREPARATION OF THE PART BREAKS (BLOCK 1)
        # ==========================================================================================================
        breaks = 'breaks' in self[part].sections

        break_interval = 0 if not breaks else int(self[part]['breaks']['interval'])
        break_time = 0 if not breaks else int(self[part]['breaks']['time'])
        break_text = self[part]['breaks']['text'] if breaks and 'text' in self[part]['breaks']\
            else f'This is a {break_time} second break.'
        break_count = 0 if not breaks else 1


        # ==========================================================================================================
        # PREPARATION OF THE PART AUDIOS
        # ==========================================================================================================

        # Randomise the audios in this part if so desired
        if 'randomise' in self[part].keys() and self[part].as_bool('randomise'):
            random.shuffle(self[part]['audios'])

        question_overwrite = 'questions' in self[part].sections

        # Loop over the audios
        for ia, audio in enumerate(self[part]['audios']):
            # Define the screen name
            current_name = f'{part}-{audio}'
            # If it's the first, set this audio as the 'next' of the intro
            if not ia:
                self[part]['intro']['next'] = current_name

            # Set this audio's 'previous' and the previous audio's next
            self[part][previous_audio]['next'] = current_name
            self[part][audio]['previous'] = previous_name

            # Prepare the current audio.
            self._prepare_part_audio(part, audio, question_overwrite)

            # Keep track of the last screen name and associated audio name
            previous_name = current_name
            previous_audio = audio

            # ======================================================================================================
            # PREPARATION OF THE PART BREAKS (BLOCK 2)
            # ======================================================================================================
            add_break = (ia + 1 == len(self[part]['audios']) and break_interval >= 0) or (
                    break_interval != 0 and (ia + 1) % break_interval == 0)

            # If a break should be included
            if breaks and add_break:
                print(break_count)
                # Set the current audio and name accordingly
                audio = f'break {break_count}'
                current_name = f'{part}-{audio}'
                # Set the previous audio's 'next' to this break
                self[part][previous_audio]['next'] = audio
                # Set up the current break dict
                self[part][audio] = {'text': break_text, 'time': break_time,
                                     'previous': previous_name}
                # Up the break counter
                break_count += 1
                # Keep track of the last screen name and associated audio name
                previous_name = current_name
                previous_audio = audio

                print(self[part].keys())

        # ==========================================================================================================
        # PREPARATION OF THE PART QUESTIONNAIRE
        # ==========================================================================================================

        if 'questionnaire' in self[part].sections:
            current_name = f'{part}-questionnaire'
            audio = 'questionnaire'
            # Set the 'previous' and the last question's 'next'
            self[part][previous_audio]['next'] = current_name
            self[part][audio]['previous'] = previous_name

            self._prepare_part_questionnaire(part)

        return audio, current_name

    def _prepare_experiment(self) -> None:
        """
        Put things in the dictionaries where they are needed for the ScreenManager to properly build the GUI.
        """
        # ==============================================================================================================
        # PREPARATION OF THE WELCOME AND GOODBYE MESSAGES
        # ==============================================================================================================

        if 'welcome' not in self.keys():
            self['welcome'] = 'Welcome to this listening experiment.\nPlease enter your participant ID:'
        else:
            # Fix the welcome message.
            self['welcome'] = self['welcome'].replace('\t', '')

        if 'goodbye' not in self.keys():
            self['goodbye'] = 'Thank you for your participation in this experiment!'
        else:
            self['goodbye'] = self['goodbye'].replace('\t', '')

        # Prepare the main questionnaire
        self._prepare_main_questionnaire()

        # Pre-define some values to start the parts loop
        previous_part = ''
        previous_audio = ''
        previous_name = 'main-questionnaire'

        # Randomise the parts in this experiment if so desired
        if 'randomise' in self.keys() and self.as_bool('randomise'):
            random.shuffle(self['parts'])

        # Loop over all the experiment parts
        for ip, part in enumerate(self['parts']):
            # Prepare the part
            previous_audio, previous_name = self._prepare_part(ip, part, previous_part, previous_audio, previous_name, )
            # Set this part as the last that was added
            previous_part = part

        # Add the end screen as the 'next' of the last screen
        self[previous_part][previous_audio]['next'] = 'end'


class PalilaAnswers:
    """
    Class managing the participant responses.

    Parameters
    ----------
    experiment : PalilaExperiment
        PalilaExperiment instance to link these answers to.

    Attributes
    ----------
    experiment : PalilaExperiment
        The linked PalilaExperiment instance.
    pid_mode: str
        Mode of setting the participant ID. Either 'auto' or 'input'.
    out: pandas.DataFrame
        The DataFrame in which the experiment answers are stored for exporting at the end.
    out_path: str
        Path defining the output file location.
    timing : bool
        Indication that the timer is running.
    """

    def __init__(self, experiment: PalilaExperiment) -> None:
        # Store the experiment inside this class
        self.experiment = experiment
        self.pid_mode = self.experiment['pid mode']
        # Set up the output dataframe
        columns = self.experiment.question_id_list
        columns.append('timer')
        self.out = pd.DataFrame('', index=['response'], columns=self.experiment.question_id_list)

        # Initialise the PID in case of auto mode
        if self.pid_mode == 'auto':
            self.pid = datetime.datetime.now().strftime('%y%m%d-%H%M')
            self.out_path = os.path.join(self.experiment.path, 'responses', f'{self.pid}.csv')
        else:
            self.pid = None

        self.timing = False

    def set_pid(self, pid: str) -> None:
        """
        Function to set the participant ID from GUI input

        Parameters
        ----------
        pid : str
            The participant ID to be set.
        """
        self.pid = pid
        self.out_path = os.path.join(self.experiment.path, 'responses', f'{self.pid}.csv')

    def save_to_file(self) -> None:
        """
        Save the answers to the pre-determined file.
        """
        self.out.to_csv(self.out_path)
        print(f'Answers successfully save to: {self.out_path}')

    def start_timer(self) -> None:
        """
        Set the start time of the experiment to later determine the completion time.
        """
        if not self.timing:
            print(f'Timer started at {datetime.datetime.now().strftime("%A %d %B %Y - %H:%M")}')
            self.out.loc['response', 'timer'] = str(time.time())
            self.timing = True

        else:
            print(f'Timer already started. Ignoring trigger.')

    def stop_timer(self) -> None:
        """
        Determine the completion time with the previously set start time.

        Raises
        ------
        RuntimeError
            In case the timer value in the PalilaAnswers().out DataFrame was not set before calling this function.
        """
        if self.out.loc['response', 'timer'] == '':
            raise RuntimeError('No start time was set in the timer. Cannot determine completion time.')
        elif self.timing:
            self.timing = False
            self.out.loc['response', 'timer'] = str(time.time() - float(self.out.loc['response', 'timer']))
            print(f'Timer stopped at {datetime.datetime.now().strftime("%A %d %B %Y - %H:%M")}.\n'
                  f'Elapsed time was {str(round(float(self.out.loc["response", "timer"]) / 60)).zfill(2)}:'
                  f'{str(round(float(self.out.loc["response", "timer"]) % 60)).zfill(2)} minutes.')

        else:
            raise RuntimeError('Timer has already stopped.')
