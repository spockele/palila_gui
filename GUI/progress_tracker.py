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

Module with the code to set the progressbar at the bottom of the audio screens.

------------------------------------------------------------------------------------------------------------------------
"""
from kivy.uix.floatlayout import FloatLayout
from kivy.lang.builder import Builder
from kivy.uix.widget import Widget


# The kivy language string to be used.
Builder.load_string(
    '''
<PartIndicator>:
    size_hint: .003, 1., 
    
    canvas:
        Color:
            rgba: (.2, .2, .2, 1.)
        Rectangle:
            pos: self.pos
            size: self.size

<AudioIndicator>:
    size_hint: .003, 1., 
    
    canvas:
        Color:
            rgba: (.2, .2, .2, 1.)
        Rectangle:
            pos: self.pos
            size: self.size
            
<Tracker>
    pos_hint: {'x': 0, 'y': 0}
    size_hint_y: .6
    
    canvas:
        Color:
            rgba: (0, 118 / 255, 194 / 255, 1.)
        Rectangle:
            pos: self.pos
            size: self.size
          
<TrackFiller>
    pos_hint: {'x': 0, 'y': 0}
    size_hint: 1., .6, 
    
    canvas:
        Color:
            rgba: (.7, .7, .7, 1.)
        Rectangle:
            pos: self.pos
            size: self.size
    '''
)


class PartIndicator(Widget):
    """
    Class for a component of the progress tracking bar.
    """
    pass


class Tracker(Widget):
    """
    Class for a component of the progress tracking bar.
    """
    pass


class TrackFiller(Widget):
    """
    Class for a component of the progress tracking bar.
    """
    pass


def construct_progress_tracker(progress: int, division: list[int]) -> FloatLayout:
    """
    Constructs a FloatLayout with the progress bar that is filled according to the given progress
    and division indicators.

    Parameters
    ----------
    progress : int
        Integer indicating what amount of progress to show on the progress bar.
    division: list[int]
        List containing the number of audio screens per parts. This will divide the progress bar into sections.

    Returns
    -------
    The FloatLayout with the progress bar filled according to the parameters.
    """
    # Sm the total number of audio screens for determining the endpoint of the progress tracker
    total = sum(division)
    # Create the empty FloatLayout for the tracker and add the filler for the background.
    progress_bar = FloatLayout(size_hint=(1., .01, ), pos_hint={'x': 0, 'y': 0})
    progress_bar.add_widget(TrackFiller())

    # Create the tracker widget with the correct size and add it to the layout
    tracker = Tracker(size_hint_x=progress / total)
    progress_bar.add_widget(tracker)

    # Start at 0
    pos = 0.
    # Loop over the division to add the ticks on the progressbar.
    for amount in division[:-1]:
        # Determine the tick position with the same method as the progress tracker
        pos += amount / total
        # Add the tick to the progressbar
        progress_bar.add_widget(PartIndicator(pos_hint={'center_x': pos, 'y': 0}))

    # Return the progress bar for addition to a screen
    return progress_bar
