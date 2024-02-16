from configobj import ConfigObj
import pandas as pd
import datetime
import random
import os


__all__ = ['PalilaExperiment', 'PalilaAnswers']


class PalilaExperiment(ConfigObj):
    """

    """
    def __init__(self, name: str):
        """

        """
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
            self[part]['audios'] = [audio for audio in self[part] if 'audio' in audio]
            # Create a list of questions in each audio dict
            for audio in self[part]['audios']:
                self[part][audio]['questions'] = [question for question in self[part][audio].sections]

        # Verify and prepare for the GUI
        self.verify_experiment()
        self._prepare_experiment()

    def verify_experiment(self):
        """
        Verification of the experiment input file to check if everything is present.
        """
        # Check that the experiment is not completely empty
        if not self.sections:
            raise SyntaxError(f'Empty experiment in input file {self.name}.palila')

        # Check for the presence of a startup questionnaire.
        if 'questionnaire' not in self.sections:
            raise SyntaxError(f'Experiment does not contain a startup questionnaire.')

        # Check if the questionnaire is split properly
        if 'manual_split' in self['questionnaire']:
            self['questionnaire']['manual_split'] = self['questionnaire'].as_bool('manual_split')
            if self['questionnaire']['manual_split']:
                for question in self['questionnaire'].sections:
                    if 'manual_screen' not in self['questionnaire'][question]:
                        raise SyntaxError('If manual split is set, each questionnaire question requires '
                                          'an assigned screen.')
        else:
            self['questionnaire']['manual_split'] = False

        # Check for the presence of experiment parts
        if not self['parts']:
            raise SyntaxError(f'Experiment does not contain any parts.')

        # Verify the individual experiment parts
        for part in self['parts']:
            self._verify_part(part)

    def _verify_part(self, part: str):
        """
        Verification of the experiment part from the input file to check if everything is present.
        """
        # Check that the part is not completely empty
        if not self[part].sections:
            raise SyntaxError(f'Empty experiment part ("{part}") found in input file {self.name}.palila')

        # Check that the part contains audio questions.
        if not self[part]['audios']:
            raise SyntaxError(f'Experiment {part} does not contain any audio questions.')

        # Check if the questionnaire is split properly
        if 'questionnaire' in self[part].sections:
            if 'manual_split' in self[part]['questionnaire']:
                self[part]['questionnaire']['manual_split'] = self[part]['questionnaire'].as_bool('manual_split')
                if self[part]['questionnaire']['manual_split']:
                    for question in self[part]['questionnaire'].sections:
                        if 'manual_screen' not in self[part]['questionnaire'][question]:
                            raise SyntaxError('If manual split is set, each questionnaire question requires '
                                              'an assigned screen.')
            else:
                self[part]['questionnaire']['manual_split'] = False

        # Check the individual audios in the experiment part
        for audio in self[part]['audios']:
            if 'filename' not in self[part][audio].keys():
                raise SyntaxError(f'No filename found for {part}: {audio}.')

            if not os.path.isfile(os.path.join(self.path, self[part][audio]['filename'])):
                raise FileNotFoundError(f'Audio file {self[part][audio]["filename"]} not found for {part}: {audio}.')

    def _prepare_experiment(self):
        """
        Put things in the dictionaries where they are needed for the ScreenManager to properly build the GUI.
        """
        # ==============================================================================================================
        # PREPARATION OF THE MAIN QUESTIONNAIRE
        # ==============================================================================================================

        if 'welcome' not in self.keys():
            self['welcome'] = 'Welcome to this listening experiment.\nPlease enter your participant ID:'
        else:
            # Fix the welcome message.
            self['welcome'] = self['welcome'].replace('\t', '')

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

        # ==============================================================================================================
        # PREPARATION OF THE EXPERIMENT PARTS
        # ==============================================================================================================

        # Pre-define some values to start the loop
        previous_part = ''
        previous_audio = ''
        previous_name = 'main-questionnaire'

        # Loop over all the experiment parts
        for ip, part in enumerate(self['parts']):
            # Set the intro as the current added screen
            audio = 'intro'
            current_name = f'{part}-intro'

            # Add the default intro if it's not in the config file
            if 'intro' not in self[part].sections:
                self[part]['intro'] = {'text': f'You have reached part {ip + 1} of the experiment.\n'
                                               f'Press "Continue" below to resume the experiment.'}

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
            # PREPARATION OF THE PART AUDIOS
            # ==========================================================================================================

            # Randomise the audios in this part if so desired
            if 'randomise' in self[part].keys() and self[part].as_bool('randomise'):
                random.shuffle(self[part]['audios'])

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

                # Define the full filepath of the audio
                self[part][audio]['filepath'] = os.path.join(self.path, self[part][audio]['filename'])

                # Define the max number of replays
                if 'max replays' not in self[part][audio].keys():
                    self[part][audio]['max replays'] = '1'

                # Extract the filler option
                if 'filler' not in self[part][audio].keys():
                    self[part][audio]['filler'] = True
                else:
                    self[part][audio]['filler'] = self[part][audio].as_bool('filler')

                # ======================================================================================================
                # PREPARATION OF THE AUDIO QUESTIONS
                # ======================================================================================================

                for question in self[part][audio]['questions']:
                    # Remove tabs from the input file in the question text
                    self[part][audio][question]['text'] = self[part][audio][question]['text'].replace('\t', '')

                    # Extract the id to the overall question id list
                    if 'id' in self[part][audio][question]:
                        self.question_id_list.append(self[part][audio][question]['id'])
                    # Generate a not-so-nice (but standardised) id when it's not defined explicitly
                    else:
                        # Extract the user input part, audio and question names from the brackets
                        part_id = part.replace('part ', '')
                        audio_id = audio.replace('audio ', '')
                        question_id = question.replace('question ', '')
                        # Put those together and add to the list
                        qid = f'{part_id.zfill(2)}-{audio_id.zfill(2)}-{question_id.zfill(2)}'
                        self.question_id_list.append(qid)
                        self[part][audio][question]['id'] = qid

                # Keep track of the last screen name and associated audio name
                previous_name = current_name
                previous_audio = audio

            # ==========================================================================================================
            # PREPARATION OF THE PART QUESTIONNAIRE
            # ==========================================================================================================
            # Set the intro as the current added screen
            current_name = f'{part}-questionnaire'
            audio = 'questionnaire'

            if 'questionnaire' in self[part].sections:
                # Set the 'previous' and the last question's 'next'
                self[part][previous_audio]['next'] = current_name
                self[part][audio]['previous'] = previous_name

                # Create a list of the questionnaire questions in the questionnaire dict
                self[part]['questionnaire']['questions'] = [question for question in
                                                            self[part]['questionnaire'].sections
                                                            if 'question' in question]

                # Set up the part questionnaire questions
                for iq, question in enumerate(self[part]['questionnaire']['questions']):
                    self[part]['questionnaire'][question]['text'] = self[part]['questionnaire'][question]['text'].replace('\t', '')

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

                # Set the questionnaire as the last screen that was added
                previous_name = current_name
                previous_audio = audio

            # Set this part as the last that was added
            previous_part = part

        # Add the end screen as the 'next' of the last screen
        self[previous_part][previous_audio]['next'] = 'end'


class PalilaAnswers:
    """
    Class managing the participant responses
    """
    def __init__(self, experiment: PalilaExperiment):
        # Store the experiment inside this class
        self.experiment = experiment
        self.pid_mode = self.experiment['pid']
        # Set up the output dataframe
        self.out = pd.DataFrame(None, index=['response'], columns=self.experiment.question_id_list)

        # Initialise the PID in case of auto mode
        if self.pid_mode == 'auto':
            self.pid = datetime.datetime.now().strftime('%y%m%d-%H%M')
            self.out_path = os.path.join(self.experiment.path, 'responses', f'{self.pid}.csv')
        else:
            self.pid = None

    def set_pid(self, pid: str) -> None:
        """
        Function to set the participant ID from GUI input
        """
        self.pid = pid
        self.out_path = os.path.join(self.experiment.path, 'responses', f'{self.pid}.csv')

    def save_to_file(self) -> None:
        """
        Save the answers to the set file
        """
        self.out.to_csv(self.out_path)
