"""
Module with the code for smaller tools used by parts of the GUI.
"""

# Copyright (c) 2025 Josephine Siebert Pockelé
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from kivy.uix.behaviors.focus import FocusBehavior
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.progressbar import ProgressBar
from kivy.properties import ListProperty
from kivy.uix.widget import Widget
from kivy.uix.bubble import Bubble

import threading
import time


__all__ = ['ProgressTracker', 'ProgressBarThread', 'NumPadBubble', ]


class PartIndicator(Widget):
    """
    Class for a component of the progress tracking bar.
    """
    pass


class Tracker(Widget):
    """
    Class for a component of the progress tracking bar.
    """
    rgba = ListProperty([0, 118 / 255, 194 / 255, 1.])


class TrackFiller(Widget):
    """
    Class for a component of the progress tracking bar.
    """
    pass


class ProgressTracker(FloatLayout):
    """
    Class containing the progress tracker of the experiment.

    Parameters
    ----------
    screen_names: list[str]
        List of screen names obtained from Kivy.screenmanager.ScreenManager.screen_names

    Attributes
    ----------
    division: dict[str: int]
        Dictionary linking screen names to their division, used as lookup table in track().
    counts: dict[str: int]
        Dictionary containing the total number of screens per division.
    tracker: dict[str: int]
        Dictionary to track the progress through each division.
    completed_screens: list[str]
        List to track the names of completed screens, to avoid double registrations in track().
    tracker_widgets: dict[int: Tracker]
        Dictionary with the tracking widgets per division.
    total: int
        Total number of screens this tracker accounts for.
    """
    def __init__(self, screen_names: list[str], **kwargs) -> None:
        super().__init__(**kwargs)

        # Initialise variables
        self.division: dict[str: int] = dict[str: int]()
        self.counts: dict[str: int] = dict[str: int]()
        self.tracker: dict[str: int] = dict[str: int]()
        self.completed_screens: list[str] = list[str]()
        self.tracker_widgets: dict[int: Tracker] = dict[int: Tracker]()
        self.total = len(screen_names)

        # Add a background fill to the tracker.
        self.add_widget(TrackFiller())

        # Go over the screen names list
        for name in screen_names:
            # Split the name by the dash
            split = name.split('-')
            if len(split) == 2:
                # Determine the division from the first part of the split name.
                div = split[0]
                # Store the division in the lookup table.
                self.division[name] = div

                if div in self.counts:
                    self.counts[div] += 1
                else:
                    self.counts[div] = 1
                    self.tracker[div] = 0

            # In case the name contains no division, subtract from the total.
            else:
                self.total -= 1

        # Work through the divisions
        pos = 0
        for div, count in self.counts.items():
            # Make the tracker widget and put it in the correct position. (making sure not to overlap the dashes)
            x = pos + .003 / 2 if pos else pos
            widget = Tracker(pos_hint={'x': x, 'y': 0}, size_hint_x=0.)

            self.add_widget(widget)
            self.tracker_widgets[div] = widget

            # Put a dash to indicate the end of a part.
            pos += count / self.total
            if pos <= 0.999:
                self.add_widget(PartIndicator(pos_hint={'center_x': pos, 'y': 0}))

    def track(self, screen_name: str, back_to_main_questionnaire: bool = False) -> None:
        """

        Parameters
        ----------
        screen_name: str
        back_to_main_questionnaire: bool, optional (default=False)

        """
        # Reset the main questionnaire part of the tracker when returning there from the end screen.
        if back_to_main_questionnaire:
            self.tracker['main'] = 0
            self.tracker_widgets['main'].size_hint_x = 0.
            self.tracker_widgets['main'].rgba = [0, 118 / 255, 194 / 255, 1.]
            self.completed_screens = [screen for screen in self.completed_screens if 'main-questionnaire' not in screen]

        # If the screen is not in the completed list yet
        if screen_name not in self.completed_screens:
            self.completed_screens.append(screen_name)

            # If the screen name is in the division dictionary.
            if screen_name in self.division:
                div = self.division[screen_name]

                # Add one to the tracker of the current division.
                self.tracker[div] += 1

                # Update the size of the tracker widget for the current division.
                new_size = (self.tracker[div] / self.counts[div]) * (self.counts[div] / self.total)
                self.tracker_widgets[div].size_hint_x = new_size

        # Do a check for any full trackers, and set to green if full.
        for div, widget in self.tracker_widgets.items():
            if self.tracker[div] == self.counts[div]:
                widget.rgba = [.4, .8, .4, 1]


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


class NumPadBubble(Bubble):
    """
    A pop-up numpad that is linked to a widget.

    Parameters
    ----------
    **kwargs
        Keyword arguments. These are passed on to the kivy.uix.bubble.Bubble constructor.

    Attributes
    ----------
    coupled_widget : kivy.uix.widget.Widget
        The widget to which the NumPadBubble is linked. The NumPad will edit text in this Widget
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.coupled_widget = None

    def on_touch_down(self, touch):
        """
        Overload of on_touch_down method. Manages the focus and whether to remove this widget based on touch location.
        """
        if self.collide_point(*touch.pos):
            FocusBehavior.ignored_touch.append(touch)
        elif not self.coupled_widget.collide_point(*touch.pos):
            self.parent.remove_widget(self)

        super().on_touch_down(touch)

    def add_text(self, value: str):
        """
        Function linked to the number buttons, to enter the number to the coupled widget's text.
        """
        if self.coupled_widget is not None:
            self.coupled_widget.text += value

    def remove_text(self):
        """
        Function linked to the backspace button, to remove the last number in the coupled widget's text.
        """
        if self.coupled_widget is not None:
            self.coupled_widget.text = self.coupled_widget.text[:-1]
