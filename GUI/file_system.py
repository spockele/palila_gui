from configobj import ConfigObj
import warnings
import random
import os


__all__ = ['PalilaExperiment']


class PalilaExperiment(ConfigObj):
    def __init__(self, name: str):
        super().__init__(os.path.abspath(f'{name}.palila'))
        self.name = name
        self.audio_path = os.path.abspath(f'{name}')

        self['parts'] = [part for part in self.sections if 'part' in part]
        for part in self['parts']:
            self[part]['audios'] = [audio for audio in self[part] if 'audio' in audio]

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

            if not os.path.isfile(os.path.join(self.audio_path, self[part][audio]['filename'])):
                raise FileNotFoundError(f'Audio file {self[part][audio]["filename"]} not found for {part}: {audio}.')

    def _prepare_experiment(self):
        """
        Put things in the dictionaries where they are needed for the ScreenManager to properly build the GUI.
        """
        previous_part = ''
        previous_audio = ''
        previous_name = ''

        self['questionnaire']['previous'] = 'start'

        for ip, part in enumerate(self['parts']):
            if self[part].as_bool('randomise'):
                random.shuffle(self[part]['audios'])

            for ia, audio in enumerate(self[part]['audios']):
                current_name = f'{part}-{audio}'
                self[part][audio]['filepath'] = os.path.join(self.audio_path, self[part][audio]['filename'])

                if previous_part == '' and previous_audio == '':
                    self['questionnaire']['next'] = current_name
                    self[part][audio]['previous'] = 'questionnaire'

                elif not ia:
                    self[previous_part]['questionnaire']['next'] = current_name
                    self[part][audio]['previous'] = previous_name

                else:
                    self[part][previous_audio]['next'] = current_name
                    self[part][audio]['previous'] = previous_name

                previous_name = current_name
                previous_audio = audio

            self[part][previous_audio]['next'] = f'{part}-questionnaire'
            self[part]['questionnaire']['previous'] = previous_name

            previous_name = f'{part}-questionnaire'
            previous_part = part

        self[previous_part]['questionnaire']['next'] = 'end'
