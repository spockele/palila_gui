from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget

Builder.load_file('GUI/audio_questions.kv')


class Filler(Widget):
    pass


class TextQuestion(BoxLayout):
    def __init__(self, question_dict: dict, **kwargs):
        super().__init__(**kwargs)

        self.question_dict = question_dict
        self.ids.question_text.text = question_dict['text']
