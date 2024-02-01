import pandas as pd
import datetime
import os

from .file_system import PalilaExperiment


class PalilaAnswers:
    def __init__(self, experiment: PalilaExperiment):
        self.experiment = experiment
        self.pid_mode = self.experiment['pid']

        self.out = pd.DataFrame(None, index=['response'], columns=self.experiment.question_id_list)

        if self.pid_mode == 'auto':
            self.pid = datetime.datetime.now().strftime('%y%m%d-%H%M')
            self.out_path = os.path.join(self.experiment.path, 'responses', f'{self.pid}.csv')
        else:
            self.pid = None

    def set_pid(self, pid: str) -> bool:
        """
        Function to set the participant ID from GUI input
        """
        if self.pid is not None:
            return True

        elif pid == '':
            return False

        else:
            self.pid = pid
            self.out_path = os.path.join(self.experiment.path, 'responses', f'{self.pid}.csv')
            return True
