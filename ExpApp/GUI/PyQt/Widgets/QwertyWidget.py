import os
import sys
import threading

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from EMG.EMGConnector import EMGConnector
from ExpApp.Utils import IMUUtils

from ExpApp.Utils.EasyPredictor import EasyPredictor
# from ExpApp.Utils.DummyPredictor import EasyPredictor
from ExpApp.Utils.VKeyboard import VKeyboard
from ExpApp.Utils.datacore_constants import INPUT_SET, KeyboardControl
from ExpApp.Utils.dictionary import Dictionary


class Communicate(QObject):
    data_signal = pyqtSignal(list)


ANGLE_RANGE = 70  # 20 .. 45

STEP = 4
MARGIN = STEP * 10
MAX_W = STEP * 400
MAX_H = STEP * 120
KEY_W = STEP * 20
KEY_H = STEP * 20
KEY_M = STEP * 2
KEY_EXTENSION = int(KEY_W * 2)
PICKER_THICKNESS = STEP / 2

_BLUE_COLOR = 0x3498DB
SLIDEBAR_W = MAX_W - 210
HIGHLIGHT_COLOR = "c9e9ff"

HIGHLIGHT_PALETTE = [
    "cfe1ff",
    "abcaff",
    "7aabff",
]

button_style = "border: 1px outset grey; border-radius: 10px; border-style: outset;"


class QwertyWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.init_communicators()
        self.frame = 1
        self.gesture = None
        self.vkeyboard = VKeyboard(config=KeyboardControl.configQ)
        model_path = os.path.dirname(__file__) + "/../../../datacore/cnn_qwerty_debug"
        self.predictor = EasyPredictor(_set=INPUT_SET, model_path=model_path)
        self._rows = len(self.vkeyboard.key_config[0])
        self._columns = len(self.vkeyboard.key_config)
        self.selected_column = self._columns - 1
        self.keyboard_active = False
        self.init_ui()
        self.right_yaw = 6
        self.left_yaw = 2
        self.yaw = self.right_yaw
        self.imu_set = False
        self.imu_fix = False
        self.tip_position = self.slidebar.width() - 10
        self.suggestion_votes = [0] * 3

    def init_communicators(self):
        self.communicator = Communicate()
        my_data_loop = threading.Thread(daemon=True,
                                        name='my_data_loop',
                                        target=self.data_send_loop,
                                        args=(self.receive_data,))
        my_data_loop.start()

    def init_ui(self):

        self.setStyleSheet("background: white")
        self.setGeometry(80, 80, MAX_W, MAX_H)

        # input line
        self.input_display = QLineEdit(self)
        self.input_display.setText("")
        self.input_display.setGeometry(MARGIN, MARGIN, MAX_W - MARGIN * 2, STEP * 14)
        self.input_display.setStyleSheet("background: none")
        self.input_display.setFocus()
        fontParam = self.input_display.font()
        fontParam.setPointSize(8 * STEP)
        self.input_display.setFont(fontParam)

        # sliding tip representing MYO orientation
        self.slidebar = QLabel(self)
        self.slidebar.setGeometry(MARGIN, self.input_display.height() + int(MARGIN * 1.5), int(MAX_W * 0.8), STEP * 5)

        # keyboard container
        self.keyboard_container = QLabel(self)
        self.keyboard_container.setGeometry(MARGIN, 2 * MARGIN + self.input_display.height() + self.slidebar.height(),
                                            int(MAX_W * 0.65), MAX_H - int(MARGIN * 3.5) - self.input_display.height())
        # keys
        self.keys = [QLabel] * (self._columns * self._rows)
        for i in range(self._rows):
            for j in range(self._columns):
                if i >= len(self.vkeyboard.key_config[j]):
                    continue
                key_button = QLabel(self.keyboard_container)
                key_button.setAlignment(Qt.AlignCenter)
                key_button.setStyleSheet(button_style + "background: white")
                key_button.setText(self.vkeyboard.key_config[j][i])
                font = key_button.font()
                font.setPointSize(STEP * 6)
                key_button.setFont(font)
                self.set_key_geometry(i, j, key_button)
                self.keys[i * self._columns + j] = key_button

        # gesture display
        self.gesture_holder = QLabel(self)
        self.gesture_holder.setGeometry(MAX_W - 150, 200, 80, 80)
        self.gesture_holder.setStyleSheet("background: transparent;")

        # suggestions area
        self.suggestions_container = QLabel(self)
        geom = self.keyboard_container.geometry()
        geom.setX(geom.x() + geom.width() + MARGIN)
        geom.setWidth(int(MAX_W * 0.125))
        self.suggestions_container.setGeometry(geom)
        self.suggestion_labels = [QLabel] * (3)
        for i in range(3):
            suggestion_box = QLabel(self.suggestions_container)
            suggestion_box.setAlignment(Qt.AlignCenter)
            suggestion_box.setStyleSheet(button_style + "background: white")
            suggestion_box.setText("")
            font = suggestion_box.font()
            font.setPointSize(STEP * 6)
            suggestion_box.setFont(font)
            suggestion_box.setGeometry(0,
                                       KEY_M * i + KEY_H * i,
                                       geom.width(), KEY_H)
            self.suggestion_labels[i] = suggestion_box

        # reset imu button
        self.reset_imu_button = QPushButton(self)
        self.reset_imu_button.setText('Reset IMU')
        self.reset_imu_button.setGeometry(MAX_W - 150, 300, 80, 40)
        self.reset_imu_button.setStyleSheet(button_style + "background: white")
        fontParam.setPointSize(10)
        self.reset_imu_button.setFont(fontParam)
        self.reset_imu_button.clicked.connect(lambda: self.reset_imu())

        self.show()
        self.input_display.setFocus()

    def reset_imu(self, yaw=None):
        if yaw is None:
            yaw = self.yaw
        print("Resetting RIGHT yaw to: " + str(yaw))
        self.right_yaw = yaw
        self.left_yaw = (yaw + ANGLE_RANGE) % 360
        self.imu_set = True

    def set_key_geometry(self, i, j, button):
        extra_margin = 0
        extra_size = 0
        if j == self.selected_column and self.keyboard_active:
            extra_size += KEY_EXTENSION
        elif j > self.selected_column and self.keyboard_active:
            extra_margin += KEY_EXTENSION
        button.setGeometry(KEY_M * j + KEY_W * j + i * int(KEY_W / 2) + extra_margin,
                           KEY_M * i + KEY_H * i,
                           KEY_W + extra_size, KEY_H)

    def highlight_column(self):
        for i in range(self._rows):
            for j in range(self._columns):
                if i >= len(self.vkeyboard.key_config[j]):
                    continue
                key_button = self.keys[i * self._columns + j]
                self.set_key_geometry(i, j, key_button)
                if j == self.selected_column and self.keyboard_active:
                    key_button.setStyleSheet(
                        button_style + "background: #" + HIGHLIGHT_PALETTE[self.vkeyboard.votes[i]])
                else:
                    key_button.setStyleSheet(button_style + "background: white")

    def highlight_suggestion_area(self):
        for i in range(3):
            suggestion_box = self.suggestion_labels[i]
            if not self.keyboard_active:
                suggestion_box.setStyleSheet(
                    button_style + "background: #" + HIGHLIGHT_PALETTE[self.suggestion_votes[i]])
            else:
                suggestion_box.setStyleSheet(button_style + "background: white")

    def get_current_column(self):
        key_selection_range = self.keyboard_container.width()
        tip_position = self.tip_position
        passed_columns = self._columns - self.selected_column

        dst_from_right = key_selection_range - tip_position
        if dst_from_right > KEY_EXTENSION + KEY_W + passed_columns * (KEY_W):
            self.selected_column -= 1

        dst_from_left = tip_position
        if dst_from_left > KEY_EXTENSION + KEY_W + self.selected_column * (KEY_W + KEY_M):
            self.selected_column += 1

        self.selected_column = min(self._columns - 1, max(0, self.selected_column))

    def paintEvent(self, event):

        # slide bar
        self.slider_pixmap = QPixmap(MAX_W - 210, 20)
        self.slider_pixmap.fill(Qt.transparent)
        painter = QPainter(self.slider_pixmap)
        path = QPainterPath()
        gradient = QLinearGradient(0, 5, MAX_W - 20, 10)
        gradient.setColorAt(0.0, QColor.fromRgb(0x3498DB))
        gradient.setColorAt(1.0, QColor.fromRgb(0x91cbf2))
        path.addRoundedRect(0, 5, MAX_W - 210, 10, 3, 3)
        painter.fillPath(path, gradient)

        # slider tip
        yaw = self.yaw
        max_width = self.slidebar.width()
        degree = IMUUtils.is_angle_between(yaw, self.right_yaw, self.left_yaw)
        if degree is not None:
            self.tip_position = (1 - degree) * max_width
            self.tip_position = min(self.tip_position, max_width - 40)

        path = QPainterPath()
        path.addRoundedRect(self.tip_position, 0, 20, 20, 2, 2)
        painter.fillPath(path, Qt.black)
        self.slidebar.setPixmap(self.slider_pixmap)

        # highlight column
        key_selection_range = self.keyboard_container.width()
        if self.tip_position > key_selection_range:
            self.keyboard_active = False
        else:
            self.keyboard_active = True
            self.get_current_column()
            self.vkeyboard.get_block_by_Index(self.selected_column)
        self.highlight_suggestion_area()
        self.highlight_column()

        # gesture image
        if self.gesture is not None:
            path = os.path.dirname(__file__) + "/img/" + self.gesture + ".png"
            self.gesture_holder.setStyleSheet("background: url(" + path + ") no-repeat center center fixed; "
                                                                          "background-color: white;")

    def data_send_loop(self, add_data_callback_func):
        self.communicator.data_signal.connect(add_data_callback_func)
        EMGConnector(self.communicator)

    def handle_imu(self, imu_array):
        yaw, pitch, roll = IMUUtils.handleIMUArray(imu_array, 360)
        if not self.imu_set:
            self.reset_imu(yaw)
        self.yaw = yaw

    def receive_data(self, data):

        self.handle_imu(data[8:-1])
        gesture = self.predictor.handleEMG(data[:8])
        if gesture is not None:
            self.gesture = gesture
            if self.keyboard_active:
                self.suggestion_votes = [0] * 3
                input_letter = self.vkeyboard.recordVote(self.gesture)
                if input_letter is not None:

                    if input_letter == "<":
                        # delete last character
                        self.input_display.setText(self.input_display.text()[:-1])
                    else:
                        # append input
                        self.input_display.setText(self.input_display.text() + input_letter)

                    # update suggestions
                    last_word = self.input_display.text().split(" ")[-1]
                    if not 0 == len(last_word):
                        predictions = Dictionary.predict_word(last_word)
                        for i in range(3):
                            self.suggestion_labels[i].setText(predictions[i])
                    else:
                        for i in range(3):
                            self.suggestion_labels[i].setText("")

            elif gesture in KeyboardControl.gesture_config_def:
                option = KeyboardControl.gesture_config_def[gesture] - 1
                self.suggestion_votes[option] += 1
                if self.suggestion_votes[option] == KeyboardControl.MAX_VOTES:
                    self.suggestion_votes = [0] * 3
                    words = self.input_display.text().split(" ")
                    words[-1] = self.suggestion_labels[option].text()
                    new_text = " ".join(words)
                    if 0 != len(new_text):
                        self.input_display.setText(new_text + " ")

        self.update()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    ex = QwertyWidget()
    sys.exit(app.exec_())
