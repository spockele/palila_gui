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

        for part in self['parts']:
            # Create a list of audios in the part dict
            self[part]['audios'] = [audio for audio in self[part] if 'audio' in audio]

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

        # Check for the "randomise" trigger
        if 'randomise' not in self[part].keys():
            self[part]['randomise'] = 'No'

        # Check that the part contains audio questions.
        if not self[part]['audios']:
            raise SyntaxError(f'Experiment {part} does not contain any audio questions.')

        # Check for the presence of a questionnaire.
        if 'questionnaire' not in self[part].sections:
            raise SyntaxError(f'Experiment {part} does not contain a final questionnaire.')

        # Check the individual audios in the experiment part
        for audio in self[part]['audios']:
            if 'max replays' not in self[part][audio].keys():
                self[part][audio]['max replays'] = '1'

            if 'filename' not in self[part][audio].keys():
                raise SyntaxError(f'No filename found for {part}: {audio}.')

            if not os.path.isfile(os.path.join(self.path, self[part][audio]['filename'])):
                raise FileNotFoundError(f'Audio file {self[part][audio]["filename"]} not found for {part}: {audio}.')

            if 'filler' not in self[part][audio].keys():
                self[part][audio]['filler'] = 'yes'

    def _prepare_experiment(self):
        """
        Put things in the dictionaries where they are needed for the ScreenManager to properly build the GUI.
        """
        previous_part = ''
        previous_audio = ''
        previous_name = ''

        # Add the start screen to the previous property of the initial questionnaire
        self['questionnaire']['previous'] = 'welcome'
        if 'default' in self['questionnaire'].keys():
            self['questionnaire']['default'] = self['questionnaire'].as_bool('default')

        # Loop over all the experiment parts
        for ip, part in enumerate(self['parts']):
            # Randomise the audios in this part if so desired
            if self[part].as_bool('randomise'):
                random.shuffle(self[part]['audios'])

            if 'default' in self[part]['questionnaire'].keys():
                self[part]['questionnaire']['default'] = self[part]['questionnaire'].as_bool('default')

            # Loop over the audios
            for ia, audio in enumerate(self[part]['audios']):
                # Define the screen name
                current_name = f'{part}-{audio}'
                # Define the full filepath of the audio
                self[part][audio]['filepath'] = os.path.join(self.path, self[part][audio]['filename'])

                self[part][audio]['filler'] = self[part][audio].as_bool('filler')

                # If this is the first audio ever
                if previous_part == '' and previous_audio == '':
                    # Set this one as the one following the initial questionnaire
                    self['questionnaire']['next'] = current_name
                    # Set the initial questionnaire as the previous of this audio
                    self[part][audio]['previous'] = 'questionnaire'

                # If this is the first audio of a part
                elif not ia:
                    # Set this one as the one following the previous part questionnaire
                    self[previous_part]['questionnaire']['next'] = current_name
                    # Set the previous part questionnaire as the previous of this audio
                    self[part][audio]['previous'] = previous_name

                # In all other cases
                else:
                    # Define this as following the previous
                    self[part][previous_audio]['next'] = current_name
                    # Define the previous as the previous of this audio
                    self[part][audio]['previous'] = previous_name

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
                        qid = f'qid-{part_id}-{audio_id}-{question_id}'
                        self.question_id_list.append(qid)
                        self[part][audio][question]['id'] = qid

                # Keep track of the last screen name and associated audio name
                previous_name = current_name
                previous_audio = audio

            # After setting up all audios of a part, set up the part questionnaire
            self[part][previous_audio]['next'] = f'{part}-questionnaire'
            self[part]['questionnaire']['previous'] = previous_name

            # Keep track of the last screen name and associated part
            previous_name = f'{part}-questionnaire'
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
