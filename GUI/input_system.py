from configobj import ConfigObj


__all__ = ['PalilaExperiment']


class PalilaExperiment(ConfigObj):
    def __init__(self, name: str):
        super().__init__(f'{name}.palila')
        self.name = name
