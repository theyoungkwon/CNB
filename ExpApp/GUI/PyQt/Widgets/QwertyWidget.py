import datetime
import os
import sys
import threading

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from EMG.EMGConnector import EMGConnector
from ExpApp.Utils import IMUUtils

from ExpApp.Utils.EasyPredictor import EasyPredictor
from ExpApp.Utils.VKeyboard import VKeyboard
from ExpApp.Utils.datacore_constants import INPUT_SET, KeyboardControl, KERAS_FRAME_LENGTH
from ExpApp.Utils.dictionary import Dictionary
from ExpApp.Utils.MyoKeyLogger import MyoKeyLogger


class Communicate(QObject):
    data_signal = pyqtSignal(list)


ANGLE_RANGE = 70  # 20 .. 45

STEP = 4
MARGIN = STEP * 10
MAX_W = STEP * 400
MAX_H = STEP * 135
KEY_W = STEP * 20
KEY_H = STEP * 20
KEY_M = STEP * 2
KEY_EXTENSION = int(KEY_W * 2)
PICKER_THICKNESS = STEP / 2

KEY_HIGHLIGHT_PALETTE = [
    "cfe1ff",
    "abcaff",
    "7aabff",
]

SUGGESTIONS_HIGHLIGHT_PALETTE = [
    "cffffd",
    "abfffe",
    "7afbff"
]

button_style = "border: 1px outset grey; border-radius: 10px; border-style: outset;"


class QwertyWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.init_communicators()
        self.angle_range = ANGLE_RANGE
        self.gesture = None
        self.max_votes = KeyboardControl.MAX_VOTES
        self.vkeyboard = VKeyboard(config=KeyboardControl.configQ)
        self.model_path = os.path.dirname(__file__) + "/../../../datacore/cnn_qwerty_debug"
        self.interval = 0.9
        self.predictor = EasyPredictor(_set=INPUT_SET, model_path=self.model_path,
                                       interval=self.interval * KERAS_FRAME_LENGTH)
        self._rows = len(self.vkeyboard.key_config[0])
        self._columns = len(self.vkeyboard.key_config)
        self.selected_column = self._columns - 1
        self.init_ui()
        self.right_yaw = 6
        self.left_yaw = 2
        self.yaw = self.right_yaw
        self.imu_set = False
        self.imu_fix = False
        self.tip_position = self.slidebar.width() - 20
        self.suggestion_votes = [0] * 3
        self.current_suggestion = 0
        log_file_name = self.get_log_file_name()
        self.logger = MyoKeyLogger(file_name=log_file_name)

    def get_log_file_name(self):
        # YYYY.MM.DD_HH.MM.SS_VOTES_INTERVAL
        return datetime.datetime.now().strftime("%Y.%m.%d_%H.%M.%S") + "_" + str(self.max_votes) + "_" + str(
            self.interval)

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

        # suggestions area
        keyboard_width = int(MAX_W * 0.65)
        self.suggestions_container = QLabel(self)
        position = QRect(MARGIN, self.input_display.height() + int(1.5 * MARGIN), keyboard_width, KEY_H)
        self.suggestions_container.setGeometry(position)
        self.suggestion_labels = [QLabel] * (3)
        suggestion_box_width = int((keyboard_width - 2 * MARGIN) / 3)
        for i in range(3):
            suggestion_box = QLabel(self.suggestions_container)
            suggestion_box.setAlignment(Qt.AlignCenter)
            suggestion_box.setStyleSheet(button_style + "background: white")
            suggestion_box.setText("")
            font = suggestion_box.font()
            font.setPointSize(STEP * 5)
            suggestion_box.setFont(font)
            suggestion_box.setGeometry(i * suggestion_box_width + i * MARGIN,
                                       0, suggestion_box_width, KEY_H)
            self.suggestion_labels[i] = suggestion_box

        # sliding tip representing MYO orientation
        self.slidebar = QLabel(self)
        self.slidebar.setGeometry(MARGIN, self.input_display.height() + int(MARGIN * 4), keyboard_width, STEP * 5)

        # keyboard container
        self.keyboard_container = QLabel(self)
        self.keyboard_container.setGeometry(MARGIN, int(
            2.5 * MARGIN) + self.input_display.height() + self.slidebar.height() + KEY_H,
                                            keyboard_width, MAX_H - int(MARGIN * 3.5) - self.input_display.height())
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

        # Settings container
        self.settings_container = QLabel(self)
        self.settings_container.setGeometry(MARGIN * 2 + keyboard_width,
                                            self.input_display.height() + int(1.5 * MARGIN),
                                            MAX_W - keyboard_width - 3 * MARGIN,
                                            MAX_H - int(3.5 * MARGIN))
        setting_width = self.settings_container.width()

        # gesture display
        self.gesture_holder = QLabel(self.settings_container)
        self.gesture_holder.setGeometry(int((setting_width - 80) / 2), 0, 80, 80)
        self.gesture_holder.setStyleSheet("background: transparent;")
        current_height = self.gesture_holder.height() + MARGIN // 2

        # reset imu button
        self.reset_imu_button = QPushButton(self.settings_container)
        self.reset_imu_button.setText('Reset IMU')
        self.reset_imu_button.setGeometry(MARGIN, current_height, setting_width - MARGIN * 2, MARGIN)
        self.reset_imu_button.setStyleSheet(button_style + "background: white")
        fontParam.setPointSize(STEP * 4)
        self.reset_imu_button.setFont(fontParam)
        self.reset_imu_button.clicked.connect(lambda: self.reset_imu())
        current_height += MARGIN // 2 + self.reset_imu_button.height()

        # votes input
        self.votes_label = QLabel(self.settings_container)
        self.votes_label.setFont(fontParam)
        self.votes_label.setText("Votes:")
        self.votes_label.setGeometry(MARGIN, current_height, setting_width // 2, MARGIN)
        self.votes_input = QSpinBox(self.settings_container)
        self.votes_input.setValue(self.max_votes)
        self.votes_input.setSingleStep(1)
        self.votes_input.setMaximum(3)
        self.votes_input.setMinimum(1)
        self.votes_input.valueChanged.connect(self.set_max_votes)
        self.votes_input.setFont(fontParam)
        self.votes_input.setGeometry(setting_width // 2 - MARGIN, current_height, setting_width // 2, MARGIN)
        current_height += MARGIN // 2 + self.votes_input.height()

        # interval input
        self.interval_label = QLabel(self.settings_container)
        self.interval_label.setFont(fontParam)
        self.interval_label.setText("Interval:")
        self.interval_label.setGeometry(MARGIN, current_height, setting_width // 2, MARGIN)
        self.interval_input = QDoubleSpinBox(self.settings_container)
        self.interval_input.setValue(self.interval)
        self.interval_input.setSingleStep(0.1)
        self.interval_input.setMaximum(2)
        self.interval_input.setMinimum(0.1)
        self.interval_input.valueChanged.connect(self.set_interval)
        self.interval_input.setFont(fontParam)
        self.interval_input.setGeometry(setting_width // 2 - MARGIN, current_height, setting_width // 2, MARGIN)
        current_height += MARGIN // 2 + self.interval_input.height()

        # interval input
        self.angle_label = QLabel(self.settings_container)
        self.angle_label.setFont(fontParam)
        self.angle_label.setText("Angle:")
        self.angle_label.setGeometry(MARGIN, current_height, setting_width // 2, MARGIN)
        self.angle_input = QDoubleSpinBox(self.settings_container)
        self.angle_input.setValue(self.angle_range)
        self.angle_input.setSingleStep(1)
        self.angle_input.setMinimum(10)
        self.angle_input.setMaximum(90)
        self.angle_input.valueChanged.connect(self.set_angle)
        self.angle_input.setFont(fontParam)
        self.angle_input.setGeometry(setting_width // 2 - MARGIN, current_height, setting_width // 2, MARGIN)
        current_height += MARGIN // 2 + self.interval_input.height()

        # record button
        self.record_button = QPushButton(self.settings_container)
        self.record_button.setText('Record')
        self.record_button.setGeometry(MARGIN, current_height, setting_width - MARGIN * 2, MARGIN)
        self.record_button.setStyleSheet(button_style + "background: white")
        self.record_button.setFont(fontParam)
        self.record_button.clicked.connect(lambda: self.logger.stop())
        current_height += MARGIN // 2 + self.reset_imu_button.height()

        self.show()
        self.input_display.setFocus()

    def set_angle(self):
        self.angle_range = self.angle_input.value()
        self.reset_imu()

    def set_interval(self):
        self.interval = self.interval_input.value()
        self.predictor = EasyPredictor(_set=INPUT_SET, model_path=self.model_path,
                                       interval=self.interval * KERAS_FRAME_LENGTH)
        self.logger = MyoKeyLogger(self.get_log_file_name())

    def set_max_votes(self):
        self.max_votes = self.votes_input.value()
        self.vkeyboard = VKeyboard(config=KeyboardControl.configQ, max_votes=self.max_votes)
        self.logger = MyoKeyLogger(self.get_log_file_name())

    def reset_interval(self):
        self.predictor.i = 0

    def reset_imu(self, yaw=None):
        if yaw is None:
            yaw = self.yaw
        print("Resetting RIGHT yaw to: " + str(yaw))
        self.right_yaw = yaw
        self.left_yaw = (yaw + self.angle_range) % 360
        self.imu_set = True

    def set_key_geometry(self, i, j, button):
        extra_margin = 0
        extra_size = 0
        if j == self.selected_column:
            extra_size += KEY_EXTENSION
        elif j > self.selected_column:
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
                if j == self.selected_column:
                    key_button.setStyleSheet(
                        button_style + "background: #" + KEY_HIGHLIGHT_PALETTE[self.vkeyboard.votes[i]])
                else:
                    key_button.setStyleSheet(button_style + "background: white")

    def highlight_suggestion_area(self):
        for i in range(3):
            suggestion_box = self.suggestion_labels[i]
            position = suggestion_box.geometry()
            if position.x() < self.tip_position <= position.x() + position.width():
                if i != self.current_suggestion:
                    self.current_suggestion = i
                    self.suggestion_votes = [0] * 3
                suggestion_box.setStyleSheet(
                    button_style + "background: #" + SUGGESTIONS_HIGHLIGHT_PALETTE[self.suggestion_votes[i]])
            else:
                suggestion_box.setStyleSheet(button_style + "background: white")

    def get_current_column(self):
        key_selection_range = self.keyboard_container.width()
        tip_position = self.tip_position
        passed_columns = self._columns - self.selected_column

        dst_from_right = key_selection_range - tip_position
        if dst_from_right > KEY_EXTENSION + KEY_W + passed_columns * (KEY_W):
            self.selected_column -= 1
            self.reset_interval()

        dst_from_left = tip_position
        if dst_from_left > KEY_EXTENSION + KEY_W + self.selected_column * (KEY_W + KEY_M):
            self.selected_column += 1
            self.reset_interval()

        self.selected_column = min(self._columns - 1, max(0, self.selected_column))

    def paintEvent(self, event):

        # slide bar
        slider_width = self.slidebar.width()
        self.slider_pixmap = QPixmap(slider_width, 20)
        self.slider_pixmap.fill(Qt.transparent)
        painter = QPainter(self.slider_pixmap)
        path = QPainterPath()
        gradient = QLinearGradient(0, 5, slider_width - 20, 10)
        gradient.setColorAt(0.0, QColor.fromRgb(0x3498DB))
        gradient.setColorAt(1.0, QColor.fromRgb(0x91cbf2))
        path.addRoundedRect(0, 5, slider_width, 10, 3, 3)
        painter.fillPath(path, gradient)

        # slider tip
        yaw = self.yaw
        degree = IMUUtils.is_angle_between(yaw, self.right_yaw, self.left_yaw)  # 0-1 if inside the angle
        if degree is not None:
            self.tip_position = (1 - degree) * slider_width
            self.tip_position = min(self.tip_position, slider_width - 20)

        path = QPainterPath()
        path.addRoundedRect(self.tip_position, 0, 20, 20, 2, 2)
        painter.fillPath(path, Qt.black)
        self.slidebar.setPixmap(self.slider_pixmap)

        # highlight column
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
            input_letter = self.vkeyboard.recordVote(self.gesture)
            if gesture != "palm":
                self.logger.record_gesture(gesture)
            if input_letter is not None:
                self.logger.record_letter(input_letter)
                self.suggestion_votes = [0] * 3
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

            # select suggestion
            if gesture == "thumb123":
                self.suggestion_votes[self.current_suggestion] += 1
                self.highlight_suggestion_area()
                if self.suggestion_votes[self.current_suggestion] == self.max_votes:
                    self.suggestion_votes = [0] * 3
                    words = self.input_display.text().split(" ")
                    words[-1] = self.suggestion_labels[self.current_suggestion].text()
                    new_text = " ".join(words)
                    if 0 != len(new_text):
                        self.input_display.setText(new_text + " ")
                        for i in range(3):
                            self.suggestion_labels[i].setText("")

        self.update()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    ex = QwertyWidget()
    sys.exit(app.exec_())
