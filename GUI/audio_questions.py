from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.lang import Builder

Builder.load_file('GUI/audio_questions.kv')


class Filler(Widget):
    pass


class ChoiceButton(Button):
    def __init__(self, choice: str = '', **kwargs):
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


class NumScaleQuestion(BoxLayout):
    def __init__(self, question_dict: dict, **kwargs):
        super().__init__(**kwargs)

        self.question_dict = question_dict
        self.ids.question_text.text = question_dict['text']

        if 'left note' in question_dict.keys():
            self.ids.left_note.text = question_dict['left note']

        if 'right note' in question_dict.keys():
            self.ids.right_note.text = question_dict['right note']

        self.min = int(question_dict['min'])
        self.max = int(question_dict['max'])

        n_button = self.max - self.min + 1
        button_width = .65 / n_button

        for bi, bv in enumerate(range(self.min, self.max + 1)):
            pos_hint = {'center_x': (.175 + button_width / 2) + (bi * button_width), 'center_y': .5}

            button = ChoiceButton(choice=str(bv))
            self.ids.answer_options.add_widget(button)

            button.size_hint_x = .8 * button_width
            button.size_hint_y = .8 * button_width * 9
            button.pos_hint = pos_hint

        self.current_answer = None

    def select_choice(self, choice: ChoiceButton):
        if self.current_answer is not None:
            self.current_answer.deselect()

        if self.current_answer == choice:
            self.current_answer = None
        else:
            self.current_answer = choice


class PointCompassQuestion(BoxLayout):
    def __init__(self, question_dict: dict, **kwargs):
        super().__init__(**kwargs)

        self.question_dict = question_dict
        self.ids.question_text.text = question_dict['text']

        self.current_answer = None

    def on_size(self, *_):
        if self.parent.n_question > 1:
            raise OverflowError('PointCompass question takes 2 question slots.')

        self.parent.n_max = 1

    def select_choice(self, choice: ChoiceButton):
        if self.current_answer is not None:
            self.current_answer.deselect()

        if self.current_answer == choice:
            self.current_answer = None
        else:
            self.current_answer = choice
