"""
Module containing the Python code of the pop-up NumPad Bubble.
"""
from kivy.uix.behaviors.focus import FocusBehavior
from kivy.uix.bubble import Bubble


__all__ = ['NumPadBubble', ]


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
