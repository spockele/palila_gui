from configparser import ConfigParser
import os


__all__ = ['ExperimentParser']


class ExperimentParser(ConfigParser):
    def __init__(self, name: str, **kwargs):
        super().__init__(**kwargs)

        self.name = name
        if not os.path.isdir(f'{name}'):
            raise NotADirectoryError(f'No directory "{name}" found. '
                                     f'Make sure the input file and input directory have the same name.')

        if not os.path.isfile(f'{name}.palila'):
            raise FileNotFoundError(f'No file "{name}.palila" found.')

        self.read(f'{name}.palila')

    def __repr__(self):
        return f'<Experiment: {self.name}, SECTIONS: {self.sections()}>'
