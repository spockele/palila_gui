"""
Module containing all the threading.Thread based tools for the GUI.
"""
from kivy.uix.progressbar import ProgressBar
import threading
import time


__all__ = ['ProgressBarThread', ]


class ProgressBarThread(threading.Thread):
    """
    Thread subclass to manage a timed ProgressBar.

    Parameters
    ----------
    progress_bar : ProgressBar
        ProgressBar instance to keep track of.
    **kwargs
        Keyword arguments. These are passed on to the threading.Thread constructor.

    Attributes
    ----------
    progress_bar : ProgressBar
        ProgressBar instance to keep track of.
    """
    def __init__(self, progress_bar: ProgressBar, **kwargs):
        super().__init__(**kwargs)
        self.progress_bar = progress_bar

    def run(self) -> None:
        """
        Run function of the Thread. Will update the progress bar every 0.1 seconds until it is full.
        """
        # Set initial time
        t0 = time.time()
        dt = .1
        # Do while the time is below the max of the progress bar
        while time.time() - t0 <= self.progress_bar.max + dt:
            # Update the progress bar value
            self.progress_bar.value = time.time() - t0
            # # Hold to not overload the system
            time.sleep(dt)
