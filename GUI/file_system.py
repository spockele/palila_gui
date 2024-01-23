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
            self._verify_part(part)
            if self[part].as_bool('randomise'):
                random.shuffle(self[part]['audios'])

    def _verify_part(self, part: str):
        if not self[part].sections:
            raise SyntaxError(f'Empty experiment part ("{part}") found in input file {self.name}.palila')

        if 'randomise' not in self[part].keys():
            self[part]['randomise'] = 'No'

        if not self[part]['audios']:
            warnings.warn(f'Experiment "{part}" does not contain any audio questions.')

        if 'questionnaire' not in self[part].sections:
            warnings.warn(f'Experiment "{part}" does not contain a final questionnaire.')

        for audio in self[part]['audios']:
            if 'max replays' not in self[part][audio].keys():
                self[part][audio]['max replays'] = '1'

            if 'filename' not in self[part][audio].keys():
                raise SyntaxError(f'No filename found for {part}: {audio}.')

            if not os.path.isfile(os.path.join(self.audio_path, self[part][audio]['filename'])):
                raise FileNotFoundError(f'Audio file {self[part][audio]["filename"]} not found for {part}: {audio}.')
