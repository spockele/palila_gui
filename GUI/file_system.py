from configobj import ConfigObj
import pandas as pd
import datetime
import random
import os


__all__ = ['PalilaExperiment', 'PalilaAnswers']


class PalilaExperiment(ConfigObj):
    def __init__(self, name: str):
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
        for part in self['parts']:
            # Create a list of audios in the part dict
            self[part]['audios'] = [audio for audio in self[part] if 'audio' in audio]
            # Create a list of the questionnaire questions in the questionnaire dict
            self[part]['questionnaire']['questions'] = [question for question in self[part]['questionnaire'].sections
                                                        if 'question' in question]
            for audio in self[part]['audios']:
                # Create a list of questions in the audio dict
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

        # Check for the presence of a questionnaire.
        if 'questionnaire' not in self[part].sections:
            raise SyntaxError(f'Experiment {part} does not contain a final questionnaire.')

        # Check if the questionnaire is split properly
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
        # Check for the default keyword in the main questionnaire
        if 'default' in self['questionnaire'].keys():
            # Convert the default setting to a boolean
            self['questionnaire']['default'] = self['questionnaire'].as_bool('default')
        else:
            # Or assign False if it is not defined
            self['questionnaire']['default'] = False
        # Get the default questionnaire setup if that is set
        if self['questionnaire']['default']:
            # self['questionnaire'].clear()
            # Load the configfile
            self['questionnaire'].update(ConfigObj(os.path.join(os.path.abspath('GUI'), 'default_questionnaire.palila')))
            # Create a list of the questionnaire questions in the questionnaire dict
            self['questionnaire']['questions'] = [question for question in self['questionnaire'].sections
                                                  if 'question' in question]

        # Setup the questionnaire dictionary
        self['questionnaire']['previous'] = 'welcome'
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

        previous_part = ''
        previous_audio = ''
        previous_name = 'main-questionnaire'

        # Loop over all the experiment parts
        for ip, part in enumerate(self['parts']):
            # Set up the intro screen
            self[part]['intro']['previous'] = previous_name
            # And set the intro as the last added screen
            current_audio = 'intro'
            current_name = f'{part}-intro'
            # In case this is the first part, set the intro as the next of the questionnaire
            if not ip:
                self['questionnaire']['next'] = current_name
            # Otherwise, set the intro as the next of the last part's questionnaire
            else:
                self[previous_part][previous_audio]['next'] = current_name

            previous_name = current_name
            previous_audio = current_audio

            # Randomise the audios in this part if so desired
            if 'randomise' in self[part].keys() and self[part].as_bool('randomise'):
                random.shuffle(self[part]['audios'])

            # Loop over the audios
            for ia, audio in enumerate(self[part]['audios']):
                # Define the screen name
                current_name = f'{part}-{audio}'
                if not ia:
                    self[part]['intro']['next'] = current_name

                # Define this as following the previous
                self[part][previous_audio]['next'] = current_name
                # Define the previous as the previous of this audio
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

                # Set up all the questions in this audio
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

            # After setting up all audios of a part, set up the part questionnaire
            self[part][previous_audio]['next'] = f'{part}-questionnaire'
            self[part]['questionnaire']['previous'] = previous_name

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

            # Keep track of the last screen name and associated part
            previous_name = f'{part}-questionnaire'
            previous_audio = 'questionnaire'
            previous_part = part

        # Add the end screen as the next of the last questionnaire
        self[previous_part]['questionnaire']['next'] = 'end'


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
