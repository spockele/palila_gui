import threading
import time

from kivy.uix.progressbar import ProgressBar


__all__ = ['ProgressBarThread', ]


class ProgressBarThread(threading.Thread):
    """
    Thread subclass to manage the ProgressBar that times audio
    """
    def __init__(self, progress_bar: ProgressBar, **kwargs):
        """
        @param progress_bar: The ProgressBar object to be timed
        """
        super().__init__(**kwargs)
        self.progress_bar = progress_bar

    def run(self):
        # Set initial time
        t0 = time.time()
        dt = .1
        # Do while the time is below the max of the progress bar
        while time.time() - t0 <= self.progress_bar.max + dt:
            # Update the progress bar value
            self.progress_bar.value = time.time() - t0
            # # Hold to not overload the system
            time.sleep(dt)
