"""
Copyright (c) 2024 Josephine Siebert Pockelé

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

------------------------------------------------------------------------------------------------------------------------

Module containing the classes that manage the interactions with files during the experiment.

------------------------------------------------------------------------------------------------------------------------
"""
from configobj import ConfigObj, Section
import pandas as pd
import datetime
import warnings
import random
import time
import copy
import os


__all__ = ['PalilaExperiment', 'PalilaAnswers']


class PalilaExperiment(ConfigObj):
    """
    Subclass of ConfigObj. Stores the full configuration of the experiment. Responsible for verification and
    pre-processing of the config file information.

    Works similar to a dictionary (see ConfigObj documentation).

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
        self.palila_path = os.path.abspath(f'{name}.palila')
        super().__init__(self.palila_path)
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
                            new_name = audio + '_' + str(ri + 1).zfill(2)
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
            self['questionnaire'] = {}

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

    def _prepare_questionnaire(self, questionnaire_dict: Section, part: str) -> dict:
        """
        Sets up the questionnaire dictionary based on the config file.

        Parameters
        ----------
        questionnaire_dict : dict
            The specific questionnaire dictionary to be pre-processed.
        part : str
            The part of the experiment where this questionnaire is located.
        """
        if part == 'main':
            # Check for the default keyword in the main questionnaire
            if 'default' in questionnaire_dict.keys():
                questionnaire_dict['default'] = questionnaire_dict.as_bool('default')
            else:
                questionnaire_dict['default'] = False

            # Get the default questionnaire setup if that is set
            if questionnaire_dict['default']:
                # Load the configfile
                questionnaire_dict.update(
                    ConfigObj(os.path.join(os.path.abspath('GUI'), 'default_questionnaire.palila'))
                )

            # Set the questionnaire's 'previous' to the welcome screen
            questionnaire_dict['previous'] = 'welcome'
            # Set the part ID correctly
            part_id = 'main'

        else:
            # Extract the part, audio and question names
            part_id = part.replace('part ', '')

        # Create a list of the questionnaire questions in the questionnaire dict
        questionnaire_dict['questions'] = [question for question in questionnaire_dict.keys()
                                           if 'question' in question]

        manual_split = questionnaire_dict['manual split']

        # Initialise the dictionary that defines the split over multiple screens
        screen_dict = dict()

        # Loop over the questionnaire questions
        for iq, question in enumerate(questionnaire_dict['questions']):
            # ==========================================================================================================
            # todo: DEPRECATED CODE
            # ---------------------
            if questionnaire_dict[question]['type'] == 'MultiMultipleChoice':
                warnings.warn_explicit('The MultiMultipleChoice question type will be removed in the future. '
                                       'For multiple-choice-multiple-answer questions, use MultipleChoice with the '
                                       'multi = yes.',
                                       DeprecationWarning, f'{self.name}.palila', 0)

            if 'id' in questionnaire_dict[question]:
                warnings.warn_explicit('The id option for Questionnaire questions is deprecated and will be '
                                       'removed in future versions. Please use the part between brackets as id.',
                                       DeprecationWarning, f'{self.name}.palila', 0)

            if 'dependant' in questionnaire_dict[question]:
                warnings.warn_explicit('The keywords "dependant" and "dependant condition" will be removed '
                                       'in future versions. Please use the new system with "unlocked by" and "unlock '
                                       'condition" instead.',
                                       DeprecationWarning, f'{self.name}.palila', 0)
            # ==========================================================================================================

            # Identify the part name for use in the Question class.
            questionnaire_dict[question]['part-audio'] = f'{part_id.zfill(2)}-questionnaire-'

            # Replace tab characters in the question text
            questionnaire_dict[question]['text'] = questionnaire_dict[question]['text'].replace('\t', '')

            # Convert multi for multiple-answer questions into a boolean, if it exists, otherwise set to False
            if 'multi' in questionnaire_dict[question]:
                questionnaire_dict[question]['multi'] = questionnaire_dict[question].as_bool('multi')
            else:
                questionnaire_dict[question]['multi'] = False

            # Obtain the index of the screen to place the question
            if manual_split:
                screen_num = str(int(questionnaire_dict[question]['manual screen']))
            else:
                screen_num = str(int(iq // 7))

            # Add this question's name to the correct screen in the screen_dict
            if screen_num not in screen_dict:
                screen_dict[screen_num] = [question]
            else:
                screen_dict[screen_num].append(question)

            # Generate a not-so-nice (but standardised) id.
            # Extract the user input part, audio and question names from the brackets
            question_id = question.replace('question ', '')
            # Put those together and add to the list
            qid = f'{part_id.zfill(2)}-questionnaire-{question_id.zfill(2)}'
            self.question_id_list.append(qid)
            questionnaire_dict[question]['id'] = qid

        # Store the split dictionary in the questionnaire dictionary
        questionnaire_dict['screen dict'] = screen_dict

        return questionnaire_dict

    def _prepare_part_audio(self, part: str, audio: str, question_overwrite: bool = False) -> None:
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
            # Add the ids of the questions to the list in this audio
            self[part][audio]['questions'] = self[part]['questions'].keys()

        # Extract the part, audio and question names
        part_id = part.replace('part ', '')
        audio_id = audio.replace('audio ', '')
        self[part][audio]['part-audio'] = f'{part_id.zfill(2)}-{audio_id.zfill(2)}'

        # Define the max number of replays
        if 'max replays' not in self[part][audio]:
            self[part][audio]['max replays'] = '1'
        # If that is more than 1, put counters in the question ID list.
        elif int(self[part][audio]['max replays']) > 1:
            if 'filename_2' in self[part][audio]:
                self.question_id_list.append(f'{self[part][audio]["part-audio"]}-replays-left')
                self.question_id_list.append(f'{self[part][audio]["part-audio"]}-replays-right')
            else:
                self.question_id_list.append(f'{self[part][audio]["part-audio"]}-replays')

        # Loop over the questions
        for question in self[part][audio]['questions']:
            # ==========================================================================================================
            # todo: DEPRECATED CODE
            # ---------------------
            if 'dependant' in self[part][audio][question]:
                warnings.warn_explicit('The keywords "dependant" and "dependant condition" will be removed '
                                       'in future versions. Please use the new system with "unlocked by" and "unlock '
                                       'condition" instead.',
                                       DeprecationWarning, f'{self.name}.palila', 0)
            # ==========================================================================================================

            # Identify the part and audio names for use in the Question class.
            self[part][audio][question]['part-audio'] = self[part][audio]['part-audio'] + '-'

            # Remove tabs from the input file in the question text
            self[part][audio][question]['text'] = self[part][audio][question]['text'].replace('\t', '')
            # TODO: Check where this multi is used, try to use in MultipleChoice questions
            # Convert multi into a boolean if it exists, otherwise set to False
            if 'multi' in self[part][audio][question]:
                self[part][audio][question]['multi'] = self[part][audio][question].as_bool('multi')
            else:
                self[part][audio][question]['multi'] = False

            # Generate a standardised question id
            # Extract the question name
            question_id = question.replace('question ', '')
            # Put everything together and add to the list
            qid = f'{part_id.zfill(2)}-{audio_id.zfill(2)}-{question_id.zfill(2)}'
            self.question_id_list.append(qid)
            self[part][audio][question]['id'] = qid

    def _prepare_part(self, ip: int, part: str, previous_part: str,
                      previous_audio: str, previous_name: str, ) -> tuple[str, str]:
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
            else f'Please take some time to refocus during this break.'
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
            add_break = break_interval != 0 and (ia + 1) % break_interval == 0 and (ia + 1) < len(self[part]['audios'])

            # If a break should be included
            if breaks and add_break:
                # Set the current audio and name accordingly
                audio = f'break {break_count}'
                current_name = f'{part}-{audio}'
                # Set the previous audio's 'next' to this break
                self[part][previous_audio]['next'] = current_name
                # Set up the current break dict
                self[part][current_name] = {'text': break_text, 'time': break_time,
                                            'previous': previous_name}
                # Up the break counter
                break_count += 1
                # Keep track of the last screen name and associated audio name
                previous_name = current_name
                previous_audio = current_name

        # ==========================================================================================================
        # PREPARATION OF THE PART QUESTIONNAIRE
        # ==========================================================================================================

        if 'questionnaire' in self[part].sections:
            current_name = f'{part}-questionnaire 1'
            audio = 'questionnaire'
            # Set the 'previous' and the last question's 'next'
            self[part][previous_audio]['next'] = current_name
            self[part][audio]['previous'] = previous_name

            self._prepare_questionnaire(self[part]['questionnaire'], part)

            previous_name = current_name
            previous_audio = audio

        if breaks and break_interval >= 0:
            # Set the current audio and name accordingly
            audio = f'break {break_count}'
            current_name = f'{part}-{audio}'
            # Set the previous audio's 'next' to this break
            self[part][previous_audio]['next'] = current_name
            # Set up the current break dict
            self[part][current_name] = {'text': break_text, 'time': break_time,
                                        'previous': previous_name}
            # Up the break counter
            break_count += 1

            previous_name = current_name
            previous_audio = current_name

        return previous_audio, previous_name

    def _prepare_experiment(self) -> None:
        """
        Put things in the dictionaries where they are needed for the ScreenManager to properly build the GUI.
        """
        # ==============================================================================================================
        # PREPARATION OF THE WELCOME AND GOODBYE MESSAGES
        # ==============================================================================================================

        if 'welcome' not in self.keys():
            # Add the default message if it is not defined in the input file
            self['welcome'] = 'Welcome to this listening experiment.\nPlease enter your participant ID:'
        else:
            # Fix the welcome message.
            self['welcome'] = self['welcome'].replace('\t', '')

        if 'goodbye' not in self.keys():
            # Add the default message if it is not defined in the input file
            self['goodbye'] = 'Thank you for your participation in this experiment!'
        else:
            # Fix the goodbye message.
            self['goodbye'] = self['goodbye'].replace('\t', '')

        if 'demo' not in self.keys():
            # Set up the demo variable
            self['demo'] = 'no'

        if 'override' not in self.keys():
            # Set up the demo variable
            self['override'] = 'no'

        # Prepare the main questionnaire
        self._prepare_questionnaire(self['questionnaire'], 'main')

        # Pre-define some values to start the parts loop
        previous_part = ''
        previous_audio = ''
        previous_name = 'main-questionnaire 1'

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

        # Initialise the indicator to show if the timer is running.
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
        """
        if self.out.loc['response', 'timer'] == '':
            print('No start time was set in the timer. Cannot determine completion time.')
        elif self.timing:
            self.timing = False
            self.out.loc['response', 'timer'] = str(time.time() - float(self.out.loc['response', 'timer']))
            print(f'Timer stopped at {datetime.datetime.now().strftime("%A %d %B %Y - %H:%M")}.\n'
                  f'Elapsed time was {str(round(float(self.out.loc["response", "timer"]) / 60)).zfill(2)}:'
                  f'{str(round(float(self.out.loc["response", "timer"]) % 60)).zfill(2)} minutes.')

        else:
            print('Timer has already stopped.')
