import typing

from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from time import time

from ExpApp.Utils.PhraseSelector import PhraseSelector

button_style = "border: 3px outset gray; border-style: outset;"

input_style = "border: 3px outset grey;" \
              "border-top-left-radius: 10px;" \
              "border-bottom-left-radius: 10px;" \
              "border-style: outset;" \
              "padding-left: 10px"

right_button_style = "border: 3px outset grey; " \
                     "border-top-right-radius: 10px;" \
                     "border-bottom-right-radius: 10px;" \
                     "border-style: outset;"


class MyInputBox(QLabel):
    buttonClicked = pyqtSignal(bool)

    def __init__(self, parent=None, ar_mode=False, reset=None):
        super(MyInputBox, self).__init__(parent)

        self.ar_mode = ar_mode
        self.reset_func = reset
        self.input_box = QTextEdit(self)
        self.input_box.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.input_box.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.input_box.setStyleSheet(input_style)
        self.input_box.setFocus()

        self.selector = PhraseSelector()

        self.target_text = "smart" #self.selector.select_word()
        self.input_text = ""
        self.markup_text()

        self.clear_button = QPushButton(self)
        self.clear_button.setText("Clear")
        self.clear_button.setStyleSheet(button_style)
        self.clear_button.clicked.connect(self.clear_input)

        self.phrase_button = QPushButton(self)
        self.phrase_button.setText("Reset" if self.ar_mode else "Phrase")
        self.phrase_button.setStyleSheet(button_style)
        self.phrase_button.clicked.connect(self.set_reference)

        self.word_button = QPushButton(self)
        self.word_button.setText("Word")
        self.word_button.setStyleSheet(right_button_style)
        self.word_button.clicked.connect(self.update_target_word)

        if self.ar_mode:
            for button in [self.clear_button, self.phrase_button, self.word_button]:
                button.setStyleSheet(
                    button.styleSheet() + "color: white;"
                )

        self.start_time = 0
        self.log = []
        self.is_log_recorded = False
        self.count = 1

    def set_reference(self):
        if not self.ar_mode:
            self.input_text = ""
            self.target_text = "the weather should become better today"
            self.markup_text()
        elif callable(self.reset_func):
            self.reset_func()

    def update_target_word(self):
        self.input_text = ""
        self.target_text = self.selector.select_word()
        self.markup_text()

    def update_target_phrase(self):
        self.input_text = ""
        self.target_text = self.selector.select_phrase()
        self.markup_text()

    def clear_input(self):
        self.input_text = ""
        self.markup_text()

    def setGeometry(self, x, y, width, height) -> None:
        super().setGeometry(x, y, width, height)
        self.input_box.setGeometry(0, 0, int(width * 0.74), height)
        font = self.input_box.font()
        font.setPointSize(int(height * 0.5))
        self.input_box.setFont(font)
        current_x = self.input_box.width()
        button_width = (width - current_x) // 3
        self.clear_button.setGeometry(current_x, 0, button_width, height)
        self.phrase_button.setGeometry(current_x + button_width, 0, button_width, height)
        self.word_button.setGeometry(current_x + button_width * 2, 0, button_width, height)
        font.setPointSize(int(height * 0.25))
        self.clear_button.setFont(font)
        self.phrase_button.setFont(font)
        self.word_button.setFont(font)

    @staticmethod
    def get_log_header():
        return "Target; Input; Time; Error rate; Used suggestion\n"

    @staticmethod
    def calculate_error_rate(s1: str, s2: str):
        s1.strip()
        s2.strip()
        s = zip(s1, s2)
        errors = 0
        for i, j in s:
            errors += 0 if i == j else 1

        return errors / len(s1)

    def setText(self, text: str, is_suggested=0) -> None:
        self.input_text = text
        if len(self.input_text) == 1:
            self.is_log_recorded = False
            self.start_time = time()
        elif len(self.input_text) >= len(self.target_text) and not self.is_log_recorded:
            error_rate = self.calculate_error_rate(self.target_text, self.input_text)
            log = f'{self.target_text};{self.input_text};{time() - self.start_time};{error_rate};{is_suggested}'
            self.log.append(log)
            self.is_log_recorded = True
            print(f'{self.count}: ' + log)
            self.count += 1
        self.markup_text()

    def get_log(self):
        avg_time = 0
        avg_error = 0
        for entry in self.log:
            avg_time += float(entry.split(";")[2])
            avg_error += float(entry.split(";")[3])
        self.count -= 1
        print(f"Average wpm: {60 / (avg_time / self.count)}; average error rate: {avg_error / self.count}")
        self.count = 1
        res = self.log
        self.log = []
        return res

    def text(self):
        return self.input_text

    def markup_text(self):
        self.input_box.clear()
        self.input_box.setTextColor(Qt.white if self.ar_mode else Qt.black)
        self.input_box.insertPlainText(self.input_text)
        self.input_box.setTextColor(Qt.gray)
        self.input_box.insertPlainText(self.target_text[len(self.input_text):])

        self.input_box.setFocus()
        cursor = self.input_box.textCursor()
        cursor.setPosition(len(self.input_text))
        self.input_box.setTextCursor(cursor)
