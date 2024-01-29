from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.button import Button

Builder.load_file('GUI/audio_questions.kv')


class Filler(Widget):
    pass


class ChoiceButton(Button):
    def __init__(self, choice: str, **kwargs):
        super().__init__(text=choice, **kwargs)

    def select(self) -> None:
        self.background_color = [.5, 1, .5, 1]

    def deselect(self) -> None:
        self.background_color = [1, 1, 1, 1]

    def on_release(self):
        self.select()
        self.parent.parent.select_choice(self)


class TextQuestion(BoxLayout):
    def __init__(self, question_dict: dict, **kwargs):
        super().__init__(**kwargs)

        self.question_dict = question_dict
        self.ids.question_text.text = question_dict['text']


class MultipleChoiceQuestion(BoxLayout):
    def __init__(self, question_dict: dict, **kwargs):
        super().__init__(**kwargs)

        self.question_dict = question_dict
        self.ids.question_text.text = question_dict['text']

        self._add_choices()
        self.current_answer = None

    def _add_choices(self):
        for choice in self.question_dict['choices']:
            self.ids.answer_options.add_widget(ChoiceButton(choice))

    def select_choice(self, choice: ChoiceButton) -> None:
        if self.current_answer is not None:
            self.current_answer.deselect()

        if self.current_answer == choice:
            self.current_answer = None
        else:
            self.current_answer = choice
