from kivy.uix.behaviors.focus import FocusBehavior
from kivy.uix.bubble import Bubble
from kivy.lang import Builder


Builder.load_file('GUI/numpad_bubble.kv')


class NumPadBubble(Bubble):
    """

    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.coupled_widget = None

    def on_touch_down(self, touch):
        """

        """
        if self.collide_point(*touch.pos):
            FocusBehavior.ignored_touch.append(touch)
        elif not self.coupled_widget.collide_point(*touch.pos):
            self.parent.remove_widget(self)

        super().on_touch_down(touch)

    def add_text(self, value: str):
        """

        """
        if self.coupled_widget is not None:
            self.coupled_widget.text += value

    def remove_text(self):
        """

        """
        if self.coupled_widget is not None:
            self.coupled_widget.text = self.coupled_widget.text[:-1]
