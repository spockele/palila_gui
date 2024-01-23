from configobj import ConfigObj
import os


__all__ = ['PalilaExperiment']


class PalilaExperiment(ConfigObj):
    def __init__(self, name: str):
        super().__init__(os.path.abspath(f'{name}.palila'))
        self.name = name
        self.audio_path = os.path.abspath(f'{name}')
