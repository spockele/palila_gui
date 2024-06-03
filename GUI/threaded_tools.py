"""
Copyright (c) 2024 Josephine Siebert Pockelé

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

------------------------------------------------------------------------------------------------------------------------

Module containing all the threading.Thread based tools for the GUI.

------------------------------------------------------------------------------------------------------------------------
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
    def __init__(self, progress_bar: ProgressBar, **kwargs) -> None:
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
