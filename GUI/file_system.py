from configobj import ConfigObj
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
            if self[part].as_bool('randomise'):
                random.shuffle(self[part]['audios'])
