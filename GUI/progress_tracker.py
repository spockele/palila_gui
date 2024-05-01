from kivy.uix.floatlayout import FloatLayout
from kivy.lang.builder import Builder
from kivy.uix.progressbar import ProgressBar
from kivy.uix.widget import Widget


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
    pass


class Tracker(Widget):
    pass


class TrackFiller(Widget):
    pass


def construct_progress_tracker(progress: int, division: list[int]):
    total = sum(division)

    progress_bar = FloatLayout(size_hint=(1., .01, ), pos_hint={'x': 0, 'y': 0})
    progress_bar.add_widget(TrackFiller())

    tracker = Tracker(size_hint_x=progress / total)
    progress_bar.add_widget(tracker)

    pos = 0.
    for amount in division[:-1]:
        pos += amount / total
        progress_bar.add_widget(PartIndicator(pos_hint={'center_x': pos, 'y': 0}))

    return progress_bar
