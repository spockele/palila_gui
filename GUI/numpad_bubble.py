from kivy.uix.behaviors.focus import FocusBehavior
from kivy.uix.widget import Widget
from kivy.uix.bubble import Bubble
from kivy.lang import Builder


Builder.load_file('GUI/numpad_bubble.kv')


class NumPadBubble(Bubble):
    def __init__(self, coupled_widget: Widget, **kwargs):
        super().__init__(**kwargs)
        self.coupled_widget = coupled_widget
        self.active = False

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            FocusBehavior.ignored_touch.append(touch)
        else:
            self.parent.remove_widget(self)
            
        super().on_touch_down(touch)

    def add_text(self, value: str):
        self.coupled_widget.text += value

    def remove_text(self):
        self.coupled_widget.text = self.coupled_widget.text[:-1]
