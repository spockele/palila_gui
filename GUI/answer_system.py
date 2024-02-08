import pandas as pd
import datetime
import os

from .file_system import PalilaExperiment


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
