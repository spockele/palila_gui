import pandas as pd

from .file_system import PalilaExperiment


class PalilaAnswers:
    def __init__(self, experiment: PalilaExperiment):
        self.experiment = experiment

        self.answers = pd.DataFrame(columns=self.experiment.question_id_list)
